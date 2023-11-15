import copy, os, argparse, time

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

def printBoard(board=board):
    for i0 in range(3):
        if i0: print('\n---|---|---          ---|---|---')

        for i1 in range(3):
            if i1: print('|', end='')
            print(' ' + board[(2 - i0) * 3 + i1].replace(' ', str((2 - i0) * 3 + i1)).replace('X', ' ').replace('O', ' '), end = ' ')
        print('          ', end='')

        for i1 in range(3):
            if i1: print('|', end='')
            print(' ' + board[(2 - i0) * 3 + i1], end = ' ')
 
def checkWon(board=board):
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


def main(args):
    playerNames = {'X': args.x, 'O': args.o}
    interfaces = {}
    currentPlayer = 'X'
    winner = ''
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

    # Set up player interfaces
    for player in ('X', 'O'):
        interface = getInterfacefromName(playerNames[player])
        interfaces[player] = interface(player, playerNames[player])

    print('{} vs {}'.format(playerNames['X'], playerNames['O']))

    while winner == '':
        for currentPlayer in ('X', 'O'):
            interface = interfaces[currentPlayer]

            printBoard()
            print('\n')

            # Get the player's move
            moveValid = False
            while not moveValid:
                spot = interface.getMove(board)
                if 0 <= spot <= 8:
                    moveValid = board[spot] == ' '
                if not moveValid:
                    interface.eliminateLastMove()

            # Adjust the board, call the move handler
            board[spot] = currentPlayer
            interface.move(spot)

            # Check for a winner
            winner = checkWon()
            if winner != '':
                print('{} won!'.format(winner))
                print('')
                printBoard()
                print('\n')

                with open('stats.ttt', 'a') as statsFile:
                    statsFile.write('game {}: {} vs {} - {} won\n'.format(gameID, playerNames['X'], playerNames['O'], playerNames[winner] if winner != 'Nobody' else 'Nobody'))

                break   # Breaks the second loop, then the first loop quits


if __name__ == '__main__':
    args = getArgs()
    main(args)
