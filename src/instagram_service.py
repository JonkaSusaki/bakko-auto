import time
import json
import urllib.parse
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from datetime import datetime

# Import the global driver instance
from driver_chrome import driver 
# Import settings
import config

# === Login & Session Management ===

def is_logged_in(driver):
    try:
        driver.get_cookie("sessionid")
        return True
    except:
        return False

def is_login_screen(driver):
    for by, sel in config.LOGIN_SELECTORS:
        try:
            if driver.find_element(by, sel):
                return True
        except NoSuchElementException:
            continue
    return False

def perform_login(driver, username, password):
    try:
        time.sleep(5) # wait for UI
        user_input = driver.find_element(By.NAME, "username")
        pass_input = driver.find_element(By.NAME, "password")

        user_input.clear()
        pass_input.clear()

        user_input.send_keys(username)
        pass_input.send_keys(password)
        pass_input.send_keys(Keys.ENTER)
        time.sleep(6) # give time for redirection
    except Exception as e:
        print(f"Error during login attempt: {e}")
        return

def ensure_logged_in(driver, username, password):
    if is_login_screen(driver):
        print("Login screen detected, attempting login...")
        perform_login(driver, username, password) # Was commented out, now active
        time.sleep(3)

def wait_until_logged_in(driver, username, password, timeout=600):
    start = time.time()
    while True:
        print("Waiting for login...")
        if is_logged_in(driver):
            print("Login successful.")
            return True # success
        
        if time.time() - start > timeout:
            raise Exception("Timeout waiting for login")
        
        ensure_logged_in(driver, username, password)
        time.sleep(3)

def instagram_login(driver, username, password):
    driver.get(config.LOGIN_URL)
    ensure_logged_in(driver, username, password)
    time.sleep(8) # Wait for home page load


# === Tab & HTML Fetching ===

def open_new_tab_safe(driver, url, timeout=10):
    initial_tabs = driver.window_handles
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

def open_new_tab_and_get_html(driver, url, username, password):
    print(f"Opening new tab: {url}")
    try:
        open_new_tab_safe(driver, url)
    except Exception:
        time.sleep(1)
        open_new_tab_safe(driver, url) # Retry

    ensure_logged_in(driver, username, password)
    time.sleep(6)

    try:
        _ = driver.current_url # Check if tab is still open
    except NoSuchWindowException:
        print("Tab closed unexpectedly, reopening...")
        open_new_tab_safe(driver, url)
        ensure_logged_in(driver, username, password)
        time.sleep(5)

    return driver.page_source

# === Data Parsing ===

def extract_instagram_data(html: str):
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    if not pre:
        raise ValueError("<pre> tag not found")

    raw_json = pre.get_text()
    data = json.loads(raw_json)

    edges = (
        data
        .get("data", {})
        .get("xdt_api__v1__feed__user_timeline_graphql_connection", {})
        .get("edges", [])
    )

    results = []
    for edge in edges:
        node = edge.get("node", {})
        caption = (
            node.get("caption", {})
                .get("text", "")
        )
        date = (
            node.get("caption", {})
                .get("created_at", "")
        )
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
            "image": candidate_over_500,
            "date": datetime.fromtimestamp(date)
        })
    return results

# === Utility ===

def create_instagram_link(username):
    variables = {
        "data": {
            "count": 12,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "username": username,
        "__relay_internal__pv__PolarisFeedShareMenurelayprovider": False
    }

    var2 = {
        "variables": json.dumps(variables, separators=(',', ':')),
        "doc_id": config.GRAPHQL_DOC_ID,
        "server_timestamps": True
    }

    query_string = urllib.parse.urlencode(var2)
    return f"{config.GRAPHQL_URL_TEMPLATE}?{query_string}"