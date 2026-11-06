'''
the functions to run the game
- grid class
-
'''
EMPTY = 0
p1 = 1
p2 = -1

class grid():
    def __init__(self):
        self.state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.player = p1
    
    def reset(self):
        self.state = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.player = p2
    
    def move(self, index):
        if self.state[index] != EMPTY:
            return False

        self.state[index] = self.player
        self.player *= -1
        return True
    
    def available_moves(self):
        return [i for i, v in enumerate(self.state) if v == EMPTY]
    
    
    def check_winner(self):
        lines = [
            (0,1,2), (3,4,5), (6,7,8),  # rows
            (0,3,6), (1,4,7), (2,5,8),  # cols
            (0,4,8), (2,4,6)            # diagonals
        ]
        
        for a, b, c in lines:
            if  EMPTY != self.state[a] == self.state[b] == self.state[c]:
                return self.state[a]

        if EMPTY not in self.state:
            return 0  # draw

        return None  # game continues
        
    def display(self):
        print (f"{self.player}'s turn")
        for i in range(0, 9, 3):
            print(f"{self.state[0+i:3+i]}")
        
    def clone(self):
        new = grid()
        new.state = self.state.copy()
        new.player = self.player
        return new
    

