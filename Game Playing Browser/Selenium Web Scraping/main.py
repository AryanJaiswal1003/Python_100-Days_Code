# Selenium controls a real browser through the WebDriver API.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ChromeOptions lets us configure Chrome before it starts.
chrome_options = webdriver.ChromeOptions()
# Keep the browser open after the script exits so the page can be inspected.
chrome_options.add_experimental_option("detach", True)

# Create a browser session and navigate to the target website.
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.python.org/")

# These examples demonstrate different locator strategies. They are commented out so that only the event-scraping example runs.
search_bar = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "q"))
)
# print(search_bar.get_attribute("placeholder"))

button = driver.find_element(By.ID, value="submit")
# print(button.size)

documentation_link = driver.find_element(By.CSS_SELECTOR, value=".documentation-widget a")
# print(documentation_link)

# XPath can locate an element by its position or relationship in the HTML tree.
bug_link = driver.find_element(By.XPATH, value='//*[@id="site-map"]/div[2]/div/ul/li[3]/a')
print(bug_link.text)

# find_elements returns a list of matching WebElements; find_element returns only one element and cannot be used directly in a for loop.
event_times = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".event-widget time"))
)
event_names = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".event-widget li a"))
)
events = {}

# Match each date with the event name at the same list index.
for n in range(len(event_times)):
    events[n] = {
        "time": event_times[n].text,
        "name": event_names[n].text
    }
print(events)

driver.quit()