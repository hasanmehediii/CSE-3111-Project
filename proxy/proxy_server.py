import socket
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import datetime
import select
import base64
from urllib.parse import urlparse
from proxy.cache_manager import cache
from proxy.request_log import request_log
import traceback

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
blacklist = config.get("blacklist", [])
content_blacklist = config.get("content_blacklist", [])
proxy_user = config.get("proxy_user")
proxy_password = config.get("proxy_password")


def is_blacklisted(url):
    domain = urlparse(url).hostname
    if not domain:
        domain = url.split(':')[0]
    for bl_domain in blacklist:
        if domain == bl_domain or domain.endswith("." + bl_domain):
            return True
    return False

def tunnel_traffic(client_socket, server_socket):
    sockets = [client_socket, server_socket]
    try:
        while True:
            readable, _, exceptional = select.select(sockets, [], sockets, 10)
            if exceptional:
                break
            if not readable:
                continue
            for sock in readable:
                data = sock.recv(8192)
                if not data:
                    return
                if sock is client_socket:
                    server_socket.sendall(data)
                else:
                    client_socket.sendall(data)
    except Exception as e:
        print(f"[TUNNEL ERROR] {e}")
    finally:
        client_socket.close()
        server_socket.close()


def handle_client(conn, addr):
    start_time = datetime.datetime.now()
    log_entry = {
        "timestamp": start_time.isoformat(),
        "method": "",
        "url": "",
        "status": "",
        "source": ""
    }
    
    retry_config = config.get('retries', {})
    total_retries = retry_config.get('total', 3)
    backoff_factor = retry_config.get('backoff_factor', 0.5)
    retry_strategy = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.proxies = {}

    try:
        request_data = conn.recv(8192)
        if not request_data:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            return

        header_end = request_data.find(b'\r\n\r\n')
        if header_end == -1:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            return
        
        headers_raw = request_data[:header_end].decode('utf-8', errors='ignore')
        body = request_data[header_end + 4:]
        request_lines = headers_raw.splitlines()

        if not request_lines:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            return

        first_line = request_lines[0]
        parts = first_line.split()
        if len(parts) < 2:
            conn.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\nContent-Length: 0\r\n\r\n")
            return

        method, url = parts[0], parts[1]
        log_entry["method"] = method
        log_entry["url"] = url
        
        headers = {}
        for line in request_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        if proxy_user:
            auth_header = headers.get('Proxy-Authorization')
            auth_required_response = (
                b'HTTP/1.1 407 Proxy Authentication Required\r\n'
                b'Proxy-Authenticate: Basic realm="Proxy"\r\n\r\n'
            )
            if auth_header is None:
                conn.sendall(auth_required_response)
                return
            try:
                auth_type, auth_token = auth_header.split()
                if auth_type.lower() != 'basic':
                    conn.sendall(auth_required_response)
                    return
                decoded_creds = base64.b64decode(auth_token).decode()
                user, password = decoded_creds.split(':', 1)
                if user != proxy_user or password != proxy_password:
                    conn.sendall(auth_required_response)
                    return
            except Exception:
                conn.sendall(auth_required_response)
                return
        
        if is_blacklisted(url):
            log_entry["status"] = "403 Forbidden"
            log_entry["source"] = "blacklist"
            response_body = b"<h1>403 Forbidden</h1><p>This site is blocked.</p>"
            response_headers = (
                f"HTTP/1.1 403 Forbidden\r\n"
                f"Content-Length: {len(response_body)}\r\n\r\n"
            )
            conn.sendall(response_headers.encode() + response_body)
            request_log.add(log_entry)
            return

        if method == 'CONNECT':
            log_entry["source"] = "tunnel"
            try:
                dest_host, dest_port = url.split(':')
                dest_port = int(dest_port)
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((dest_host, dest_port))
                conn.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                log_entry["status"] = "200 Connection established"
                request_log.add(log_entry)
                tunnel_traffic(conn, server_socket)
                return
            except Exception as e:
                traceback.print_exc()
                log_entry["status"] = "502 Bad Gateway"
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                request_log.add(log_entry)
                return

        if not url.startswith("http"):
            url = "http://" + url

        if method == 'GET':
            cached_response_data = cache.get(url)
            if cached_response_data:
                log_entry["source"] = "cache"
                log_entry["status"] = "200 OK"
                conn.sendall(cached_response_data)
                request_log.add(log_entry)
                return

            log_entry["source"] = "network"
            try:
                forward_headers = headers.copy()
                headers_to_remove = ['Proxy-Authorization', 'Host', 'Connection', 'Keep-Alive']
                for h in headers_to_remove:
                    if h in forward_headers:
                        del forward_headers[h]

                response = session.get(url, headers=forward_headers, timeout=10)
                log_entry["status"] = f"{response.status_code} {response.reason}"
                
                res_headers = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding', 'connection']:
                         res_headers += f"{key}: {value}\r\n"
                res_headers += "Connection: close\r\n\r\n"
                
                res_body = response.content
                full_response = res_headers.encode('utf-8') + res_body
                
                cache.set(url, full_response)
                conn.sendall(full_response)

            except Exception as e:
                traceback.print_exc()
                log_entry["status"] = "502 Bad Gateway"
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            
            request_log.add(log_entry)
        else:
            log_entry["status"] = "405 Method Not Allowed"
            conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            request_log.add(log_entry)

    except Exception as e:
        traceback.print_exc()
        log_entry["status"] = "500 Internal Server Error"
        if log_entry["method"]:
            request_log.add(log_entry)
    finally:
        conn.close()

def start_proxy(port=8080, ttl=300):
    global config, blacklist, content_blacklist, proxy_user, proxy_password
    config = load_config()
    blacklist = config.get("blacklist", [])
    content_blacklist = config.get("content_blacklist", [])
    proxy_user = config.get("proxy_user")
    proxy_password = config.get("proxy_password")
    cache.ttl = ttl
    print(f"🚀 Proxy server running on port {port}")
    if proxy_user:
        print(f"🔑 Proxy authentication enabled for user: {proxy_user}")
    print(f"Loaded {len(blacklist)} blacklisted domains.")
    print(f"Loaded {len(content_blacklist)} blocked content types.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(10)

    while True:
        client_conn, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr)).start()