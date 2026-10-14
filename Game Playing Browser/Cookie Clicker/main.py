# Selenium imports provide browser control, element locators, and explicit waits.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, time

# Configure Chrome and keep its window open after Python exits.
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# Open the game and allow its initial HTML and JavaScript to load.
driver.get("https://ozh.github.io/cookieclicker/")

sleep(3)        # Waiting for the Page to load:

def dismiss_cookie_consent():
    """Dismiss the consent banner when it is displayed."""
    # find_elements returns an empty list when the banner is absent, so this
    # helper can safely be called more than once.
    consent_buttons = driver.find_elements(By.CSS_SELECTOR, "a.cc_btn_accept_all")
    if not consent_buttons:
        return

    try:
        # Wait until the overlay button can receive a click.
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.cc_btn_accept_all"))
        ).click()
        print("Cookie consent dismissed.")
    except TimeoutException:
        print("Cookie consent was found but could not be dismissed.")


# The consent overlay can block clicks on the game, so remove it first.
dismiss_cookie_consent()

# Select English during the game's first-run language prompt.
print("Looking for language selection...")
try:
    # Select the English Language:
    lang_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "langSelect-EN"))
    )
    print("Found language button, clicking...")
    lang_button.click()
    sleep(3) # loading

except (NoSuchElementException, TimeoutException):
    print("Language Selection not Found...")

sleep(2)    # Settling up the things
dismiss_cookie_consent()

# Product IDs are numbered from product0 through product17 in the game HTML.
items_ids = [f"product{i}" for i in range(18)]

# Check for purchases every five seconds and stop after five minutes.
wait_time = 5
timeout = time() + wait_time        # Checks for the purchase every 5 seconds
five_min = time() + 60 * 5          # The program runs for 5 minutes

while True:
    try:
        # Reacquire the element because JavaScript may rebuild the game UI.
        cookie = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "bigCookie"))
        )
        cookie.click()
    except NoSuchWindowException:
        print("Browser window was closed. Stopping the game.")
        break
    except (StaleElementReferenceException, TimeoutException):
        print("Cookie was not available; retrying.")
        continue

    # Every five seconds, inspect the current cookie total and store.
    if time() > timeout:
        try:
            # Read the live counter rendered by the game.
            cookies_ele = driver.find_element(By.ID, value='cookies')
            cookie_text = cookies_ele.text

            # Convert text such as "123 cookies" or "1,234 cookies" to an int.
            cookie_count = int(cookie_text.split()[0].replace(",", ""))

            # Each product is a div whose ID starts with "product".
            products = driver.find_elements(By.CSS_SELECTOR, value="div[id^='product']")

            # Products appear in increasing price order. Reverse the list and
            # choose the first enabled item, the most expensive available one.
            best_item = None
            for product in reversed(products):
                if "enabled" in (product.get_attribute("class") or ""):
                    best_item = product
                    break

            # Dismiss any overlay again before clicking the store item.
            if best_item:
                dismiss_cookie_consent()
                best_item.click()
                print(f"Bought item: {best_item.get_attribute('id')}")

        except NoSuchWindowException:
            print("Browser window was closed. Stopping the game.")
            break
        except (NoSuchElementException, StaleElementReferenceException, ValueError):
            print("Couldn't find Cookie count or Items...")

        # Schedule the next store check five seconds from now.
        timeout = time() + wait_time

    # Stop once the five-minute runtime has elapsed.
    if time() > five_min:
        try:
            cookies_ele = driver.find_element(By.ID, value="cookies")
            print(f"Final Result: {cookies_ele.text}")
        except (NoSuchElementException, NoSuchWindowException):
            print("Couldn't get Final Cookie Count...")
        break