from plugins.base import Plugin
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

class Plugin(Plugin):
    name = "Auto Queue"

    def __init__(self):
        self.enabled = False
        self.driver = None

    def on_ui(self, context):
        self.driver = context["driver"]
        board_reader = context["board_reader"]
        if (board_reader.get_game_over_state()):
            time.sleep(1)
            self.click_new_game()

    def click_new_game(self):
        try:
            btn = self.driver.find_element(
                By.CSS_SELECTOR,
                '[data-cy="game-over-modal-new-game-button"]'
            )

            if btn.is_displayed():
                btn.click()
                print("[AUTO] Clicked New Game")
                return True

            return False

        except NoSuchElementException:
            return False

        except ElementClickInterceptedException:
            print("[AUTO] Click intercepted (maybe animation?)")
            return False

        except Exception as e:
            print("[AUTO] click_new_game error:", e)
            return False