import os
import re
import smtplib

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

url = "https://www.amazon.com/dp/B075CYMYK6?psc=1&ref_=cm_sw_r_cp_ud_ct_FM9M699VKHTT47YD50Q6"
header = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(url, headers=header)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

price_tag = soup.select_one(".a-offscreen")
title_tag = soup.select_one("#productTitle")

if price_tag is None or title_tag is None:
    raise RuntimeError("Could not find the product price or title on the page.")

price_text = price_tag.get_text(strip=True)
price_match = re.search(r"\d+(?:\.\d+)?", price_text.replace(",", ""))
if price_match is None:
    raise ValueError(f"Could not parse a numeric price from {price_text!r}.")
price = float(price_match.group())
title = title_tag.get_text(" ", strip=True)
print(price)
print(title)

buy_price = 100
email = os.getenv("GMAIL_ADDRESS")
password = os.getenv("GMAIL_APP_PASSWORD")

if price < buy_price:
    if not email or not password:
        print("Email credentials are not configured. Skipping email notification.")
    else:
        message = f"Subject: Amazon Price Alert!\n\n{title} is on sale for {price_text}!\n{url}"
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(email, password)
            connection.sendmail(email, email, message.encode("utf-8"))
