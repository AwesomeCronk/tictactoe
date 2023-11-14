import copy, logging, os, random, argparse, time

from playerInterfaces import getInterfacefromName


board = [' '] * 9

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'x',
        type=str,
        help='set player X'
    )
    parser.add_argument(
        'o',
        type=str,
        help='set player O'
    )
    parser.add_argument(
        '-d',
        '--delay',
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

def main(args):
    logging.info('main()')

    playerNames = {'X': args.x, 'O': args.o}
    players = {}
    currentPlayer = 'X'
    winner = ''
    aiPlayers = {}
    gameID = 0

    # Generate game ID and statistics file
    if not os.path.exists('stats.ttt'):
        with open('stats.ttt', 'w'):
            pass
    with open('stats.ttt', 'r') as statsFile:
        for line in statsFile:
            id = int(line[:-1].split()[1][0:-1])
            if id >= gameID:
                gameID += 1
    logging.debug('gameID is {}'.format(gameID))

    # Set up player interfaces
    for player in ('X', 'O'):
        interface = getInterfacefromName(playerNames[player])
        players[player] = interface(player, playerNames[player])

    print('{} vs {}'.format(playerNames['X'], playerNames['O']))

    while winner == '':
        logging.info("{}'s turn\n".format(playerNames[currentPlayer]))
        printBoard()
        print('\n')

        success = False
        while not success:
            success = move(currentPlayer, players[currentPlayer].getMove())
            if not success: players[currentPlayer].eliminateLastMove()    # For this state, that was not a valid move

        winner = checkWon()
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
