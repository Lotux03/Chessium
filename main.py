import logging
from core.driver import start_driver
from core.engine import ChessEngine
from core.board_reader import BoardReader
from core.plugin_manager import PluginManager
from core.controller import Controller
from gui.tkinter_gui import GUI

logging.basicConfig(format="[%(levelname)s] %(message)s")


def main():
    driver = start_driver()

    engine = ChessEngine()
    board_reader = BoardReader(driver)

    plugins = PluginManager()
    plugins.load_plugins()

    controller = Controller(engine, board_reader, plugins, driver)

    gui = GUI(plugins)

    print("[MAIN] Starting controller...")
    controller.start_loop()

    gui.run()


if __name__ == "__main__":
    main()
