import re
from urllib.parse import urlparse, parse_qs, urlencode

DOMAIN_CONFIG = {
    "www.virgio.com": {"product_patterns": [r"/product/.*", r"/products/.*"]},
    "www.tatacliq.com": {"product_patterns": [r"/product/", r"/p/.*"]},
    "www.nykaafashion.com": {"product_patterns": [r"/p/.*"]},
    "www.westside.com": {"product_patterns": [r"/products/.*"]},
}

def normalize_url(url):
    parsed = urlparse(url)

    # Keep only specific query parameters (e.g. id, sku, pid)
    important_params = ['id', 'pid', 'sku']
    original_qs = parse_qs(parsed.query)
    filtered_qs = {k: v for k, v in original_qs.items() if k in important_params}

    new_query = urlencode(filtered_qs, doseq=True)

    normalized = parsed._replace(fragment="", query=new_query)
    return normalized.geturl()

def is_valid_product_url(domain, url):
    patterns = DOMAIN_CONFIG.get(domain, {}).get("product_patterns", [])
    return any(re.search(pattern, url) for pattern in patterns)