from plugins.base import Plugin


class Plugin(Plugin):
    name = "Eval Bar"

    def __init__(self):
        self.enabled = False
        self._injected = False

    def on_ui(self, context):
        if self._injected:
            return

        driver = context["driver"]

        try:
            driver.find_element("css selector", "wc-chess-board")
        except Exception:
            return

        self._inject_ui(driver)
        self._injected = True
        print("[EvalBar] Injected")

    def on_best_move(self, context):
        pov_score = context.get("score")
        if pov_score is None:
            return

        driver = context["driver"]
        percent = self._score_to_percent(pov_score)
        self._update_bar(driver, percent)

    def _score_to_percent(self, pov_score):
        if pov_score.is_mate():
            mate = pov_score.relative.mate()
            return 100 if mate > 0 else 0

        score = pov_score.relative.score(mate_score=10000) or 0
        # ±1000 centipawns maps to 0-100%
        percent = 50 + (score / 1000 * 50)
        return max(0, min(100, percent))

    def _inject_ui(self, driver):
        driver.execute_script("""
        if (document.getElementById('chessium-eval-container')) return;

        const board = document.querySelector('wc-chess-board');
        if (!board) return;

        const container = document.createElement('div');
        container.id = 'chessium-eval-container';
        container.style.cssText = `
            position: absolute; left: -35px; top: 0;
            width: 25px; height: 100%;
            background: #111; border-radius: 4px; overflow: hidden;
        `;

        const bar = document.createElement('div');
        bar.id = 'chessium-eval-bar';
        bar.style.cssText = 'position: absolute; bottom: 0; width: 100%; height: 50%; background: white;';

        container.appendChild(bar);
        board.parentElement.style.position = 'relative';
        board.parentElement.appendChild(container);
        """)

    def _update_bar(self, driver, percent):
        driver.execute_script("""
        const bar = document.getElementById('chessium-eval-bar');
        if (bar) bar.style.height = arguments[0] + '%';
        """, percent)
