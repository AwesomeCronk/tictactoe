import os, random

from utils import hashBoard, unhashBoard


class _playerInterface:
    def __init__(self, player, playerName):
        self.player = player
        self.playerName = playerName

    def getMove(self, board):
        raise NotImplementedError()

    def eliminateLastMove(self):
        raise NotImplementedError()

    def move(self, spot):
        raise NotImplementedError()

    def postGame(self, winner):
        raise NotImplementedError()


def getInterfacefromName(name):    
    if name[0:6] == 'menace':
        return menaceAI
    else:
        return textInput


# Plain human input, prompts the user for a position
class textInput(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)

    def getMove(self, board):
        return int(input('Move for {} ({}): '.format(self.playerName, self.player)))

        # This might be removable depending on how _playerInterface.move() works out
        # try:
        #     choice = int(input('Move for {}: '.format(player)))
        # except ValueError:
        #     print('Invalid entry, could not get integer')
        #     choice = self.getMove()
        # 
        # if choice in range(9):
        #     return choice
        # else:
        #     print('Invalid entry: {}, out of range'.format(choice))
        #     return self.getMove()

    def eliminateLastMove(self):
        print('Invalid entry, try again')

    def move(self, spot):
        pass

    def postGame(self, winner):
        pass


# My sad attempt at making a minimax AI... not tested and guaranteed not to work
class minimaxAI(_playerInterface):
    class branch():
        def __init__(self, minimax, hash):
            self.minimax = minimax      # True: playing as X; False: Playing as O
            self.hash = hash
            self.value = 0
            self.move = -1
            self.branches = []

            self.initBranches()

        def initBranches(self):
            self.board = unHashBoard(self.hash)
            for spot, value in enumerate(self.board):
                if value == ' ':     # If a move can be placed there
                    branchBoard = copy.copy(self.board)
                    branchBoard[spot] = 'X' if self.minimax else 'O'
                    self.branches.append(minimaxAI.branch(self.minimax, hashBoard(branchBoard)))

        def eval(self):
            self.value = 0

            if len(self.branches) > 0:
                for branch in self.branches:
                    branch.eval()
                    if self.minimax and branch.value > self.value:
                        self.value = branch.value
                    elif not self.minimax and branch.value < self.value:
                        self.value = branch.value
            else:
                winner = checkWon(self.board)
                if self.winner == 'X':
                    self.value = 1
                elif self.winner == 'O':
                    self.value = -1

    def __init__(self, minimax):
        self.minimax = minimax
        self.rootBranch = self.branch(board, self.minimax)

    def eval(self, state):
        pass


# Implements the MENACE algorithm
class menaceAI(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)
        self.matchboxPath = playerName + '.mnc'
        self.matchboxes = []
        self.movesThisGame = []     # Store the matchbox number and the position played in tuples
        
        if not os.path.exists(self.matchboxPath):
            self.initMatchboxFile()
        self.loadMatchboxes()

    def initMatchboxFile(self):
        with open(self.matchboxPath, 'w') as matchboxFile:
            for i in range(3 ** 9):
                spotsWritten = []
                for j in range(10):
                    spot = random.randint(0, 8)
                    matchboxFile.write(str(spot) + ' ')
                    spotsWritten.append(spot)

                # Ensure any available spot can be played
                for j in range(9):
                    if not j in spotsWritten:
                        matchboxFile.write(str(j) + ' ')
                matchboxFile.write('\n')

    def loadMatchboxes(self):
        self.matchboxes = []
        with open(self.matchboxPath, 'r') as matchboxFile:
            for matchbox in matchboxFile:
                self.matchboxes.append([])
                for bead in matchbox[:-1].split():
                    self.matchboxes[-1].append(int(bead))
    
    def saveMatchboxes(self):
        with open(self.matchboxPath, 'w') as matchboxFile:
            for matchbox in self.matchboxes:
                matchboxFile.write(' '.join([str(spot) for spot in matchbox]))
                matchboxFile.write('\n')

    def getMove(self, board):
        # By pretending we're X even when we're O, the AI can use the same training file for both
        if self.player == 'O':
            inversion = {' ': ' ', 'X': 'O', 'O': 'X'}
            invBoard = [inversion[spot] for spot in board]
            hash = hashBoard(invBoard)
        else:
            hash = hashBoard(board)

        matchbox = self.matchboxes[hash]

        try:
            spot = random.choice(matchbox)
        except IndexError:      # Matchbox is empty
            matchbox = list(range(9))
            self.matchboxes[hash] = matchbox
            spot = random.choice(matchbox)

        self.movesThisGame.append((hash, spot))
        print('{} ({}) moves at {}'.format(self.playerName, self.player, spot))

        return spot

    def eliminateLastMove(self):
        # Take the last item out of movesThisGame
        hash, spot = self.movesThisGame[-1]
        del self.movesThisGame[-1]

        self.matchboxes[hash] = [i for i in self.matchboxes[hash] if i != spot]

    def move(self, spot):
        pass

    def postGame(self, winner):
        for hash, spot in self.movesThisGame:
            if winner == 'Nobody':
                self.matchboxes[hash].append(spot)

            elif winner == self.player:
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)

            else:
                self.matchboxes[hash].remove(spot)
                
        self.saveMatchboxes()
