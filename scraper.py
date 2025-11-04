import asyncio
from playwright.async_api import async_playwright

async def scrape_rozetka():
    print("launching scraper...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        path = "https://rozetka.com.ua/"
        await page.goto(path)

        print("Page loaded ^-^")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_rozetka())