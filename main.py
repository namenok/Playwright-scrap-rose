from fastapi import FastAPI
from scraper import scrape_rozetka
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

client = MongoClient(CONNECTION_STRING)
db = client['scrapers_db']
rozetka_collection = db['rozetka_products']
prom_collection = db['prom_products']

app = FastAPI(title="RoseScraper")

@app.get("/products")
async def get_products_from_db():
    print("API endpoint /products was called!")

    products_cursor = collection.find()

    products_list = []
    for doc in products_cursor:
        doc["_id"] = str(doc["_id"])
        products_list.append(doc)

    print(f"Found {len(products_list)} items in the database.")

    return {"products": products_list}



@app.get("/scrape")
async def run_scraper_endpoint():

    print("API endpoint /scrape was called!")
    scraped_data = await scrape_rozetka()

    for doc in scraped_data:
        doc["_id"] = str(doc["_id"])

    print(f"Scraper finished, returning {len(scraped_data)} items.")
    return {"products": scraped_data}