import socket
import threading
import requests
from proxy.cache_manager import cache

HOST = '127.0.0.1'
PORT = 8080

def handle_client(conn, addr):
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

        # Only handle GET requests for now
        if method != 'GET':
            conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            conn.close()
            return

        # Ensure URL has scheme
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Check cache
        cached_data = cache.get(url)
        if cached_data:
            print(f"[CACHE HIT] {url}")
            response_body = cached_data
        else:
            print(f"[FETCH] {url}")
            try:
                response = requests.get(url)
                response_body = response.text
                cache.set(url, response_body)
            except Exception as e:
                print(f"[ERROR] {e}")
                conn.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                conn.close()
                return

        # Construct valid HTTP/1.1 response
        response_headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=UTF-8\r\n"
            f"Content-Length: {len(response_body.encode())}\r\n"
            "Connection: close\r\n\r\n"
        )

        conn.sendall(response_headers.encode() + response_body.encode())

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def start_proxy(port=8080, ttl=300):
    cache.ttl = ttl
    print(f"🚀 Proxy server running on port {port}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(10)

    while True:
        client_conn, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr)).start()