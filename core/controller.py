import logging
import threading
import time
import chess
from selenium.webdriver.common.by import By


class Controller:

    def __init__(self, engine, board_reader, plugins, driver):
        self.engine = engine
        self.board_reader = board_reader
        self.plugins = plugins
        self.driver = driver

        self.board = None
        self.info = None
        self.move = None
        self.last_fen = None
        self.running = True

    def start_loop(self):
        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        print("[CONTROLLER] Loop started")

        while self.running:
            try:
                self._tick()
            except Exception as e:
                logging.error("Controller error: %s", e)

            time.sleep(0.2)

    def _tick(self):
        self._trigger_on_ui()

        game_over = self.board_reader.get_game_over_state()
        if game_over:
            print(f"[CONTROLLER] Game over: {game_over['title']} - {game_over['reason']}")
            self._handle_game_over()
            return

        self.board = self.board_reader.read()

        if not self.board or not self.board.piece_map():
            return

        fen = self.board.board_fen()

        if self.last_fen and self.board_reader.is_new_game(self.last_fen, fen):
            print("[CONTROLLER] New game detected")
            self.info = None
            self.move = None
            self.engine.restart()

        if fen != self.last_fen:
            self._trigger_on_move()
            self.last_fen = fen

        self._trigger_on_best_move()

    def _handle_game_over(self):
        self.engine.kill()
        self._reset_state()

        new_board = self._wait_for_new_board()
        if new_board:
            self.board = new_board
            self.last_fen = new_board.board_fen()
            print("[CONTROLLER] Ready for new game")
            self.engine.restart()
            self._trigger_on_move()

    def _wait_for_new_board(self, timeout=10):
        print("[CONTROLLER] Waiting for new board...")
        start = time.time()

        while time.time() - start < timeout:
            board = self.board_reader.read()
            if board and board.piece_map() and len(board.board_fen()) > 10:
                print("[CONTROLLER] New board detected")
                return board
            time.sleep(0.3)

        print("[CONTROLLER] Timeout waiting for new board")
        return None

    def _reset_state(self):
        print("[CONTROLLER] Resetting game state")
        self.last_fen = None
        self.board = None
        self.info = None
        self.move = None

    def _resolve_turn(self):
        turn = self.board_reader.detect_turn()
        if turn is not None:
            return turn

        player_color = self.board_reader.detect_player_color()
        if player_color in (chess.WHITE, chess.BLACK):
            return player_color

        return None

    def _trigger_on_ui(self):
        self.plugins.trigger("on_ui", self._make_context())

    def _trigger_on_best_move(self):
        if not self.move:
            return
        self.plugins.trigger("on_best_move", self._make_context())

    def _trigger_on_move(self):
        turn = self._resolve_turn()
        if turn is None:
            return

        self.board.turn = turn

        try:
            score, move = self.engine.analyse_position(self.board)
            if score is None or move is None:
                return

            self.info = score
            self.move = move

        except chess.engine.EngineTerminatedError:
            print("[ENGINE] Terminated unexpectedly, restarting...")
            self.engine.restart()
            return

        except chess.engine.EngineError as e:
            print("[ENGINE] Error:", e)
            return

        self.plugins.trigger("on_move", self._make_context())

    def _make_context(self):
        return {
            "score": self.info,
            "move": self.move,
            "engine": self.engine,
            "board": self.board,
            "board_reader": self.board_reader,
            "plugins": self.plugins,
            "driver": self.driver,
        }
