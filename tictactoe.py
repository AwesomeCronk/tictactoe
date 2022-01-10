import copy, logging, os, random, argparse, time

board = [' '] * 9

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-x',
        type=str,
        nargs=1,
        default='human',
        help='set player X'
    )
    parser.add_argument(
        '-o',
        type=str,
        nargs=1,
        default='human',
        help='set player O'
    )
    parser.add_argument(
        '-d',
        type=float,
        default=0.5,
        help='set delay for AI players'
    )
    return parser.parse_args()

def printBoard():
    logging.info('printBoard()')
    for i in range(3):
        if i:
            print('\n---|---|---          ---|---|---')
        for j in range(3):
            if j:
                print('|', end='')
            print(' ' + board[i * 3 + j].replace(' ', str(i * 3 + j)).replace('X', ' ').replace('O', ' '), end = ' ')
        print('          ', end='')
        for j in range(3):
            if j:
                print('|', end='')
            print(' ' + board[i * 3 + j], end = ' ')

def getMove(player):
    logging.info('getMove({})'.format(repr(player)))
    try:
        choice = int(input('Move for {}: '.format(player)))
    except ValueError:
        print('Invalid entry, could not get integer')
        choice = getMove(player)

    if choice in range(9):
        return choice
    else:
        print('Invalid entry: {}, out of range'.format(choice))
        return getMove(player)
        

def move(player, spot):
    logging.info('move({}, {})'.format(repr(player), repr(spot)))
    global board
    openSpots = []

    for i, value in enumerate(board):
        if value == ' ':
            openSpots.append(i)

    if spot in openSpots:
        board[spot] = player
        return True
    else:
        print('Space {} occupied by {}; {} cannot go there'.format(spot, board[spot], player))
        return False

def checkWon(board=board):
    logging.info('checkWon()')
    winner = ''
    for i in range(3):
        if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] and board[i * 3] != ' ':    # Check rows
            winner = board[i * 3]
        elif board[i] == board[i + 3] == board[i + 6] and board[i] != ' ':      # Check Columns
            winner = board[i]
        elif board[0] == board[4] == board[8] and board[0] != ' ':      # Check down-right
            winner = board[0]
        elif board[2] == board[4] == board[6] and board[2] != ' ':      # Check down-left
            winner = board[2]

    if winner == '' and not ' ' in board:
        winner = 'Nobody'
    return winner

# Generate a number to define the unique state of the board
# If we operate on the principle of base 3 mathematics, we can get a base 3 number and still use
# it in base 10, since it will always be unique for unique board states
# 0: ' '; 1: 'X'; 2: 'O'
def hashBoard(board=board):
    logging.info('hashBoard()')
    hash = 0
    for i in range(9):
        hash *= 3
        if board[i] == 'X':
            hash += 1
        elif board[i] == 'O':
            hash += 2
            logging.debug('hash result: {}'.format(hash))
    return hash

def unHashBoard(hash):
    logging.info('unHashBoard()')
    board = []
    types = [' ', 'X', 'O']
    remaining = hash
    for i in range(9):
        last = remaining % 3
        logging.debug('remaining: {} last: {}'.format(remaining, last))
        board.insert(0, types[last])
        remaining = remaining // 3
    return board

# My sad attempt at making a minimax AI... not tested and guaranteed not to work
class minimaxAI():
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

class menaceAI():
    def __init__(self, matchboxPath, player):
        self.matchboxPath = matchboxPath
        self.player = player
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

    def getMove(self):
        hash = hashBoard()
        matchbox = self.matchboxes[hash]
        spot = random.choice(matchbox)
        self.movesThisGame.append((hash, spot))

        print('Move for {} (menace): {}'.format(self.player, spot))
        return spot

    def eliminateLastMove(self):
        hash, spot = self.movesThisGame[-1]
        del self.movesThisGame[-1]
        self.matchboxes[hash] = [i for i in self.matchboxes[hash] if i != spot]
        logging.debug('pruned board for {} to {}'.format(hash, self.matchboxes[hash]))

    def tune(self, winner):
        for hash, spot in self.movesThisGame:
            if winner == 'Nobody':
                logging.debug('Adding 1 instance of {} to {} (menace {})'.format(spot, hash, self.player))
                self.matchboxes[hash].append(spot)
            elif winner == self.player:
                logging.debug('Adding 3 instances of {} to {} (menace {})'.format(spot, hash, self.player))
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)
                self.matchboxes[hash].append(spot)
            else:
                logging.debug('Removing 1 instance of {} from {} (menace {})'.format(spot, hash, self.player))
                self.matchboxes[hash].remove(spot)
        self.saveMatchboxes()

def main(args):
    logging.info('main()')
    players = {'X': args.x[0], 'O': args.o[0]}
    currentPlayer = 'X'
    winner = ''
    aiPlayers = {}
    gameID = 0

    if not os.path.exists('stats.ttt'):
        with open('stats.ttt', 'w'):
            pass
    with open('stats.ttt', 'r') as statsFile:
        for line in statsFile:
            id = int(line[:-1].split()[1][0:-1])
            if id >= gameID:
                gameID += 1
    logging.debug('gameID is {}'.format(gameID))

    if 'menace' in players['X']:
        aiPlayers['X'] = menaceAI('{}.mnc'.format(players['X']), 'X')
        logging.debug('Player X is {}'.format(players['X']))
    if 'menace' in players['O']:
        aiPlayers['O'] = menaceAI('{}.mnc'.format(players['O']), 'O')
        logging.debug('Player O is {}'.format(players['O']))

    while winner == '':
        logging.info("Player {}'s turn".format(currentPlayer))
        print('')
        print('{} vs {}'.format(players['X'], players['O']))
        printBoard()
        print('\n')

        success = False
        while not success:
            if currentPlayer in aiPlayers.keys():
                time.sleep(args.d)
                logging.debug('Getting AI move for {} ({})'.format(currentPlayer, players[currentPlayer]))
                success = move(currentPlayer, aiPlayers[currentPlayer].getMove())
                if not success:
                    logging.debug('Pruning move from AI')
                    aiPlayers[currentPlayer].eliminateLastMove()    # For this state, that was not a valid move
            else:
                success = move(currentPlayer, getMove(currentPlayer))

        # hash = hashBoard()
        # unHashedBoard = unHashBoard(hash)
        winner = checkWon()

        # logging.debug('hash is {}'.format(repr(hash)))
        # logging.debug('hash returns {}'.format(repr(unHashedBoard)))
        logging.debug('winner is {}'.format(repr(winner)))

        if winner != '':
            print('Winner is {}!'.format(winner))
            print('')
            printBoard()
            print('\n')

            with open('stats.ttt', 'a') as statsFile:
                statsFile.write('game {}: {} vs {} - {} won\n'.format(gameID, players['X'], players['O'], players[winner] if winner != 'Nobody' else 'Nobody'))

            for aiPlayer in aiPlayers.values():
                aiPlayer.tune(winner)

        if currentPlayer == 'X':
            currentPlayer = 'O'
        else:
            currentPlayer = 'X'

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='tictactoe.log',
        filemode='w'
    )

    args = getArgs()
    main(args)
