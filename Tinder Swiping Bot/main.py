from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from time import sleep
import os

TINDOG_URL = "https://app.100daysofpython.dev/services/tindog/u/BOedDOrWACQzJ_YVz9mvqpC2yN8nTYrL"
FACEBARK_EMAIL = os.getenv("TINDOG_EMAIL")
FACEBARK_PASSWORD = os.getenv("TINDOG_PASSWORD")

# Start Chrome and open the Tindog practice website.
driver = webdriver.Chrome()
driver.get(TINDOG_URL)

# Open the login form, then choose Facebark as the login provider.
sleep(2)
login_button = driver.find_element(By.XPATH, value='//*[text()="Log in"]').click()

sleep(1)
facebark_btn = driver.find_element(By.CLASS_NAME, value='btn-facebark').click()

# The Facebark login opens in a second browser window. Keep the original
# Tindog window handle so we can return to it after logging in.
sleep(2)
base_window = driver.window_handles[0]
facebark_window = driver.window_handles[1]
driver.switch_to.window(facebark_window)
print(driver.title)

# Fill in credentials from environment variables and submit the login form.
# Set TINDOG_EMAIL and TINDOG_PASSWORD before running this script.
email = driver.find_element(By.ID, value='email')
password = driver.find_element(By.ID, value='pass')


if not FACEBARK_EMAIL:
	raise ValueError("TINDOG_EMAIL environment variable is not set")
email.send_keys(FACEBARK_EMAIL)

if not FACEBARK_PASSWORD:
	raise ValueError("TINDOG_PASSWORD environment variable is not set")
password.send_keys(FACEBARK_PASSWORD)
password.send_keys(Keys.ENTER)

# Return to Tindog after authentication is complete.
sleep(2)
driver.switch_to.window(base_window)
print(driver.title)

# Clear the location permission prompt shown after login.
sleep(2)
allow_location = driver.find_element(By.XPATH, value='//button[text()="Allow"]').click()

# Close the notification opt-out popup if it appears.
sleep(1)
popup_rem = driver.find_element(By.XPATH, value='//button[text()="Not interested"]').click()

# Accept the site's cookie notice before interacting with profiles.
sleep(1)
accept_cookie = driver.find_element(By.XPATH, value='//button[text()="I Accept"]').click()

# Like up to 20 profiles. A match popup can cover the Like button, so close
# it and continue with the next profile when Selenium cannot click the button.
for n in range(20):
	sleep(1)
	try:
		like_btn = driver.find_element(By.CLASS_NAME, value='btn-like').click()
	except ElementClickInterceptedException:
		# Dismiss the match popup, if present, then continue swiping.
		try:
			driver.find_element(By.CSS_SELECTOR, value='.match-popup a').click()
		except NoSuchElementException:
			sleep(2)
	except NoSuchElementException:
		# The page may still be loading or may have no more profiles.
		sleep(2)

# Close the browser cleanly when the swiping loop is finished.
driver.quit()