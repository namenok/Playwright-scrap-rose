import asyncio
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError


async def scrape_rozetka():
    print("launching scraper (headless mode)...")
    scraped_data = []

    async with async_playwright() as p:
        # --- CHANGE 1: Run in background ---
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        })

        path = "https://rozetka.com.ua/"
        await page.goto(path)

        # 1. Close banners (if they exist)
        try:
            await page.click('[data-testid="cookie-banner-close"]', timeout=3000)
            print("Closed cookie banner.")
        except Exception as e:
            print("Cookie banner not found, continuing.")

        try:
            await page.click('[data-testid="city-confirmation-cancel"]', timeout=2000)
            print("Closed city-confirmation pop-up.")
        except Exception as e:
            print("City pop-up not found, continuing.")

        # The search text itself remains in Ukrainian, as this is what we type
        await page.fill('[name="search"]', 'навушники')
        print("Clicking 'Search' button...")
        await page.click('[data-testid="search-suggest-submit"]')

        # 3. Wait for navigation
        print("Waiting for navigation to /headphones/ page...")
        await page.wait_for_url("**/headphones/**", timeout=60000)
        print("Successfully navigated to results page!")

        product_card_selector = "div.item"

        print(f"Waiting for product cards to be attached ({product_card_selector})...")
        await page.wait_for_selector(product_card_selector, state='attached', timeout=60000)
        print("Product cards are ATTACHED to HTML!")

        product_cards = await page.locator(product_card_selector).all()
        print(f"Found {len(product_cards)} items (products and ads) on the page.")

        # --- MAIN SCRAPING LOOP ---
        for card in product_cards:
            try:
                # --- CHANGE 2: Add 2-second timeout ---
                # If this is an ad, we won't wait 30 seconds
                title_element = card.locator("a.tile-title")
                price_element = card.locator("rz-tile-price")

                title = await title_element.text_content(timeout=2000)
                price = await price_element.text_content(timeout=2000)

                if title and price:
                    title_clean = title.strip()
                    # Replace non-breaking space with a regular space
                    price_clean = price.strip().replace('\xa0', ' ')

                    print(f"TITLE: {title_clean} | PRICE: {price_clean}")
                    scraped_data.append({"title": title_clean, "price": price_clean})
                else:
                    # This will trigger if text_content() returns None or empty string
                    print("Skipping card (no title or price).")

            except PlaywrightTimeoutError:
                # This will trigger if the locator isn't found in 2 seconds
                print("Skipping (most likely an ad) - TimeoutError")
            except Exception as e:
                # Other potential errors
                print(f"Failed to parse card: {e}")

        await browser.close()
        print("Browser closed.")
        return scraped_data


if __name__ == "__main__":
    data = asyncio.run(scrape_rozetka())
    print("\n" + "=" * 20 + " RESULT " + "=" * 20)
    print(data)