import logging
from core.driver import get_driver

class OverlayManager: 

    def __init__(self):
        self.driver = get_driver

    def draw_arrow(self, start, end, move):

        logging.debug(f"Drawing arrow {move}")

        js = f"""
        console.log("Arrow {move}");
        """

        try:
            self.driver.execute_script(js)

        except:
            logging.warning("Arrow failed")
