# 🏯 Temple Trap Puzzle Solver & Game 🎮🐍  

Welcome to **Temple Trap** – an AI-powered puzzle solver with a slick Pygame visualization!  
Can you escape the temple… or will you get trapped forever? 👀🔥  

---

## 📂 Project Files Breakdown  

- **`temple_trap_solver.py`** 🧠  
  The brain of the project – implements **A\*** search to solve puzzle levels and guide the pawn safely to the exit.  

- **`puzzle_levels.py`** 🧩  
  Defines the **tiles** and **level layouts** for the game. Think of it as the puzzle blueprint 🏗️. (Use this if you want to add the new puzzle)

- **`temple_trap_game.py`** 🎮  
  Pygame visualization where you can **play** the puzzle yourself or watch the solver in action with smooth autoplay!  

- **`main.py`** 🚀  
  CLI tool that runs the solver across all levels and prints out the solution path step-by-step in the terminal.Use this if you want to solve the temple trap on own by taking hints at some steps.  

- **`details of temple trap.pdf`**:
  This pdf explains in more detail of what this project is.

---

## Adding the New puzzle 🧩 

For adding new puzzle the format looks like this

```python 
'Name of the level you want to give': {
        'board': [RECT,RHOM , '>', '=', '*', 'X', '.', '+',None], # Positions of tiles (See the board and find the signs)
        'pawn_pos': 5, # Intial position of the pawn 
        'orientation':[1,0,2,0,0,2,0,1,0] # This is important! It defines the tile orientation that is the no of turns need to be turned to get that orientation.(You can simply see how far the sign of the tile from bottom left in the clockwise direction)
    },
```

## ⚡ How to Run  

### 🔑 Install dependencies  
```bash
pip install -r requirements.txt
```

### 🤖 Run solver in the terminal  
```bash
python main.py
```

### 🎮 Play the game   
```bash
python temple_trap_game.py
```

---

## 🕹️ Pygame Controls  

- **Level Controls:**  
  ⬅️ / ➡️ → Switch levels  
  🔄 `R` → Reset level  

- **Solver Controls:**  
  `S` → Solve with A*  
  `N` → Next step  
  `A` → Toggle autoplay  

- **Pawn Movement:**  
  ⇧ + Arrow Keys → Move pawn directionally  
  Numpad `1-9` → Move pawn to cell  

- **Mouse:**  
  Click → Slide adjacent tile  
  ⇧ + Click → Move pawn to that cell (If the pawn is movable to the tile) 

---

## ✨ Final Words  

AI + Puzzle + Visualization = Pure Temple Mayhem!  
Escape the temple, one tile at a time... 🏃‍♂️💨💎  

---
