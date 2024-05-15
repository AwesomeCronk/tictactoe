import copy


def hashBoard(board: list):
    hash = 0
    for i in range(9):
        hash *= 3
        if board[8 - i] == 'X':
            hash += 1
        elif board[8 - i] == 'O':
            hash += 2
    return hash

def unhashBoard(hash: int):
    board = []
    symbols = [' ', 'X', 'O']
    remaining = hash
    for i in range(9):
        last = remaining % 3
        board.append(symbols[last])
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

# Flips the board (0 = horizontal, 1 = vertical)
def flipBoard(board: list, direction: int):
    if direction:
        return transformBoard(board, [6, 7, 8, 3, 4, 5, 0, 1, 2])
    else:
        return transformBoard(board, [2, 1, 0, 5, 4, 3, 8, 7, 6])

# Recursively finds the best alternative hash to a given hash. Returns the same if none better found.
def getBestAltHash(hash):
    # print('Finding best alt hash for {}'.format(hash))

    board = unhashBoard(hash)
    altHashes = []
    transformations = [
        (rotateBoard, 1),
        (rotateBoard, 2),
        (rotateBoard, 3),
        (flipBoard, 0),
        (flipBoard, 1)
    ]

    for transformer, parameter in transformations:
        altHash = hashBoard(transformer(board, parameter))
        altHashes.append(altHash)

    # print('altHashes:', altHashes)

    if len(altHashes):
        bestAltHash = min(altHashes)
        bestAltHashIndex = altHashes.index(bestAltHash)
        transformations = [transformations[bestAltHashIndex],]  # Keep the transformation that produced bestAltHash, ditch the rest
    else:
        bestAltHash = hash
        bestAltHashIndex = -1
        transformations = []    # Didn't transform it, don't return any transformations

    # print('Best alt hash is', bestAltHash)
    # print('Found {} via {}, transformation {}'.format(bestAltHash, transformations, bestAltHashIndex))

    # Only one "layer" of transformations has been checked. If we actually found an alternative we
    # need to heck for alternatives to the alternative
    if bestAltHash < hash:
        altAltHash, altTransformations = getBestAltHash(bestAltHash)
        if altAltHash < bestAltHash:
            bestAltHash = altAltHash
            transformations += altTransformations

    return bestAltHash, transformations

def reverseTransformations(transformations: list):
    newTransformations = copy.copy(transformations)
    for t, transformation in enumerate(newTransformations):
        transformer, parameter = transformation
        # If it's a rotation, figure the way to undo the rotation
        if transformer is rotateBoard:
            newTransformations[t] = (transformer, (4 - parameter) % 4)
        # The way to undo a flip is the same flip

    # Finally, transformations must be undone in reverse
    newTransformations.reverse()
    return newTransformations

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

# Checks if a hash represents a board in a valid game state
# Not used during games, only in auxillary programs
def hashIsValidGameState(hash):
    board = unhashBoard(hash)

    # Can a game reach this state at all?
    if board.count('X') > board.count('O') + 1:
        return False

    # Would the game be won by now?
    elif checkWinner(board) in ('X', 'O'):
        return False

    else:
        return True

