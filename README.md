# Smart Proxy and Cache Server

<p align="center">
  <img src="proxy.png" alt="Server Logo" width="150" height="150"/>
  <br>
  <strong>Smart Proxy Server</strong>
</p>

A simple smart proxy server with caching capabilities and a web dashboard to monitor the cache. Its a basic type simulation of Computer Networking Project.

## Features

*   HTTP Proxy Server
*   Caching of GET requests
*   Time-to-live (TTL) for cached objects
*   Web dashboard to view cached URLs and their content
*   Configurable proxy port, dashboard port, and cache TTL

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Navigate to the project directory:
    ```bash
    cd Smart-Proxy-Server
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

1.  Run the application:
    ```bash
    python app.py
    ```
2.  The proxy server will start on the port specified in `config.json` (default: 8080).
3.  The dashboard will be available on the port specified in `config.json` (default: 5000).

4.  To use the proxy, configure your browser or use a command-line tool like `curl`.

    Example with `curl`:
    ```bash
    curl -x http://127.0.0.1:8080 http://du.ac.bd
    ```

## Dashboard

The web dashboard provides a view of the cached URLs.

*   **URL**: `http://127.0.0.1:5000` (by default)
*   **Features**:
    *   Shows the total number of cached URLs.
    *   Lists all cached URLs.
    *   Allows previewing the cached content in a new tab.

## Configuration

The `config.json` file is used to configure the proxy server and dashboard.

```json
{
  "proxy_port": 8080,
  "dashboard_port": 5000,
  "cache_ttl": 300
}
```

*   `proxy_port`: The port for the proxy server.
*   `dashboard_port`: The port for the web dashboard.
*   `cache_ttl`: The time-to-live for cached objects in seconds.

## Testing

To test the `MemoryCache` independently, you can run the `dashboard_app.py` file directly and access the `/test_memory_cache` route.

1.  Run the dashboard app:
    ```bash
    python -m dashboard.dashboard_app
    ```
2.  Open your browser to `http://127.0.0.1:5000/test_memory_cache`.

## Author

*   **Mehedi Hasan**
    *   CSE, University of Dhaka
    *   GitHub: [hasanmehediii](https://github.com/hasanmehediii)
    *   Email: [mhmehedi.csedu@gmail.com](mailto:mhmehedi.csedu@gmail.com), [mehedi-2022415897@cs.du.ac.bd](mailto:mehedi-2022415897@cs.du.ac.bd)