
from Board import *
from Cell import *
from Piece import *
from Player import *
import random as R
import time

#STRATEGIES

STRATEGY_massugu = lambda deep: lambda currPl, game, stepNum: game.select_move(
            game.strategy_massugu(
                currPl, 
                iBoard(
                    game.board, 
                    game.getPieces("L"), 
                    game.getPieces("R")
                ),
                currStep = stepNum
            ), 
            currPl.side
        )

STRATEGY_ASHIKAZU = lambda deep: lambda currPl, game, stepNum: game.select_move(
            game.strategy_ashikazu(
                currPl, 
                iBoard(
                    game.board, 
                    game.getPieces("L"), 
                    game.getPieces("R")
                ),
                currStep = stepNum, depth = deep
            ), 
            currPl.side
        )




class Game:
    #movePiece, turn-loop, dice, util
    pArray = [1/16, 4/16, 6/16, 4/16, 1/16]
    
    def __init__(self, p1Name = None, p2Name = None):
        player1 = Player("L", [Piece("L") for i in range(7)], p1Name)
        player2 = Player("R", [Piece("R") for i in range(7)], p2Name)

        self.playerDict = {
            "L": player1,
            "R": player2
        }
        
        self.board = Board(player1.pieces + player2.pieces)

    def roll_dice(self):
        return len([num for num in [R.random() for i in range(4)] if num >= 0.5])
    
    def getPieces(self, side):
        return self.playerDict.get(side).pieces
    
    def getPiece(self, side, pieceNum):
        for p in self.getPieces(side):
            if p.pieceNum == pieceNum:
                return p
        assert False, "fuck, there's no piece you demanded"

    def oppSide(self, side):
        return "R" if side == "L" else side
    
    def otherPlayer(self, side):
        return self.playerDict.get("R") if side == "L" else self.playerDict.get("L")
    
    def piece_filter(self, side, currStep, blackboard):
        filteredArr, pSet = [], blackboard.getPSet(side)
        for p in pSet:
            assert p.position is not None, f'p {p} is sus, board is {blackboard}.'
            destination = blackboard.nStepNextCell(p.position, currStep, blackboard.getPath(side))
            
            if destination is None or "end" in p.position.property:
                continue

            isBlocked = destination.contain and (destination.getContainPiece().side == side and not "end" in destination.property)
            canMove = "peace" not in destination.property and not isBlocked
            shouldMove = not "end" in p.position.property
            if canMove and shouldMove: filteredArr.append(p)
        
        return filteredArr
    
    def select_move(self, utilArr, side):
        sortedUtilArr = utilArr[:]
        if sortedUtilArr == []: return None
        sortedInd = list( range( len(sortedUtilArr) ) )

        #print(f'DEBUG: sortedInd is {sortedInd} and sUA is {sUA}')

        keyF = lambda x: sortedUtilArr[x][1].getDistance( 
            sortedUtilArr[x][1].getPSet(side)[x].position, 
            sortedUtilArr[x][1].getStart(side) 
        )

        sortedInd = sorted(sortedInd, key = keyF)
        for i in range(len(sortedInd)):
            sortedUtilArr[i] = utilArr[sortedInd[i]]
            
        optimalInd = max( 
            range( len(sortedUtilArr) ), 
            key = lambda x: sortedUtilArr[x][0]
        )
        
        #print(f'DEBUG: utilArr is {utilArr}')
        #print(f'DEBUG: sUA is {sortedUtilArr}')
        #print(f'DEBUG: optInd is {optimalInd}')

        return sortedUtilArr[optimalInd][2]
    
    def strategy_massugu(self, currPlayer, blackboard, currStep = 0, depth = 0):
        curPieces = self.piece_filter(currPlayer.side, currStep, blackboard)

        utilsArr = [self.util_massugu(p, iBoard(blackboard), currStep) for p in curPieces]
        #print(f'DEBUG: filtered list is {curPieces}')
        #print(f'DEBUG: filtered utilList is {utilsArr}')
        return utilsArr
    
    def util_massugu(self, tgPiece, blackboard, stepNum):
        destination = blackboard.nStepNextCell(tgPiece.position, stepNum, blackboard.getPath(tgPiece.side))
        destPiece = destination.getContainPiece()
        utils = blackboard.getDistance(destination, blackboard.getStart(tgPiece.side))
        
        if destPiece is not None:
            utils += blackboard.getDistance(blackboard.getStart(destPiece.side), destPiece.position)
        
        #print(f'DEBUG: now altering board {id(blackboard)}')
        blackboard.movePiece(tgPiece, stepNum)
        return (utils, blackboard, tgPiece.pieceNum)
    
    def strategy_ashikazu(self, currPlayer, blackboard, currStep = 0, depth = 2):
        curPieces = self.piece_filter(
            currPlayer.side, currStep, 
            iBoard(
                blackboard, 
                blackboard.leftPs, 
                blackboard.rightPs
            )
        )

        if currStep > 0:
            utilsArr = [self.util_ashikazu_kakutei(
                    p, iBoard(blackboard), currStep
                ) for p in curPieces
            ]
        else:
            utilsArr = [utilT for utilT in [self.util_ashikazu_kakuritsu(
                    p, iBoard(blackboard), currStep
                ) for p in curPieces
            ] if utilT is not None]
        
        if utilsArr == []: return []
        
        depth -= 1
        adversary = currPlayer
        while depth > 0:
            #print(f'DEBUG: when depth is {depth} left, utilsArr is {utilsArr}')
            #print(f'DEBUG: opponent is {adversary}')
            adversary = self.otherPlayer(adversary.side)
            advUtilsArr = []
            # generate an adversary utils array
            # then subtract based on pieceNum matching.
            for op in blackboard.getPSet(adversary.side): # should be using data from blackboard here...
                utilsPair = self.util_ashikazu_kakuritsu(
                    op, iBoard(blackboard), currStep
                )
                if utilsPair is not None:
                    advUtilsArr.append(utilsPair)
                else:
                    continue
            
            if advUtilsArr == []: 
                break #this may be the last move already.
            
            tempUtilArr = []
            for uP in advUtilsArr:
                tgUPair = max(utilsArr, key = lambda x: int(x[2] == uP[2]))
                if adversary.side != currPlayer.side:
                    tempUtilArr.append(
                        (tgUPair[0] - uP[0], uP[1], tgUPair[2])
                    )
                else:
                    tempUtilArr.append(
                        (tgUPair[0] + uP[0], uP[1], tgUPair[2])
                    )
            utilsArr = tempUtilArr
            depth -= 1

        return utilsArr
    
    def util_ashikazu_kakutei(self, tgPiece, blackboard, stepNum):
        destination = blackboard.nStepNextCell(tgPiece.position, stepNum, blackboard.getPath(tgPiece.side))
        assert destination is not None, f'destination is None :sip: for tgPiece {tgPiece}'
        destPiece = destination.getContainPiece()
        utils = blackboard.getDistance(tgPiece.position, destination)

        if destPiece is not None:
           utils += blackboard.getDistance(blackboard.getStart(destPiece.side), destPiece.position)
        
        blackboard.movePiece(tgPiece, stepNum)

        if "rosetta" in destination.property:
            rosettaUtilArr = self.strategy_ashikazu(
                self.playerDict.get(tgPiece.side),
                iBoard(blackboard, blackboard.leftPs, blackboard.rightPs),
                depth = 1
            )
            if rosettaUtilArr != []:
                return max(
                    rosettaUtilArr, 
                    key = lambda utilTuple: utilTuple[0]
                )
        return (utils, blackboard, tgPiece.pieceNum)
    
    def util_ashikazu_kakuritsu(self, tgPiece, blackboard, stepNum):
        stepsUtilArr = []
        for step in range(1, 5):
            mobilePs = self.piece_filter(
                tgPiece.side,
                step,
                blackboard
            )


            if tgPiece not in mobilePs:
                continue
            #print(f'DEBUG: step was {step}')
            #print(f'DEBUG: {tgPiece} is in {mobilePs}')

            bBoardTwo = iBoard(blackboard)
            stepUtils = self.util_ashikazu_kakutei(bBoardTwo.getPiece(tgPiece.side, tgPiece.pieceNum), bBoardTwo, step)
            stepsUtilArr.append(stepUtils)
        
        return max(
            stepsUtilArr,
            key = lambda utilTuple: utilTuple[0]
        ) if stepsUtilArr != [] else None
    
    def victoryCheck(self, side):
        tgSet = self.getPieces(side)
        return any(["end" not in p.position.property for p in tgSet])
    
    def play(self, strategyLeft, strategyRight, depthLeft = 2, depthRight = 2, spectate = False):

        def isBoardOverlay(game):
            LP = sorted([p.position.position for p in game.getPieces("L") 
                if not "start" in p.position.property and not "end" in p.position.property])
            RP = sorted([p.position.position for p in game.getPieces("R") 
                if not "start" in p.position.property and not "end" in p.position.property])
            for i in range(len(LP) - 1):
                if len(LP) == 1: break
                if LP[i] == LP[i + 1]: return True
            for i in range(len(RP) - 1):
                if len(RP) == 1: break
                if RP[i] == RP[i + 1]: return True
            return False

        gameLog = open(r'gamePlayLog.txt', 'w')
        strategyDict = {
            "L": strategyLeft(depthLeft),
            "R": strategyRight(depthRight)
        }
        currPlayer = self.playerDict.get("L")
        turnCnt = 1
        
        while True: #self.victoryCheck(currPlayer.side):
            #assert turnCnt <= 500, f'I\'ve seen enough. Stop the game and show board.\n{self.board}'
            #print(f'\nDEBUG: this is turn {turnCnt} of player {currPlayer}')
            tgProperty = "rosetta"

            while "rosetta" in tgProperty:
                turnStep = self.roll_dice()
                start = time.time()
                if turnStep == 0:
                    #print(f'DEBUG: bummers, this is a fucking zero.')
                    break

                tgStrat = strategyDict.get(currPlayer.side)
                tgInd = tgStrat(currPlayer, self, turnStep)

                #print(f'DEBUG: current step is {turnStep}')

                if tgInd is not None:
                    tgPiece = currPlayer.pieces[tgInd]
                    self.board.movePiece(tgPiece, turnStep)
                    #print(f'DEBUG: in turn {turnCnt}, {tgPiece} was moved to {tgPiece.position}.')
                    tgProperty = tgPiece.position.property
                else:
                    tgProperty = ""
                    #print(f'DEBUG: in turn {turnCnt}, nothing could be moved.\n')
                
                end = time.time()
                assert not isBoardOverlay(self), "Board has an overlay."
                if spectate: gameLog.write(f'\nTurn {turnCnt}, player: {currPlayer.side}:\nrolled{turnStep}\n{self.board}')
                #print(f'This turn took time {(end - start):.3f}')
            
            if not self.victoryCheck(currPlayer.side): break
            
            currPlayer = self.otherPlayer(currPlayer.side)
            turnCnt += 1
        
        gameInfo = f'Turn Count: {turnCnt}\nWinner: {currPlayer}'
        #print(gameInfo)
        return (currPlayer.side, turnCnt)
    


def strategyCompare(strategyLeft, strategyRight, dL = 2, dR = 2, trialCnt = 25):
    winDict = {
        "L": 0,
        "R": 0
    }
    aveTurnCnt = 0
    for i in range(trialCnt):
        #print(f'DEBUG: Game {i + 1} started')
        g = Game()

        game_played = g.play(strategyLeft, strategyRight, depthLeft = dL, depthRight = dR)
        winner, turnCnt = game_played[0], game_played[1]
        winDict[winner] = winDict.get(winner) + 1
        aveTurnCnt += turnCnt / trialCnt
        #print(f'DEBUG: Game {i + 1} ended')
        if i == trialCnt // 4 or i == trialCnt // 2:
            print(f'DEBUG: We are {i} games through {dL} vs {dR}!! :yay:')
    return f'Left win rate: {(winDict.get("L")/trialCnt):.3f}, turnCnt: {(aveTurnCnt):.3f}'

#print( strategyCompare(STRATEGY_massugu, STRATEGY_ASHIKAZU, dL = 3, dR = 8, trialCnt = 100) )
#"""
depthArr = [0, 1, 6, 10, 12, 15]
netMsg = ""
for i in [5]:
    for j in range(6):
        
        if i == 0: 
            stratL = STRATEGY_massugu
            stratStrL = "MASSUGU"
        else: 
            stratL = STRATEGY_ASHIKAZU
            stratStrL = f"ASHIKAZU depth {depthArr[i]}"

        if j == 0: 
            stratR = STRATEGY_massugu
            stratStrR = "MASSUGU"
        else: 
            stratR = STRATEGY_ASHIKAZU
            stratStrR = f"ASHIKAZU depth {depthArr[j]}"
        if i == 4 and j < 4: 
            print(f'DEBUG: matchup of {stratStrL} vs {stratStrR} is skipped')
            continue

        print(f'DEBUG: Starting simulation of {stratStrL} vs {stratStrR}')
        explain = strategyCompare(stratL, stratR, dL = depthArr[i], dR = depthArr[j], trialCnt = 200)
        netMsg += f'Left Strat: {stratStrL}; Right Strat: {stratStrR}\n {explain}'
        print(netMsg)
    netMsg = ""
"""
#testing section
def average(arr):
    arr = [i for i in arr if type(i) is int or type(i) is float]
    return sum([i/len(arr) for i in arr])

g = Game()
currPl = g.playerDict.get("L")
oppPl = g.playerDict.get("R")
g.board.movePiece(currPl.pieces[0], 2)
g.board.movePiece(currPl.pieces[1], 1)
g.board.movePiece(currPl.pieces[2], 5)
g.board.movePiece(currPl.pieces[3], 10)
g.board.movePiece(currPl.pieces[4], 3)
g.board.movePiece(currPl.pieces[5], 14)
g.board.movePiece(oppPl.pieces[0], 3)
g.board.movePiece(oppPl.pieces[1], 4)
g.board.movePiece(oppPl.pieces[2], 6)
g.board.movePiece(oppPl.pieces[3], 12)
g.board.movePiece(oppPl.pieces[4], 7)
g.board.movePiece(oppPl.pieces[5], 11)

testSteps = list(range(5))
print(g.board)

totalTimeArr = []
totalChoiceArr = []
for d in range(0, 16):
    timeArr = []
    choiceArr = []
    #print(f'current depth is {d}')
    for i in testSteps:
        start = time.time()
        if d == 0:
            k = STRATEGY_massugu(1)(currPl, g, i)
        else:
            k = STRATEGY_ASHIKAZU(d)(currPl, g, i)
        #print(f'current step is {i}')

        #print(f'uA is {uA}')
        #print(f'Optimal move is {currPl.pieces[k]}')
        #print('\n')

        end = time.time()
        #print(f'time for this Trial: {(end - start)} seconds.')
        timeArr.append(round(end - start, 3))
        if k is not None:
            choiceArr.append(f'{currPl.pieces[k].side}{currPl.pieces[k].pieceNum}')
        else:
            choiceArr.append(f'N')
        

    totalTimeArr.append(timeArr)
    totalChoiceArr.append(choiceArr)

for i in range(len(totalTimeArr)):
    print(f'timeArr for depth {i} is {average(totalTimeArr[i])}')
for i in range(len(totalTimeArr)):
    print(f'choiceArr for depth {i} is {totalChoiceArr[i]}')

g = Game()
currPl = g.playerDict.get("L")
oppPl = g.playerDict.get("R")
g.board.movePiece(currPl.pieces[0], 1)
g.board.movePiece(currPl.pieces[1], 3)
g.board.movePiece(currPl.pieces[2], 6)
g.board.movePiece(currPl.pieces[3], 9)
g.board.movePiece(currPl.pieces[4], 14)
g.board.movePiece(oppPl.pieces[0], 2)
g.board.movePiece(oppPl.pieces[1], 5)
g.board.movePiece(oppPl.pieces[2], 7)
g.board.movePiece(oppPl.pieces[3], 12)
g.board.movePiece(oppPl.pieces[4], 13)

testSteps = list(range(5))
print(g.board)

totalTimeArr = []
totalChoiceArr = []
for d in range(0, 16):
    timeArr = []
    choiceArr = []
    #print(f'current depth is {d}')
    for i in testSteps:
        start = time.time()
        if d == 0:
            k = STRATEGY_massugu(1)(currPl, g, i)
        else:
            k = STRATEGY_ASHIKAZU(d)(currPl, g, i)
        #print(f'current step is {i}')

        #print(f'uA is {uA}')
        #print(f'Optimal move is {currPl.pieces[k]}')
        #print('\n')

        end = time.time()
        #print(f'time for this Trial: {(end - start)} seconds.')
        timeArr.append(round(end - start, 3))
        if k is not None:
            choiceArr.append(f'{currPl.pieces[k].side}{currPl.pieces[k].pieceNum}')
        else:
            choiceArr.append(f'N')
        

    totalTimeArr.append(timeArr)
    totalChoiceArr.append(choiceArr)

for i in range(len(totalTimeArr)):
    print(f'timeArr for depth {i} is {average(totalTimeArr[i])}')
for i in range(len(totalTimeArr)):
    print(f'choiceArr for depth {i} is {totalChoiceArr[i]}')

g = Game()
currPl = g.playerDict.get("L")
oppPl = g.playerDict.get("R")
g.board.movePiece(currPl.pieces[0], 1)
g.board.movePiece(currPl.pieces[1], 6)
g.board.movePiece(currPl.pieces[2], 9)
g.board.movePiece(currPl.pieces[3], 12)
g.board.movePiece(oppPl.pieces[0], 4)
g.board.movePiece(oppPl.pieces[1], 7)
g.board.movePiece(oppPl.pieces[2], 10)
g.board.movePiece(oppPl.pieces[3], 14)

testSteps = list(range(5))
print(g.board)

totalTimeArr = []
totalChoiceArr = []
for d in range(0, 16):
    timeArr = []
    choiceArr = []
    #print(f'current depth is {d}')
    for i in testSteps:
        start = time.time()
        if d == 0:
            k = STRATEGY_massugu(1)(currPl, g, i)
        else:
            k = STRATEGY_ASHIKAZU(d)(currPl, g, i)
        #print(f'current step is {i}')

        #print(f'uA is {uA}')
        #print(f'Optimal move is {currPl.pieces[k]}')
        #print('\n')

        end = time.time()
        #print(f'time for this Trial: {(end - start)} seconds.')
        timeArr.append(round(end - start, 3))
        if k is not None:
            choiceArr.append(f'{currPl.pieces[k].side}{currPl.pieces[k].pieceNum}')
        else:
            choiceArr.append(f'N')
        

    totalTimeArr.append(timeArr)
    totalChoiceArr.append(choiceArr)

for i in range(len(totalTimeArr)):
    print(f'timeArr for depth {i} is {average(totalTimeArr[i])}')
for i in range(len(totalTimeArr)):
    print(f'choiceArr for depth {i} is {totalChoiceArr[i]}')

#"""