import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from plugins.base import Plugin


class Plugin(Plugin):
    name = "Auto Queue"

    def __init__(self):
        self.enabled = False

    def on_ui(self, context):
        board_reader = context["board_reader"]

        if not board_reader.get_game_over_state():
            return

        time.sleep(1)
        self._click_new_game(context["driver"])

    def _click_new_game(self, driver):
        try:
            btn = driver.find_element(
                By.CSS_SELECTOR,
                '[data-cy="game-over-modal-new-game-button"]'
            )
            if btn.is_displayed():
                btn.click()
                print("[AUTO QUEUE] Clicked New Game")
                return True
            return False

        except NoSuchElementException:
            return False
        except ElementClickInterceptedException:
            print("[AUTO QUEUE] Click intercepted")
            return False
        except Exception as e:
            print(f"[AUTO QUEUE] Error: {e}")
            return False
