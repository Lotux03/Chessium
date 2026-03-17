import chess
import chess.engine
import os
import threading

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

        self.lock = threading.Lock()

    def get_best_move(self, context):
        if not self.lock.acquire(blocking=False):
            print("[ENGINE] Skipping best move (engine busy)")
            return None

        try:
            result = self.engine.play(
                context["board"],
                chess.engine.Limit(time=0.2)
            )

            return result.move.uci()

        finally:
            self.lock.release()
        
    def get_score(self, board):
        if not self.lock.acquire(blocking=False):
            print("[ENGINE] Skipping get score (engine busy)")
            return None
        
        info = self.engine.analyse(board, chess.engine.Limit(time=0.2))
        return info
    
    def analyse_position(self, board):
        if not self.lock.acquire(blocking=False):
            print("[ENGINE] Skipping analyse (engine busy)")
            return None, None

        try:
            info = self.engine.analyse(
                board,
                chess.engine.Limit(time=0.2)
            )

            score = info.get("score")
            move = None

            if "pv" in info and len(info["pv"]) > 0:
                move = info["pv"][0].uci()

            return score, move

        finally:
            self.lock.release()

    def restart(self):
        if not self.lock.acquire(blocking=False):
            print("[ENGINE] Skipping restart (engine busy)")
            return None
        
        self.engine.quit()
        self.__init__()
