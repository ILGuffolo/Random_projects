'''
dungeon generator scripts
and helper function to run it
'''

from room_gen import generate_room, Room
from item_gen import generate_loot, Loot, generate_item, Item

class Dungeon():
    '''
    main dungeon class containing every inforamtion about it:
    
    structure layout: room grid (2d matrix) of room classes
    other attributes
    - name
    - rating
    - modifiers[]
    - 
    '''
    
    def __init__(self, rating, name = "Untitled dungeon", modifiers = None):
        
        self.rating = rating
        self.name = name
        self.modifiers = modifiers if modifiers is not None else []
        self.rooms = self.generate_grid()
        
    
    def generate_grid(self):
        
        # Rating to grid algorithm
        # square L = 2*r+1 (plus endWalls)
        
        lenght = 2 * self.rating + 1
        
        grid = [[generate_room([x, y], rating= self.rating) for x in range(lenght)] for y in range(lenght)]
        
        for row in grid:# aviable path generation (all)
            for room in row:
                
                x, y = room.position

                if y == 0:
                    if "north" in room.paths:
                        room.paths.remove("north")

                if y == lenght - 1:
                    if "south" in room.paths:
                        room.paths.remove("south")

                if x == 0:
                    if "west" in room.paths:
                        room.paths.remove("west")

                if x == lenght - 1:
                    if "east" in room.paths:
                        room.paths.remove("east")
                
        return grid
        
    def print_layout(self):
        grid = self.rooms
        size = len(grid)

        for y in range(size):

            # --- ROOM ROW ---
            room_line = ""

            for x in range(size):
                room = grid[y][x]

                loot_count = len(room.loot)
                item_count = sum(len(l.items) for l in room.loot)

                room_line += f"[{loot_count}.{item_count}]"

                # horizontal connection (east)
                if x < size - 1:
                    right_room = grid[y][x + 1]

                    if "east" in room.paths and "west" in right_room.paths:
                        room_line += "=="
                    else:
                        room_line += "  "

            print(room_line)

            # --- VERTICAL CONNECTION ROW ---
            if y < size - 1:
                conn_line = ""

                for x in range(size):

                    room = grid[y][x]
                    down_room = grid[y + 1][x]

                    # spacing under room
                    conn = "  "

                    if "south" in room.paths and "north" in down_room.paths:
                        conn = " | | "

                    conn_line += conn

                    # spacing between columns
                    if x < size - 1:
                        conn_line += "  "

                print(conn_line)
        

        
    
    
    