"""Small helpers shared by the proxy and dashboard."""
import base64
import socket
from urllib.parse import urlparse


def parse_http_request(raw: bytes):
    """Parse the first chunk of an HTTP request.

    Returns (method, url, headers_dict, body_bytes) or None on failure.
    """
    if not raw:
        return None

    header_end = raw.find(b"\r\n\r\n")
    if header_end == -1:
        return None

    head = raw[:header_end].decode("utf-8", errors="ignore")
    body = raw[header_end + 4:]
    lines = head.splitlines()
    if not lines:
        return None

    parts = lines[0].split()
    if len(parts) < 2:
        return None

    method, url = parts[0], parts[1]
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
    return method, url, headers, body


def normalize_url(url: str) -> str:
    if not url.lower().startswith(("http://", "https://")):
        return "http://" + url
    return url


def check_basic_auth(header_value: str, expected_user: str, expected_password: str) -> bool:
    if not header_value:
        return False
    try:
        scheme, token = header_value.split()
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(token).decode("utf-8", errors="ignore")
        user, password = decoded.split(":", 1)
        return user == expected_user and password == expected_password
    except Exception:
        return False


def is_blacklisted(url: str, blacklist) -> bool:
    """Match the URL's host against any entry in the blacklist (incl. subdomains)."""
    host = urlparse(url).hostname
    if not host:
        # CONNECT form: host:port
        host = url.split(":", 1)[0]
    if not host:
        return False
    host = host.lower()
    for bl in blacklist:
        bl = bl.lower()
        if host == bl or host.endswith("." + bl):
            return True
    return False


def is_content_type_blocked(content_type: str, blocked_list) -> bool:
    """Match a Content-Type header (e.g. 'image/jpeg; charset=utf-8') against
    the configured block list. Supports prefix wildcards like 'image/*'."""
    if not content_type or not blocked_list:
        return False
    primary = content_type.split(";", 1)[0].strip().lower()
    for entry in blocked_list:
        entry = entry.strip().lower()
        if not entry:
            continue
        if entry == primary:
            return True
        if entry.endswith("/*"):
            if primary.startswith(entry[:-1]):
                return True
    return False


def safe_close(sock: socket.socket | None):
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass
