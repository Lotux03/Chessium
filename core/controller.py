import logging
import threading
import time
import chess
import automation.browser as browser

class Controller:

    def __init__(self, engine, board_reader, overlays, plugins, driver):

        self.engine = engine
        self.board_reader = board_reader
        self.overlays = overlays
        self.plugins = plugins
        self.driver = driver
        self.browser = browser.Browser()
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
                self.board = self.board_reader.read()

                if not self.board.piece_map():
                    time.sleep(0.2)
                    continue

                self.trigger_on_ui()

                fen = self.board.board_fen()

                if self.last_fen:
                    if self.board_reader.is_new_game(self.last_fen, fen):
                        print("[CONTROLLER] New game detected")
                        self.info = None
                        self.move = None
                        # OPTIONAL:
                        # self.engine.restart()

                if fen != self.last_fen:
                    self.trigger_on_move()
                    self.last_fen = fen

                self.trigger_on_best_move()

            except Exception as e:
                logging.error("Controller error")
                logging.error(e)

            time.sleep(0.2)

    def trigger_on_ui(self):
        if(self.browser.site_loaded()):
            self.plugins.trigger("on_ui", self.create_context())

    def trigger_on_best_move(self):
        # Check if its the players turn turn
        if not self.move:
            return
        
        # Apply Context
        context = self.create_context()
            
        self.plugins.trigger("on_best_move", context)

    def trigger_on_move(self):
        turn = self.board_reader.detect_turn()
        if turn is None:
            return
        
        self.board.turn = turn
        
        # Get move score
        try:
            score, move = self.engine.analyse_position(self.board)

            if score is None or move is None:
                return

            self.info = score
            self.move = move

        except chess.engine.EngineTerminatedError:
            print("[ENGINE] Engine terminated. Restarting...")
            self.engine.restart()

        except chess.engine.EngineError as e:
            print("[ENGINE] Engine error:", e)
        
        self.plugins.trigger("on_board", self.create_context())

    def trigger(self, event, *args, **kwargs):

        for plugin in self.plugins:

            if not getattr(plugin, "enabled", True):
                continue

            func = getattr(plugin, event, None)

            if not callable(func):
                continue

            try:

                func(*args, **kwargs)

            except Exception as e:

                print(f"[PLUGIN ERROR] {plugin.name} -> {event}")
                print(e)

    def create_context(self):

        return {
            "score": self.info,
            "move": self.move,
            "engine": self.engine,
            "board": self.board,
            "board_reader": self.board_reader,
            "plugins": self.plugins,
            "driver": self.driver,
            "overlay": self.overlays
        }