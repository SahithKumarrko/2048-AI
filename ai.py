import math
from datetime import datetime
from colorama import Fore as colors,init
init()
minSearchTime = 0.3

class Tile:
    def __init__(self,position,value):
        self.x = position["x"]
        self.y = position["y"]
        self.value = value or 2
        self.previousPosition  = None
        self.mergedFrom = None
    def savePosition(self):
        self.previousPosition = {"x":self.x,"y":self.y}
    def updatePosition(self,position):
        self.x = position["x"]
        self.y = position["y"]
    def clone(self):
        newTile = Tile({ "x": self.x, "y": self.y }, self.value)
        return newTile

class Grid:
    def __init__(self,size):
        self.size = size
        self.startTiles = 1
        self.cells = []
        self.indexes = []
        for x in range(self.size):
            self.cells.append([])
            for y in range(self.size):
                self.cells[x].append(None)
        for x in range(4):
            self.indexes.append([])
            for y in range(4):
                self.indexes[x].append({"x":x,"y":y})
        self.vectors = {
                    0: { "x": 0,  "y": -1 }, # up
                    1: { "x": 1,  "y": 0 },  # right
                    2: { "x": 0,  "y": 1 },  # down
                    3: { "x": -1, "y": 0 }   # left
                }
    
    def eachCell(self,callback):
        for x in range(self.size):
            for y in range(self.size):
                callback(x,y,self.cells[x][y])
    
    def availableCells(self):
        cells = []
        def addCell(x,y,tile):
            # print("Tile : ",tile)
            if tile==None:
                # print("Tile Value : ",tile.value)
                cells.append({"x":x,"y":y})
        self.eachCell(addCell)
        # print("Cells : ",cells)
        return cells

    def cellsAvailable(self):
        return not(not(len(self.availableCells())))
    
    def withinBounds(self,position):
        return (position["x"] >= 0 and position["x"] < self.size and
                position["y"] >= 0 and position["y"] < self.size)

    def cellContent(self,cell):
        if self.withinBounds(cell):
            return self.cells[cell["x"]][cell["y"]]
        return None
    
    def insertTile(self,tile):
        # print("Recieved tile value : ",tile.x,tile.y,tile.value)
        self.cells[tile.x][tile.y] = tile
    
    def removeTile(self,tile):
        self.cells[tile.x][tile.y] = None

    def clone(self):
        newGrid = Grid(self.size)
        for x in range(self.size):
            for y in range(self.size):
                if self.cells[x][y]!=None:
                    newGrid.insertTile(self.cells[x][y].clone())
        return newGrid
    

    def cellOccupied(self,cell):
        return not(not(self.cellContent(cell)))

    def cellAvailable(self,cell):
        return not(self.cellOccupied(cell))

    def moveTile(self,tile,cell):
        self.cells[tile.x][tile.y] = None
        self.cells[cell["x"]][cell["y"]] = tile
        tile.updatePosition(cell)

    def getVector(self,direction):
        return self.vectors[direction]
    
    def buildTraversals(self,vector):
        traversals = { "x": [], "y": [] }
        for pos in range(self.size):
            traversals["x"].append(pos)
            traversals["y"].append(pos)
        if vector["x"] == 1:
            traversals["x"].reverse()
        if vector["y"] == 1:
            traversals["y"].reverse()
        return traversals
    
    def findFarthestPosition (self,cell,vector):
        previous = 0
        while True:
            previous = cell
            cell = { "x": previous["x"] + vector["x"], "y": previous["y"] + vector["y"] }
            if not(self.withinBounds(cell) and self.cellAvailable(cell)):
                break
        return {"farthest": previous,"next_p": cell}
    
    def tileMatchesAvailable(self):
        tile = None
        for x in range(self.size):
            for y in range(self.size):
                tile = self.cellContent({"x":x,"y":y})
                if tile!=None:
                    for direction in range(4):
                        vector = self.getVector(direction)
                        cell = {"x":x+vector["x"],"y":y + vector["y"]}
                        other = self.cellContent(cell)
                        if (other and other.value==tile.value):
                            return True
        return False
    
    def positionsEqual(self,first,second):
        return first["x"] == second.x and first["y"] == second.y
                        

    def movesAvailable(self):
        return self.cellsAvailable() or self.tileMatchesAvailable()

    def islands(self):
        def mark(x,y,value):
            if (x >= 0 and x <= 3 and y >= 0 and y <= 3 and self.cells[x][y] and self.cells[x][y].value == value and not(self.cells[x][y].marked)):
                self.cells[x][y].marked = True
                for direction in range(4):
                    vector = self.getVector(direction)
                    mark(x + vector["x"], y + vector["y"], value)
        
        islands_v = 0
        for x in range(4):
            for y in range(4):
                if self.cells[x][y] != None:
                    self.cells[x][y].marked = False
        
        for x in range(4):
            for y in range(4):
                if (self.cells[x][y]!=None and not(self.cells[x][y].marked)):
                    islands_v += 1
                    mark(x, y , self.cells[x][y].value)
        
        return islands_v

    def smoothness(self):
        smoothness_v = 0
        for x in range(4):
            for y in range(4):
                if (self.cellOccupied(self.indexes[x][y])):
                    value = math.log(self.cellContent(self.indexes[x][y]).value) / math.log(2)
                    for direction in [1,2]:
                        vector = self.getVector(direction)
                        targetCell = self.findFarthestPosition(self.indexes[x][y], vector)["next_p"]
                        if (self.cellOccupied(targetCell)):
                            target = self.cellContent(targetCell)
                            targetValue = math.log(target.value) / math.log(2)
                            smoothness_v -= abs(value - targetValue)
        return smoothness_v
    
    def monotonicity2(self):
        totals = [0,0,0,0]
        for x in range(4):
            current = 0
            next_p = current+1
            while next_p<4:
                while next_p<4 and not(self.cellOccupied(self.indexes[x][next_p])):
                    next_p += 1
                if next_p>=4:
                    next_p -= 1
                currentValue = math.log(self.cellContent(self.indexes[x][current]).value) / math.log(2) if self.cellOccupied({"x":x, "y":current}) else 0
                nextValue = math.log(self.cellContent(self.indexes[x][next_p]).value) / math.log(2) if self.cellOccupied({"x":x, "y":next_p}) else 0
                if (currentValue > nextValue):
                    totals[0] += nextValue - currentValue
                elif (nextValue > currentValue):
                    totals[1] += currentValue - nextValue
                current = next_p
                next_p += 1
        for y in range(4):
            current = 0
            next_p = current+1
            while next_p<4:
                while next_p<4 and not(self.cellOccupied(self.indexes[next_p][y])):
                    next_p += 1
                if next_p>=4:
                    next_p -= 1
                currentValue = math.log(self.cellContent(self.indexes[current][y]).value) / math.log(2) if self.cellOccupied({"x":current, "y":y}) else 0
                nextValue = math.log(self.cellContent(self.indexes[next_p][y]).value) / math.log(2) if self.cellOccupied({"x":next_p, "y":y}) else 0
                if (currentValue > nextValue):
                    totals[2] += nextValue - currentValue
                elif (nextValue > currentValue):
                    totals[3] += currentValue - nextValue
                current = next_p
                next_p += 1
        return max(totals[0], totals[1]) + max(totals[2], totals[3])
    
    def maxValue(self):
        max_v = 0
        for x in range(4):
            for y in range(4):
                if (self.cellOccupied(self.indexes[x][y])):
                    value = self.cellContent(self.indexes[x][y]).value
                    if (value > max_v):
                        max_v = value
        return math.log(max_v) / math.log(2)
    
    def isWin(self):
        for x in range(4):
            for y in range(4):
                if (self.cellOccupied(self.indexes[x][y])):
                    # print("Cell Occupied : ",self.indexes[x][y],self.cellOccupied(self.indexes[x][y]))
                    if (self.cellContent(self.indexes[x][y]).value == 2048):
                        return True
        return False
    
    def prepareTiles(self):
        def prepare(x,y,tile):
            if tile!=None:
                tile.mergedFrom = None
                tile.savePosition()
        self.eachCell(prepare)

    def move(self,direction):

        cell = None
        tile = None

        vector     = self.getVector(direction)
        traversals = self.buildTraversals(vector)
        moved      = False
        score      = 0
        won        = False
        self.prepareTiles()

        for x in traversals["x"]:
            for y in traversals["y"]:
                cell = self.indexes[x][y]
                tile = self.cellContent(cell)
                if tile!=None:
                    position = self.findFarthestPosition(cell, vector)
                    next_p = self.cellContent(position["next_p"])
                    if (next_p and next_p.value == tile.value and not(next_p.mergedFrom)):
                        merged = Tile(position["next_p"], tile.value * 2)
                        merged.mergedFrom = [tile, next_p]

                        self.insertTile(merged)
                        self.removeTile(tile)

                        # Converge the two tiles' positions
                        tile.updatePosition(position["next_p"])

                        # Update the score
                        score += merged.value

                        if merged.value == 2048:
                            won = True
                    else:
                        self.moveTile(tile, position["farthest"])
                    if not self.positionsEqual(cell, tile):
                        moved = True
        return {"moved": moved, "score": score, "won": won}


class AI:
    def __init__(self,grid):
        self.grid = grid
    def eval(self):
        emptyCells = len(self.grid.availableCells())

        smoothWeight = 0.1
        mono2Weight = 1.0
        emptyWeight = 2.7
        maxWeight = 1.0
        # print("Empty : ",emptyCells)
        return self.grid.smoothness() * smoothWeight + self.grid.monotonicity2() * mono2Weight + math.log(emptyCells) * emptyWeight + self.grid.maxValue() * maxWeight

    def search(self,depth,alpha,beta,positions,cutoffs):
        bestScore = 0
        bestMove = -1
        result = 0
        bestScore = alpha
        for direction in range(4):
            newGrid = self.grid.clone()
            if newGrid.move(direction)["moved"]:
                positions += 1
                if newGrid.isWin():
                    print("Winning state reached")
                    return { "move": direction, "score": 10000, "positions": positions, "cutoffs": cutoffs }
                newAI = AI(newGrid)
                if depth==0:
                    result = { "move": direction, "score": newAI.eval() }
                else:
                    result = newAI.search(depth-1, bestScore, beta, positions, cutoffs)
                    if result["score"] > 9900:
                        result["score"] -= 1
                    positions = result["positions"]
                    cutoffs = result["cutoffs"]
                if result["score"] > bestScore:
                    bestScore = result["score"]
                    bestMove = direction
                if bestScore > beta:
                    cutoffs += 1
                    return { "move": bestMove, "score": beta, "positions": positions, "cutoffs": cutoffs }
        return { "move": bestMove, "score": bestScore, "positions": positions, "cutoffs": cutoffs }
    
    def iterativeDeep(self):
        start = datetime.now()
        depth = 0
        best = 0
        while True:
            newBest = self.search(depth,-10000,10000,0,0)
            if newBest["move"] == -1:
                break
            else:
                best = newBest
            depth += 1
            if not((datetime.now() - start).total_seconds() < minSearchTime):
                print("Completed searching exiting")
                break
        return best
    
    def getBest(self):
        return self.iterativeDeep()
    
    def translate(self,move):
        return {
                    0: 'up',
                    1: 'right',
                    2: 'down',
                    3: 'left'
                }[move]


grid = Grid(4)
ai = AI(grid)
# cells = [[4,0,2,8],[0,0,8,64],[0,8,16,32],[0,8,128,4]]
# cells = [[0,0,2,8],[0,0,16,8],[2,2,4,32],[0,0,0,8]]
# cells = [[2,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,2]]
cells= [[0,0,2,4],[0,0,0,64],[0,4,2,16],[16,2,16,4]]
for i in range(4):
    for j in range(4):
        if cells[i][j]!=0:
            # print("Valaue : ",cells[i][j])
            grid.insertTile(Tile({"x":i,"y":j},cells[i][j]))
# for i in range(4):
#     for j in range(4):
#         if grid.cells[i][j]!=None:
#             # print(i,j)
#             print("Value : ",i,j,grid.cells[i][j].value)

best = ai.getBest()
print("\n\n")
# print("Best move : ",colors.RED + "Testing" + colors.RESET)
# moved = grid.move(best["move"])
move = best["move"]
if move==0:
    print("Best move : ",colors.RED + ai.translate(move).upper() + colors.RESET,end="\r")
if move==1:
    print("Best move : ",colors.LIGHTGREEN_EX + ai.translate(move).upper() + colors.RESET,end="\r")
if move==2:
    print("Best move : ",colors.MAGENTA + ai.translate(move).upper() + colors.RESET,end="\r")
if move==3:
    print("Best move : ",colors.YELLOW + ai.translate(move).upper() + colors.RESET,end="\r")
    
# print("Grid moved : ",moved)
