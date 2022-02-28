from random import random
from functools import partial

def gen_board():
    tiles = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    board = []
    for i in range(16):
        tile = tiles[int(random() * len(tiles))]
        tiles.remove(tile)
        board.append(tile)
    return board

def idx_to_pt(idx):
    return (idx % 4, int(idx / 4))

def pt_to_idx(pt):
    return pt[0] + pt[1] * 4

def randomize(base):
    def up(board):
        pos = board.index(16)
        x, y = idx_to_pt(pos)
        if y < 3 :
            new_pos = pt_to_idx((x, y + 1))
            board[pos], board[new_pos] = board[new_pos], board[pos]
            
    def down(board):
        pos = board.index(16)
        x, y = idx_to_pt(pos)
        if y > 0:
            new_pos = pt_to_idx((x, y - 1))
            board[pos], board[new_pos] = board[new_pos], board[pos]

    def left(board):
        pos = board.index(16)
        x, y = idx_to_pt(pos)
        if x > 0:
            new_pos = pt_to_idx((x - 1, y))
            board[pos], board[new_pos] = board[new_pos], board[pos]

    def right(board):
        pos = board.index(16)
        x, y = idx_to_pt(pos)
        if x < 3:
            new_pos = pt_to_idx((x+1, y))
            board[pos], board[new_pos] = board[new_pos], board[pos]
    
    moves = [up, down, left, right]
    for _ in range(1000):
        move = moves[int(random() * 4)]
        move(base)

    return base

def inversions(board):
    output = 0
    for i in range(len(board)):
        for j in range(i, len(board)):
            if board[j] < board[i]:
                output += 1

    return output

def distance(board):
    board_pos = board.index(16)
    board_x = board_pos % 4
    board_y = int(board_pos / int(4))

    dist = (3 - board_x) + (3 - board_y)
    return dist

def solvable(board):
    dist = distance(board)
    inversion_count = inversions(board)
    print(f"Dist: {dist}")
    print(f"Inversions: {inversion_count}")
    if (inversion_count + dist) % 2 == 0:
        return True

    return False

def test():
    for _ in range(100):
        board = gen_board()
        if not solvable(board):
            idx1 = board.index(14)
            idx2 = board.index(15)
            board[idx1], board[idx2] = board[idx2], board[idx1]

            if not solvable(board):
                print(f"Failed on should-be-solvable {board}")
                for row in range(4):
                    print("{0:>2} {1:>2} {2:>2} {3:>2}".format(board[row*4], board[row*4+1], board[row*4+2], board[row*4+3]))
            else:
                print("Fixed!")


    print("It works")

if __name__ == '__main__':
    test()