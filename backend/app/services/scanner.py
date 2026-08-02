import re
from dataclasses import dataclass
from decimal import Decimal
from playwright.async_api import async_playwright
from app.domain.models import StockStatus

PRODUCT_ID_PATTERNS = [re.compile(r"/prn/[^/]+/prid/(\d+)"), re.compile(r"product_id=(\d+)"), re.compile(r"/(\d{4,})(?:\?|$)")]

@dataclass(frozen=True)
class AvailabilitySnapshot:
    is_available: bool
    price: Decimal | None
    mrp: Decimal | None
    discount_percent: float | None
    eta_minutes: int | None
    dark_store: str | None
    stock_status: StockStatus

class BlinkitScanner:
    def extract_product_id(self, url: str) -> str:
        for pattern in PRODUCT_ID_PATTERNS:
            match = pattern.search(url)
            if match:
                return match.group(1)
        raise ValueError("Blinkit product URL does not contain a recognizable product id")

    async def scan_product_city(self, product_url: str, latitude: float, longitude: float) -> AvailabilitySnapshot:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(geolocation={"latitude": latitude, "longitude": longitude}, permissions=["geolocation"])
            page = await context.new_page()
            await page.goto(product_url, wait_until="networkidle", timeout=45000)
            content = await page.locator("body").inner_text(timeout=10000)
            await browser.close()
        normalized = content.lower()
        unavailable = any(term in normalized for term in ["out of stock", "currently unavailable", "not serviceable"])
        price_match = re.search(r"₹\s*([0-9,]+(?:\.\d+)?)", content)
        price = Decimal(price_match.group(1).replace(",", "")) if price_match else None
        status = StockStatus.out_of_stock if unavailable else StockStatus.available
        return AvailabilitySnapshot(not unavailable, price, None, None, None, None, status)
