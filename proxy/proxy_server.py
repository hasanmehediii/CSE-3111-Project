"""TCP server loop for the proxy.

`start_proxy` is called from a background thread by app.py. It binds the
listening socket, accepts connections, and dispatches each one to
`handle_client` in its own thread.
"""
import signal
import socket
import threading

from proxy.cache_manager import cache
from proxy.config import config
from proxy.request_handler import handle_client
from proxy.tunnel import tunnel_traffic  # re-exported for back-compat

_shutdown_event = threading.Event()


def request_shutdown(*_args):
    """Signal the server loop to exit (used by SIGINT/SIGTERM handlers)."""
    _shutdown_event.set()


def start_proxy(port: int | None = None, ttl: int | None = None) -> None:
    """Bind and serve. Blocks until `_shutdown_event` is set or a fatal error occurs."""
    # Apply runtime config overrides (e.g. TTL from CLI)
    if ttl is not None:
        cache.ttl = ttl
    if port is None:
        port = int(config.get("proxy_port", 8080))
    bind_host = config.get("bind_host", "0.0.0.0")

    # Optional: install signal handlers when running on the main thread.
    try:
        signal.signal(signal.SIGINT, request_shutdown)
        signal.signal(signal.SIGTERM, request_shutdown)
    except (ValueError, OSError):
        # Not in main thread — that's fine, app.py owns signals.
        pass

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((bind_host, int(port)))
    except OSError as e:
        print(f"[proxy] failed to bind {bind_host}:{port}: {e}")
        return
    server.listen(64)
    server.settimeout(0.5)  # let us poll the shutdown event

    proxy_user = config.get("proxy_user")
    print(f"[proxy] listening on {bind_host}:{port}")
    if proxy_user:
        print(f"[proxy] auth enabled for user '{proxy_user}'")
    print(f"[proxy] cache: {config.get('cache_type')} (ttl={cache.ttl}s)")
    bl = config.get("blacklist", []) or []
    cbl = config.get("content_blacklist", []) or []
    print(f"[proxy] domain blacklist: {len(bl)} entries; content blacklist: {len(cbl)} entries")

    try:
        while not _shutdown_event.is_set():
            try:
                conn, addr = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                name=f"proxy-client-{addr[0]}:{addr[1]}",
                daemon=True,
            )
            t.start()
    finally:
        try:
            server.close()
        except OSError:
            pass
        print("[proxy] server stopped")


def stop():
    """Trigger shutdown from another thread (e.g. dashboard endpoint)."""
    request_shutdown()


# Re-exports so any external code that imported these names still works
__all__ = ["start_proxy", "stop", "tunnel_traffic"]
