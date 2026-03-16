import chess
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException



piece_map = {
    "wp": "P","wr":"R","wn":"N","wb":"B","wq":"Q","wk":"K",
    "bp": "p","br":"r","bn":"n","bb":"b","bq":"q","bk":"k"
}


class BoardReader:

    def __init__(self, driver):
        self.driver = driver

    def get_board_element(self):

        try:
            return self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")

        except:
            return None

    def read(self):

        board_el = self.get_board_element()

        if not board_el:
            logging.debug("Board not found.")
            return chess.Board(None)

        board = chess.Board(None)

        pieces = board_el.find_elements(By.CSS_SELECTOR, ".piece")

        for p in pieces:

            try:
                classes = p.get_attribute("class").split()

            except StaleElementReferenceException:
                continue

            if len(classes) < 3:
                continue

            piece_code = classes[1]
            square_code = classes[2]

            symbol = piece_map.get(piece_code)

            if not symbol:
                continue

            try:

                file = int(square_code[7]) - 1
                rank = int(square_code[8]) - 1

                sq = chess.square(file, rank)

                board.set_piece_at(
                    sq,
                    chess.Piece.from_symbol(symbol)
                )

            except:
                print(f"Bad square parse: {square_code}")

        return board
    
    def detect_turn(self):
        try:
            clocks = self.driver.find_elements(By.CSS_SELECTOR, ".clock-component")
            if len(clocks) < 2:
                return None

            board_el = self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
            flipped = "flipped" in board_el.get_attribute("class")

            top_clock, bottom_clock = clocks[0], clocks[1]
            bottom_is_white = "clock-white" in bottom_clock.get_attribute("class")

            if flipped:
                white_clock = top_clock
                black_clock = bottom_clock
            else:
                white_clock = bottom_clock if bottom_is_white else top_clock
                black_clock = bottom_clock if bottom_clock != white_clock else top_clock

            if "clock-player-turn" in white_clock.get_attribute("class"):
                return chess.WHITE
            if "clock-player-turn" in black_clock.get_attribute("class"):
                return chess.BLACK

            return None
        except Exception as e:
            print("detect_active_turn error:", e)
            return None
        
    def detect_player_color(self):
        try:
            board = self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")

            classes = board.get_attribute("class") or ""

            if "flipped" in classes:
                return chess.BLACK
            else:
                return chess.WHITE

        except Exception as e:
            print("[BOARD_READER] detect_player_color error:", e)
            return None
