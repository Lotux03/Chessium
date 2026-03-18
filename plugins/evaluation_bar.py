from plugins.base import Plugin


class Plugin(Plugin):
    name = "Eval Bar"

    def __init__(self):
        self.enabled = False

    def on_ui(self, context):
        driver = context["driver"]

        try:
            driver.find_element("css selector", "wc-chess-board")
        except Exception:
            return

        # Always check if the container is actually in the DOM.
        # Don't use a flag — chess.com can navigate and wipe the DOM at any
        # time, and a stale flag would prevent re-injection indefinitely.
        result = driver.execute_script("""
        const board = document.querySelector('wc-chess-board');
        if (!board || !board.parentElement) return 'no board';

        // Already injected and still attached — nothing to do
        if (document.getElementById('chessium-eval-container')) return 'exists';

        const container = document.createElement('div');
        container.id = 'chessium-eval-container';
        container.style.cssText = `
            position: absolute; left: -35px; top: 0;
            width: 25px; height: 100%;
            background: #333; border-radius: 4px; overflow: hidden;
            z-index: 999;
        `;

        const bar = document.createElement('div');
        bar.id = 'chessium-eval-bar';
        bar.style.cssText = `
            position: absolute; bottom: 0; width: 100%; height: 50%;
            background: white; transition: height 0.3s ease;
        `;

        container.appendChild(bar);
        board.parentElement.style.position = 'relative';
        board.parentElement.appendChild(container);
        return 'injected';
        """)

        if result == 'injected':
            print("[EvalBar] Injected")

    def on_best_move(self, context):
        pov_score = context.get("score")
        if pov_score is None:
            return

        percent = self._score_to_percent(pov_score)
        self._update_bar(context["driver"], percent)

    def _score_to_percent(self, pov_score):
        white_score = pov_score.white()

        if white_score.is_mate():
            mate = white_score.mate()
            return 100 if mate > 0 else 0

        cp = white_score.score(mate_score=10000) or 0
        percent = 50 + (cp / 600 * 50)
        return max(0, min(100, percent))

    def _update_bar(self, driver, percent):
        driver.execute_script("""
        const bar = document.getElementById('chessium-eval-bar');
        if (bar) bar.style.height = arguments[0] + '%';
        """, percent)