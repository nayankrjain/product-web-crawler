from app.dao import fetch_product_urls


domains = [
   "www.westside.com",
    "www.tatacliq.com",
    "www.virgio.com",
    "www.nykaafashion.com"
]

# Fetch documents in pages
for domain in domains:
    page = 0
    batch_size = 1000
    while True:
        cursor = fetch_product_urls(domain, page, batch_size)

        # If there are no more documents, break the loop
        documents = list(cursor)
        if not documents:
            print(f"No more documents found for {domain}")
            break

        # Process the documents
        for document in documents:
            print(f'domain:{document["domain"]}, producl_url:{document["url"]}')

        # Move to the next page
        page += 1
