from playwright.sync_api import sync_playwright
import requests
import json
import os

BOT_TOKEN = "7068655383:AAHNBTN9cyI1U5evgh-igr3Lpc2Wgy5MRDQ"
CHAT_ID = "1495993642"
PRICE_FILE = "prices.json"

ITEMS = [
    {
        "name": "Samsung Galaxy A56 5G",
        "url": "https://www.lazada.com.ph/products/pdp-i4969703056.html"
    },
    {
        "name": "Iphone 13",
        "url": "https://www.lazada.com.ph/products/pdp-i4565121749-s26228488681.html"
    },
]

def load_prices():
    return json.load(open(PRICE_FILE)) if os.path.exists(PRICE_FILE) else {}

def save_prices(data):
    json.dump(data, open(PRICE_FILE, "w"), indent=2)

def send(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

def get_price(page, url):
    page.goto(url, timeout=60000)
    page.wait_for_timeout(3000)
    selectors = [
        ".pdp-v2-product-price-content-salePrice-amount"
    ]
    for s in selectors:
        el = page.query_selector(s)
        if el:
            text = el.inner_text().replace("₱", "").replace(",", "").strip()
            return float(text)
    raise Exception("Price not found")

def main():
    prices = load_prices()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for item in ITEMS:
            name, url = item["name"], item["url"]
            try:
                price = get_price(page, url)
                last = prices.get(name)
                if last is None:
                    prices[name] = price
                    send(f"👀 Tracking started for {name}\nPrice: ₱{price:.2f}")
                elif price != last:
                    send(f"💰 {name} price changed!\nOld: ₱{last:.2f}\nNew: ₱{price:.2f}")
                    prices[name] = price
                else:
                    print(f"{name}: No change.")
            except Exception as e:
                send(f"⚠️ Error tracking {name}: {e}")

        browser.close()
    save_prices(prices)

if __name__ == "__main__":
    main()
