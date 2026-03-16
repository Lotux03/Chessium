# Chessium

### Visual Chess AI overlay – highlights, arrows, and engine moves in your browser.

Chessium transforms online chess boards into interactive tactical maps. See every move, track engine suggestions, and visualize your game like a pro. Built to run in Chromium-based browsers, Chessium works alongside Stockfish for real-time move analysis.

# Features
- [x] Autobot

- [x] Draw arrows from one square to another.

- [x] Ad Blocker

- [x] Evaluation Bar

- [x] Plugin integration for community

- [ ] Highlight specific squares dynamically.

+ [ ] Toggle between arrows and highlights.

- [x] Supports real-time Stockfish integration for move suggestions.

- [x] Fully browser-based overlay—works on chess.com.

- [x] Lightweight and easy to extend.

# Installation

Clone this repository:

`git clone https://github.com/Lotux03/Chessium.git`

`cd Chessium`

Install dependencies:

Open `Install Dependencies.bat`

Make sure you have Chromium/Chrome installed and a Stockfish engine executable (stockfish.exe) in your project folder.

# Usage

### Run the Batch script:

Open `Run.bat`

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

<img width="729" height="727" alt="Screenshot 2026-03-11 191322" src="https://github.com/user-attachments/assets/43dbda6f-4960-40c3-8afb-e5abd8dbfb83" />
<img width="1915" height="1027" alt="image" src="https://github.com/user-attachments/assets/38d6b487-676c-4c3c-94df-5c4ba813afd5" />
<img width="1917" height="1028" alt="image" src="https://github.com/user-attachments/assets/57cfb3fb-b99a-4c11-9268-5aecacc78639" />
<img width="1911" height="1026" alt="image" src="https://github.com/user-attachments/assets/213b074a-cc1b-4a0e-96c8-3beb9caa6036" />

# Contributing

- Currently experimental.

- Fork and submit pull requests for improvements.

- Suggestions welcome for:

  * Multi-move visualization

  * Smarter arrow/line drawing

  * Dynamic toggling UI

# License

MIT License © 2026

