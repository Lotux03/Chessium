import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

_driver = None


def start_driver():
    global _driver

    if _driver is not None:
        logging.warning("Driver already started.")
        return _driver

    logging.info("Starting Chrome driver...")

    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        _driver = webdriver.Chrome(options=options)
        _driver.get("https://www.chess.com/play/online")
        logging.info("Driver started successfully.")
    except Exception as e:
        logging.exception("Driver failed to start")
        raise

    return _driver


def get_driver():
    global _driver

    if _driver is None:
        logging.warning("Driver requested before initialization.")
        return start_driver()

    return _driver


def close_driver():
    global _driver

    if _driver:
        logging.info("Closing driver")
        try:
            _driver.quit()
        except Exception:
            logging.warning("Driver failed to close cleanly")
        finally:
            _driver = None
