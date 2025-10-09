from flask import Flask, render_template, request, abort
from proxy.cache_manager import cache
from cache.memory_cache import MemoryCache

def create_dashboard():
    dashboard_app = Flask(__name__)

    @dashboard_app.route('/')
    def index():
        total_cached = cache.size()
        cached_urls = cache.keys()
        return render_template('index.html', total_cached=total_cached, cached_urls=cached_urls)

    @dashboard_app.route('/view')
    def view_page():
        url = request.args.get('url')
        if not url:
            abort(400)
        content = cache.get(url)
        if not content:
            return "❌ No cached content found for this URL.", 404
        return content

    @dashboard_app.route('/test_memory_cache')
    def test_memory_cache():
        memory_cache = MemoryCache(capacity=100)
        memory_cache.set("test_key", "test_value")
        retrieved_value = memory_cache.get("test_key")
        return f"Retrieved value from MemoryCache: {retrieved_value}"

    return dashboard_app

if __name__ == '__main__':
    app = create_dashboard()
    app.run(debug=True)