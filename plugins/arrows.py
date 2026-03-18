from plugins.base import Plugin
from core.driver import get_driver


class Plugin(Plugin):
    name = "Best Move Arrows"

    def on_best_move(self, context):
        move = context.get("move")
        if not move or len(move) < 4:
            return

        start = move[:2]
        end = move[2:4]
        driver = context.get("driver") or get_driver()

        self._draw_arrow(driver, start, end)

    def _draw_arrow(self, driver, start_sq, end_sq):
        try:
            driver.execute_script(f"""
            const board = document.querySelector('wc-chess-board');
            if (!board) return;

            let svg = document.querySelector('#chessium-arrows');
            if (!svg) {{
                svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                svg.id = 'chessium-arrows';
                svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;';
                svg.setAttribute('viewBox', '0 0 100 100');
                board.appendChild(svg);
            }}

            svg.innerHTML = '';

            const flipped = board.classList.contains('flipped');
            const files = 'abcdefgh';

            function sqToXY(sq) {{
                let file = files.indexOf(sq[0]);
                let rank = parseInt(sq[1]) - 1;
                if (flipped) {{ file = 7 - file; rank = 7 - rank; }}
                return [(file + 0.5) / 8 * 100, (7 - rank + 0.5) / 8 * 100];
            }}

            const [sx, sy] = sqToXY('{start_sq}');
            const [ex, ey] = sqToXY('{end_sq}');

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', sx); line.setAttribute('y1', sy);
            line.setAttribute('x2', ex); line.setAttribute('y2', ey);
            line.setAttribute('stroke', 'orange');
            line.setAttribute('stroke-width', '2.5');
            line.setAttribute('stroke-linecap', 'round');
            svg.appendChild(line);

            const size = 2.5;
            const angle = Math.atan2(ey - sy, ex - sx);
            const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            const p1x = ex - size * Math.cos(angle - Math.PI / 6);
            const p1y = ey - size * Math.sin(angle - Math.PI / 6);
            const p2x = ex - size * Math.cos(angle + Math.PI / 6);
            const p2y = ey - size * Math.sin(angle + Math.PI / 6);
            arrow.setAttribute('points', `${{ex}},${{ey}} ${{p1x}},${{p1y}} ${{p2x}},${{p2y}}`);
            arrow.setAttribute('fill', 'orange');
            svg.appendChild(arrow);
            """)
        except Exception as e:
            print(f"[ARROWS] Draw error: {e}")
