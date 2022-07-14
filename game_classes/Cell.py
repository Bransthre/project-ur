
class Cell:
    """
    A cell is a box/place on the board that accepts a piece.
    Some cells may have special effects.

    typeChart: a dictionary storing the type of cells according to their board position
    """
    typeChart = {"L0": "rosetta",
                "L4": "start",
                "L5": "end",
                "L6": "rosetta",
                "M3": "peace rosetta",
                "R0": "rosetta",
                "R4": "start",
                "R5": "end",
                "R6": "rosetta"}

    def __init__(self, row, column, isCopy = False, contain = []):
        """
        Constructor of Cell Class.
        It grants a Cell object attributes as:

        position: a string indicating its position on board.
        next: the cell next to this cell.
        contain: the piece this cell contains.
        property: the property of this cell.
        """
        self.row = row
        self.column = column
        self.position = f'{column}{row}'
        self.contain = contain[:]
        self.isCopy = isCopy

        if Cell.typeChart.get(self.position) is not None:
            self.property = Cell.typeChart.get(self.position)
        else:
            self.property = "normal"
        
    def getContainPiece(self):
        return self.contain[0] if self.contain else None
    
    def removePiece(self, tgP):
        assert tgP in self.contain, f'{tgP} is not in {self.contain}'
        self.contain.remove(tgP)
    
    def getCopy(self):
        return Cell(self.row, self.column, isCopy = True)
    
    def __eq__(self, other):
        assert isinstance(other, Cell), f'other is now {other}'
        return self.row == other.row and self.column == other.column and self.isCopy == other.isCopy
    
    def __str__(self):
        return f'{self.position} ({self.property})'
    
    def __repr__(self):
        if self.contain:
            return f'Cell({self.position[0]}, {self.position[1]}, {self.contain})'
        return f'Cell({self.position[0]}, {self.position[1]})'

