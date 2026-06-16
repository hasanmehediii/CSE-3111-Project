"""HTTP request handling: parse, authenticate, filter, cache, forward.

`handle_client` is the per-connection entry point called by the server loop
in `proxy_server.py`.
"""
import datetime
import socket
import traceback

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from proxy.cache_manager import cache
from proxy.config import config
from proxy.request_log import request_log
from proxy.stats import stats
from proxy.utils import (
    check_basic_auth,
    is_blacklisted,
    is_content_type_blocked,
    normalize_url,
    parse_http_request,
    safe_close,
)
from proxy.tunnel import tunnel_traffic

# A Session is created once and reused across connections. This avoids
# the per-connection cost of building a Retry strategy + adapters.
_session: requests.Session | None = None


def get_session() -> requests.Session:
    global _session
    if _session is not None:
        return _session

    retry_cfg = config.get("retries", {}) or {}
    strategy = Retry(
        total=int(retry_cfg.get("total", 3)),
        backoff_factor=float(retry_cfg.get("backoff_factor", 0.5)),
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
    )
    adapter = HTTPAdapter(max_retries=strategy)
    sess = requests.Session()
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    # Prevent infinite proxy loops if anything in the app uses requests
    sess.proxies = {}
    _session = sess
    return sess


def reset_session():
    """Used by tests; drops the cached Session so a fresh one is built."""
    global _session
    if _session is not None:
        try:
            _session.close()
        except Exception:
            pass
    _session = None


def _send_407(conn):
    body = (
        b"HTTP/1.1 407 Proxy Authentication Required\r\n"
        b'Proxy-Authenticate: Basic realm="Proxy"\r\n'
        b"Content-Length: 0\r\n\r\n"
    )
    try:
        conn.sendall(body)
    except OSError:
        pass


def _send_simple(conn, status_line, body=b""):
    payload = status_line.encode() + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\nConnection: close\r\n\r\n" + body
    try:
        conn.sendall(payload)
    except OSError:
        pass


def _build_proxy_response(response: requests.Response) -> bytes:
    """Convert a requests.Response into raw HTTP/1.1 bytes suitable for caching."""
    head = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
    skip = {"transfer-encoding", "content-encoding", "connection", "keep-alive", "proxy-connection"}
    for key, value in response.headers.items():
        if key.lower() in skip:
            continue
        head += f"{key}: {value}\r\n"
    head += "Connection: close\r\n\r\n"
    return head.encode("utf-8") + response.content


def handle_client(conn: socket.socket, addr):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "method": "",
        "url": "",
        "status": "",
        "source": "",
        "client": f"{addr[0]}:{addr[1]}" if addr else "",
    }

    try:
        try:
            request_data = conn.recv(65536)
        except OSError:
            return

        parsed = parse_http_request(request_data)
        if parsed is None:
            _send_simple(conn, "HTTP/1.1 400 Bad Request")
            return

        method, url, headers, _body = parsed
        log_entry["method"] = method
        log_entry["url"] = url

        # ---- Authentication ----
        proxy_user = config.get("proxy_user")
        proxy_password = config.get("proxy_password")
        if proxy_user:
            if not check_basic_auth(headers.get("Proxy-Authorization", ""), proxy_user, proxy_password or ""):
                _send_407(conn)
                log_entry["status"] = "407 Proxy Auth Required"
                log_entry["source"] = "auth"
                request_log.add(log_entry)
                return

        # ---- Domain blacklist (applies to both GET and CONNECT) ----
        if is_blacklisted(url, config.get("blacklist", []) or []):
            stats.record_blacklist()
            log_entry["status"] = "403 Forbidden"
            log_entry["source"] = "blacklist"
            request_log.add(log_entry)
            body = b"<h1>403 Forbidden</h1><p>This site is blocked by proxy policy.</p>"
            _send_simple(conn, "HTTP/1.1 403 Forbidden", body)
            return

        # ---- HTTPS tunnel ----
        if method == "CONNECT":
            log_entry["source"] = "tunnel"
            try:
                host, _, port_s = url.partition(":")
                dest_port = int(port_s or 443)
                upstream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                upstream.settimeout(10)
                upstream.connect((host, dest_port))
                conn.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                log_entry["status"] = "200 Connection established"
                tunnel_traffic(conn, upstream)
            except Exception:
                traceback.print_exc()
                stats.record_error()
                log_entry["status"] = "502 Bad Gateway"
                try:
                    conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                except OSError:
                    pass
            finally:
                request_log.add(log_entry)
            return

        # ---- HTTP methods ----
        full_url = normalize_url(url)

        if method == "GET":
            # Cache lookup
            cached = cache.get(full_url)
            if cached:
                stats.record_hit(len(cached))
                stats.update_peak(cache.size())
                log_entry["source"] = "cache"
                log_entry["status"] = "200 OK (cached)"
                try:
                    conn.sendall(cached)
                except OSError:
                    pass
                request_log.add(log_entry)
                return

            # Cache miss: forward
            log_entry["source"] = "origin"
            forward_headers = {k: v for k, v in headers.items() if k.lower() not in {
                "proxy-authorization", "host", "connection", "keep-alive", "proxy-connection"
            }}
            try:
                resp = get_session().get(
                    full_url,
                    headers=forward_headers,
                    timeout=float(config.get("request_timeout", 15)),
                    allow_redirects=True,
                    stream=False,
                )
                log_entry["status"] = f"{resp.status_code} {resp.reason}"

                # Don't cache redirects — clients should re-fetch and re-cache the target.
                if 300 <= resp.status_code < 400:
                    stats.record_miss(len(resp.content))
                    try:
                        conn.sendall(_build_proxy_response(resp))
                    except OSError:
                        pass
                    request_log.add(log_entry)
                    return

                # Content blacklist: do not cache, but still pass through.
                ctype = resp.headers.get("Content-Type", "")
                if is_content_type_blocked(ctype, config.get("content_blacklist", []) or []):
                    stats.record_content_block()
                    stats.record_miss(len(resp.content))
                    log_entry["source"] = "origin-blocked"
                    request_log.add(log_entry)
                    try:
                        conn.sendall(_build_proxy_response(resp))
                    except OSError:
                        pass
                    return

                full = _build_proxy_response(resp)
                cache.set(full_url, full)
                stats.record_miss(len(full))
                stats.update_peak(cache.size())
                try:
                    conn.sendall(full)
                except OSError:
                    pass
            except requests.exceptions.RequestException as e:
                traceback.print_exc()
                stats.record_error()
                log_entry["status"] = "502 Bad Gateway"
                _send_simple(conn, "HTTP/1.1 502 Bad Gateway")
            except Exception:
                traceback.print_exc()
                stats.record_error()
                log_entry["status"] = "500 Internal Server Error"
                _send_simple(conn, "HTTP/1.1 500 Internal Server Error")

            request_log.add(log_entry)
            return

        # Other methods: forward, don't cache
        log_entry["source"] = "origin"
        forward_headers = {k: v for k, v in headers.items() if k.lower() not in {
            "proxy-authorization", "host", "connection", "keep-alive", "proxy-connection"
        }}
        try:
            resp = get_session().request(
                method,
                full_url,
                headers=forward_headers,
                data=_body,
                timeout=float(config.get("request_timeout", 15)),
            )
            log_entry["status"] = f"{resp.status_code} {resp.reason}"
            try:
                conn.sendall(_build_proxy_response(resp))
            except OSError:
                pass
        except Exception:
            traceback.print_exc()
            stats.record_error()
            log_entry["status"] = "502 Bad Gateway"
            _send_simple(conn, "HTTP/1.1 502 Bad Gateway")
        request_log.add(log_entry)

    except Exception:
        traceback.print_exc()
        stats.record_error()
    finally:
        safe_close(conn)
