import asyncio
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

from app.crawler_enums import Status
from app.dao import fetch_html, update_html, check_if_url_exists, insert_product_url, insert_html
from app.helpers import normalize_url, is_valid_product_url
from celery_app import celery_app

# Global domain-based semaphore (not shared across processes)
domain_semaphores = {}

def get_domain(url):
    return urlparse(url).netloc

def get_semaphore_for_domain(domain, limit=2):
    if domain not in domain_semaphores:
        domain_semaphores[domain] = asyncio.Semaphore(limit)
    return domain_semaphores[domain]

def get_headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }

def sync_rate_limited_fetch(url: str, retries=3, backoff_base=2):
    domain = get_domain(url)
    semaphore = get_semaphore_for_domain(domain)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def limited_request():
        async with semaphore:
            for attempt in range(retries):
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.get(url, headers=get_headers())
                        if response.status_code == 429:
                            sleep_time = backoff_base ** attempt + random.uniform(0, 1)
                            print(f"[429] Rate limited for {url}, backing off {sleep_time:.2f}s")
                            await asyncio.sleep(sleep_time)
                            continue
                        response.raise_for_status()
                        return response.text
                except Exception as e:
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(backoff_base ** attempt)
                    return None
            return None

    return loop.run_until_complete(limited_request())


@celery_app.task(name="tasks.fetch_and_save_html")
def fetch_and_save_html(url_id):
    url = None
    try:
        doc = fetch_html(url_id)
        if not doc or "url" not in doc:
            print(f"[WARN] Document not found or missing url for ID: {url_id}")
            return

        url = doc["url"]
        print(F"Fetching URL {url}")
        html = sync_rate_limited_fetch(url)

        update_query = {
            "$set": {
                "html": html,
                "status": Status.FETCHED,
                "fetched_at": datetime.now()
            }
        }
        update_html(url_id, update_query)

        # Kick off parsing in background
        parse_and_discover_links.delay(url_id)

    except Exception as e:
        print({"status": "error", "url": url, "error": str(e)})
        update_query = {"$set": {"status": Status.FAILED}}
        update_html(url_id, update_query)




@celery_app.task(name="tasks.parse_and_discover_links")
def parse_and_discover_links(url_id: str):
    doc = fetch_html(url_id)

    if not doc or "html" not in doc or not doc["html"]:
        print(f"[WARN] Document not found or missing HTML for ID: {url_id}")
        return
    print(f"Parsing ${doc['_id']}")
    soup = BeautifulSoup(doc["html"], "html.parser")
    base_url = doc["base_url"] or ""
    domain = urlparse(base_url).netloc

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        normalized_url = normalize_url(full_url)
        if base_url in normalized_url and not check_if_url_exists(normalized_url):
            print(domain, normalized_url)
            if is_valid_product_url(domain, normalized_url):
                print(f"Found product URL: {normalized_url}")
                insert_product_url({"domain":domain, "url": normalized_url})
            print(f"[INFO] Queuing new URL: {normalized_url}")
            document = {
                "url": normalized_url,
                "base_url": base_url,
                "status": Status.QUEUED
            }
            inserted_id = insert_html(document)
            fetch_and_save_html.delay(inserted_id)