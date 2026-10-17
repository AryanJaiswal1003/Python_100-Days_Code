from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
import time


# Account whose followers will be collected.
SIMILAR_ACCOUNT = "elaineducasse"
# These values are used to fill in the login form.
# For real projects, store them in environment variables instead of source code.
USERNAME = "your_email"
PASSWORD = "your_app_password"
# The practice website provides the login and followers pages used by this bot.
BASE_URL = "https://app.100daysofpython.dev/services/share-a-naan"
LOGIN_URL = f"{BASE_URL}/login"


class InstaFollower:
    def __init__(self) -> None:
        # Create a Chrome session and keep the browser open after the script ends.
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        # Open the login page and wait briefly for the form to load.
        self.driver.get(LOGIN_URL)
        time.sleep(2)

        # Close the cookie prompt if it appears.
        decline = self.driver.find_elements(By.XPATH, value="//button[contains(text(), 'Decline')]")
        if decline:
            decline[0].click()

        # Fill in the credentials and submit the form.
        username = self.driver.find_element(By.NAME, "username")
        password = self.driver.find_element(By.NAME, "password")

        username.send_keys(USERNAME)
        password.send_keys(PASSWORD)
        time.sleep(1)

        password.send_keys(Keys.ENTER)
        time.sleep(2)

        # Dismiss optional post-login prompts when they are displayed.
        save_info = self.driver.find_elements(By.XPATH, value="//div[contains(text(), 'Not now')]")
        if save_info:
            save_info[0].click()
        time.sleep(1)

        notifications = self.driver.find_elements(By.XPATH, value="//button[contains(text(), 'Not Now')]")
        if notifications:
            notifications[0].click()

    def find_followers(self):
        # Navigate to the selected account's followers dialog.
        self.driver.get(f"{BASE_URL}/u/{SIMILAR_ACCOUNT}/followers")
        time.sleep(2)

        # Locate the scrollable part of the dialog.
        modal = self.driver.find_element(By.CSS_SELECTOR, ".followers-scroll")
        for _ in range(10):
            # Move to the bottom so the page loads another batch of followers.
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(1)

    def follow(self):
        # Find all follow/unfollow buttons loaded into the followers dialog.
        all_button = self.driver.find_elements(By.CSS_SELECTOR, ".followers-scroll button")
        for button in all_button:
            # Do not click accounts that are already followed; that would open
            # an "Unfollow?" confirmation dialog instead.
            if button.get_attribute("data-following") == "true":
                continue

            try:
                # Follow the account represented by this button.
                button.click()
                time.sleep(1)
            except ElementClickInterceptedException:
                # If a confirmation dialog blocks the click, cancel it so the
                # script can continue with the remaining buttons.
                self.driver.find_element(By.XPATH, value="//button[normalize-space()='Cancel']",).click()


# Run the workflow in order: log in, load followers, then follow new accounts.
bot = InstaFollower()
bot.login()
bot.find_followers()
bot.follow()