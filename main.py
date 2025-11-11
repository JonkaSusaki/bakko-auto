# main.py
import instaloader
import sys
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import json
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

app = FastAPI()

INSTAGRAM_USER = "j31789958"
INSTAGRAM_PASS = "aVM9aGvV!n)LnQM"

LOGIN_SELECTORS = [
    (By.NAME, "username"),
    (By.CSS_SELECTOR, "input[name='username']"),
    (By.CSS_SELECTOR, "input[name='password']"),
]

def is_logged_in(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Profile']")
        return True
    except:
        return False
    
def wait_until_logged_in(driver, username, password, timeout=600):
    """
    Polls every 3 seconds: am I logged in?
    If not, attempts login again.
    Timeout after X seconds.
    """
    start = time.time()
    
    while True:
        if is_logged_in(driver):
            return True  # success
        
        # If timeout exceeded → fail
        if time.time() - start > timeout:
            raise Exception("Timeout waiting for login")
        
        # If still on a login screen → try logging in again
        ensure_logged_in(driver, username, password)
        
        time.sleep(3)

def is_login_screen(driver):
    for by, sel in LOGIN_SELECTORS:
        try:
            if driver.find_element(by, sel):
                return True
        except NoSuchElementException:
            continue
    return False

def perform_login(driver, username, password):
    try:
        # wait for UI
        time.sleep(5)

        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")

        user_input.clear()
        pass_input.clear()

        user_input.send_keys(username)
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.ENTER)

        # give time for redirection
        time.sleep(6)

    except Exception as e:
        return

def ensure_logged_in(driver, username, password):
    """
    Detects if Selenium is currently on a login screen.
    If yes, login again.
    """
    if is_login_screen(driver):
        perform_login(driver, username, password)
        time.sleep(3)

def get_instaloader():
    L = instaloader.Instaloader()

    L.user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/100.0.4896.75 Safari/537.36"
    )
    L.sleep = True
    L.min_sleep = 5
    L.max_sleep = 15

    try:
        L.load_session_from_file(INSTAGRAM_USER)
    except (FileNotFoundError, instaloader.exceptions.ConnectionException):
        try:
            L.login(INSTAGRAM_USER, INSTAGRAM_PASS)
            L.save_session_to_file()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Login failed: {e}")

    return L


@app.get("/profile/{username}")
def get_profile(username: str):
    L = get_instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return {"username": username, "profile_url": profile.get_browser_url()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {e}")
    

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Run headless only if needed:
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1200, 800)
    return driver


def instagram_login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")

    ensure_logged_in(driver, username, password)

    # Wait for home page load OR for any known element after login
    time.sleep(8)  # Adjust as needed; Instagram is dynamic


def open_new_tab_and_get_html(driver, url, username, password):
    # 1. Safely open the tab
    try:
        new_tab = open_new_tab_safe(driver, url)
    except Exception:
        # Retry once if Instagram blocked or closed the tab
        time.sleep(1)
        new_tab = open_new_tab_safe(driver, url)

    # 2. After switching, handle login screen if redirected
    ensure_logged_in(driver, username, password)

    # 3. Wait for page load
    time.sleep(6)

    # 4. Instagram sometimes closes the tab AFTER login → detect & reopen
    try:
        _ = driver.current_url
    except NoSuchWindowException:
        # Re-open same URL
        new_tab = open_new_tab_safe(driver, url)
        ensure_logged_in(driver, username, password)
        time.sleep(5)

    # 5. Return html
    return driver.page_source

def open_new_tab_safe(driver, url, timeout=10):
    initial_tabs = driver.window_handles

    # Open new tab
    driver.execute_script(f"window.open('{url}', '_blank');")

    # Wait for a new tab to appear
    start = time.time()
    while len(driver.window_handles) == len(initial_tabs):
        if time.time() - start > timeout:
            raise Exception("Timeout: new tab did not open")
        time.sleep(0.2)

    # The last tab is the one we just opened
    new_tab = [h for h in driver.window_handles if h not in initial_tabs][0]

    # Safely switch to the new tab with retries
    for _ in range(5):
        try:
            driver.switch_to.window(new_tab)
            return new_tab
        except NoSuchWindowException:
            time.sleep(0.3)

    raise Exception("Failed to switch to newly opened tab")

TARGET_URL = "https://www.instagram.com/graphql/query?variables=%7B%22data%22%3A%7B%22count%22%3A12%2C%22include_relationship_info%22%3Atrue%2C%22latest_besties_reel_media%22%3Atrue%2C%22latest_reel_media%22%3Atrue%7D%2C%22username%22%3A%22aproveiteacidade%22%2C%22__relay_internal__pv__PolarisFeedShareMenurelayprovider%22%3Afalse%7D&doc_id=7898261790222653&server_timestamps=true"

USERNAME = "j31789958"
PASSWORD = "aVM9aGvV!n)LnQM"

def extract_instagram_data(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # Extract <pre> content
    pre = soup.find("pre")
    if not pre:
        raise ValueError("<pre> tag not found")

    raw_json = pre.get_text()
    data = json.loads(raw_json)

    # Navigate to edges
    edges = (
        data
        .get("data", {})
        .get("xdt_api__v1__feed__user_timeline_graphql_connection", {})
        .get("edges", [])
    )

    results = []

    for edge in edges:
        node = edge.get("node", {})

        # Extract caption
        caption = (
            node.get("caption", {})
                .get("text", "")
        )

        # Get first candidate with width > 500
        candidates = (
            node.get("image_versions2", {})
                .get("candidates", [])
        )

        candidate_over_500 = next(
            (c for c in candidates if c.get("width", 0) > 500),
            None
        )

        results.append({
            "caption": caption,
            "image": candidate_over_500
        })

    return results

@app.get("/fetch-instagram")
def fetch_instagram():
    driver = create_driver()
    try:
        instagram_login(driver, USERNAME, PASSWORD)
        wait_until_logged_in(driver, USERNAME, PASSWORD)
        html = open_new_tab_and_get_html(driver, TARGET_URL, USERNAME, PASSWORD)
        return {"content": extract_instagram_data(html)}
    finally:
        driver.quit()