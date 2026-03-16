from plugins.base import Plugin
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import chess

class Plugin(Plugin):
    name = "Auto Move [wip]"

    def __init__(self):
        self.enabled = False
        self.move_count = 0
        self.count = 0

    def on_best_move(self, engine, board_reader, overlays, plugins, driver, context):
        # Check if enabled
        if not self.enabled:
            return
        
        # Variables
        move = context['move']
        turn = board_reader.detect_turn()
        player_color = board_reader.detect_player_color()
        driver = context["driver"]
        board_el = driver.find_element("css selector", "wc-chess-board")
        start = move[:2]
        end = move[2:]
        flipped = False

        # Set a delay for move
        if self.count == 1:
            self.count = 0
            time.sleep(self.delay())
        else:
            self.count = 1
            return
    
        # Check if its my turn to move
        if(turn == player_color):
            if (turn == chess.BLACK):
                flipped = True
            # Move
            self.move_count += 1
            self.move_piece(start, end, board_el, driver, flipped)

    def move_piece(self, start, end, board_el, driver, flipped):
        self.click_square(start, board_el, driver, flipped)
        time.sleep(0.05)
        self.click_square(end, board_el, driver, flipped)

    def click_square(self, square, board_el, driver, flipped):
        x, y = self.square_to_xy_move(square, flipped) #flipped)

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
            num = random.randint(3, 10)
        return num