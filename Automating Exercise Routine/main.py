import os
import tempfile
import time
from pathlib import Path

# Selenium drives Chrome. Explicit waits make the script pause until elements
# are ready instead of interacting with a page that is still loading.
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    SessionNotCreatedException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


# --------------------------- Configuration ---------------------------
# Change these values when the website or class requirements change.
GYM_URL = "https://appbrewery.github.io/gym/"
TARGET_TIME = "6:00 PM"
RETRY_DELAY = 2

# Credentials are read from environment variables instead of being stored here.
# GYM_NAME is only used if the account needs to be registered automatically.
email = os.getenv("GYM_EMAIL")
password = os.getenv("GYM_PASSWORD")
name = os.getenv("GYM_NAME", "Gym Member")

if not email or not password:
    raise RuntimeError("Set GYM_EMAIL and GYM_PASSWORD before running.")


def create_driver() -> webdriver.Chrome:
    """Start Chrome with a reusable profile, falling back to a temporary one."""
    # Reusing a profile preserves browser settings between runs.
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument(f"--user-data-dir={Path.cwd() / 'chrome_profile'}")

    try:
        return webdriver.Chrome(options=options)

    except SessionNotCreatedException:
        # A profile can be locked when another Chrome process is using it.
        # A temporary profile allows this run to continue safely.
        print("Saved Chrome profile is unavailable; using a temporary profile.")
        profile_argument = next(
            argument
            for argument in options.arguments
            if argument.startswith("--user-data-dir=")
        )
        options.arguments.remove(profile_argument)
        options.add_argument(f"--user-data-dir={tempfile.mkdtemp(prefix='gym-selenium-')}")

        try:
            return webdriver.Chrome(options=options)

        except SessionNotCreatedException as error:
            raise RuntimeError("Chrome could not start. Close Chrome windows and try again.") from error


# All functions use this one browser session and one ten-second explicit wait.
driver = create_driver()
wait = WebDriverWait(driver, 10)
login_url = f"{GYM_URL.rstrip('/')}/login/"


def error_message() -> str:
    """Return the site's login or registration error, if one is displayed."""
    # An empty result means the page has not displayed an authentication error.
    errors = driver.find_elements(By.ID, "error-message")
    return errors[0].text.strip() if errors else ""


def submit_auth_form(register: bool) -> None:
    """Open the selected form, fill it, and submit it."""
    assert email is not None and password is not None
    driver.get(login_url)

    if register:
        # The login page switches between login and registration with this button.
        wait.until(ec.element_to_be_clickable((By.ID, "toggle-login-register"))).click()

    if register:
        # Registration has one extra field; login only needs email and password.
        wait.until(ec.presence_of_element_located((By.ID, "name-input"))).send_keys(name)

    # These two fields are shared by both forms, so fill them in one loop.
    for field_id, value in (
        ("email-input", email),
        ("password-input", password),
    ):
        field = wait.until(ec.presence_of_element_located((By.ID, field_id)))
        field.clear()
        field.send_keys(value)

    wait.until(ec.element_to_be_clickable((By.ID, "submit-button"))).click()


def auth_result(browser):
    """Tell WebDriverWait whether authentication succeeded or returned an error."""
    # The URL may change before the schedule elements render, so either success
    # signal is accepted. Otherwise return the site's visible error message.
    if browser.current_url.rstrip("/").endswith("/schedule"):
        return "success"
    if browser.find_elements(By.ID, "schedule-page"):
        return "success"
    return error_message() or False


def register_user() -> None:
    """Register the account, retrying only transient network failures."""
    attempt = 0
    while True:
        attempt += 1
        try:
            submit_auth_form(register=True)
            result = wait.until(auth_result)

            if result == "success":
                print(f"Registration succeeded on attempt {attempt}.")
                return
            if "already registered" in result.lower():
                # An existing account can be used by the login flow.
                print("Account already exists; continuing with login.")
                return
            if "network request failed" not in result.lower():
                # Permanent errors should be reported instead of retried forever.
                raise RuntimeError(f"Registration failed: {result}")
        except TimeoutException:
            result = "timed out"

        # Only network failures and timeouts reach this retry path.
        print(f"Registration attempt {attempt} {result}; retrying...")
        time.sleep(RETRY_DELAY)


def login_until_success() -> None:
    """Log in until successful, registering the account if it does not exist."""
    registration_attempted = False
    attempt = 0

    while True:
        attempt += 1
        try:
            submit_auth_form(register=False)
            result = wait.until(auth_result)

            if result == "success":
                print(f"Login succeeded on attempt {attempt}.")
                return

            # These messages mean the credentials are valid in format but no
            # account exists, so registration should be attempted once.
            unknown_account_errors = (
                "user not found",
                "user details not available",
                "not registered",
            )
            if any(text in result.lower() for text in unknown_account_errors):
                if registration_attempted:
                    # Prevent an endless register/login loop if registration, appears to succeed but the account remains unavailable.
                    raise RuntimeError("Registration completed, but the account is still unavailable.")

                registration_attempted = True
                print("Account not found; registering the configured user.")
                register_user()
                continue

            if "network request failed" not in result.lower():
                # Invalid credentials and other permanent errors should stop.
                raise RuntimeError(f"Login failed: {result}")
        except TimeoutException:
            result = "timed out"

        # Network failures and timeouts are treated as temporary issues.
        print(f"Login attempt {attempt} {result}; retrying...")
        time.sleep(RETRY_DELAY)


def book_target_classes() -> int:
    """Book or join the waitlist for Tuesday/Thursday classes at TARGET_TIME."""
    # Keep separate counts for reporting, then return their combined total.
    counts = {"booked": 0, "waitlisted": 0, "existing": 0}

    # Each class is displayed as a card with an id beginning with "class-card-".
    for card in driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']"):
        day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
        day = day_group.find_element(By.TAG_NAME, "h2").text
        class_time = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text

        if not any(day_name in day for day_name in ("Tue", "Thu")):
            # Classes on other days are not part of this automation.
            continue
        if TARGET_TIME not in class_time:
            # Ignore classes at times other than the configured target time.
            continue

        class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text
        button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")
        action = button.text

        if action in ("Booked", "Waitlisted"):
            # Do not click a class that is already booked or waitlisted.
            counts["existing"] += 1
            print(f"Already {action.lower()}: {class_name} on {day}")
        elif action == "Book Class":
            # There is space available, so make a normal booking.
            button.click()
            counts["booked"] += 1
            print(f"Booked: {class_name} on {day}")
        elif action == "Join Waitlist":
            # The class is full, but the user can join its waitlist.
            button.click()
            counts["waitlisted"] += 1
            print(f"Joined waitlist: {class_name} on {day}")

        time.sleep(0.5)

    return sum(counts.values())


def verify_bookings(expected_count: int) -> None:
    """Open My Bookings and count the matching Tuesday/Thursday bookings."""
    # Use the known route directly because the site's link transition is flaky.
    driver.get(f"{GYM_URL.rstrip('/')}/my-bookings/")
    wait.until(ec.presence_of_element_located((By.ID, "my-bookings-page")))

    verified_count = 0
    # The page may contain non-booking cards, so inspect only cards with a
    # matching "when" paragraph and the requested day/time.
    for card in driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']"):
        try:
            when_text = card.find_element(By.XPATH, ".//p[strong[text()='when:']]").text

            if (("Tue" in when_text or "Thu" in when_text) and TARGET_TIME in when_text):
                print(f"Verified: {card.find_element(By.TAG_NAME, 'h3').text}")
                verified_count += 1

        except NoSuchElementException:
            # Non-booking cards do not contain a "when" paragraph.
            continue

    print(
        f"\nVerification result: expected {expected_count}, "
        f"found {verified_count}.")

    if expected_count == verified_count:
        print("Success: all bookings are verified.")
    else:
        print(f"Mismatch: missing {expected_count - verified_count} bookings.")


# Run the workflow in order: authenticate, book matching classes, and verify
# that the expected bookings appear on the account page.
login_until_success()
total_booked = book_target_classes()
print(f"\nTotal Tuesday/Thursday {TARGET_TIME} classes: {total_booked}")
verify_bookings(total_booked)
