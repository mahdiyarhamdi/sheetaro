"""Automated backup service for Sheetaro.

Creates a backup of the PostgreSQL database and uploads directory every 6 hours,
then sends the backup file to admin users via Telegram bot.
"""

import os
import sys
import time
import json
import asyncio
import logging
import subprocess
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime

import httpx

# ── Config ──────────────────────────────────────────────────────
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL_HOURS", "6")) * 3600
BACKUP_DIR = Path("/backups")
UPLOADS_DIR = Path("/uploads")
MAX_RETENTION = int(os.getenv("BACKUP_RETENTION_COUNT", "10"))

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "sheetaro")
POSTGRES_USER = os.getenv("POSTGRES_USER", "sheetaro_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")  # e.g. http://193.228.90.237:3005

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("backup")


# ── Helpers ─────────────────────────────────────────────────────

def _get_proxy_url() -> str | None:
    """Read SOCKS5 proxy URL from shared xray config (if enabled)."""
    status_path = Path("/proxy_config/status.json")
    if status_path.exists():
        try:
            data = json.loads(status_path.read_text())
            if data.get("enabled"):
                return "socks5://xray:10808"
        except Exception:
            pass
    return None


def _get_admin_telegram_ids() -> list[int]:
    """Query admin Telegram IDs directly from PostgreSQL."""
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = POSTGRES_PASSWORD
        result = subprocess.run(
            [
                "psql",
                "-h", POSTGRES_HOST,
                "-U", POSTGRES_USER,
                "-d", POSTGRES_DB,
                "-t", "-A",
                "-c", "SELECT telegram_id FROM users WHERE role = 'ADMIN' AND telegram_id IS NOT NULL",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        ids: list[int] = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line:
                try:
                    ids.append(int(line))
                except ValueError:
                    pass
        return ids
    except Exception as e:
        logger.error("Failed to query admin Telegram IDs: %s", e)
        return []


# ── Core ────────────────────────────────────────────────────────

def create_backup() -> Path | None:
    """Create a .tar.gz archive containing the DB dump and uploads."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"sheetaro_backup_{timestamp}.tar.gz"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 1. Database dump
        db_dump = tmp / "database.sql"
        logger.info("Dumping PostgreSQL database...")
        try:
            env = os.environ.copy()
            env["PGPASSWORD"] = POSTGRES_PASSWORD
            proc = subprocess.run(
                [
                    "pg_dump",
                    "-h", POSTGRES_HOST,
                    "-U", POSTGRES_USER,
                    "-d", POSTGRES_DB,
                    "--clean",
                    "--if-exists",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                env=env,
            )
            if proc.returncode != 0:
                logger.error("pg_dump failed: %s", proc.stderr[:500])
                return None
            db_dump.write_text(proc.stdout)
            logger.info("DB dump: %.1f KB", db_dump.stat().st_size / 1024)
        except Exception as e:
            logger.error("Database dump error: %s", e)
            return None

        # 2. Create tar.gz
        logger.info("Creating archive...")
        try:
            with tarfile.open(str(backup_path), "w:gz") as tar:
                tar.add(str(db_dump), arcname="database.sql")
                if UPLOADS_DIR.exists() and any(UPLOADS_DIR.iterdir()):
                    tar.add(str(UPLOADS_DIR), arcname="uploads")
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info("Backup ready: %s (%.1f MB)", backup_path.name, size_mb)
            return backup_path
        except Exception as e:
            logger.error("Archive creation error: %s", e)
            return None


def _get_download_url(filename: str) -> str:
    """Build the public download URL for a backup file."""
    base = PUBLIC_BASE_URL.rstrip("/") if PUBLIC_BASE_URL else "http://localhost:3005"
    return f"{base}/api/v1/admin/backups/{filename}"


async def send_to_admins(backup_path: Path) -> None:
    """Send a download link for the backup to every admin on Telegram."""
    admin_ids = _get_admin_telegram_ids()
    if not admin_ids:
        logger.warning("No admin Telegram IDs found — skipping notification")
        return

    proxy_url = _get_proxy_url()
    file_size = backup_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    ts = datetime.now().strftime("%Y/%m/%d  %H:%M")
    download_url = _get_download_url(backup_path.name)

    message = (
        f"🗄 بکاپ خودکار شیتارو\n"
        f"📅 {ts}\n"
        f"💾 {size_mb:.1f} MB\n\n"
        f"شامل: دیتابیس + تصاویر و فایل‌ها\n\n"
        f"📥 لینک دانلود:\n{download_url}\n\n"
        f"⚠️ برای دانلود باید با حساب ادمین لاگین باشید."
    )

    client_kwargs: dict = dict(timeout=httpx.Timeout(30.0), verify=False)
    if proxy_url:
        client_kwargs["proxy"] = proxy_url

    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    async with httpx.AsyncClient(**client_kwargs) as client:
        for aid in admin_ids:
            try:
                resp = await client.post(
                    f"{base}/sendMessage",
                    json={"chat_id": aid, "text": message},
                )
                if resp.status_code == 200:
                    logger.info("Backup link sent to admin %s", aid)
                else:
                    logger.error("Telegram error for %s: %s", aid, resp.text[:200])
            except Exception as e:
                logger.error("Failed to contact admin %s: %s", aid, e)


def cleanup_old_backups() -> None:
    """Keep only the N most recent backup files."""
    backups = sorted(BACKUP_DIR.glob("sheetaro_backup_*.tar.gz"), reverse=True)
    for old in backups[MAX_RETENTION:]:
        try:
            old.unlink()
            logger.info("Removed old backup: %s", old.name)
        except Exception as e:
            logger.error("Cleanup error for %s: %s", old.name, e)


async def run_backup() -> None:
    """Execute one full backup cycle."""
    logger.info("=== Backup cycle started ===")
    backup_path = create_backup()
    if backup_path:
        await send_to_admins(backup_path)
        cleanup_old_backups()
        logger.info("=== Backup cycle complete ===")
    else:
        logger.error("=== Backup cycle FAILED ===")


# ── Main loop ───────────────────────────────────────────────────

def main() -> None:
    """Run backup on startup (after a short delay) and then every N hours."""
    hours = BACKUP_INTERVAL / 3600
    logger.info("Backup service started — interval: %.0fh, retention: %d", hours, MAX_RETENTION)

    # Wait for other services to be ready
    logger.info("Waiting 60s for services to initialise...")
    time.sleep(60)

    while True:
        try:
            asyncio.run(run_backup())
        except Exception as e:
            logger.error("Unhandled error in backup cycle: %s", e)

        logger.info("Next backup in %.0f hours", hours)
        time.sleep(BACKUP_INTERVAL)


if __name__ == "__main__":
    main()
