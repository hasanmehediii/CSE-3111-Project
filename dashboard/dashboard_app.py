"""Flask dashboard for monitoring and controlling the proxy."""
import os
import urllib3
import requests
from flask import Flask, abort, jsonify, render_template, request, url_for

from proxy.cache_manager import cache, flush_all, invalidate
from proxy.config import config
from proxy.request_log import request_log
from proxy.stats import stats

# Silence only the warning from the dashboard's outbound requests.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_dashboard() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    cache_type = (config.get("cache_type") or "memory").capitalize()
    proxy_user = config.get("proxy_user")
    proxy_password = config.get("proxy_password")
    proxy_port = int(config.get("proxy_port", 8080))

    def _proxy_url():
        if proxy_user and proxy_password:
            return f"http://{proxy_user}:{proxy_password}@127.0.0.1:{proxy_port}"
        return f"http://127.0.0.1:{proxy_port}"

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            total_cached=cache.size(),
            cached_urls=cache.keys(),
            blacklist=config.get("blacklist", []) or [],
            content_blacklist=config.get("content_blacklist", []) or [],
            cache_type=cache_type,
            stats=stats.snapshot(),
        )

    @app.route("/view")
    def view_page():
        url = request.args.get("url", "")
        if not url:
            abort(400)
        content = cache.get(url)
        if not content:
            return "No cached content for this URL.", 404
        return content

    @app.route("/api/requests")
    def api_requests():
        return jsonify(request_log.get_all())

    @app.route("/api/stats")
    def api_stats():
        snapshot = stats.snapshot()
        snapshot["current_cached"] = cache.size()
        return jsonify(snapshot)

    @app.route("/api/cache/invalidate", methods=["POST"])
    def api_invalidate():
        data = request.get_json(silent=True) or {}
        url = data.get("url") or request.args.get("url", "")
        removed = invalidate(url) if url else False
        return jsonify({"url": url, "removed": removed})

    @app.route("/api/cache/clear", methods=["POST"])
    def api_clear():
        n = flush_all()
        return jsonify({"cleared": n})

    @app.route("/api/config/reload", methods=["POST"])
    def api_reload():
        config.reload()
        return jsonify({"reloaded": True})

    @app.route("/proxy-request", methods=["POST"])
    def proxy_request():
        data = request.get_json(silent=True) or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400

        try:
            request_log.clear_for_url(url)
            resp = requests.get(
                url,
                proxies={"http": _proxy_url(), "https": _proxy_url()},
                verify=False,
                timeout=15,
            )
            latest = request_log.get_latest_for_url(url)
            cache_status = (latest or {}).get("source", "unknown")
            return jsonify({
                "content": resp.text,
                "status": cache_status,
                "http_status": resp.status_code,
            })
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    application = create_dashboard()
    application.run(debug=True)
