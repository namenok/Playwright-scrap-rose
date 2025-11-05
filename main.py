from fastapi import FastAPI
from scraper import scrape_rozetka


app = FastAPI(title="RoseScraper")

@app.get("/scrape")
async def run_scraper_endpoint():
    """
        Runs the Rozetka scraper and returns the findings.
        """
    print("API endpoint /scrape was called!")
    scraped_data = await scrape_rozetka()

    print(f"Scraper finished, returning {len(scraped_data)} items.")

    return {"products": scraped_data}