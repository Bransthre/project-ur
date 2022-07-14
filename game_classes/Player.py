
class Player:

    playerNum = 0
    def __init__(self, side, pieces, name):
        self.playerID = Player.playerNum
        if name is not None:
            self.name = name
        else:
            self.name = f'名もなき {self.playerID}'
        Player.playerNum += 1
        self.side = side
        self.pieces = pieces
    
    def __str__(self):
        return f'player {self.side}: {self.name}'

