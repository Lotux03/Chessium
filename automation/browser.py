from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from core.driver import get_driver


class Browser:

    def __init__(self):
        self.driver = get_driver()

    def site_loaded(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
            return True
        except NoSuchElementException:
            return False
