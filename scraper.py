import asyncio
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError


async def scrape_rozetka():
    print("launching scraper...")
    scraped_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        })

        path = "https://rozetka.com.ua/"
        await page.goto(path)

        try:
            await page.click('[data-testid="cookie-banner-close"]', timeout=3000)

        except Exception as e:
            print("coki ban did not appear, carry  on")

        try:
            await page.click('[data-testid="city-confirmation-cancel"]', timeout=2000)

        except Exception as e:
            print("town did not appear, carry on")

        await page.fill('[name="search"]', 'навушники')

        await page.click('[data-testid="search-suggest-submit"]')


        await page.wait_for_url("**/headphones/**", timeout=60000)

        product_card_selector = "div.catalog-grid__cell"

        try:
            await page.wait_for_selector(product_card_selector, state='attached', timeout=60000)

            product_cards = await page.locator(product_card_selector).all()


            for card in product_cards:
                try:

                    title_element = card.locator(".tile-title")
                    price_element = card.locator(".rz-tile-price")

                    title = await title_element.text_content()
                    price = await price_element.text_content()

                    title_clean = title.strip()
                    price_clean = price.strip().replace('\xa0', ' ')

                    print(f"НАЗВА: {title_clean} | ЦІНА: {price_clean}")
                    scraped_data.append({"title": title_clean, "price": price_clean})

                except Exception as e:

                    print(f"did not manage to parse")

        except PlaywrightTimeoutError:
            print("\n" + "=" * 30)
            print(f"error: did not wait for selector '{product_card_selector}'.")

            await page.screenshot(path="debug.png")
            page_content = await page.content()
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(page_content)


        await browser.close()
        return scraped_data


if __name__ == "__main__":
    data = asyncio.run(scrape_rozetka())
    print("\n--- result ---")
    print(data)