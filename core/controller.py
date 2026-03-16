import logging
import threading
import time
import chess.engine
import chess
import os
import automation.browser as browser

class Controller:

    def __init__(self, engine, board_reader, overlays, plugins, driver):

        self.engine = engine
        self.board_reader = board_reader
        self.overlays = overlays
        self.plugins = plugins
        self.driver = driver
        self.browser = browser.Browser()

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
                    "overlay": self.overlays,
                    "driver": self.driver,
                    "engine": self.engine
                }

                if(self.browser.site_loaded()):
                    self.plugins.trigger("on_ui", context)



                context = {
                    "board": board,
                    "overlay": self.overlays,
                    "driver": self.driver,
                    "engine": self.engine
                }

                # print(context)

                # board update event
                self.plugins.trigger("on_board", self.engine, self.board_reader, self.overlays, self.plugins, self.driver, context)

                turn = self.board_reader.detect_turn()
                if turn is None:
                    continue
                board.turn = turn

                try:
                    move = self.engine.get_best_move(board)
                except:
                    print("Engine crashed in controller. Restarting...")
                    self.engine.restart()
                    
                    continue

                if move:
                    try:
                        info = self.engine.get_score(board)
                    except:
                        print("Engine crashed in controller. Restarting...")
                        self.engine.restart()
                        continue

                    context = {
                        "score" : info["score"],
                        "move" : move,
                        "overlay": self.overlays,
                        "driver": self.driver,
                        "engine": self.engine
                    }

                    # print("running on best move")
                    # engine result event
                    self.plugins.trigger("on_best_move", self.engine, self.board_reader, self.overlays, self.plugins, self.driver, context)

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