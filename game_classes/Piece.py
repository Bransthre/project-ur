
class Piece:

    canCapture = True
    pieceNumArr = [0, 0]

    def __init__(self, side, isCopy = False, pieceNum = None, mobile = True):
        assert side == "L" or side == "R", "side is not on appropriate side"
        self.side = side
        self.position = None
        self.isCopy = isCopy
        self.canMove = mobile
        
        if pieceNum is None:
            self.pieceNum = Piece.pieceNumArr[self.sideNum(self.side)] % 7
            Piece.pieceNumArr[self.sideNum(self.side)] += 1
        else:
            self.pieceNum = pieceNum % 7
        self.code = f'{self.side}{self.pieceNum}'
    
    def sideNum(self, side):
        return 0 if side == "L" else 1
    
    def getCopy(self):
        return Piece(self.side, isCopy = True, pieceNum = self.pieceNum, mobile = self.canMove)

    def __eq__(self, other):
        assert isinstance(other, Piece)
        return self.side == other.side and self.pieceNum == other.pieceNum

    def __str__(self):
        return f'{self.side}{self.pieceNum}; copy{self.isCopy} @ {self.position}'
    
    def __repr__(self):
        return str(self)
        return f'Piece({self.side}); id:{id(self)}'
    