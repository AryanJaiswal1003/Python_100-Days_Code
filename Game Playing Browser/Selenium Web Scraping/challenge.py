# Selenium provides the browser automation API.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Keep Chrome open after the script exits so the result can be inspected.
chrome_option = webdriver.ChromeOptions()
chrome_option.add_experimental_option("detach", True)

# Create the browser session.
driver = webdriver.Chrome(options=chrome_option)

# Open the page containing the practice registration form.
driver.get("https://appbrewery.github.io/fake-newsletter-signup/")

# Locate form fields by their HTML name attributes.
first_name = driver.find_element(By.NAME, value='fName')
last_name = driver.find_element(By.NAME, value='lName')
email = driver.find_element(By.NAME, value='email')

# send_keys simulates typing into each field.
first_name.send_keys("Robert")
last_name.send_keys("Browne")
email.send_keys("robertbrowne@email.com")

# Locate the submit button with a CSS selector and click it.
submit = driver.find_element(By.CSS_SELECTOR, value="form button")
submit.click()