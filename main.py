
from puzzle_levels import LEVELS
from temple_trap_solver import GameState, a_star_search
from puzzle_levels import TILES,update_tiles_orientation
from pprint import pprint

def solve_puzzle(level_name, level_data):
    print(f"--- Solving Level: {level_name} ---")
    tiles=update_tiles_orientation(TILES,level_data)
    # pprint(tiles)
    initial_state = GameState(board=level_data['board'],pawn_pos= level_data['pawn_pos'],tiles_state=tiles)
    
    solution_path = a_star_search(initial_state)
    
    if solution_path[0]:
        print(f"Solution found with cost {solution_path[1]}!")
        for step in solution_path[0]:
            print(step)
    else:
        print("No solution found.")
    print("\n")

if __name__ == "__main__":
    for level_name, level_data in LEVELS.items():
        solve_puzzle(level_name, level_data)
