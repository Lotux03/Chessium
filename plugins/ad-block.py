from plugins.base import Plugin
from selenium.webdriver.common.by import By

class Plugin(Plugin):
    name = "Ad Block"

    def __init__(self):
        self.enabled = False
        self.ready = False

    def on_ui(self, context):
        if not self.enabled:
            return

        driver = context["driver"]

        if not self.ready:
            try:
                driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
                print("[AdBlock] Chess UI detected")
                self.ready = True
            except:
                return
            
        try:
            driver.execute_script("""
            if (!document.getElementById("chessium-adblock")) {
                let style = document.createElement("style");
                style.id = "chessium-adblock";
                style.innerHTML = "#board-layout-ad { display:none !important; }";
                document.head.appendChild(style);
            }

            let ad = document.getElementById("board-layout-ad");
            if (ad) ad.remove();
            """)
        except Exception as e:
            print("[AdBlock ERROR]", e)