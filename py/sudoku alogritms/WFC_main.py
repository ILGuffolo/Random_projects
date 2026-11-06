import random
import time


'''
--- Wave Function Collapse ---
- sudoku solver
deterministic collapse
optional entropy guessing

## TO DO ##

- hidden collapse (val in solo un subspace)
- box hidden collapse (row/col in box con val exlusive)
- entropy guesses
- optimizing performance:
    - big time sink serching file
'''


### Cell Class ###
class Cell:
    def __init__(self, grid, r, c, value):
        self.grid = grid
        self.r = r
        self.c = c
        self.value = value
        self.subspace = [value] if value != 0 else list(range(1, 10))

    def value(self):
        """Return the current value in the cell"""
        return self._value

    def set(self, v):
        """Set the value and collapse subspace"""
        self._value = v
        self.subspace = [v] if v != 0 else set(range(1, 10))
        self.grid._data[self.r][self.c] = v

    def row(self):
        """Return list of Cell objects in the same row"""
        return [self.grid.elem(self.r, i) for i in range(9)]

    def col(self):
        """Return list of Cell objects in the same column"""
        return [self.grid.elem(i, self.c) for i in range(9)]

    def box(self):
        """Return list of Cell objects in the same 3x3 box"""
        br, bc = 3 * (self.r // 3), 3 * (self.c // 3)
        return [self.grid.elem(r, c) for r in range(br, br+3) for c in range(bc, bc+3)]
    
    def subRemove(self, v, ini=False):
        '''removes values form subspace and collapses'''
        if v in self.subspace:
            self.subspace.remove(v)
            #print(f"subspace reduced: {v}")
            
        if len(self.subspace) == 1 and ini == False:
            #print("subspace collpased {self.subspace[0]}")
            self.set(self.subspace[0])
            mainStack.append(stackBuilder(self, self.subspace[0]))



### Grid class ###
class Grid:
    def __init__(self, digits):
        if len(digits) != 81:
            raise ValueError("Digits string must be 81 characters")
        self._data = []
        self._cells = []
        for i in range(0, 81, 9):
            row_vals = [int(d) for d in digits[i:i+9]]
            row_cells = [Cell(self, r=len(self._data), c=j, value=v) for j, v in enumerate(row_vals)]
            self._data.append(row_vals)
            self._cells.append(row_cells)
    
    def elem(self, r, c):
        return self._cells[r][c]

    def grid(self):
        return self._data
    
    def init(self):
        for r in range(9):
            for c in range(9):
                val = self._data[r][c]
                cl = self.elem(r, c)
                if val != 0:
                    #print(f"init precollapse at {r}, {c} = {val}")
                    cl.set(val)
                    mainStack.append(stackBuilder(cl, val))
                    

# -extract a single line from the dataset- #
path = "sudoku.csv"
def getGrid(target_line):
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if i == target_line:
                return line.strip().split(",")

# -for colored text- #
def color(text, code):
    return f"\033[{code}m{text}\033[0m"
RED = "31"       #error  
GREEN = "32"     #solved numbers
YELLOW = "33"
BLUE = "34"      #given numbers
GRAY = "90"      #empty

# -Print gird- #
def print_grid_compare(original, solved):
    for r in range(9):
        if r % 3 == 0:
            print("+-------+-------+-------+")

        for c in range(9):
            if c % 3 == 0:
                print("|", end=" ")

            v = solved[r][c]
            orig = original[r][c]

            if v == 0:
                # Empty cell
                print(color(".", GRAY), end=" ")
            elif orig != 0 and v != orig:
                # Changed original clue → red
                print(color(v, RED), end=" ")
            elif orig != 0:
                # Original clue → blue
                print(color(v, BLUE), end=" ")
            else:
                # Filled by solver → green
                print(color(v, GREEN), end=" ")

        print("|")

    print("+-------+-------+-------+")
    
    
    
def print_grid(grid):
    for r in range(9):
        if r % 3 == 0:
            print("+-------+-------+-------+")

        for c in range(9):
            if c % 3 == 0:
                print("|", end=" ")

            v = grid[r][c]

            if v == 0:
                # Empty cell
                print(color(".", GRAY), end=" ")
            else:
                # Filled → blue
                print(color(v, BLUE), end=" ")

        print("|")

    print("+-------+-------+-------+")
    
# -deterministic collapse full grid- #
def fullCollapse(grid):
    finish = True
    for r in range(9):
        for c in range(9):
            cell = grid.elem(r, c)
            if len(cell.subspace) == 1 and cell.value == 0:
                cell.subRemove(-1)
                finish = False 
            stackEval()
    if finish == True : return 
                
                

# stack builder #
def stackBuilder(c, val):
    stack = [val]
    stack.extend(c.row())
    stack.extend(c.col())
    stack.extend(c.box())
    global GlobalstackNumber
    GlobalstackNumber += 1
    return stack    
        
# stack eval #
def stackEval(ini=False):
    while(len(mainStack)>=1):
        stack = mainStack[0]
        for s in stack:
            if s not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                if s.value == 0:
                    s.subRemove(stack[0], ini)
        mainStack.pop(0)
        
def justMakeGrid(string):
    return [[int(string[c + 9*r]) for c in range (9)] for r in range(9)]


def solve_one(gridID, isPrint=True, isDebug=False):
    #global setup
    
    global mainStack
    mainStack = []
    
    global GlobalstackNumber
    GlobalstackNumber = 0

    #grid setup & print
    IDn = gridID
    unsolved, solved = getGrid(IDn)

    unsolvedGrid = Grid(unsolved)
    original = justMakeGrid(unsolved)

    if isPrint: print_grid(unsolvedGrid.grid())

    unsolvedGrid.init()
    if isPrint: print(f"init completed: {len(mainStack)}")

    #start solver
    stackEval(mainStack[0]) #eval all init values
    if isPrint: print("init collapse completed")
    fullCollapse(unsolvedGrid)
    if isPrint: print("collapse finish")
    if isPrint: print_grid_compare(original, unsolvedGrid.grid())
    if isPrint: print(f"global stack evaluated: {GlobalstackNumber}")
    
    for r in unsolvedGrid.grid():
        if 0 in r: return 0
    return 1

            
#_____________________________________________   MAIN   _____________________________________________#

#global setup
mainStack = []
GlobalstackNumber = 0

cycles = 1000
offset = 1

somma = 0
print(f"evaluation started for {cycles} cycles")

t_start = time.time()

for i in range(cycles):
    print(f"cycle n: {i}")
    somma += solve_one(offset + i, False)
    
t_end = time.time()
t_length = int(t_end - t_start)

print(f"evaluation ended with {somma} fully completed")

print("It took", t_length, "seconds!")
print(f"time average of: {t_length/cycles} sec/cycle")

