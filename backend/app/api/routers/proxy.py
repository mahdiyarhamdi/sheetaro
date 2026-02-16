"""Proxy management API router for V2Ray/Xray configuration."""

import json
import logging
import asyncio
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_admin_user
from app.utils.v2ray_parser import parse_v2ray_link, SOCKS_INBOUND_PORT

logger = logging.getLogger(__name__)

router = APIRouter()

PROXY_CONFIG_DIR = Path("/app/proxy_config")
XRAY_CONFIG_PATH = PROXY_CONFIG_DIR / "config.json"
PROXY_STATUS_PATH = PROXY_CONFIG_DIR / "status.json"

SOCKS_PROXY_URL = f"socks5://xray:{SOCKS_INBOUND_PORT}"
TELEGRAM_TEST_URL = "https://api.telegram.org"


class ProxyLinkRequest(BaseModel):
    """Request to set a V2Ray proxy link."""
    link: str


class ProxyStatusResponse(BaseModel):
    """Proxy status response."""
    enabled: bool
    link: str | None = None
    protocol: str | None = None
    server: str | None = None
    connected: bool = False


def _ensure_config_dir():
    """Ensure proxy config directory exists."""
    PROXY_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_status() -> dict:
    """Read current proxy status."""
    if PROXY_STATUS_PATH.exists():
        try:
            return json.loads(PROXY_STATUS_PATH.read_text())
        except Exception:
            pass
    return {"enabled": False}


def _write_status(data: dict):
    """Write proxy status."""
    _ensure_config_dir()
    PROXY_STATUS_PATH.write_text(json.dumps(data, indent=2))


def _write_xray_config(config: dict):
    """Write xray configuration."""
    _ensure_config_dir()
    XRAY_CONFIG_PATH.write_text(json.dumps(config, indent=2))


def _extract_server_info(link: str) -> tuple[str, str]:
    """Extract protocol and server address from a V2Ray link."""
    link = link.strip()
    if link.startswith("vmess://"):
        protocol = "vmess"
    elif link.startswith("vless://"):
        protocol = "vless"
    elif link.startswith("trojan://"):
        protocol = "trojan"
    elif link.startswith("ss://"):
        protocol = "shadowsocks"
    else:
        protocol = "unknown"

    # Try to extract server from outbound config
    try:
        config = parse_v2ray_link(link)
        outbound = config["outbounds"][0]
        settings = outbound.get("settings", {})
        if "vnext" in settings:
            server = settings["vnext"][0]["address"]
        elif "servers" in settings:
            server = settings["servers"][0]["address"]
        else:
            server = "unknown"
    except Exception:
        server = "unknown"

    return protocol, server


async def _test_proxy_connectivity(timeout: float = 15.0) -> tuple[bool, float, str]:
    """Test proxy connectivity to Telegram API. Returns (success, latency_ms, message)."""
    try:
        async with httpx.AsyncClient(
            proxy=SOCKS_PROXY_URL,
            timeout=httpx.Timeout(timeout),
            verify=False,
        ) as client:
            import time
            start = time.monotonic()
            response = await client.get(TELEGRAM_TEST_URL)
            latency = (time.monotonic() - start) * 1000
            if response.status_code in (200, 404):
                return True, latency, f"Connected ({latency:.0f}ms)"
            return False, latency, f"HTTP {response.status_code}"
    except httpx.ProxyError as e:
        return False, 0, f"Proxy error: {str(e)[:100]}"
    except httpx.ConnectError as e:
        return False, 0, f"Connection failed: {str(e)[:100]}"
    except httpx.TimeoutException:
        return False, 0, f"Timeout after {timeout}s"
    except Exception as e:
        return False, 0, f"Error: {str(e)[:100]}"


@router.get(
    "/admin/proxy",
    response_model=ProxyStatusResponse,
    summary="Get proxy status",
)
async def get_proxy_status(
    _: dict = Depends(get_current_admin_user),
) -> ProxyStatusResponse:
    """Get current V2Ray proxy configuration status."""
    st = _read_status()
    resp = ProxyStatusResponse(
        enabled=st.get("enabled", False),
        link=st.get("link"),
        protocol=st.get("protocol"),
        server=st.get("server"),
        connected=False,
    )

    # Quick connectivity check if enabled
    if resp.enabled:
        try:
            ok, _, _ = await asyncio.wait_for(
                _test_proxy_connectivity(timeout=8),
                timeout=10,
            )
            resp.connected = ok
        except Exception:
            resp.connected = False

    return resp


@router.post(
    "/admin/proxy",
    response_model=ProxyStatusResponse,
    summary="Set V2Ray proxy link",
)
async def set_proxy(
    body: ProxyLinkRequest,
    _: dict = Depends(get_current_admin_user),
) -> ProxyStatusResponse:
    """Parse a V2Ray link, generate xray config, and save it."""
    try:
        config = parse_v2ray_link(body.link)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid V2Ray link: {str(e)}",
        )

    protocol, server = _extract_server_info(body.link)

    # Write xray config
    _write_xray_config(config)

    # Write status
    status_data = {
        "enabled": True,
        "link": body.link,
        "protocol": protocol,
        "server": server,
    }
    _write_status(status_data)

    logger.info(f"Proxy configured: {protocol} via {server}")

    return ProxyStatusResponse(
        enabled=True,
        link=body.link,
        protocol=protocol,
        server=server,
        connected=False,
    )


@router.post(
    "/admin/proxy/test",
    summary="Test proxy connectivity",
)
async def test_proxy(
    _: dict = Depends(get_current_admin_user),
) -> dict:
    """Test the current proxy configuration by connecting to Telegram API."""
    st = _read_status()
    if not st.get("enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No proxy configured",
        )

    ok, latency, message = await _test_proxy_connectivity(timeout=15)

    return {
        "success": ok,
        "latency_ms": round(latency),
        "message": message,
    }


@router.delete(
    "/admin/proxy",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove proxy configuration",
)
async def remove_proxy(
    _: dict = Depends(get_current_admin_user),
) -> None:
    """Remove the V2Ray proxy configuration."""
    _write_status({"enabled": False})
    # Write empty xray config
    empty_config = {
        "log": {"loglevel": "warning"},
        "inbounds": [],
        "outbounds": [{"protocol": "freedom"}],
    }
    _write_xray_config(empty_config)
    logger.info("Proxy configuration removed")


@router.post(
    "/admin/proxy/restart",
    summary="Signal services to restart and pick up new proxy config",
)
async def restart_proxy_services(
    _: dict = Depends(get_current_admin_user),
) -> dict:
    """Write a restart signal file that bot checks on next poll cycle."""
    _ensure_config_dir()
    # Write a signal file; the bot's wrapper script detects this and exits,
    # Docker restart policy will bring it back with new config.
    signal_path = PROXY_CONFIG_DIR / "restart_signal"
    signal_path.write_text("restart")
    logger.info("Restart signal written for bot")
    return {"message": "Restart signal sent. Bot will restart within ~30 seconds."}
