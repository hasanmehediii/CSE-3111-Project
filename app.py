"""Entry point: starts the proxy in a background thread and runs the dashboard.

Handles SIGINT/SIGTERM by signaling the proxy to shut down and asking Werkzeug
to stop. Threads are daemons so the process can exit cleanly.
"""
import signal
import sys
import threading

from dashboard.dashboard_app import create_dashboard
from proxy.config import config
from proxy.proxy_server import start_proxy, stop as stop_proxy


def _install_signal_handlers(stop_event: threading.Event):
    def _handle(signum, _frame):
        print(f"\n[main] received signal {signum}, shutting down...")
        stop_proxy()
        stop_event.set()

    signal.signal(signal.SIGINT, _handle)
    signal.signal(signal.SIGTERM, _handle)


def main():
    proxy_port = int(config.get("proxy_port", 8080))
    cache_ttl = int(config.get("cache_ttl", 300))

    stop_event = threading.Event()
    _install_signal_handlers(stop_event)

    proxy_thread = threading.Thread(
        target=start_proxy,
        args=(proxy_port, cache_ttl),
        name="proxy-server",
        daemon=True,
    )
    proxy_thread.start()

    dashboard = create_dashboard()
    dashboard_port = int(config.get("dashboard_port", 5000))
    print(f"[main] dashboard running on http://127.0.0.1:{dashboard_port}")
    try:
        dashboard.run(host="0.0.0.0", port=dashboard_port, debug=False, use_reloader=False)
    finally:
        stop_proxy()
        stop_event.set()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_proxy()
        sys.exit(0)
