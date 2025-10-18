# Temple Trap: An AI-Powered Puzzle Solver

Welcome to the Temple Trap puzzle solver! This project features an intelligent solver that uses the A* search algorithm to find the optimal solution to the Temple Trap board game. It also includes an interactive Pygame visualization that allows you to play the game, test your own strategies, and watch the solver in action.

## 📜 Project Overview

The goal in Temple Trap is to guide a pawn to the exit of a shifting temple maze. This is achieved by sliding tiles to reconfigure the pathways. This project provides both a tool to find the most efficient solution and a platform to interact with the puzzle visually.

### Core Components

*   **`temple_trap_solver.py`**: The brain of the operation. This script contains the implementation of the A* search algorithm, which intelligently explores possible moves to find the shortest solution path.
*   **`temple_trap_game.py`**: A visual and interactive version of the game built with Pygame. You can manually slide tiles and move the pawn, or you can let the AI solver take the wheel.
*   **`puzzle_levels.py`**: This file acts as the blueprint for the puzzles, defining the layout of the tiles and the starting conditions for various levels.
*   **`main.py`**: A command-line tool that runs the solver for all defined levels and prints the step-by-step solution for each.

## 🚀 Getting Started

### Prerequisites

*   Python 3.x
*   Pygame

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Thotamsetty-Nikilesh/Temple-Trap
    cd temple-trap
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### How to Run

*   **To play the interactive game:**
    ```bash
    python temple_trap_game.py
    ```
*   **To run the solver in your terminal:**
    ```bash
    python main.py
    ```

## 🎮 Game Controls

The Pygame interface provides the following controls:

*   **Level Navigation:**
    *   **← / → Arrow Keys**: Switch between puzzle levels.
    *   **R**: Reset the current level.
*   **AI Solver:**
    *   **S**: Solve the current puzzle with the A* algorithm.
    *   **N**: View the next step in the solution path.
    *   **A**: Toggle autoplay to watch the solver complete the puzzle.
*   **Manual Play:**
    *   **Mouse Click**: Slide a tile into an adjacent empty space.
    *   **Shift + Arrow Keys**: Move the pawn directionally.
    *   **Numpad 1-9**: Move the pawn to a specific cell.

## 🧩 Adding New Puzzles

You can define your own levels in `puzzle_levels.py`. Use the following format:

```python
'new-level-name': {
    'board': [RECT, RHOM, '>', '=', '*', 'X', '.', '+', None], # Tile layout
    'pawn_pos': 5,                                           # Pawn's starting position
    'orientation': [1, 0, 2, 0, 0, 2, 0, 1, 0]               # Tile rotations
},
