# Chessium

### Visual Chess AI overlay – highlights, arrows, and engine moves in your browser.

Chessium transforms online chess boards into interactive tactical maps. See every move, track engine suggestions, and visualize your game like a pro. Built to run in Chromium-based browsers, Chessium works alongside Stockfish for real-time move analysis.

# Features
- [x] Autobot

- [x] Draw arrows from one square to another.

- [ ] Highlight specific squares dynamically.

+ [x] Toggle between arrows and highlights.

- [x] Supports real-time Stockfish integration for move suggestions.

- [x] Fully browser-based overlay—works on chess.com and other sites.

- [x] Lightweight and easy to extend.

# Installation

Clone this repository:

`git clone https://github.com/Lotux03/Chessium.git`

`cd Chessium`

Install dependencies (Python + Selenium + Stockfish):

`pip install selenium chess`

Make sure you have Chromium/Chrome installed and a Stockfish engine executable (stockfish.exe) in your project folder.

# Usage

### Run the Python script:

`python Chessium.py`

It should open then [Chess.com](https://www.chess.com/play/) for you.

Chessium will detect the board and draw arrows/highlights for the engine’s best moves automatically

### Toggle display mode (hardcoded for now):

toggle_display("arrows")       # Show arrows
toggle_display("highlights")   # Show square highlights
How it Works

Reads the board state via Selenium.

Converts board squares (a1-h8) into SVG coordinates.

Draws arrows or rectangles on a transparent SVG overlay.

Uses Stockfish engine to calculate the best move in real-time.

# Screenshots

(Optional: Add screenshots of arrows and highlights on the chess board here)

# Contributing

- Currently experimental.

- Fork and submit pull requests for improvements.

- Suggestions welcome for:

  * Multi-move visualization

  * Smarter arrow/line drawing

  * Dynamic toggling UI

# License

MIT License © 2026
