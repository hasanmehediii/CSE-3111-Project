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

## Accessing from Other Devices

Yes, you can use the proxy server from another device (like a different laptop or a phone) on the same network. This section provides a comprehensive guide to set up cross-platform proxy access.

### Prerequisites

Before you begin, ensure:

*   Both devices are connected to the same network (Wi-Fi or Ethernet).
*   The proxy server is running on the host machine.
*   The firewall is not blocking the proxy port (default: `8080`).
*   Network connectivity is working between both devices.

### Step 1: Find the Local IP Address of the Proxy Server

The key to accessing your proxy from another device is identifying the correct IP address of the machine running the proxy server.

**On Linux/macOS (Proxy Server)**

Open a terminal and run:

```bash
ip addr show
# or
ifconfig
```

Look for your active network interface (typically `wlan0`, `eth0`, `enp1s0`, or `en0`) and note the IPv4 address. It usually follows the pattern `192.168.x.x` or `10.0.x.x`.

*Example output:*

```
wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.105/24 brd 192.168.1.255 scope global dynamic wlan0
```

In this example, the IP address is `192.168.1.105`.

**On Windows (Proxy Server)**

Open `Command Prompt` and run:

```cmd
ipconfig
```

Look for the active connection (Wi-Fi or Ethernet) and note the "IPv4 Address". For example: `192.168.1.105`.

### Step 2: Verify Firewall Settings

Your firewall might be blocking access to the proxy port. You need to allow incoming connections on port `8080` (or your custom proxy port).

**On Linux (Proxy Server)**

If using `UFW` (Uncomplicated Firewall):

```bash
# Check if UFW is enabled
sudo ufw status

# Allow port 8080
sudo ufw allow 8080

# Or allow from specific IP (recommended for security)
sudo ufw allow from 192.168.1.100 to any port 8080
```

If using `firewalld`:

```bash
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

**On Windows (Proxy Server)**

1.  Open **Windows Defender Firewall** → **Allow an app through firewall**.
2.  Click **Change settings**, then **Allow another app**.
3.  Browse and select your Python installation or the app running **CacheCaught**.
4.  Ensure both **Private** and **Public** networks are checked (or just **Private** if on a local network).
5.  Click **Add**.

Alternatively, open `PowerShell` as **Administrator**:

```powershell
# Allow port 8080 through Windows Firewall
New-NetFirewallRule -DisplayName "Allow CacheCaught Proxy" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### Step 3: Verify Network Connectivity

Before configuring the proxy, test if both devices can communicate:

From the client device, ping the proxy server:

*   **Linux/macOS:**
    ```bash
    ping 192.168.1.105
    ```
*   **Windows:**
    ```cmd
    ping 192.168.1.105
    ```

If you get responses, connectivity is working. If not, check that both devices are on the same network and no network isolation is enabled.

### Step 4: Configure the Proxy on the Client Device

**On Windows (Client)**

1.  Open **Settings** → **Network & Internet** → **Proxy**.
2.  Under "Manual proxy setup", toggle **Use a proxy server** ON.
3.  Enter:
    *   **Address**: `192.168.1.105` (replace with your server's IP)
    *   **Port**: `8080` (or your custom port)
4.  Click **Save**.

For command-line tools like `curl`:

```cmd
curl -x http://proxy_mehedi:mehedi@192.168.1.105:8080 http://example.com
```

**On Linux/macOS (Client)**

For system-wide proxy:

```bash
export http_proxy="http://proxy_mehedi:mehedi@192.168.1.105:8080"
export https_proxy="http://proxy_mehedi:mehedi@192.168.1.105:8080"
```

For **Firefox** browser:

1.  Open **Preferences** → **Network Settings** → **Settings**.
2.  Choose "Manual proxy configuration".
3.  Enter:
    *   **HTTP Proxy**: `192.168.1.105`
    *   **Port**: `8080`
    *   **HTTPS Proxy**: `192.168.1.105`
    *   **Port**: `8080`
4.  Check "Also use this proxy for HTTPS".

For **Chrome** browser:

*   **Linux:**
    ```bash
    google-chrome --proxy-server="http://proxy_mehedi:mehedi@192.168.1.105:8080"
    ```
*   **macOS:**
    ```bash
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --proxy-server="http://proxy_mehedi:mehedi@192.168.1.105:8080"
    ```

### Troubleshooting Cross-Platform Issues

**Cannot Access Proxy from Windows to Linux or Linux to Windows**

This is typically caused by firewall issues. Follow this checklist:

**1. Verify the Server is Listening on All Interfaces**

The proxy should be configured to listen on `0.0.0.0`, not just `127.0.0.1`. Check your `config.json` or the proxy initialization code. Look for something like:

```python
# Ensure the proxy binds to all interfaces
server.bind(('0.0.0.0', proxy_port))
```

If it's bound to `127.0.0.1`, only local connections will work. Update the configuration if needed.

**2. Double-check the Firewall Rules**

Make sure the firewall rules are actually applied:

*   **Linux: Check UFW rules**
    ```bash
    sudo ufw status numbered
    ```
*   **Windows: Verify the firewall rule**
    ```powershell
    Get-NetFirewallRule -DisplayName "Allow CacheCaught Proxy"
    ```

**3. Test Connectivity with `telnet`/`nc`**

From the client device, test if you can reach the port:

*   **Linux/macOS:**
    ```bash
    nc -zv 192.168.1.105 8080
    ```
*   **Windows (PowerShell):**
    ```powershell
    Test-NetConnection -ComputerName 192.168.1.105 -Port 8080
    ```

If this fails, the firewall is likely blocking it.

**4. Check Network Adapter Settings**

On Linux, ensure the network adapter is not in "local only" mode:

```bash
# Check if the network adapter has an IP
ip addr show wlan0
```

**5. Disable Firewall Temporarily (Testing Only)**

To isolate firewall as the issue, temporarily disable it:

*   **Linux:**
    ```bash
    sudo ufw disable
    ```
*   **Windows (PowerShell, as Administrator):**
    ```powershell
    Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled $false
    ```

Try accessing the proxy again. If it works, re-enable the firewall and apply the specific rules mentioned above.

**6. Router Configuration**

Ensure your router is not blocking inter-device communication. Some guest networks isolate devices. Check your router's isolation settings.

### Testing the Proxy

Once configured, test with a simple HTTP request:

*   **Linux/macOS:**
    ```bash
    curl -x http://proxy_mehedi:mehedi@192.168.1.105:8080 http://example.com
    ```
*   **Windows (Command Prompt or PowerShell):**
    ```cmd
    curl.exe -x http://proxy_mehedi:mehedi@192.168.1.105:8080 http://example.com
    ```

You should see the response from `example.com`. If successful, your proxy is working across devices.

### Best Practices

*   **Use HTTPS for sensitive data**: If transmitting sensitive information, consider setting up HTTPS on the proxy.
*   **Change default credentials**: Update `proxy_user` and `proxy_password` in `config.json` for security.
*   **Network isolation**: Use firewall rules to restrict access to trusted IPs only.
*   **Monitor the dashboard**: Access `http://192.168.1.105:5000` (from another device) to verify cache activity.


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