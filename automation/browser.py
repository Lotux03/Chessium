import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from core.driver import get_driver

class Browser:
    def __init__(self):
        self.driver = get_driver()

    def start(self):

        logging.info("Starting Chrome")

        options = Options()

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.driver.get("https://www.chess.com/play/online")

    def site_loaded(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
            return True
        except:
            return False