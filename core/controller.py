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
                self.trigger_on_ui()

                game_over = None
                if (self.board_reader.get_game_over_state() != None):
                    game_over = self.board_reader.get_game_over_state()

                if game_over:
                    print("[CONTROLLER] Game Over detected")

                    # stop engine cleanly
                    self.engine.kill()

                    # reset internal state
                    self.reset_game_state()


                    # wait for new board to load
                    new_board = self.wait_for_new_board()

                    if new_board:
                        self.board = new_board
                        self.last_fen = new_board.board_fen()
                        print("[CONTROLLER] Ready for new game")
                        self.engine.__init__()

                    continue
                
                self.board = self.board_reader.read()

                if not self.board.piece_map():
                    time.sleep(0.2)
                    continue

                fen = self.board.board_fen()

                if self.last_fen:
                    if self.board_reader.is_new_game(self.last_fen, fen):
                        print("[CONTROLLER] New game detected")
                        self.info = None
                        self.move = None
                        # OPTIONAL:
                        self.engine.restart()

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
            if (self.board_reader.detect_player_color() == chess.WHITE):
                turn = chess.WHITE
            elif (self.board_reader.detect_player_color() == chess.BLACK):
                turn = chess.BLACK
            else:
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
    
    def reset_game_state(self):
        print("[CONTROLLER] Resetting game state")

        self.last_fen = None
        self.board = None
        self.info = None
        self.move = None

    def wait_for_new_board(self, timeout=10):
        print("[CONTROLLER] Waiting for new board...")

        start = time.time()

        while time.time() - start < timeout:
            board = self.board_reader.read()

            if board and board.piece_map():
                fen = board.board_fen()

                # detect starting position or any valid fresh board
                if len(fen) > 10:
                    print("[CONTROLLER] New board detected")
                    return board

            time.sleep(0.3)

        print("[CONTROLLER] Timeout waiting for new board")
        return None