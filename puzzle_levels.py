import copy
from pprint import pprint

"""
Temple Trap Puzzle Levels
This file contains the definitions of the tiles and puzzle levels
for the Temple Trap game.
"""

# Sides of a tile are labeled I, II, III, IV in clockwise order from the top.
# I: Top, II: Right, III: Bottom, IV: Left

# Sides of a tile are labeled I, II, III, IV in clockwise order from the top.
# I: Top, II: Right, III: Bottom, IV: Left



RHOM='RHOMBUS'
RECT='RECTANGLE'
TILES = {
    '=': {'top_opens': {1, 2}, 'ground_opens': set(), 'has_hole': False, 'has_stairs': False},
    
    'RECTANGLE': {'top_opens': {1, 2}, 'ground_opens': set(), 'has_hole': False, 'has_stairs': False},
    
    '+': {'top_opens': {2, 4}, 'ground_opens': set(), 'has_hole': False, 'has_stairs': False},
    
    'RHOMBUS': {'top_opens': {4}, 'ground_opens': {2}, 'has_hole': True, 'has_stairs': True, 'stairs_side': 4},
    
    '*': {'top_opens': {4}, 'ground_opens': {2}, 'has_hole': True, 'has_stairs': True, 'stairs_side': 4},
    
    '>': {'top_opens': set(), 'ground_opens': {1, 2}, 'has_hole': True, 'has_stairs': False},
    
    'X': {'top_opens': set(), 'ground_opens': {1, 2}, 'has_hole': True, 'has_stairs': False},
    
    '.': {'top_opens': set(), 'ground_opens': {1, 2}, 'has_hole': True, 'has_stairs': False},
}

LEVELS = {

    # From the PDF figures
    'starter-1': {
        'board': ['+', RHOM, 'X', RECT, None, '.', '=', '*', '>'],
        'pawn_pos': 8,
        'orientation':[0,0,2,1,0,3,0,0,2]
    },
    'starter-2': {
        'board': ['=', '*', 'X', RECT, None, RHOM, '.', '+', '>'],
        'pawn_pos': 1,
        'orientation':[2,3,0,0,0,0,0,2,2]
    },
    'starter-3': {
        'board': ['X', '*', RECT, RHOM, '.','>', '=', None, '+'],
        'pawn_pos': 1,
        'orientation':[2,1,3,0,3,0,0,0,1]
    },
    'starter-4': {
        'board': [RECT, RHOM, '.','*', 'X','>', None,'=', '+'],
        'pawn_pos': 3,
        'orientation':[1,0,2,1,0,3,0,0,0]
    },

    'junior-1': {
        'board': ['X','>','*','=',RECT,'+','.',None,RHOM],
        'pawn_pos': 6,
        'orientation':[2,1,3,2,1,1,0,0,1]
    },
    'junior-2': {
        'board': ['+','*','X','>',None,RHOM,'.',RECT,'='],
        'pawn_pos': 5,
        'orientation':[0,0,1,0,None,2,0,3,1]
    },
    'junior-3': {
        'board': ['+',"=",RECT,RHOM,'*','X',None,'>','.'],
        'pawn_pos': 5,
        'orientation':[1,0,2,2,0,2,0,2,1]
    },
    'junior-4': {
        'board': ['X',".",'+',RECT,None,RHOM,'=','*','>'],
        'pawn_pos': 7,
        'orientation':[2,0,1,1,0,0,0,0,2]
    },

    'expert-1': {
        'board': [RHOM, RECT, '+', 'X', '>', '=', '.', '*',None],
        'pawn_pos': 0,
        'orientation':[1,2,3,0,2,3,3,1,0]
    },
    'expert-2': {
        'board': [RECT, "=", RHOM, '+', '>', 'X', None, '.','*'],
        'pawn_pos': 4,
        'orientation':[2,0,1,0,2,1,0,3,3]
    },
    'expert-3': {
        'board': ['+', "=", None, RECT, '.', RHOM, '*', 'X','>'],
        'pawn_pos': 5,
        'orientation':[1,2,0,0,1,2,0,0,2]
    },
    'expert-4': {
        'board': [RECT,RHOM , '>', '=', '*', 'X', '.', '+',None],
        'pawn_pos': 5,
        'orientation':[1,0,2,0,0,2,0,1,0]
    },
    # 'expert-42': {
    #     'board': ['>',"X" , RECT, None, '.', '*', RHOM, '+','='],
    #     'pawn_pos': 0,
    #     'orientation':[1,2,2,0,0,2,2,0,3]
    # },
    'expert-11': {
        'board': [RHOM,">" , '+', '*', '.',None, 'X', RECT,'='],
        'pawn_pos': 6,
        'orientation':[0,2,3,0,3,0,0,1,2]
    },
    # 'expert-60': {
    #     'board': ['>',"=" , None, '.', RECT, '*', RHOM, '+','X'],
    #     'pawn_pos': 5,
    #     'orientation':[2,1,0,2,3,0,2,1,3]
    # },
}

def update_tiles_orientation(TILES,level_data,verbose=False):
    orientation=level_data["orientation"]
    TILES_CP=copy.deepcopy(TILES)
    for i,tile in enumerate(level_data['board']):
        if tile is None:
            continue
        value=TILES_CP[tile]
        # Update top opens 
        lst_top_opens=[]
        for el in list(value['top_opens']):
            lst_top_opens.append((el-1+orientation[i])%4+1)
        TILES_CP[tile]['top_opens']=set(lst_top_opens)
        # Update ground opens
        lst_ground_opens=[]
        for el in list(value['ground_opens']):
            lst_ground_opens.append((el-1+orientation[i])%4+1)
        TILES_CP[tile]['ground_opens']=set(lst_ground_opens)

        # Update stairs side
        if 'stairs_side' in value:
            TILES_CP[tile]['stairs_side']=(value['stairs_side']-1+orientation[i])%4+1
        if verbose:
            print(f"updated levels of tile:\"{tile}\" from ")
            pprint(value)
            print(f"to")
            pprint(TILES_CP[tile])  
    return TILES_CP
if __name__ == "__main__":
    pprint(TILES)
    print('*'*100)
    pprint(update_tiles_orientation(TILES,level_data=LEVELS['starter1'],verbose=False))


# 0 | 1 | 2
# ---------
# 3 | 4 | 5
# ---------
# 6 | 7 | 8
