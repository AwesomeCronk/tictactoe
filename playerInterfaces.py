import os, random, socket, sys, time

from utils import *


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
        return menace
    elif name[0:5] == 'denso':
        return denso
    elif name[0:6] == 'cognex':
        return cognex
    else:
        return textInput


# Plain human input, prompts the user for a position
class textInput(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)

    def getMove(self, board):
        try:
            return int(input('Move for {} ({}): '.format(self.playerName, self.player)))
        except ValueError:
            return -1
            
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
class menace(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)
        self.matchboxPath = playerName + '.mnc'
        self.matchboxes = []
        self.movesThisGame = []     # Store the matchbox number and the position played in tuples
        
        if not os.path.exists(self.matchboxPath):
            self.initMatchboxFile()
        self.loadMatchboxes()

        print('Using {}'.format(self.matchboxPath))

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
        # If the matchbox file is incomplete, load empty matchboxes
        while len(self.matchboxes) < (3 ** 9):
            self.matchboxes.append([])
    
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

        bestAltHash, transformations = getBestAltHash(hash)

        print('Hash is {}, best alt hash is {}'.format(hash, bestAltHash))

        
        matchbox = self.matchboxes[bestAltHash]
        
        try:
            spot = random.choice(matchbox)
        except IndexError:      # Matchbox is empty
            print('Matchbox {} is empty, setting to 0-8'.format(bestAltHash))
            matchbox = list(range(9))
            self.matchboxes[bestAltHash] = matchbox
            spot = random.choice(matchbox)

        # Set this here so that at adjustments can be made at the alt matchbox directly
        # Must be done before spot gets transformed to match original hash
        self.movesThisGame.append((bestAltHash, spot))

        # This only occurs if there was a better alt hash
        if transformations:
            print('Alt hash spot is', spot)
            # print('Transformations are', transformations)
            undoTransformations = reverseTransformations(transformations)
            # print('Undo transformations are', undoTransformations)
            effectBoard = [' '] * 9
            effectBoard[spot] = 'X'

            for transformer, parameter in undoTransformations:
                effectBoard = transformer(effectBoard, parameter)

            spot = effectBoard.index('X')

        print('{} ({}) moves at {}'.format(self.playerName, self.player, spot))

        return spot

    # Take the last item out of movesThisGame
    def eliminateLastMove(self):
        hash, spot = self.movesThisGame[-1]
        del self.movesThisGame[-1]
        print('{} ({}) removing {} from matchbox {}'.format(self.playerName, self.player, spot, hash))

        # print(self.matchboxes[hash], end=' : ')
        self.matchboxes[hash] = [i for i in self.matchboxes[hash] if i != spot]
        # print(self.matchboxes[hash])

    def move(self, spot):
        pass

    def postGame(self, winner):
        print('{} adjustments:'.format(self.playerName))
        for hash, spot in self.movesThisGame:
            if winner == 'Nobody':
                print('{} + {}'.format(hash, spot))
                self.matchboxes[hash].append(spot)

            elif winner == self.player:
                print('{} + ({} * 3)'.format(hash, spot))
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)

            else:
                print('{} - {}'.format(hash, spot))
                self.matchboxes[hash].remove(spot)
                
        self.saveMatchboxes()


# Interfaces with the DENSO robot at school
class denso(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)

        controlClass = getInterfacefromName(self.playerName[5:])
        if controlClass is cognex:
            print('Cannot control DENSO with COGNEX')
            sys.exit(1)
        self.control = controlClass(self.player, self.playerName)
        
        densoAddress = ('10.1.0.64', 5001)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to robot at {}...'.format(densoAddress), end=' ')
        self.socket.connect(densoAddress)
        time.sleep(2)
        print('Connected!')

    def getMove(self, board):
        return self.control.getMove(board)

    def eliminateLastMove(self):
        return self.control.eliminateLastMove()

    def move(self, spot):
        self.control.move(spot)
        print('Commanding robot motion')
        self.socket.send('move\r\n{}\r\n'.format(spot).encode())
        # time.sleep(5)

    def postGame(self, winner):
        self.control.postGame(winner)
        print('Waiting to stop robot program')
        time.sleep(8)
        self.socket.send(b'quit\r\n\r\n')
        time.sleep(0.1)
        self.socket.close()


# Interfaces with the COGNEX camera at school
class cognex(_playerInterface):
    def __init__(self, player, playerName):
        _playerInterface.__init__(self, player, playerName)
        
        cognexAddress = ('10.1.0.55', 5001)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to camera at {}...'.format(cognexAddress), end=' ')
        self.socket.connect(cognexAddress)
        print('Connected!')
        
        print('Logging in...')
        self.socket.send(b'admin\r\n\r\n')
        resp = self.socket.recv(1024)
        print(resp.decode())

    def getPlayerButton(self):
        self.socket.send(b'GVK011\r\n')
        time.sleep(0.2)
        resp = self.socket.recv(1024).decode().strip().splitlines()[1]

        if resp == '0.000':
            return 0    
        elif resp == '1.000':
            return 1
        else:
            return None

    def capture(self):
        self.socket.send(b'SE8\r\n')
        time.sleep(0.2)
        self.socket.recv(1024)

    def fetchBoardImage(self):
        ssCol = 'K' if self.player == 'X' else 'L'
        image = []

        for ssRow in range(5):
            self.socket.send('GV{}{:>03}\r\n'.format(ssCol, ssRow).encode())
            time.sleep(0.2)
            image.append(self.socket.recv(1024).decode().strip().splitlines()[1])

        return image

    def decodeSpot(self, board, image):
        spot = -1

        for i in range(5):
            if not '#ERR' in image[i]:
                x, y = [float(number) for number in image[i].split('|')]
                print('X:', x, 'Y:', y)
                
                thisSpot = 0
                if x < 80: thisSpot += 2
                elif x < 160: thisSpot += 1
                if y >= 120: thisSpot += 6
                elif y >= 60: thisSpot += 3

                if board[thisSpot] == ' ':
                    spot = thisSpot
                    break

        return spot

    def getMove(self, board):
        playerButton = self.getPlayerButton()
        while not playerButton:
            time.sleep(0.2)
            playerButton = self.getPlayerButton()

        print('Capturing image, fetching image, decoding spot')
        self.capture()
        image = self.fetchBoardImage()
        spot = self.decodeSpot(board, image)

        print('{} ({}) moves at {}'.format(self.playerName, self.player, spot))

        return spot

    def eliminateLastMove(self):
        pass

    def move(self, spot):
        pass

    def postGame(self, winner):
        self.socket.close()
