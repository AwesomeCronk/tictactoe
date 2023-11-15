def hashBoard(board):
    hash = 0
    for i in range(9):
        hash *= 3
        if board[i] == 'X':
            hash += 1
        elif board[i] == 'O':
            hash += 2
    return hash

def unhashBoard(hash):
    board = []
    types = [' ', 'X', 'O']
    remaining = hash
    for i in range(9):
        last = remaining % 3
        board.insert(0, types[last])
        remaining = remaining // 3
    return board
