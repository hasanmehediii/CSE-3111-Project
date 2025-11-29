from flask import Flask, render_template, request, abort, jsonify
import json
import requests
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

    @dashboard_app.route('/proxy-request', methods=['POST'])
    def proxy_request():
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # The proxy's address
        proxy_address = f'http://{config["proxy_user"]}:{config["proxy_password"]}@127.0.0.1:{config["proxy_port"]}'
        
        proxies = {
            'http': proxy_address,
            'https': proxy_address
        }
        
        try:
            # Clear previous log for this URL to get a fresh status
            request_log.clear_for_url(url)

            # Make the request through the proxy
            response = requests.get(url, proxies=proxies, verify=False) # verify=False for simplicity

            # Now, check the log for the request we just made
            latest_request = request_log.get_latest_for_url(url)
            
            cache_status = 'undefined' # Default
            if latest_request:
                cache_status = latest_request.get('source', 'undefined')


            return jsonify({
                'content': response.text,
                'status': cache_status
            })
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e)}), 500

    return dashboard_app

if __name__ == '__main__':
    app = create_dashboard()
    app.run(debug=True)