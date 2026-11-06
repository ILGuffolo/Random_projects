from runner import *

start = ""

def WinCondition(runner):
    
    
#items
i = []

#rooms
r = []

#MAIN
def main():
    gr = GameRunner(intro=start,
                    rooms=r,
                    items=i,
                    current_room="",
                    win_condition=WinCondition,
                    win_message="",
                    inventory=[])
    gr.begin_game()


#MAIN CALL
main()

