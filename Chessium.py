from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import chess
import chess.engine
import time

ENGINE_PATH = "stockfish.exe"

driver = webdriver.Chrome()
driver.get("https://www.chess.com/play/online")

engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

piece_map = {
    "wp": "P", "wr": "R", "wn": "N", "wb": "B", "wq": "Q", "wk": "K",
    "bp": "p", "br": "r", "bn": "n", "bb": "b", "bq": "q", "bk": "k"
}

def read_board():
    board = chess.Board(None)
    pieces = driver.find_elements(By.CSS_SELECTOR, ".piece")
    
    print("\n--- BOARD DETECTED ---")
    
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

    print(board)
    print("FEN:", board.fen())
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
driver.execute_script(js_init_svg)

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


def draw_arrow_line(start_sq, end_sq):
    sx, sy = square_to_xy(start_sq)
    ex, ey = square_to_xy(end_sq)
    js = f"""
    const svg = document.querySelector('svg.arrows');
    if (!svg) return;

    // Create marker once
    if (!document.querySelector('#arrowhead')) {{
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', 3);
        marker.setAttribute('markerHeight', 3);
        marker.setAttribute('refX', 0);
        marker.setAttribute('refY', 1.5);
        marker.setAttribute('orient', 'auto');
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 3 1.5, 0 3');
        polygon.setAttribute('fill', 'orange');
        marker.appendChild(polygon);
        defs.appendChild(marker);
        svg.appendChild(defs);
    }}

    // Clear old arrows
    svg.querySelectorAll('line').forEach(l => l.remove());

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', {sx});
    line.setAttribute('y1', {sy});
    line.setAttribute('x2', {ex});
    line.setAttribute('y2', {ey});
    line.setAttribute('stroke', 'orange');
    line.setAttribute('stroke-width', 2);
    line.setAttribute('marker-end', 'url(#arrowhead)');
    svg.appendChild(line);
    """
    driver.execute_script(js)
    
def toggle_display(mode="arrows"):
    # mode: "arrows" or "highlights"
    js = f"""
    const arrows = document.querySelector('svg.arrows');
    const highlights = document.querySelector('svg.highlights');
    if (arrows) arrows.style.display = '{'block' if mode=='arrows' else 'none'}';
    if (highlights) highlights.style.display = '{'block' if mode=='highlights' else 'none'}';
    """
    driver.execute_script(js)

# Main loop
while True:
    try:
        board = read_board()
    except Exception as e:
        print("Error reading board:", e)
        continue

    try:
        result = engine.play(board, chess.engine.Limit(time=0.2))
        best_move = result.move.uci()
        start, end = best_move[:2], best_move[2:]

        # Toggle: show highlights or arrows
        # toggle_display("highlights")
        # draw_highlight(end)

        toggle_display("arrows")
        draw_arrow_line(start, end)
    except Exception as e:
        print("Engine error:", e)
        # engine.quit()
        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    time.sleep(3)