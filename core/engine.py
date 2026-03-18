import os
import threading
import chess
import chess.engine


class ChessEngine:

    def __init__(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../stockfish.exe"))
        assert os.path.exists(path), f"Stockfish not found at {path}"

        print(f"[ENGINE] Loading: {path}")

        self._path = path
        self._lock = threading.Lock()
        self._start()

    def _start(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self._path)
        self.engine.configure({"Threads": 2, "Hash": 128})

    def analyse_position(self, board):
        if not self._lock.acquire(blocking=False):
            print("[ENGINE] Busy, skipping analysis")
            return None, None

        try:
            info = self.engine.analyse(board, chess.engine.Limit(time=0.2))
            score = info.get("score")
            move = info["pv"][0].uci() if info.get("pv") else None
            return score, move
        finally:
            self._lock.release()

    def get_best_move(self, board):
        """Play a move directly via engine (used by auto-move plugin)."""
        if not self._lock.acquire(blocking=False):
            print("[ENGINE] Busy, skipping best move")
            return None

        try:
            result = self.engine.play(board, chess.engine.Limit(time=0.2))
            return result.move.uci()
        finally:
            self._lock.release()

    def restart(self):
        """Quit and restart the engine process cleanly."""
        if not self._lock.acquire(blocking=False):
            print("[ENGINE] Busy, skipping restart")
            return

        try:
            self.engine.quit()
        except Exception:
            pass
        finally:
            self._lock.release()

        self._start()
        print("[ENGINE] Restarted")

    def kill(self):
        """Terminate the engine process."""
        if not self._lock.acquire(blocking=False):
            print("[ENGINE] Busy, skipping kill")
            return

        try:
            self.engine.quit()
        except Exception:
            pass
        finally:
            self._lock.release()

        print("[ENGINE] Killed")
