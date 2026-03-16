from plugins.base import Plugin
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

class Plugin(Plugin):
    name = "Auto Move [wip]"

    def __init__(self):
        self.enabled = False
        self.move_count = 0
        self.count = 0

    def on_best_move(self, move, board, turn, context):
        if not self.enabled:
            return

        driver = context["driver"]
        board_el = driver.find_element("css selector", "wc-chess-board")

        start = move[:2]
        end = move[2:]

        if self.count == 1:
            self.count = 0
            #time.sleep(self.delay())
        else:
            self.count = 1
            return
    
        if(turn):
            self.move_count += 1
            self.move_piece(start, end, board_el, driver)

    def move_piece(self, start, end, board_el, driver):
        self.click_square(start, board_el, driver)
        time.sleep(0.05)
        self.click_square(end, board_el, driver)

    def click_square(self, square, board_el, driver):
        #flipped = "flipped" in (board_el.get_attribute("class") or "")
        x, y = self.square_to_xy_move(square, False)#flipped)

        rect = board_el.rect
        px = rect["width"] * x
        py = rect["height"] * y
        offset_x = px - rect["width"] / 2
        offset_y = py - rect["height"] / 2

        ActionChains(driver)\
            .move_to_element_with_offset(board_el, offset_x, offset_y)\
            .click()\
            .perform()

    def square_to_xy_move(self, square, flipped=False):
        files = "abcdefgh"
        file = files.index(square[0])
        rank = int(square[1]) - 1

        if flipped:
            file = 7 - file
            rank = 7 - rank

        x = (file + 0.5) / 8
        y = (7 - rank + 0.5) / 8
        return x, y

    def delay(self):
        if self.move_count <= 6:
            num = random.randint(0, 5)
        elif self.move_count <= 15:
            num = random.randint(6, 10)
        else:
            num = random.randint(3, 25)
        return num