import heapq
from puzzle_levels import TILES
DIRECTIONS={
     -1: "Left",
      1: "Right", 
     -3: "Up",
      3: "Down"
}
class GameState:
    # This is the state definition of the problem
    def __init__(self,board,pawn_pos,pawn_layer="GROUND",g_cost=0,path=None,tiles_state=None):
        self.board=tuple(board)  # Defining the board state
        # Defining the pawns position
        self.pawn_pos=pawn_pos
        self.pawn_layer=pawn_layer
        self.g_cost=g_cost# Defining the g cost i.e.. total cost till now
        self.path=path if path is not None else [] # Defining the path if one exist assign it else to empty list
        self.blank_pos=self.board.index(None)# Initialising the blank position according the board data
        self.TILES=tiles_state# This defines how the tiles are oriented

    # These are  needed for heapq if the costs of two states tally it is used for comparision
    def __lt__(self,other):
        return (self.g_cost+self.heuristic()) < (other.g_cost+other.heuristic())
    def __eq__(self, other):
        return self.board == other.board and self.pawn_pos == other.pawn_pos and self.pawn_layer == other.pawn_layer
    def __hash__(self):
        return hash((self.board, self.pawn_pos, self.pawn_layer))
    
    def heuristic(self):
        # Heuristic is a manhattan distance from current pawn position to the exit
        pawn_row, pawn_col = self.pawn_pos // 3, self.pawn_pos % 3
        exit_row, exit_col = 0, 0
        return abs(pawn_row - exit_row) + abs(pawn_col - exit_col)
    
def get_neighbors(cell):
    # This determines the plausible neighbors 
    # Returns: a dictionary with keys:0 indexed cell posn  and values:a tuple indicating the move(ex:if the cell%3>0 so it can move to left if pawn can move btw posn 4 and posn 2  )
    neighbors=dict()
    if cell % 3 > 0:  neighbors[cell - 1]  = (4, 2)
    if cell % 3 < 2:  neighbors[cell + 1]  = (2, 4)
    if cell // 3 > 0: neighbors[cell - 3] = (1, 3)
    if cell // 3 < 2: neighbors[cell + 3] = (3, 1)
    return neighbors

def can_move_between_cells(state,from_cell,to_cell,layer):
    # This is the helper function that decides whether the blocks are connected or not
    from_tile_name = state.board[from_cell]
    to_tile_name = state.board[to_cell]
    if from_tile_name is None or to_tile_name is None:return False
    from_tile,to_tile=state.TILES[from_tile_name],state.TILES[to_tile_name]
    neighbors=get_neighbors(from_cell)
    # Cell is not found so there is no way pawn can move .This also provides extra safety for the next line.
    if to_cell not in neighbors:return False
    from_side,to_side=neighbors[to_cell]
    openings='top_opens' if layer=='TOP' else 'ground_opens'
    return from_side in from_tile[openings] and to_side in to_tile[openings]

def get_reachable_cells(state):
    q=[(state.pawn_pos,state.pawn_layer,0)] # The last value of list indicates the cost for the pawn movement
    # This is the final return of this  returns the reachable cell and the pawn cost as a dict
    reachable_cells={}
    visited_for_search={
        
    }

    head=0
    while head<len(q):
        curr_pos,curr_layer,cost=q[head];head+=1
        if (curr_pos,curr_layer) in visited_for_search:
            continue
        visited_for_search[(curr_pos,curr_layer)]=cost
        reachable_cells[(curr_pos,curr_layer)]=cost
        for neighbor in get_neighbors(curr_pos):
            # If the pawn can move between the neighbor cell we have to append
            if can_move_between_cells(state,curr_pos,neighbor,curr_layer) and (neighbor,curr_layer) not in visited_for_search:
                q.append((neighbor,curr_layer,cost+1))

        # Adding the cells which are reachable by stairs
        curr_tile_name=state.board[curr_pos]
        if curr_tile_name and state.TILES[curr_tile_name]['has_stairs']:
            other_layer='GROUND' if curr_layer=="TOP" else "TOP"
            q.append((curr_pos,other_layer,cost))# Cost doesnt change for the climbing stairs in the same tile
    return reachable_cells

def is_goal_state(state):
    # The goal is reached if the pawn can WALK to cell 0 and exit.
    # It does not need to be already at cell 0.
    reachable_cells = get_reachable_cells(state)
    tile_at_exit_name = state.board[0]
    if tile_at_exit_name is None:
        return False,-1
    
    tile_at_exit = state.TILES[tile_at_exit_name]

    # Check if a walk to the exit is possible on the GROUND layer # Since the exit is at the top(on grass) it cannot be in ground
    # if (0, 'GROUND') in reachable_cells and 4 in tile_at_exit['ground_opens']:
    #     return True,reachable_cells[(0,'GROUND')]

    # # Check if a walk to the exit is possible on the TOP layer
    if (0, 'TOP') in reachable_cells and 4 in tile_at_exit['top_opens']:
        return True,reachable_cells[(0,'TOP')]
    
    return False,-1

def get_valid_actions(state):
    actions=[]

    # Adding the pawn moves
    reachable_cells=get_reachable_cells(state)
    for (pos,layer),cost in reachable_cells.items():
        # If the position is current position
        if (pos, layer) == (state.pawn_pos, state.pawn_layer):
            continue

        destination_tile_name=state.board[pos]
        if destination_tile_name and state.TILES[destination_tile_name]['has_hole']:
            new_path=state.path + [f'Move pawn to {pos} ({layer}) (COST:{state.g_cost + cost})']
            actions.append(GameState(list(state.board), pos, layer, state.g_cost + cost, new_path,state.TILES))
    # Adding the possible slide moves
    blank_pos=state.blank_pos
    for neighbor_pos,_ in get_neighbors(blank_pos).items():
        tile_to_slide_pos=neighbor_pos
        tile_to_slide_name=state.board[tile_to_slide_pos]

        # Pawn cannot be on the tile that is about to slide.
        if state.TILES[tile_to_slide_name]['has_hole'] and tile_to_slide_pos == state.pawn_pos:
            continue
        # Slide the tile to the blank position
        new_board=list(state.board)
        new_board[blank_pos], new_board[tile_to_slide_pos] = new_board[tile_to_slide_pos], new_board[blank_pos]
        direction=DIRECTIONS[blank_pos-tile_to_slide_pos]
        new_path = state.path + [f"Slide {tile_to_slide_name} {direction} (from {tile_to_slide_pos} to {blank_pos}) (COST:{state.g_cost + 1})"]
        actions.append(GameState(new_board, state.pawn_pos, state.pawn_layer, state.g_cost + 1, new_path,state.TILES))

    return actions
# DONE! defining of states is over lets implement the A* search algorithm now
def a_star_search(initial_state):
    f_cost=initial_state.g_cost+initial_state.heuristic()
    frontier=[(f_cost,initial_state)]
    explored=set()

    while frontier:
        _,current_state=heapq.heappop(frontier)

        if current_state in explored:
            continue
        is_goal,cost=is_goal_state(current_state)
        if is_goal:
            final_path=current_state.path+['Walk to Exit!']
            return final_path,current_state.g_cost+cost+1 # +1 is for walking to exit
        
        explored.add(current_state)
        for next_state in get_valid_actions(current_state):
            if next_state not in explored:
                f_cost = next_state.g_cost + next_state.heuristic()
                heapq.heappush(frontier, (f_cost, next_state))

    return None,0

