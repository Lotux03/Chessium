from plugins.base import Plugin
from core.driver import get_driver


class Plugin(Plugin):
    name = "Best Move Arrows"

    def on_new_game(self, context):
        """Clear arrows when a new game starts - the old SVG may be orphaned."""
        driver = context.get("driver") or get_driver()
        self._clear_arrows(driver)

    def on_best_move(self, context):
        move = context.get("move")
        if not move or len(move) < 4:
            return

        driver = context.get("driver") or get_driver()
        self._draw_arrow(driver, move[:2], move[2:4])

    def _clear_arrows(self, driver):
        try:
            driver.execute_script("""
            const svg = document.querySelector('#chessium-arrows');
            if (svg) { svg.innerHTML = ''; svg.remove(); }
            """)
        except Exception as e:
            print(f"[ARROWS] Clear error: {e}")

    def _draw_arrow(self, driver, start_sq, end_sq):
        try:
            driver.execute_script(f"""
            const board = document.querySelector('wc-chess-board');
            if (!board) return;

            // Recreate SVG if it got orphaned when chess.com rebuilt the board element
            let svg = document.querySelector('#chessium-arrows');
            if (svg && !board.contains(svg)) {{
                svg.remove();
                svg = null;
            }}
            if (!svg) {{
                svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                svg.id = 'chessium-arrows';
                svg.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10;';
                svg.setAttribute('viewBox', '0 0 800 800');
                board.appendChild(svg);
            }}

            svg.innerHTML = '';

            const flipped = board.classList.contains('flipped');
            const files = 'abcdefgh';
            const CELL = 100; // each square is 100 units in an 800x800 viewBox

            function sqToXY(sq) {{
                let file = files.indexOf(sq[0]);   // 0=a .. 7=h
                let rank = parseInt(sq[1]) - 1;    // 0=rank1 .. 7=rank8

                // When flipped (playing black), the board is rotated 180 degrees
                if (flipped) {{
                    file = 7 - file;
                    rank = 7 - rank;
                }}

                // X increases left→right with file
                // Y increases top→bottom, rank 8 is at top so invert rank
                const x = (file + 0.5) * CELL;
                const y = (7 - rank + 0.5) * CELL;
                return [x, y];
            }}

            const [sx, sy] = sqToXY('{start_sq}');
            const [ex, ey] = sqToXY('{end_sq}');

            const angle = Math.atan2(ey - sy, ex - sx);
            const headSize = 22;
            const stemShorten = headSize * 0.85;

            // Stem — shortened so it doesn't poke through the arrowhead
            const lx = ex - stemShorten * Math.cos(angle);
            const ly = ey - stemShorten * Math.sin(angle);

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', sx); line.setAttribute('y1', sy);
            line.setAttribute('x2', lx); line.setAttribute('y2', ly);
            line.setAttribute('stroke', 'rgba(255, 165, 0, 0.85)');
            line.setAttribute('stroke-width', '18');
            line.setAttribute('stroke-linecap', 'round');
            svg.appendChild(line);

            // Arrowhead
            const p1x = ex - headSize * Math.cos(angle - Math.PI / 6);
            const p1y = ey - headSize * Math.sin(angle - Math.PI / 6);
            const p2x = ex - headSize * Math.cos(angle + Math.PI / 6);
            const p2y = ey - headSize * Math.sin(angle + Math.PI / 6);

            const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            arrow.setAttribute('points', `${{ex}},${{ey}} ${{p1x}},${{p1y}} ${{p2x}},${{p2y}}`);
            arrow.setAttribute('fill', 'rgba(255, 165, 0, 0.85)');
            svg.appendChild(arrow);
            """)
        except Exception as e:
            print(f"[ARROWS] Draw error: {e}")