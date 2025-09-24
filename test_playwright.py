import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://play.ezygamer.com/"
    out = "playwright_smoke.png"
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=20000)
            await page.screenshot(path=out, full_page=True)
            await browser.close()
        print("OK:", out)
    except Exception as e:
        print("ERR:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
