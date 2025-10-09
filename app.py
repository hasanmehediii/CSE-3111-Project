import threading
import json
from proxy.proxy_server import start_proxy
from dashboard.dashboard_app import create_dashboard

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

if __name__ == "__main__":
    config = load_config()

    # Start Proxy Server
    proxy_thread = threading.Thread(
        target=start_proxy,
        args=(config["proxy_port"], config["cache_ttl"]),  # now works
        daemon=True
    )
    proxy_thread.start()

    # Start Dashboard
    app = create_dashboard()
    app.run(port=config["dashboard_port"], debug=False)
