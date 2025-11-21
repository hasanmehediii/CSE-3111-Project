from flask import Flask, render_template, request, abort, jsonify
import json
from proxy.cache_manager import cache
from proxy.request_log import request_log

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def create_dashboard():
    dashboard_app = Flask(__name__)
    config = load_config()
    blacklist = config.get("blacklist", [])
    cache_type = config.get("cache_type", "memory")

    @dashboard_app.route('/')
    def index():
        total_cached = cache.size()
        cached_urls = cache.keys()
        return render_template(
            'index.html',
            total_cached=total_cached,
            cached_urls=cached_urls,
            blacklist=blacklist,
            cache_type=cache_type.capitalize()
        )

    @dashboard_app.route('/view')
    def view_page():
        url = request.args.get('url')
        if not url:
            abort(400)
        content = cache.get(url)
        if not content:
            return "❌ No cached content found for this URL.", 404
        return content

    @dashboard_app.route('/api/requests')
    def api_requests():
        return jsonify(request_log.get_all())

    return dashboard_app

if __name__ == '__main__':
    app = create_dashboard()
    app.run(debug=True)