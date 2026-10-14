# Selenium provides the browser automation API.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure Chrome before starting the browser.
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

# Create the browser session and choose a desktop-sized viewport.
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1280, 900)

# Open the page that contains the elements we will interact with.
driver.get("https://en.wikipedia.org/wiki/Main_Page")

# CSS selectors are compact patterns for locating HTML elements.
article_count = driver.find_element(By.CSS_SELECTOR, value="#articlecount a")
# article_count.click()

# LINK_TEXT finds an anchor whose visible text exactly matches the value.
all_portals = driver.find_element(By.LINK_TEXT, value="Content portals")
# all_portals.click()

# Wait until the input is visible before interacting with it.
search = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "searchInput"))
)

# send_keys types text into the input; Keys.ENTER submits the search form.
search.send_keys("Python", Keys.ENTER)