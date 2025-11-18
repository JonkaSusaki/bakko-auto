# config.py
import os
from selenium.webdriver.common.by import By

# --- Sensitive Credentials ---
# Load from environment variables, with a fallback to your hardcoded values
INSTAGRAM_USER = os.getenv("INSTAGRAM_USER", "<your_instagram_username>")
INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS", "<your_instagram_password>")

# --- URLs ---
LOGIN_URL = "https://www.instagram.com/accounts/login/"
GRAPHQL_URL_TEMPLATE = "https://www.instagram.com/graphql/query"

# This is the hardcoded query from your original file
TARGET_URL = "https://www.instagram.com/graphql/query?variables=%7B%22data%22%3A%7B%22count%22%3A12%2C%22include_relationship_info%22%3Atrue%2C%22latest_besties_reel_media%22%3Atrue%2C%22latest_reel_media%22%3Atrue%7D%2C%22username%22%3A%22aproveiteacidade%22%2C%22__relay_internal__pv__PolarisFeedShareMenurelayprovider%22%3Afalse%7D&doc_id=7898261790222653&server_timestamps=True"

# --- Constants for GraphQL ---
GRAPHQL_DOC_ID = "7898261790222653"

# --- Selenium Selectors ---
LOGIN_SELECTORS = [
    (By.NAME, "username"),
    (By.CSS_SELECTOR, "input[name='username']"),
    (By.CSS_SELECTOR, "input[name='password']"),
]