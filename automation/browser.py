import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from core.driver import get_driver

class Browser:

    def start(self):

        logging.info("Starting Chrome")

        options = Options()

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = get_driver()

        driver.get("https://www.chess.com/play/online")
