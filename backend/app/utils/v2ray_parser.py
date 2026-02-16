"""V2Ray/Xray link parser - converts vmess/vless/trojan/ss links to xray config."""

import base64
import json
import re
from urllib.parse import urlparse, parse_qs, unquote


SOCKS_INBOUND_PORT = 10808


def parse_v2ray_link(link: str) -> dict:
    """Parse a V2Ray link and return xray-core compatible config JSON."""
    link = link.strip()

    if link.startswith("vmess://"):
        return _parse_vmess(link)
    elif link.startswith("vless://"):
        return _parse_vless(link)
    elif link.startswith("trojan://"):
        return _parse_trojan(link)
    elif link.startswith("ss://"):
        return _parse_shadowsocks(link)
    else:
        raise ValueError(f"Unsupported protocol. Supported: vmess://, vless://, trojan://, ss://")


def _base_config(outbound: dict) -> dict:
    """Wrap an outbound in a full xray config with SOCKS inbound."""
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "port": SOCKS_INBOUND_PORT,
                "listen": "0.0.0.0",
                "protocol": "socks",
                "settings": {"auth": "noauth", "udp": True},
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls"],
                },
            }
        ],
        "outbounds": [outbound],
    }


def _build_stream_settings(
    net: str = "tcp",
    tls: str = "",
    sni: str = "",
    host: str = "",
    path: str = "",
    alpn: str = "",
    fp: str = "",
    header_type: str = "none",
    service_name: str = "",
    authority: str = "",
    flow: str = "",
    **_extra,
) -> dict:
    """Build streamSettings block for xray config."""
    ss: dict = {"network": net}

    # TLS / Reality
    if tls in ("tls", "xtls"):
        tls_settings: dict = {}
        if sni:
            tls_settings["serverName"] = sni
        if alpn:
            tls_settings["alpn"] = alpn.split(",")
        if fp:
            tls_settings["fingerprint"] = fp
        tls_settings["allowInsecure"] = True
        ss["security"] = "tls"
        ss["tlsSettings"] = tls_settings
    elif tls == "reality":
        reality: dict = {}
        if sni:
            reality["serverName"] = sni
        if fp:
            reality["fingerprint"] = fp
        ss["security"] = "reality"
        ss["realitySettings"] = reality
    else:
        ss["security"] = "none"

    # Transport
    if net == "ws":
        ws: dict = {}
        if path:
            ws["path"] = path
        if host:
            ws["headers"] = {"Host": host}
        ss["wsSettings"] = ws
    elif net == "grpc":
        grpc: dict = {}
        if service_name:
            grpc["serviceName"] = service_name
        if authority:
            grpc["authority"] = authority
        ss["grpcSettings"] = grpc
    elif net == "tcp":
        if header_type == "http":
            ss["tcpSettings"] = {
                "header": {
                    "type": "http",
                    "request": {
                        "path": [path] if path else ["/"],
                        "headers": {"Host": [host]} if host else {},
                    },
                }
            }
    elif net == "h2" or net == "http":
        h2: dict = {}
        if path:
            h2["path"] = path
        if host:
            h2["host"] = [host]
        ss["httpSettings"] = h2

    return ss


# ──────── VMess ────────

def _parse_vmess(link: str) -> dict:
    """Parse vmess://BASE64 link."""
    raw = link[len("vmess://"):]
    # Some links have padding issues
    raw += "=" * (-len(raw) % 4)
    try:
        data = json.loads(base64.b64decode(raw).decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid vmess link: {e}")

    address = data.get("add", "")
    port = int(data.get("port", 443))
    uid = data.get("id", "")
    aid = int(data.get("aid", 0))
    security = data.get("scy", "auto")
    net = data.get("net", "tcp")
    tls = data.get("tls", "")
    sni = data.get("sni", "") or data.get("host", "")
    host = data.get("host", "")
    path = data.get("path", "")
    header_type = data.get("type", "none")
    fp = data.get("fp", "")
    alpn = data.get("alpn", "")

    if not address or not uid:
        raise ValueError("vmess link missing address or id")

    outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": address,
                    "port": port,
                    "users": [
                        {
                            "id": uid,
                            "alterId": aid,
                            "security": security,
                        }
                    ],
                }
            ]
        },
        "streamSettings": _build_stream_settings(
            net=net, tls=tls, sni=sni, host=host, path=path,
            header_type=header_type, fp=fp, alpn=alpn,
        ),
    }

    return _base_config(outbound)


# ──────── VLESS ────────

def _parse_vless(link: str) -> dict:
    """Parse vless://UUID@server:port?params#name link."""
    # Remove fragment (name)
    url_str = link.split("#")[0]
    # Parse as URI
    match = re.match(r"vless://([^@]+)@([^:]+):(\d+)\??(.*)", url_str)
    if not match:
        raise ValueError("Invalid vless link format")

    uid, address, port_str, query_str = match.groups()
    port = int(port_str)
    params = parse_qs(query_str)

    def p(key: str, default: str = "") -> str:
        return params.get(key, [default])[0]

    flow = p("flow")
    outbound: dict = {
        "protocol": "vless",
        "settings": {
            "vnext": [
                {
                    "address": address,
                    "port": port,
                    "users": [
                        {
                            "id": uid,
                            "encryption": p("encryption", "none"),
                            **({"flow": flow} if flow else {}),
                        }
                    ],
                }
            ]
        },
        "streamSettings": _build_stream_settings(
            net=p("type", "tcp"),
            tls=p("security"),
            sni=p("sni"),
            host=p("host"),
            path=p("path"),
            alpn=p("alpn"),
            fp=p("fp"),
            service_name=p("serviceName"),
            authority=p("authority"),
            flow=flow,
        ),
    }

    return _base_config(outbound)


# ──────── Trojan ────────

def _parse_trojan(link: str) -> dict:
    """Parse trojan://password@server:port?params#name link."""
    url_str = link.split("#")[0]
    match = re.match(r"trojan://([^@]+)@([^:]+):(\d+)\??(.*)", url_str)
    if not match:
        raise ValueError("Invalid trojan link format")

    password, address, port_str, query_str = match.groups()
    password = unquote(password)
    port = int(port_str)
    params = parse_qs(query_str)

    def p(key: str, default: str = "") -> str:
        return params.get(key, [default])[0]

    outbound = {
        "protocol": "trojan",
        "settings": {
            "servers": [
                {
                    "address": address,
                    "port": port,
                    "password": password,
                }
            ]
        },
        "streamSettings": _build_stream_settings(
            net=p("type", "tcp"),
            tls=p("security", "tls"),
            sni=p("sni", address),
            host=p("host"),
            path=p("path"),
            alpn=p("alpn"),
            fp=p("fp"),
            service_name=p("serviceName"),
        ),
    }

    return _base_config(outbound)


# ──────── Shadowsocks ────────

def _parse_shadowsocks(link: str) -> dict:
    """Parse ss://BASE64@server:port#name or ss://METHOD:PASSWORD@server:port#name."""
    raw = link[len("ss://"):].split("#")[0]

    # Format 1: ss://BASE64@server:port
    if "@" in raw:
        user_part, server_part = raw.rsplit("@", 1)
        # Try base64 decode the user part
        try:
            user_part += "=" * (-len(user_part) % 4)
            decoded = base64.b64decode(user_part).decode("utf-8")
            method, password = decoded.split(":", 1)
        except Exception:
            method, password = user_part.split(":", 1)
        address, port_str = server_part.rsplit(":", 1)
    else:
        # Format 2: ss://BASE64 (everything encoded)
        try:
            raw += "=" * (-len(raw) % 4)
            decoded = base64.b64decode(raw).decode("utf-8")
            match = re.match(r"([^:]+):([^@]+)@([^:]+):(\d+)", decoded)
            if not match:
                raise ValueError("Cannot parse ss link")
            method, password, address, port_str = match.groups()
        except Exception as e:
            raise ValueError(f"Invalid ss link: {e}")

    port = int(port_str)

    outbound = {
        "protocol": "shadowsocks",
        "settings": {
            "servers": [
                {
                    "address": address,
                    "port": port,
                    "method": method,
                    "password": password,
                }
            ]
        },
    }

    return _base_config(outbound)
