from game2048 import GameManager
import time
import random
from os import system,name
from colorama import init, Fore, Style
init(autoreset=True)

cur_color = []
COLORS = [
            Fore.GREEN + Style.BRIGHT,
            Fore.BLUE + Style.BRIGHT,
            Fore.CYAN + Style.BRIGHT,
            Fore.RED + Style.BRIGHT,
            Fore.MAGENTA + Style.BRIGHT,
            Fore.YELLOW + Style.BRIGHT,
        ]
def prepare_str(direction,current_color):
    lc = list(set(COLORS) - set(current_color))
    rcolor = random.choice(lc)
    return [rcolor]

def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

grid = None
last_grid = None
  
gm = GameManager()
print("\nStarted....\n\n")
gm.board.board = [[None,None,2,None],[None,None,None,None],[None,None,None,None],[2,None,4,4]]
grid = gm.getGrid()
# print("Got the grid and finding next move")
# t0 = time.time()
next_move = gm.ai.getNextMove(grid)
# t1 = time.time()
cur_color = prepare_str(next_move,cur_color)

clear()

print("\n\n\n\n\n\n\n\n\n\n\t\t\t\tNext Key : ",cur_color[0] + next_move)

# print("Next Key : ",cur_color[0] + "next_move",end="\r")

# print("Time taken : ",(t1 - t0))