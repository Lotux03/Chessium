import chess
import chess.engine
import logging
import os


class ChessEngine:

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "../", "stockfish.exe")
        path = os.path.abspath(path)
        assert os.path.exists(path), f"Engine not found at {path}"

        print(f"Loading engine: {path}")

        if not os.path.exists(path):
            print("Stockfish not found")

        self.engine = chess.engine.SimpleEngine.popen_uci(path)

        self.engine.configure({
            "Threads": 2,
            "Hash": 128
        })

    def get_best_move(self, board):

        try:
            result = self.engine.play(
                board,
                chess.engine.Limit(time=0.2)
            )

            move = result.move.uci()

            # print(f"Engine move: {move}")

            return move

        except chess.engine.EngineTerminatedError:

            print("Engine crashed. Restarting...")

            self.restart()

            return None
        
    def get_score(self, board):
        info = self.engine.analyse(board, chess.engine.Limit(time=0.2))
        return info

    def restart(self):
        self.engine.quit()
        self.__init__()
