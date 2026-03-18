from plugins.base import Plugin


class Plugin(Plugin):
    name = "Ad Block"

    def __init__(self):
        self.enabled = False
        self._injected = False

    def on_ui(self, context):
        driver = context["driver"]

        if not self._injected:
            try:
                driver.find_element("css selector", "wc-chess-board")
                self._injected = True
                print("[AdBlock] Chess UI detected")
            except Exception:
                return

        self._remove_ads(driver)

    def _remove_ads(self, driver):
        try:
            driver.execute_script("""
            // Inject persistent CSS to hide ad elements
            if (!document.getElementById('chessium-adblock')) {
                const style = document.createElement('style');
                style.id = 'chessium-adblock';
                style.innerHTML = `
                    #board-layout-ad,
                    #ad_unit,
                    .game-over-ad-container-component,
                    .game-over-ad-slot,
                    [id^="google_ads_iframe_"] {
                        display: none !important;
                        visibility: hidden !important;
                        pointer-events: none !important;
                    }
                `;
                document.head.appendChild(style);
            }

            // Hard-remove known ad elements from the DOM
            ['board-layout-ad', 'ad_unit'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.remove();
            });

            document.querySelectorAll(`
                .game-over-ad-container-component,
                .game-over-ad-slot,
                iframe[id^="google_ads_iframe_"]
            `).forEach(el => el.remove());
            """)
        except Exception as e:
            print(f"[AdBlock] Error: {e}")
