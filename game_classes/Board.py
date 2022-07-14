from Cell import *
from Piece import *

class Board:

    def __init__(self, inGamePs, field = None):
        self.field = [ [Cell(row, col) for col in ["L", "M", "R"]] for row in range(8) ]
        if inGamePs is not None:
            self.inGamePs = inGamePs
            for pieces in inGamePs:
                self.getStart(pieces.side).contain.append(pieces)
                pieces.position = self.getStart(pieces.side)
    
    def __str__(self):
        displayStr = "=" * 25
        for row in self.field:
            displayStr += "\n"
            for cell in row:
                displaySeg = " | ".join([p.code for p in cell.contain])
                if displaySeg == "": displaySeg = "Empty"
                displayStr += " || " + displaySeg
            displayStr += " || "
            displayStr += "\n" + "=" * 25
        return displayStr
    
    def __repr__(self):
        return f'DEBUG:'
        return f'Board(); id: {id(self)}'
    
    def getFieldInfo(self, limit = 7):
        infoArr = []
        for p in self.inGamePs:
            if p.pieceNum <= limit:
                infoArr.append((f'{p.side}{p.pieceNum}', p.position.position))
        return infoArr

    def getDistance(self, cellA, cellB):
        pathLeft = self.getPath("L")
        pathRight = self.getPath("R")
        assert type(cellA) is Cell, f'cellA is {cellA}'
        assert type(cellB) is Cell, f'cellB is {cellB}'

        cell1, cell2 = self.getCell(cellA.row, cellA.column), self.getCell(cellB.row, cellB.column)
        if cell1 in pathLeft and cell2 in pathLeft:
            return abs(pathLeft.index(cell1) - pathLeft.index(cell2))
        else:
            return abs(pathRight.index(cell1) - pathRight.index(cell2))

    def getStart(self, side):
        return self.field[4][self.getColNum(side)]
    
    def getEnd(self, side):
        return self.field[5][self.getColNum(side)]

    def getColNum(self, col):
        columnDict = {'L': 0,
                'M': 1,
                'R': 2}
        assert col in columnDict, f'{col} is not in dictionary.'

        return columnDict.get(col)
    
    def movePiece(self, tgPiece, step):
        destination = self.nStepNextCell(tgPiece.position, step, self.getPath(tgPiece.side))
        if destination is None: return

        tgPiece.position.removePiece(tgPiece)

        if len(destination.contain) and "end" not in destination.property and "start" not in destination.property:
            destP = destination.contain[0]
            destination.removePiece(destP)
            tgStart = self.getStart(destP.side)
            destP.position = tgStart
            tgStart.contain.append(destP)
            
        
        destination.contain.append(tgPiece)
        #assert "start" in destination.property or len(destination.contain) <= 1, f'overlap on cell {destination} with {destination.contain}'
        tgPiece.position = destination
        

    def nextCell(self, tgCell, side):
        if tgCell.property == "end":
            return None
        if tgCell.position == "L0" or tgCell.position == "R0":
            return self.getCell(0, "M")
        if tgCell.position == "M7":
            return self.getCell(7, side)
        if tgCell.position[0] == "M":
            return self.getCell(tgCell.row + 1, "M")
        else:
            return self.getCell(tgCell.row - 1, tgCell.column)
    
    def getPath(self, side):
        curCell = self.getStart(side)
        path = []
        while type(curCell) is Cell:
            path.append(curCell)
            curCell = self.nextCell(curCell, side)
            if curCell.property == "end":
                path.append(curCell)
                break
        return path
    
    def nStepNextCell(self, tgCell, steps, path):
        indTgCell = path.index(self.getCell(tgCell.row, tgCell.column))
        if indTgCell + steps >= len(path):
            return None
        else:
            return path[indTgCell + steps]

    def getCell(self, row, column):
        return self.field[row][self.getColNum(column)]


class iBoard(Board):

    def __init__(self, board, leftPs = None, rightPs = None):
        super().__init__(None)
        self.original = board

        #DEBUG: Please optimize/shorten this seciton of code later.

        if leftPs is not None:
            self.leftPs = [p.getCopy() for p in leftPs]
        else:
            self.leftPs = board.leftPs

        if rightPs is not None:
            self.rightPs = [p.getCopy() for p in rightPs]
        else:
            self.rightPs = board.rightPs
        
        self.piecesDict = {
            "L": self.leftPs,
            "R": self.rightPs
        }
        self.inGamePs = self.leftPs + self.rightPs
        self.field = [ [Cell(row, col, isCopy = True) for col in ["L", "M", "R"]] for row in range(8) ]

        fieldInfo = self.original.getFieldInfo()
        for piece, pos in fieldInfo:
            tgPiece, tgPos = self.piecesDict.get(piece[0])[int(piece[1])], self.getCell(int(pos[1]), pos[0])
            tgPiece.position = tgPos
            tgPos.contain.append(tgPiece)
    
    def otherPSet(self, pSet):
        if pSet == self.leftPs:
            return self.rightPs
        else:
            return self.leftPs
    
    def getPSet(self, side):
        return self.leftPs if side == "L" else self.rightPs
    
    def getPieces(self, side):
        return self.piecesDict.get(side)
    
    def getPiece(self, side, pieceNum):
        for p in self.getPSet(side):
            if p.pieceNum == pieceNum:
                return p
        assert False, "there's no piece you demanded"