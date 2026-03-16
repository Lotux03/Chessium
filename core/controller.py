import logging
import threading
import time
import chess.engine
import chess
import os

class Controller:

    def __init__(self, engine, board_reader, overlays, plugins, driver):

        self.engine = engine
        self.board_reader = board_reader
        self.overlays = overlays
        self.plugins = plugins
        self.driver = driver

        self.running = True

    def start_loop(self):

        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):

        print("[CONTROLLER] Loop started")

        while self.running:
            try:

                board = self.board_reader.read()

                if not board.piece_map():
                    time.sleep(0.2)
                    continue

                context = {
                    "board": board,
                    "overlay": self.overlays,
                    "driver": self.driver,
                    "engine": self.engine
                }

                # print(context)

                # board update event
                self.plugins.trigger("on_board", context)

                turn = self.board_reader.detect_turn()
                if turn is None:
                    continue
                board.turn = turn

                try:
                    move = self.engine.get_best_move(board)
                except:
                    print("Engine crashed. Restarting...")
                    self.engine.quit()  # Make sure old process is dead
                    path = os.path.join(os.path.dirname(__file__), "../", "stockfish.exe")
                    path = os.path.abspath(path)
                    assert os.path.exists(path), f"Engine not found at {path}"
                    self.engine = chess.engine.SimpleEngine.popen_uci(path)
                    self.engine.configure({"Threads": 2, "Hash": 128})
                    continue

                if move:

                    context["move"] = move

                    # print("running on best move")
                    # engine result event
                    self.plugins.trigger("on_best_move", move, board, turn, context)

            except Exception as e:

                logging.error("Controller error")
                logging.error(e)


            time.sleep(0.2)

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