import copy


def hashBoard(board: list):
    hash = 0
    for i in range(9):
        hash *= 3
        if board[i] == 'X':
            hash += 1
        elif board[i] == 'O':
            hash += 2
    return hash

def unhashBoard(hash: int):
    board = []
    types = [' ', 'X', 'O']
    remaining = hash
    for i in range(9):
        last = remaining % 3
        board.insert(0, types[last])
        remaining = remaining // 3
    return board

def transformBoard(board, transformMap):
    newBoard = copy.copy(board)
    for i in range(9):
        newBoard[i] = board[transformMap[i]]
    return newBoard

# Rotates the board clockwise <angle> * 90 deg
def rotateBoard(board: list, angle: int):
    assert 0 <= angle <= 3
    transformMaps = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [2, 5, 8, 1, 4, 7, 0, 3, 6],
        [8, 7, 6, 5, 4, 3, 2, 1, 0],
        [6, 3, 0, 7, 4, 1, 8, 5, 2]
    ]
    return transformBoard(board, transformMaps[angle])

# Vertically flips the board
def vflipBoard(board: list):
    return transformBoard(board, [6, 7, 8, 3, 4, 5, 0, 1, 2])

# Horizontally flips the board
def hflipBoard(board: list):
    return transformBoard(board, [2, 1, 0, 5, 4, 3, 8, 7, 6])

# Recursively finds the best alternative hash to a given hash. Returns the same if none better found.
def getBestAltHash(hash):
    board = unhashBoard(hash)
    altHashes = []

    for altHash in [
        hashBoard(rotateBoard(board, 1)),
        hashBoard(rotateBoard(board, 2)),
        hashBoard(rotateBoard(board, 3)),
        hashBoard(vflipBoard(board)),
        hashBoard(hflipBoard(board))
    ]:
        if altHash < hash and not altHash in altHashes: altHashes.append(altHash)

    if len(altHashes):
        bestAltHash = min(altHashes)
    else:
        bestAltHash = hash

    # Only one "layer" of transformations has been checked. If we actually found an alternative we
    # need to heck for alternatives to the alternative
    if bestAltHash < hash:
        bestAltHash = min(bestAltHash, getBestAltHash(bestAltHash))

    return bestAltHash

def printBoard(board: list, end='\n'):
    for i0 in range(3):
        if i0: print('\n---|---|---          ---|---|---')

        for i1 in range(3):
            if i1: print('|', end='')
            print(' ' + board[(2 - i0) * 3 + i1].replace(' ', str((2 - i0) * 3 + i1)).replace('X', ' ').replace('O', ' '), end = ' ')
        print('          ', end='')

        for i1 in range(3):
            if i1: print('|', end='')
            print(' ' + board[(2 - i0) * 3 + i1], end = ' ')

    print('', end=end)
 
def checkWinner(board: list):
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
