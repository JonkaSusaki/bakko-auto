# driver_manager.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def create_driver():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # remove headless if you want visible Chrome
    # opts.add_argument("--headless")

    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1200, 900)
    return driver

driver = create_driver()  # singleton