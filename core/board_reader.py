import chess
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

PIECE_MAP = {
    "wp": "P", "wr": "R", "wn": "N", "wb": "B", "wq": "Q", "wk": "K",
    "bp": "p", "br": "r", "bn": "n", "bb": "b", "bq": "q", "bk": "k",
}

START_FEN = chess.Board().board_fen()


class BoardReader:

    def __init__(self, driver):
        self.driver = driver

    def _get_board_element(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
        except NoSuchElementException:
            return None

    def read(self):
        board_el = self._get_board_element()
        if not board_el:
            logging.debug("Board element not found")
            return chess.Board(None)

        board = chess.Board(None)

        for piece_el in board_el.find_elements(By.CSS_SELECTOR, ".piece"):
            try:
                classes = piece_el.get_attribute("class").split()
            except StaleElementReferenceException:
                continue

            if len(classes) < 3:
                continue

            symbol = PIECE_MAP.get(classes[1])
            if not symbol:
                continue

            square_code = classes[2]
            try:
                file = int(square_code[7]) - 1
                rank = int(square_code[8]) - 1
                sq = chess.square(file, rank)
                board.set_piece_at(sq, chess.Piece.from_symbol(symbol))
            except (IndexError, ValueError):
                logging.debug(f"Bad square parse: {square_code}")

        return board

    def detect_turn(self):
        try:
            clocks = self.driver.find_elements(By.CSS_SELECTOR, ".clock-component")
            if len(clocks) < 2:
                return None

            board_el = self._get_board_element()
            if not board_el:
                return None

            flipped = "flipped" in board_el.get_attribute("class")
            top_clock, bottom_clock = clocks[0], clocks[1]
            bottom_is_white = "clock-white" in bottom_clock.get_attribute("class")

            if flipped:
                white_clock, black_clock = top_clock, bottom_clock
            else:
                white_clock = bottom_clock if bottom_is_white else top_clock
                black_clock = top_clock if bottom_is_white else bottom_clock

            if "clock-player-turn" in white_clock.get_attribute("class"):
                return chess.WHITE
            if "clock-player-turn" in black_clock.get_attribute("class"):
                return chess.BLACK

            return None

        except Exception as e:
            logging.debug(f"detect_turn error: {e}")
            return None

    def detect_player_color(self):
        try:
            board_el = self._get_board_element()
            if not board_el:
                return None
            classes = board_el.get_attribute("class") or ""
            return chess.BLACK if "flipped" in classes else chess.WHITE
        except Exception as e:
            logging.debug(f"detect_player_color error: {e}")
            return None

    def is_new_game(self, old_fen, new_fen):
        # Reset to starting position
        if new_fen == START_FEN and old_fen != START_FEN:
            return True

        # Large jump in piece count suggests a new game loaded
        old_pieces = sum(c.isalpha() for c in old_fen)
        new_pieces = sum(c.isalpha() for c in new_fen)
        if abs(old_pieces - new_pieces) > 10:
            return True

        return False

    def get_game_over_state(self):
        try:
            modal = self.driver.find_element(
                By.CSS_SELECTOR,
                ".board-modal-component.game-over-modal-container"
            )
            if not modal.is_displayed():
                return None

            title = modal.find_element(By.CSS_SELECTOR, ".header-title-component").text
            subtitle = modal.find_element(By.CSS_SELECTOR, ".header-subtitle-first-line").text

            return {"title": title, "reason": subtitle}

        except Exception:
            return None
