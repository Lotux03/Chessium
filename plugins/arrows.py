from plugins.base import Plugin
from core.driver import get_driver


class Plugin(Plugin):

    name = "Best Move Arrows"

    def on_best_move(self, engine, board_reader, overlays, plugins, driver, context):
        move = context['move']
        start = move[:2]
        end = move[2:]

        draw_arrow(start, end, move)

def draw_arrow(start_sq, end_sq, move):

    driver = get_driver()

    try:

        js = f"""
        const board = document.querySelector('wc-chess-board');
        if (!board) return;

        let svg = document.querySelector('#chessium-arrows');

        if (!svg) {{
            svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.id = "chessium-arrows";
            svg.style.position = "absolute";
            svg.style.top = "0";
            svg.style.left = "0";
            svg.style.width = "100%";
            svg.style.height = "100%";
            svg.style.pointerEvents = "none";
            svg.setAttribute("viewBox", "0 0 100 100");

            board.appendChild(svg);
        }}

        // clear old arrows
        svg.innerHTML = "";

        const flipped = board.classList.contains("flipped");

        function sqToXY(square) {{

            const files = "abcdefgh";

            let file = files.indexOf(square[0]);
            let rank = parseInt(square[1]) - 1;

            if (flipped) {{
                file = 7 - file;
                rank = 7 - rank;
            }}

            const x = (file + 0.5) / 8 * 100;
            const y = (7 - rank + 0.5) / 8 * 100;

            return [x, y];
        }}

        const [sx, sy] = sqToXY("{start_sq}");
        const [ex, ey] = sqToXY("{end_sq}");

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');

        line.setAttribute("x1", sx);
        line.setAttribute("y1", sy);
        line.setAttribute("x2", ex);
        line.setAttribute("y2", ey);

        line.setAttribute("stroke", "orange");
        line.setAttribute("stroke-width", "2.5");
        line.setAttribute("stroke-linecap", "round");

        svg.appendChild(line);

        const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');

        const size = 2.5;

        const angle = Math.atan2(ey - sy, ex - sx);

        const ax = ex;
        const ay = ey;

        const p1x = ax - size * Math.cos(angle - Math.PI / 6);
        const p1y = ay - size * Math.sin(angle - Math.PI / 6);

        const p2x = ax - size * Math.cos(angle + Math.PI / 6);
        const p2y = ay - size * Math.sin(angle + Math.PI / 6);

        arrow.setAttribute(
            "points",
            `${{ax}},${{ay}} ${{p1x}},${{p1y}} ${{p2x}},${{p2y}}`
        );

        arrow.setAttribute("fill", "orange");

        svg.appendChild(arrow);
        """

        driver.execute_script(js)

    except Exception as e:

        print("Arrow draw error:", e)
