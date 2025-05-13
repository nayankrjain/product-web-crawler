from bson import ObjectId

from pymongo import MongoClient

# MongoDB connection
mongo_client = MongoClient("mongodb://admin:adminpassword@localhost:27017/?authSource=admin")
crawler_db = mongo_client["crawler_db"]

def insert_html(document):
    collection = crawler_db["page_htmls"]
    insert_result = collection.insert_one(document)
    return str(insert_result.inserted_id)


def fetch_html(object_id):
    collection = crawler_db["page_htmls"]
    doc = collection.find_one({"_id": ObjectId(object_id)})
    return doc or None

def check_if_url_exists(url):
    collection = crawler_db["page_htmls"]
    return collection.count_documents({"url": url}) != 0

def update_html(object_id, update_query):
    collection = crawler_db["page_htmls"]
    collection.update_one(
        {"_id": ObjectId(object_id)},
        update_query
    )

def insert_product_url(document):
    collection = crawler_db["product_urls"]
    collection.insert_one(document)

def fetch_product_urls(domain, page, batch_size):
    collection = crawler_db["product_urls"]
    return collection.find({"domain": domain}).skip(page * batch_size).limit(batch_size)







