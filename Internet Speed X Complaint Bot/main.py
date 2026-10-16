import os
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Speedtest and Y page URLs.
SPEEDTEST_URL = "https://www.speedtest.net/"
Y_LOGIN_URL = "https://app.100daysofpython.dev/services/y/login"

# Internet plan speeds used in the complaint message.
PROMISED_DOWN = 1000
PROMISED_UP = 1000

# Credentials are read from the root .env file and are never hard-coded here.
Y_EMAIL = os.getenv("Y_EMAIL")
Y_PASSWORD = os.getenv("Y_PASSWORD")


class InternetSpeedTwitterBot:
    """Measure the internet connection and post the result to Y."""

    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        # These values are filled after the speed test finishes.
        self.down = ""
        self.up = ""

    def get_internet_speed(self) -> None:
        """Run Speedtest and save the download and upload speeds."""
        self.driver.get(SPEEDTEST_URL)

        # The page may show either an "Accept" or "Continue" privacy button.
        self._dismiss_privacy_dialog()

        # Start the test only after the current GO button is available.
        wait = WebDriverWait(self.driver, 10)
        start_button = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[aria-label^="start speed test"]')
            )
        )

        # The fixed header can cover the button, so scroll it below the header
        # before triggering its click handler.
        self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            window.scrollBy(0, rect.top - 120);
            arguments[0].click();
            """,
            start_button,
        )

        # Wait for the results instead of guessing how long the test will take.
        result_wait = WebDriverWait(self.driver, 90)
        self.down = self._read_speed(result_wait, "Download")
        self.up = self._read_speed(result_wait, "Upload")

    def _dismiss_privacy_dialog(self) -> None:
        """Click the privacy button when Speedtest displays one."""
        privacy_buttons = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#onetrust-accept-btn-handler, button",
        )

        for button in privacy_buttons:
            button_id = button.get_attribute("id")
            button_text = button.text.strip()

            if button_id == "onetrust-accept-btn-handler" or button_text in {
                "Continue",
                "Accept",
            }:
                self.driver.execute_script("arguments[0].click();", button)
                return

    def _read_speed(self, wait: WebDriverWait, direction: str) -> str:
        """Read a completed Download or Upload value from the results card."""
        result_selector = (
            f"//p[contains(normalize-space(), '{direction}')]"
            "/following-sibling::h3[1]"
        )
        return wait.until(EC.visibility_of_element_located((By.XPATH, result_selector))).text

    def tweet_at_provider(self) -> None:
        """Log in to Y and post a message containing the measured speeds."""
        if not Y_EMAIL:
            raise ValueError("Y_EMAIL environment variable is not set")
        if not Y_PASSWORD:
            raise ValueError("Y_PASSWORD environment variable is not set")

        # Fill in the login form and submit it.
        self.driver.get(Y_LOGIN_URL)

        wait = WebDriverWait(self.driver, 30)
        wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(Y_EMAIL)
        wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(Y_PASSWORD)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))).click()

        # The compose box is loaded only after a successful login.
        tweet_compose = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Post text"]'))
        )
        tweet = (
            f"Hey Internet Provider, why is my speed "
            f"{self.down}down/{self.up}up when I pay for "
            f"{PROMISED_DOWN}down/{PROMISED_UP}up?!"
        )
        tweet_compose.send_keys(tweet)

        # Submit the message after its text has been entered.
        post_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Post' or @aria-label='Post']"
        ))).click()


# Run the speed test first so the measured values are available to the post.
bot = InternetSpeedTwitterBot()
bot.get_internet_speed()
bot.tweet_at_provider()
# Close Chrome after the post has been submitted.
bot.driver.quit()
