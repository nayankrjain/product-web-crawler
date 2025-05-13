from app.crawler_enums import Status
from app.dao import insert_html
from app.tasks import fetch_and_save_html

start_urls = [
    "https://www.virgio.com/",
    "https://www.tatacliq.com/",
    "https://www.nykaafashion.com/",
    "https://www.westside.com/"
]

for url in start_urls:
    document = {
        "url": url,
        "base_url": url,
        "status": Status.QUEUED
    }

    inserted_id = insert_html(document)
    fetch_and_save_html.delay(inserted_id)


