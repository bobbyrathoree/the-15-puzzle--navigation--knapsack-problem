#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: [PLEASE PUT YOUR NAMES AND USER IDS HERE]
#
# Based on skeleton code by D. Crandall, September 2019
#
from queue import PriorityQueue
import sys

MOVES = {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}


def rowcol2ind(row, col):
    return row * 4 + col


def ind2rowcol(ind):
    return int(ind / 4), ind % 4


def valid_index(row, col):
    return 0 <= row <= 3 and 0 <= col <= 3


def swap_ind(list, ind1, ind2):
    return (
        list[0:ind1]
        + (list[ind2],)
        + list[ind1 + 1 : ind2]
        + (list[ind1],)
        + list[ind2 + 1 :]
    )


def swap_tiles(state, row1, col1, row2, col2):
    return swap_ind(state, *(sorted((rowcol2ind(row1, col1), rowcol2ind(row2, col2)))))


def printable_board(row):
    return ["%3d %3d %3d %3d" % (row[j : (j + 4)]) for j in range(0, 16, 4)]


# return a list of possible successor states
def successors(state):
    (empty_row, empty_col) = ind2rowcol(state.index(0))
    return [
        (swap_tiles(state, empty_row, empty_col, empty_row + i, empty_col + j), c)
        for (c, (i, j)) in MOVES.items()
        if valid_index(empty_row + i, empty_col + j)
    ]


# check if we've reached the goal
def is_goal(state):
    return sorted(state[:-1]) == list(state[:-1]) and state[-1] == 0


# The solver! - using BFS right now
def solve(initial_board):
    fringe = [(initial_board, "")]
    while len(fringe) > 0:
        (state, route_so_far) = fringe.pop()
        for (succ, move) in successors(state):
            if is_goal(succ):
                return route_so_far + move
            fringe.insert(0, (succ, route_so_far + move))
    return False


# test cases
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise (Exception("Error: expected 2 arguments"))

    start_state = []
    with open(sys.argv[1], "r") as file:
        for line in file:
            start_state += [int(i) for i in line.split()]

    if sys.argv[2] != "original":
        raise (
            Exception(
                "Error: only 'original' puzzle currently supported -- you need to implement the other two!"
            )
        )

    if len(start_state) != 16:
        raise (Exception("Error: couldn't parse start state file"))

    print("Start state: \n" + "\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    route = solve(tuple(start_state))

    print("Solution found in " + str(len(route)) + " moves:" + "\n" + route)
