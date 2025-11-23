# CacheCaught: Smart Proxy and Cache Server

<p align="center">
  <img src="attachments/proxy.png" alt="Server Logo" width="150" height="150"/>
  <br>
  <strong>CacheCaught</strong>
</p>

A powerful, extensible, and smart proxy server with advanced caching capabilities and a web dashboard to monitor traffic. Originally a simple simulation for a Computer Networking Project, it has been enhanced with several advanced features.

## Features

*   **HTTP/HTTPS Proxying**: Acts as an intermediary for your HTTP and HTTPS traffic.
*   **Multi-Strategy Caching**:
    *   **In-Memory**: A basic, thread-safe in-memory cache.
    *   **Redis**: Uses a Redis backend for persistent caching.
    *   **LRU (Least Recently Used)**: An intelligent cache that automatically evicts the oldest items when it reaches its configured size limit.
*   **Request Retries**: Automatically retries failed requests with a configurable backoff strategy, making it resilient to transient network issues.
*   **Domain Blacklisting**: Blocks access to specified domains.
*   **Content-Type Filtering**: Blocks requests for certain content types (e.g., images, videos) to save bandwidth.
*   **Basic Proxy Authentication**: Secures the proxy by requiring a username and password.
*   **Web Dashboard**: A simple web interface to monitor cache activity.

## Screenshots

![Dashboard Screenshot](attachments/cache_hit.png)


## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/hasanmehediii/CSE-3111-Project
    ```
2.  Navigate to the project directory:
    ```bash
    cd CSE-3111-Project
    ```
3.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
4.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
5.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  (Optional) Configure your proxy settings in the `config.json` file.
2.  Run the application:
    ```bash
    python app.py
    ```
3.  The proxy server will start on the port specified in `config.json` (default: 8080).
4.  The dashboard will be available on the port specified in `config.json` (default: 5000).

5.  To use the proxy, configure your browser or a command-line tool. If authentication is enabled, you will need to provide the username and password.

    **Example with `curl`:**
    ```bash
    # Replace with your actual username, password, and proxy IP/port
    curl -x http://proxy_mehedi:mehedi@127.0.0.1:8080 http://du.ac.bd
    ```

### Accessing from Other Devices

Yes, you can use the proxy server from another device (like a different laptop or a phone) on the same Wi-Fi network. The server is configured to accept connections from any device on the network.

**1. Find the Local IP Address of the Machine Running the Proxy**

*   **On Linux or macOS:** Open a terminal and run `ip a` or `ifconfig`. Look for the `inet` address under your Wi-Fi or Ethernet adapter (e.g., `wlan0` or `enp1s0`). It will likely start with `192.168.x.x`.
*   **On Windows:** Open Command Prompt (`cmd.exe`) and run `ipconfig`. Look for the "IPv4 Address" under your active Wi-Fi or Ethernet adapter.

**2. Configure the Proxy on the Other Device**

On your second device, go to its system-wide network or proxy settings.
*   **Server/IP:** Enter the IP address you found in step 1.
*   **Port:** Enter the port the proxy is running on (default is `8080`).
*   **Authentication:** If you have enabled the `proxy_user` and `proxy_password` in the config, your device or browser will prompt you for them. Some systems allow you to save the username and password directly in the proxy settings.

Once configured, all web traffic from your second device will be routed through the Smart Proxy Server.

## Dashboard

The web dashboard provides a view of the cached URLs.

*   **URL**: `http://127.0.0.1:5000` (by default)
*   **Features**:
    *   Shows the total number of cached URLs.
    *   Lists all cached URLs.
    *   Allows previewing the cached content in a new tab.

## Configuration

The `config.json` file is used to configure the proxy server. You can change anything here for your customization.

```json
{
    "proxy_port": 8080,
    "dashboard_port": 5000,
    "cache_type": "lru",
    "cache_ttl": 300,
    "cache_max_size": 100,
    "redis": {
        "host": "localhost",
        "port": 6379
    },
    "proxy_user": "proxy_mehedi",
    "proxy_password": "mehedi",
    "blacklist": [
        "example.com"
    ],
    "content_blacklist": [
        "image/jpeg",
        "video/mp4"
    ],
    "retries": {
        "total": 3,
        "backoff_factor": 0.5
    }
}
```

*   `proxy_port`, `dashboard_port`: Ports for the proxy and web dashboard.
*   `cache_type`: Caching strategy. Can be `"memory"`, `"redis"`, or `"lru"`.
*   `cache_ttl`: Time-to-live for cached objects in seconds.
*   `cache_max_size`: (For LRU cache) The maximum number of items to store.
*   `redis`: Configuration for the Redis cache backend.
*   `proxy_user`, `proxy_password`: Credentials for proxy authentication. If `proxy_user` is `null` or empty, no authentication is required.
*   `blacklist`: A list of domains to block.
*   `content_blacklist`: A list of MIME types to block.
*   `retries`: Configuration for the request retry mechanism.

## Author

*   **Mehedi Hasan**
    *   CSE, University of Dhaka
    *   GitHub: [hasanmehediii](https://github.com/hasanmehediii)
    *   Email: [mhmehedi.csedu@gmail.com](mailto:mhmehedi.csedu@gmail.com)
    *   Email: [mehedi-2022415897@cs.du.ac.bd](mailto:mehedi-2022415897@cs.du.ac.bd)