import os
import uuid
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, expect


def test_minipay_browser_workflow():
    load_dotenv(".env")
    key = os.environ["MINIPAY_API_KEY"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1280, "height": 900}
        )

        try:
            page.goto(
                "http://127.0.0.1:8000/ui/",
                wait_until="domcontentloaded"
            )

            expect(page.locator("h1")).to_have_text(
                "MiniPay Support Console"
            )

            page.locator("#apiKey").fill(key)

            # Test 1: Successful transaction search
            page.locator("#reference").fill("TXN00000001")
            page.locator("#searchBtn").click()

            expect(page.locator("#searchStatus")).to_have_text(
                "HTTP 200"
            )

            expect(page.locator("#searchResult")).to_contain_text(
                "TXN00000001"
            )

            page.screenshot(
                path="evidence/ui-search-success.png",
                full_page=True
            )

            # Test 2: Transaction not found
            page.locator("#reference").fill(
                "MISSING-" + uuid.uuid4().hex
            )
            page.locator("#searchBtn").click()

            expect(page.locator("#searchStatus")).to_have_text(
                "HTTP 404"
            )

            page.screenshot(
                path="evidence/ui-search-not-found.png",
                full_page=True
            )

            # Test 3: Create synthetic demo payment
            page.locator("#customerId").fill("1")
            page.locator("#amount").fill("125.50")
            page.locator("#payBtn").click()

            expect(page.locator("#payStatus")).to_have_text(
                "HTTP 201"
            )

            expect(page.locator("#paymentResult")).to_contain_text(
                '"status": "SUCCESS"'
            )

            page.screenshot(
                path="evidence/ui-payment-success.png",
                full_page=True
            )

        finally:
            browser.close()
