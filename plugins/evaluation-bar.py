from plugins.base import Plugin

class Plugin(Plugin):

    name = "Eval Bar"
    initialized = False

    def on_ui(self, context):

        if self.initialized:
            return

        driver = context["driver"]

        try:
            board = driver.find_element("css selector", "wc-chess-board")
        except:
            return

        print("[EvalBar] Board detected, injecting UI")

        self.inject_ui(driver)

        self.initialized = True

    def inject_ui(self, driver):
        driver.execute_script("""
        if (document.getElementById("chessium-eval-container")) return;

        let board = document.querySelector("wc-chess-board");

        if (!board) return;

        let container = document.createElement("div");
        container.id = "chessium-eval-container";

        container.style.position = "absolute";
        container.style.left = "-35px";
        container.style.top = "0px";
        container.style.width = "25px";
        container.style.height = "100%";
        container.style.background = "#111";
        container.style.borderRadius = "4px";
        container.style.overflow = "hidden";

        let bar = document.createElement("div");
        bar.id = "chessium-eval-bar";

        bar.style.position = "absolute";
        bar.style.bottom = "0";
        bar.style.width = "100%";
        bar.style.height = "50%";
        bar.style.background = "white";

        container.appendChild(bar);

        board.parentElement.style.position = "relative";
        board.parentElement.appendChild(container);
        """)

    def on_best_move(self, context):
        pov_score = context["score"]

        # numeric centipawns
        if pov_score.is_mate():
            mate = pov_score.relative.mate()
            percent = 100 if mate > 0 else 0
        else:
            score = pov_score.relative.score(mate_score=10000)
            if score is None:
                score = 0
            # map ±1000 centipawns to bar height
            percent = 50 + (score / 1000 * 50)
            percent = max(0, min(100, percent))

        self.update_eval(context["driver"], percent)


    def update_eval(self, driver, score):
        # map centipawn score to 0-100%
        percent = 50 + (score / 100.0 * 50)  # roughly ±5 pawns = full bar
        if percent > 100:
            percent = 100
        if percent < 0:
            percent = 0

        driver.execute_script("""
            let bar = document.getElementById("chessium-eval-bar");
            if (bar) {
                bar.style.height = arguments[0] + "%";
            }
        """, percent)
