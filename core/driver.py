from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

driver = None


def start_driver():

    global driver

    if driver is not None:
        logging.warning("Driver already started.")
        return driver

    logging.info("Starting Chrome driver...")

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)

        driver.get("https://www.chess.com/play/online")

        logging.info("Driver started successfully.")

    except Exception as e:

        logging.exception("Driver failed to start")
        raise e

    return driver


def get_driver():

    global driver

    if driver is None:
        logging.warning("Driver requested before initialization.")
        driver = start_driver()

    return driver


def close_driver():

    global driver

    if driver:

        logging.info("Closing driver")

        try:
            driver.quit()
        except:
            logging.warning("Driver failed to close")

        driver = None
