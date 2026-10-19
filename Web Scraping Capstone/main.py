from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests

# Step 1: Scrape rental links, addresses, and prices from the Zillow clone.
GOOGLE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScFCpH7WFbQO6y3-AQBnWMIAX5ohwmm6WxN5iAPhJu1689jTQ/viewform?usp=header"

# These headers make the request look like it came from a normal web browser.
header = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
}

# Download the page that contains the sample rental listings.
response = requests.get("https://appbrewery.github.io/Zillow-Clone/", headers=header)

data = response.text
soup = BeautifulSoup(data, "html.parser")

# Find every property link inside a property card.
link_ele = soup.select(".StyledPropertyCardDataWrapper a")
all_links = [str(link["href"]) for link in link_ele]
print(all_links)

# Find each address and remove the separator, extra line breaks, and whitespace.
add_ele = soup.select(".StyledPropertyCardDataWrapper address")
all_address = [address.get_text().replace(" | ", " ").strip() for address in add_ele]

print(f"\n Post cleanup, the {len(all_address)} address look like this:\n")
print(all_address)

# Find prices, keep only elements containing "$", and remove "/mo" or extra price text.
price_ele = soup.select(".StyledPropertyCardDataWrapper span")
all_prices = [price.get_text().replace("/mo", "").split("+")[0] for price in price_ele if "$" in price.text]

print(f"\n After been cleaned up. The {len(all_prices)} prices now look like: \n")
print(all_prices)

# Step 2: Open the Google Form and submit one property per form response.

# Keep Chrome open after the script finishes so submissions can be inspected.
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options = chrome_options)

for n in range(len(all_links)):
    # Reload the blank form before entering the next property.
    driver.get(GOOGLE_FORM)
    wait = WebDriverWait(driver, 10)

    # Google Forms enables its fields asynchronously. Wait for the three
    # visible inputs after they become enabled.
    text_inputs = wait.until(
        EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "input[jsname='YPqjbf'][aria-disabled='false']")
        )
    )
    if len(text_inputs) < 3:
        raise RuntimeError("The Google Form did not expose its three input fields.")

    address, price, link = text_inputs[:3]

    # Fill the fields in the same order as they appear in the form.
    address.send_keys(all_address[n])
    price.send_keys(all_prices[n])
    link.send_keys(all_links[n])

    # Wait until the Submit button is ready, then submit this property.
    submit_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "div[role='button'][jsname='M2UYVd']")
        )
    )
    submit_btn.click()