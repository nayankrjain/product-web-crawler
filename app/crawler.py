import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

visited = set()
semaphore = asyncio.Semaphore(10)  # concurrency limit

DOMAIN_CONFIG = {
    "www.virgio.com": {"product_patterns": [r"/product/.*", r"/products/.*"]},
    "www.tatacliq.com": {"product_patterns": [r"/product/", r"/p/.*"]},
    "www.nykaafashion.com": {"product_patterns": [r"/p/.*"]},
    "www.westside.com": {"product_patterns": [r"/products/.*"]},
    "www.bewakoof.com": {"product_patterns": [r"/p/.*"]}
}

async def fetch(session, url):
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

def is_valid_product_url(domain, url):
    patterns = DOMAIN_CONFIG.get(domain, {}).get("product_patterns", [])
    return any(re.search(pattern, url) for pattern in patterns)

async def crawl(session, base_url, url):
    print(f"base_url: {base_url}, url:{url}")
    if url in visited:
        return
    visited.add(url)

    html = await fetch(session, url)
    if not html:
        return


    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc

    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a_tag['href'])
        if base_url in full_url and full_url not in visited:
            print(domain, full_url)
            if is_valid_product_url(domain, full_url):
                print(f"Found product URL: {full_url}")
                # Save to DB here
            await crawl(session, base_url, full_url)

async def main(start_urls):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(crawl(session, url, url) for url in start_urls))

start_urls = [
    "https://www.virgio.com"
]

asyncio.run(main(start_urls))
