import socket
import threading
import requests
import json
import datetime
from urllib.parse import urlparse
from proxy.cache_manager import cache
from proxy.request_log import request_log

HOST = '127.0.0.1'
PORT = 8080

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
blacklist = config.get("blacklist", [])

def is_blacklisted(url):
    domain = urlparse(url).hostname
    return domain in blacklist

def handle_client(conn, addr):
    start_time = datetime.datetime.now()
    log_entry = {
        "timestamp": start_time.isoformat(),
        "method": "",
        "url": "",
        "status": "",
        "source": ""
    }
    try:
        # Receive the request
        request = conn.recv(8192).decode(errors="ignore")
        if not request:
            conn.close()
            return

        # Parse the first line (e.g., GET http://example.com/ HTTP/1.1)
        first_line = request.splitlines()[0]
        parts = first_line.split()
        if len(parts) < 2:
            conn.close()
            return

        method, url = parts[0], parts[1]
        log_entry["method"] = method
        log_entry["url"] = url

        # Ensure URL has scheme for parsing
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Blacklist check
        if is_blacklisted(url):
            print(f"[BLACKLISTED] {url}")
            log_entry["status"] = "403 Forbidden"
            log_entry["source"] = "blacklist"
            conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n<h1>403 Forbidden</h1><p>This site is blocked by the proxy.</p>")
            conn.close()
            request_log.add(log_entry)
            return

        # Only handle GET requests for now
        if method != 'GET':
            log_entry["status"] = "405 Method Not Allowed"
            conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            conn.close()
            request_log.add(log_entry)
            return

        # Check cache
        cached_data = cache.get(url)
        if cached_data:
            print(f"[CACHE HIT] {url}")
            log_entry["source"] = "cache"
            log_entry["status"] = "200 OK"
            response_body = cached_data
        else:
            print(f"[FETCH] {url}")
            log_entry["source"] = "fetch"
            try:
                response = requests.get(url)
                response_body = response.text
                cache.set(url, response_body)
                log_entry["status"] = f"{response.status_code} {response.reason}"
            except Exception as e:
                print(f"[ERROR] {e}")
                log_entry["status"] = "502 Bad Gateway"
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                conn.close()
                request_log.add(log_entry)
                return

        # Construct valid HTTP/1.1 response
        response_headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(response_body.encode())}\r\n"
            "Connection: close\r\n\r\n"
        )

        conn.sendall(response_headers.encode() + response_body.encode())
        request_log.add(log_entry)

    except Exception as e:
        print(f"[ERROR] {e}")
        log_entry["status"] = "500 Internal Server Error"
        request_log.add(log_entry)
    finally:
        conn.close()

def start_proxy(port=8080, ttl=300):
    global config, blacklist
    config = load_config()
    blacklist = config.get("blacklist", [])
    cache.ttl = ttl
    print(f"🚀 Proxy server running on port {port}")
    print(f"Loaded {len(blacklist)} blacklisted domains.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(10)

    while True:
        client_conn, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr)).start()