import copy, os, argparse, time

from utils import printBoard, checkWinner
from playerInterfaces import getInterfacefromName


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
        '-c',
        '--count',
        type=int,
        default=1,
        help='Number of games to play'
    )
    return parser.parse_args()

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
    board = [' '] * 9

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

            printBoard(board, end='\n\n')

            # Get the player's move
            moveValid = False
            for i in range(20):
                spot = interface.getMove(board)
                if 0 <= spot <= 8:
                    moveValid = board[spot] == ' '
                if not moveValid:
                    interface.eliminateLastMove()
                else:
                    break
            else:   # nobreak
                print('Failed to get valid move, aborting game')

            # Adjust the board, call the move handler
            board[spot] = currentPlayer
            interface.move(spot)

            # Check for a winner
            winner = checkWinner(board)
            if winner != '':
                print('{} won!'.format(winner))
                print('')
                printBoard(board, end='\n\n')

                for currentPlayer in ('X', 'O'):
                    interfaces[currentPlayer].postGame(winner)

                with open('stats.ttt', 'a') as statsFile:
                    statsFile.write('game {}: {} vs {} - {} won\n'.format(gameID, playerNames['X'], playerNames['O'], playerNames[winner] if winner != 'Nobody' else 'Nobody'))

                break   # Breaks the second loop, then the first loop quits


if __name__ == '__main__':
    args = getArgs()
    assert args.count > 0
    for c in range(args.count):
        main(args)
