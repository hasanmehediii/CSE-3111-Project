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
