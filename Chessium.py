from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random
import chess
import chess.engine
import time
import os


ENGINE_PATH = "stockfish.exe"

# driver = webdriver.Chrome()
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("https://www.chess.com/play/online")

engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
engine.configure({"Threads": 2, "Hash": 128})

last_board_fen = None
loop = 0
oldboard = chess.Board(None)
oldbestmove = ""
oldstart = ""
oldend = ""
boardstatus = "..."
bestmovestatus = "..."
colortomove = "..."
count = 0

piece_map = {
    "wp": "P", "wr": "R", "wn": "N", "wb": "B", "wq": "Q", "wk": "K",
    "bp": "p", "br": "r", "bn": "n", "bb": "b", "bq": "q", "bk": "k"
}

def get_board():
    try:
        board = driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
        return board

    except:
        return None

def read_board():
    board_el = get_board()
    if board_el is None:
        return chess.Board(None)

    board = chess.Board(None)
    pieces = board_el.find_elements(By.CSS_SELECTOR, ".piece")  
    
    for p in pieces:
        try:
            classes = p.get_attribute("class").split()
        except StaleElementReferenceException:
            continue

        if len(classes) < 3:
            continue

        piece_code = classes[1]  # e.g., 'wp'
        square_code = classes[2] # e.g., 'square-82'

        piece_symbol = piece_map.get(piece_code)
        if not piece_symbol:
            continue

        # Convert 'square-XY' -> chess.square
        file_index = int(square_code[7]) - 1  # 1-8 -> 0-7
        rank_index = int(square_code[8]) - 1
        chess_sq = chess.square(file_index, rank_index)
        board.set_piece_at(chess_sq, chess.Piece.from_symbol(piece_symbol))

    # print(board)
    # print("FEN:", board.fen())
    return board

def square_to_xy(sq):
    """Convert chess square (e.g., 'e2') to board SVG coordinates (center)."""
    file_to_x = {'a': 6.25, 'b': 18.75, 'c': 31.25, 'd': 43.75,
                 'e': 56.25, 'f': 68.75, 'g': 81.25, 'h': 93.75}
    rank_to_y = {'1': 93.75, '2': 81.25, '3': 68.75, '4': 56.25,
                 '5': 43.75, '6': 31.25, '7': 18.75, '8': 6.25}
    return file_to_x[sq[0]], rank_to_y[sq[1]]

js_init_svg = """
if (!document.querySelector('svg.arrows')) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'arrows');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('style', 'position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;');
    document.body.appendChild(svg);
}

if (!document.querySelector('svg.highlights')) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'highlights');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('style', 'position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;');
    document.body.appendChild(svg);
}
"""
js_add_toggle = """
if (!document.querySelector('#bot-toggle')) {

    const username = document.querySelector('[data-test-element="user-tagline-username"]');
    if (!username) return;

    const container = document.createElement('div');
    container.style.display = "inline-flex";
    container.style.gap = "5px";
    container.style.marginLeft = "10px";

    const toggle = document.createElement('button');
    toggle.id = "bot-toggle";
    toggle.innerText = "BOT OFF";
    toggle.dataset.enabled = "false";

    toggle.style.padding = "2px 8px";
    toggle.style.fontSize = "12px";
    toggle.style.borderRadius = "6px";
    toggle.style.border = "1px solid #555";
    toggle.style.cursor = "pointer";
    toggle.style.background = "#aa3333";
    toggle.style.color = "white";

    toggle.onclick = function() {
        if (toggle.dataset.enabled === "true") {
            toggle.dataset.enabled = "false";
            toggle.innerText = "BOT OFF";
            toggle.style.background = "#aa3333";
        } else {
            toggle.dataset.enabled = "true";
            toggle.innerText = "BOT ON";
            toggle.style.background = "#33aa33";
        }
    };

    const side = document.createElement('button');
    side.id = "side-toggle";
    side.innerText = "WHITE";
    side.dataset.side = "white";

    side.style.padding = "2px 8px";
    side.style.fontSize = "12px";
    side.style.borderRadius = "6px";
    side.style.border = "1px solid #555";
    side.style.cursor = "pointer";
    side.style.background = "#444";
    side.style.color = "white";

    side.onclick = function() {
        if (side.dataset.side === "white") {
            side.dataset.side = "black";
            side.innerText = "BLACK";
        } else {
            side.dataset.side = "white";
            side.innerText = "WHITE";
        }
    };

    container.appendChild(toggle);
    container.appendChild(side);

    username.parentElement.appendChild(container);
}
"""

def draw_highlight(square):
    x, y = square_to_xy(square)
    js = f"""
    const svg = document.querySelector('svg.highlights');
    if (!svg) return;
    svg.innerHTML = '';

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', {x-5});
    rect.setAttribute('y', {y-5});
    rect.setAttribute('width', 10);
    rect.setAttribute('height', 10);
    rect.setAttribute('fill', 'rgba(255, 255, 0, 0.5)');
    svg.appendChild(rect);
    """
    driver.execute_script(js)

def generate_arrow_points(start_sq, end_sq):
    """Generate polygon points and rotation for an arrow from start to end."""
    sx, sy = square_to_xy(start_sq)
    ex, ey = square_to_xy(end_sq)

    dx = ex - sx
    dy = ey - sy

    # Determine if vertical, horizontal, or diagonal
    if dx == 0:  # vertical move (pawn/rook)
        length = abs(dy)
        points = f"{sx-1.25} {sy}, {sx-1.25} {sy+length}, {sx+1.25} {sy+length}, {sx+1.25} {sy}, {sx} {sy+length+4}"
        rotation = 0
    elif dy == 0:  # horizontal move
        length = abs(dx)
        points = f"{sx} {sy-1.25}, {sx+length} {sy-1.25}, {sx+length} {sy+1.25}, {sx} {sy+1.25}, {sx+length+4} {sy}"
        rotation = 90
    else:  # diagonal/knight move
        # Rotation based on slope
        import math
        angle = math.degrees(math.atan2(dy, dx))
        # rectangle for arrow (simplified)
        points = f"{sx-1.25} {sy}, {sx-1.25} {sy+abs(dy)}, {sx+1.25} {sy+abs(dy)}, {sx+1.25} {sy}, {sx} {sy+abs(dy)+4}"
        rotation = angle

    return points, rotation, sx, sy  # include center for transform

def draw_arrow_line(start_sq, end_sq, bestmove, flasher):
    sx, sy = square_to_xy(start_sq)
    ex, ey = square_to_xy(end_sq)
    js = f"""
    const svg = document.querySelector('svg.arrows');
    if (!svg) return;

    svg.querySelectorAll('polygon').forEach(l => l.remove());

    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('id', 'arrow-{bestmove}');
    polygon.setAttribute('class', 'arrow');
    polygon.setAttribute(
        'points',
        '{sx} {sy}, {ex} {ey}, {ex+1} {ey+1}, {sx+1} {sy+1}'
    );
    polygon.setAttribute('stroke', 'black');
    polygon.setAttribute('style', 'fill: rgba(255,170,0,0.8); opacity:0.5;');
    polygon.setAttribute('stroke-width', 2);
    polygon.setAttribute('marker-end', 'url(#arrowhead)');
    svg.appendChild(polygon);
    """

    if flasher == 1:
        js += """
        let flashes = 0;

        function doFlash(){
            if (flashes >= 10) return;

            const flash = document.createElement('div');
            flash.style.position = 'fixed';
            flash.style.top = '0';
            flash.style.left = '0';
            flash.style.width = '100vw';
            flash.style.height = '100vh';
            flash.style.background = 'rgba(255,0,0,1)';
            flash.style.zIndex = '999999';
            flash.style.pointerEvents = 'none';

            document.body.appendChild(flash);

            setTimeout(() => {
                flash.remove();
            }, 20);

            flashes++;
            setTimeout(doFlash, 80);
        }

        doFlash();
        """
            

    driver.execute_script(js)

def detect_turn():
    try:
        clocks = driver.find_elements(By.CSS_SELECTOR, ".clock-component")
        if len(clocks) < 2:
            return None

        board = get_board()
        if board is None:
            return None

        flipped = "flipped" in board.get_attribute("class")

        # Clock order: [top, bottom]
        top_clock, bottom_clock = clocks[0], clocks[1]

        # Determine bottom clock (your clock)
        bottom_is_white = "clock-white" in bottom_clock.get_attribute("class")
        top_is_white = "clock-white" in top_clock.get_attribute("class")

        # Map clocks to color regardless of flip
        if flipped:
            white_clock = top_clock
            black_clock = bottom_clock
        else:
            white_clock = bottom_clock if bottom_is_white else top_clock
            black_clock = bottom_clock if bottom_clock != white_clock else top_clock

        # Check which clock has the turn
        if "clock-player-turn" in white_clock.get_attribute("class"):
            return chess.WHITE
        if "clock-player-turn" in black_clock.get_attribute("class"):
            return chess.BLACK

        return None
    except Exception as e:
        print("detect_turn error:", e)
        return None

def get_play_side():
    try:
        side = driver.execute_script("""
        const btn = document.querySelector('#side-toggle');
        if (!btn) return "white";
        return btn.dataset.side;
        """)

        if side == "black":
            return chess.BLACK
        return chess.WHITE

    except:
        return chess.WHITE
    
def toggle_display(mode="arrows"):
    # mode: "arrows" or "highlights"
    js = f"""
    const arrows = document.querySelector('svg.arrows');
    const highlights = document.querySelector('svg.highlights');
    if (arrows) arrows.style.display = '{'block' if mode=='arrows' else 'none'}';
    if (highlights) highlights.style.display = '{'block' if mode=='highlights' else 'none'}';
    """
    driver.execute_script(js)

def offer_draw():
    try:
        wait = WebDriverWait(driver, 5)

        # Click Draw button
        draw_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="draw-offer-button"]'))
        )
        draw_button.click()

        # Click confirmation Yes
        yes_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="confirm-yes"]'))
        )
        yes_button.click()

        print("Draw offer sent.")

    except Exception as e:
        print("Failed to offer draw:", e)

def is_board_flipped():
    board = driver.find_element(By.CSS_SELECTOR, "wc-chess-board")
    classes = board.get_attribute("class") or ""
    return "flipped" in classes

def printstatus(board, bestmove, colormove):
    global oldboard, oldbestmove, colortomove

    if (board != oldboard or bestmove != oldbestmove or colormove != colortomove):
        os.system("cls")
        print(f"Board: ", board)
        print(f"Best Move:", bestmove)
        print(f"Turn:", colormove)
        oldboard = board
        oldbestmove = bestmove

def bot_enabled():
    try:
        state = driver.execute_script("""
        const btn = document.querySelector('#bot-toggle');
        if (!btn) return false;
        return btn.dataset.enabled === "true";
        """)
        return state
    except:
        return False
# Run this after the page loads

def ensure_toggle(): driver.execute_script(js_add_toggle)

js_click_logger = """
if (!window._clickLoggerAdded) {
    window._clickLoggerAdded = true;

    const board = document.querySelector('wc-chess-board') || document.querySelector('chess-board');
    if (!board) {
        console.log("Board not found.");
        return;
    }

    function coordsToSquare(pctX, pctY){
        const file = Math.floor(pctX / 12.5);
        const rank = 7 - Math.floor(pctY / 12.5);

        const files = "abcdefgh";

        return files[file] + (rank + 1);
    }

    function logEvent(e){
        const rect = board.getBoundingClientRect();

        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const pctX = (x / rect.width) * 100;
        const pctY = (y / rect.height) * 100;

        const square = coordsToSquare(pctX, pctY);

        console.log(
            "[Chess Click]",
            "type:", e.type,
            "| px:", x.toFixed(1), y.toFixed(1),
            "| pct:", pctX.toFixed(2)+"%", pctY.toFixed(2)+"%",
            "| square:", square,
            "| client:", e.clientX, e.clientY
        );
    }

    board.addEventListener("mousedown", logEvent);
    board.addEventListener("mouseup", logEvent);
    board.addEventListener("click", logEvent);

    console.log("Chess click logger attached.");
}
"""

def square_to_xy_move(square, flipped=False):
    files = "abcdefgh"

    file = files.index(square[0])
    rank = int(square[1]) - 1

    if flipped:
        file = 7 - file
        rank = 7 - rank

    x = (file + 0.5) / 8
    y = (7 - rank + 0.5) / 8

    return x, y

    """
    Converts algebraic square (e.g., 'e2') into percentage coordinates
    relative to chess.com board container. Returns pctX, pctY.
    """
    files = "abcdefgh"
    file_idx = files.index(square[0])
    rank_idx = int(square[1]) - 1  # 0-based

    if flipped:
        file_idx = 7 - file_idx
        rank_idx = 7 - rank_idx

    # Center of the square
    pctX = (file_idx + 0.5) / 8 * 100
    pctY = (7 - rank_idx + 0.5) / 8 * 100  # Invert Y for top-left = a8

    return pctX, pctY
    files = 'abcdefgh'
    file_idx = files.index(square[0])
    rank_idx = int(square[1]) - 1

    if flipped:
        file_idx = 7 - file_idx
        rank_idx = 7 - rank_idx

    pctX = (file_idx + 0.5) / 8 * 100
    pctY = (7 - rank_idx + 0.5) / 8 * 100  # Chess.com top-left is a8

    return pctX, pctY

def click_square(square):

    board = driver.find_element(By.CSS_SELECTOR, "wc-chess-board")

    flipped = is_board_flipped()
    x, y = square_to_xy_move(square, flipped)

    rect = board.rect

    # convert % -> pixels
    px = rect["width"] * x
    py = rect["height"] * y

    # convert to center-relative offsets (important)
    offset_x = px - rect["width"] / 2
    offset_y = py - rect["height"] / 2

    ActionChains(driver)\
        .move_to_element_with_offset(board, offset_x, offset_y)\
        .click()\
        .perform()
    
def move_piece(start, end):
    click_square(start)
    time.sleep(0.05)   # tiny delay helps chess.com register move
    click_square(end)

blarg = 0 # change this to 1 for debug clicks

while True:
    

    #print("Click on any square on the board — coordinates will appear in the browser console.")

    while (loop != 1):
        count = 0
        printstatus(boardstatus, bestmovestatus, colortomove) # print best move out to user


        ensure_toggle()


        board = read_board()

        turn = detect_turn()
        if turn is None:
            time.sleep(0.2)
            continue

        board.turn = turn

        if turn == chess.WHITE:
            colortomove = "White"
        else:
            colortomove = "Black"

        if board.piece_map(): # if board
            boardstatus = "Good"
            if blarg == 1:
                driver.execute_script(js_click_logger)
                blarg = 0
        else: # else 
            boardstatus = "Missing..." # tell the user no board found and wait for a board
            continue

        PLAY_AS = get_play_side()

        if turn != PLAY_AS:
            time.sleep(0.5)
            continue

        try:
            result = engine.play(board, chess.engine.Limit(time=0.2))
        except chess.engine.EngineTerminatedError:
            engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
            engine.configure({"Threads": 2, "Hash": 128})
            continue

        best_move = result.move.uci()
        bestmovestatus = best_move
        start, end = best_move[:2], best_move[2:]
            
        if (oldstart != start or oldend != end): # if not best move arrow drawn
            toggle_display("arrows")
            if (random.randint(0, 100) == 0): # i think its funny
                flash = 1
            else:
                flash = 0

            if (random.randint(0, 1000) == 0): # i think its funny
                offer_draw()

            draw_arrow_line(start, end, best_move, flash) # draw best move 
            oldstart = start
            oldend = end
            
        
        if bot_enabled():
            delay = random.randint(1, 15)
            print(f"Waiting {delay} seconds before move...")
            time.sleep(delay)
            time.sleep(0.1)
            if not driver.find_elements(By.CSS_SELECTOR, "wc-chess-board"):
                continue
            #bum_move(start, end, get_play_side())
            move_piece(start, end)
        