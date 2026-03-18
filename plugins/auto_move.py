import time
import random
import chess
from selenium.webdriver.common.action_chains import ActionChains
from plugins.base import Plugin


class Plugin(Plugin):
    name = "Auto Move"

    def __init__(self):
        self.enabled = False
        self.move_count = 0

    def on_best_move(self, context):
        board_reader = context["board_reader"]
        driver = context["driver"]
        move = context.get("move")

        if not move or len(move) < 4:
            return

        turn = board_reader.detect_turn()
        player_color = board_reader.detect_player_color()

        if turn != player_color:
            return

        time.sleep(self._delay())

        flipped = (turn == chess.BLACK)
        board_el = driver.find_element("css selector", "wc-chess-board")

        self.move_count += 1
        self._move_piece(move[:2], move[2:4], board_el, driver, flipped)

    def _move_piece(self, start, end, board_el, driver, flipped):
        self._click_square(start, board_el, driver, flipped)
        time.sleep(0.05)
        self._click_square(end, board_el, driver, flipped)

    def _click_square(self, square, board_el, driver, flipped):
        x, y = self._square_to_xy(square, flipped)
        rect = board_el.rect
        offset_x = rect["width"] * x - rect["width"] / 2
        offset_y = rect["height"] * y - rect["height"] / 2

        ActionChains(driver) \
            .move_to_element_with_offset(board_el, offset_x, offset_y) \
            .click() \
            .perform()

    def _square_to_xy(self, square, flipped=False):
        files = "abcdefgh"
        file = files.index(square[0])
        rank = int(square[1]) - 1

        if flipped:
            file = 7 - file
            rank = 7 - rank

        return (file + 0.5) / 8, (7 - rank + 0.5) / 8

    def _delay(self):
        if self.move_count <= 6:
            return random.randint(0, 5)
        elif self.move_count <= 15:
            return random.randint(6, 10)
        else:
            return random.randint(3, 10)
