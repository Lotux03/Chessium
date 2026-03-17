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
                style.innerHTML = `
                    #board-layout-ad,
                    #ad_unit,
                    .game-over-ad-container-component,
                    .game-over-ad-slot,
                    [id^="google_ads_iframe_"] {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                        pointer-events: none !important;
                    }
                `;
                document.head.appendChild(style);
            }

            // Hard remove known ads
            let ids = [
                "board-layout-ad",
                "ad_unit"
            ];

            ids.forEach(id => {
                let el = document.getElementById(id);
                if (el) {
                    el.remove();
                    console.log("[AdBlock] Removed:", id);
                }
            });

            // Remove dynamic ad containers
            document.querySelectorAll(`
                .game-over-ad-container-component,
                .game-over-ad-slot,
                iframe[id^="google_ads_iframe_"]
            `).forEach(el => {
                el.remove();
            });
            """)
        except Exception as e:
            print("[AdBlock ERROR]", e)





