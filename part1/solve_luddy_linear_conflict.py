#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: [PLEASE PUT YOUR NAMES AND USER IDS HERE]
#
# Based on skeleton code by D. Crandall, September 2019
#
import math
import heapq
import collections
import copy
import sys
import collections
from datetime import datetime

startTime = datetime.now()

MOVES = {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}

# For each node, the total cost of getting from the start node to the goal
# by passing by that node. That value is partly known, partly heuristic.
# stgptn: start to goal passing that node
stgptn_score = collections.defaultdict(lambda: float("inf"))


# def calculate_manhattan_distance(puzz):
#     distance = 0
#     m = eval(puzz)
#     # print(m, puzz, type(m), type(puzz))
#     for i in range(4):
#         for j in range(4):
#             if m[i][j] == 0:
#                 continue
#             distance += abs(i - (m[i][j] / 4)) + abs(j - (m[i][j] % 4))
#     # print("distance: ", distance, "\n\n")
#     return distance


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
# def successors(state):
#     print(type(state), state)
#     (empty_row, empty_col) = ind2rowcol(state.index(0))
#     return [
#         (swap_tiles(state, empty_row, empty_col, empty_row + i, empty_col + j), c)
#         for (c, (i, j)) in MOVES.items()
#         if valid_index(empty_row + i, empty_col + j)
#     ]


# check if we've reached the goal
# def is_goal(state):
#     return sorted(state[:-1]) == list(state[:-1]) and state[-1] == 0


# def heuristic_estimate_manhattan(m):
#     distance = 0
#
#     for i in range(4):
#         for j in range(4):
#             if m[i][j] == 0:
#                 continue
#             distance += abs(i - (m[i][j] / 4)) + abs(j - (m[i][j] % 4))
#
#     return distance


# The solver! - using BFS right now
# def solve_bfs(initial_board):
#     fringe = [(initial_board, "")]
#     expanded_nodes_list = set()
#     expanded_nodes_ctr = 0
#     while len(fringe) > 0:
#         (state, route_so_far) = fringe.pop()
#         for (succ, move) in successors(state):
#             if is_goal(succ):
#                 return route_so_far + move
#             if str(succ) in expanded_nodes_list:
#                 continue
#             expanded_nodes_list.add(str(succ))
#             fringe.insert(0, (succ, route_so_far + move))
#         expanded_nodes_ctr += 1
#     return False


def quantify_list_to_dict(board_blocks_list):
    """
    Converts a 2D list of integers into a dictionary.
    """
    dictionary = dict()

    for row in range(len(board_blocks_list)):
        for col in range(len(board_blocks_list[0])):
            dictionary[board_blocks_list[row][col]] = (col, row)

    return dictionary


def swap_location(
    target: dict, new_location_of_zero: tuple, original_location_of_zero: tuple
):
    # Move the zero
    target[0] = new_location_of_zero

    # Move the other element that was replaced back to zero's original position
    target[
        [
            number
            for number, location in target.items()
            if number != 0 and location == new_location_of_zero
        ][0]
    ] = original_location_of_zero


class PuzzleBoard:
    def __init__(self, board_blocks, path_taken_until_now):
        """
        Constructor. Takes a dictionary of integer-tuple pairs that describe block positions.
        Alternatively, takes a 2D list array that is then converted to dict.
        """
        if isinstance(board_blocks, list):
            self.board_blocks = quantify_list_to_dict(board_blocks)
        else:
            self.board_blocks = board_blocks
        self.width = self.__get_width__()
        self.height = int(len(self.board_blocks) / self.width)
        self.path_taken_until_now = path_taken_until_now

    def __eq__(self, other):
        """
        Equals function. Returns whether block dictionaries are equal.
        """
        if other == None:
            return False
        return self.board_blocks == other.board_blocks

    def __lt__(self, other):
        """
        Less-than function. Compares f-scores.
        """
        if other == None:
            return False
        return stgptn_score[self] < stgptn_score[other]

    def __hash__(self):
        """
        Hash function. Hashes a frozenset of the blocks.
        """
        return hash(frozenset(self.board_blocks.items()))

    def __get_width__(self):
        """
        Returns the width of this puzzle.
        """
        max_width = 0
        for value in self.board_blocks.values():
            max_width = max(value[0], max_width)

        return max_width + 1

    def to_string(self):
        """
        Returns the state in an easy-to-read fashion.
        """
        array = []
        for y in range(self.height):
            # print("y:",y)
            row = []
            for x in range(self.width):
                # print("x:",x)
                for block in self.board_blocks.items():
                    # print(block)
                    if block[1] == (x, y):
                        row.append(block[0])
                        break
            array.append(row)

        string = "\n".join("\t".join("%i" % x for x in y) for y in array)
        return string

    def calculate_manhattan_distance(self, other):
        """
        Finds the heuristic estimation of the cost to reach another state from this one.
        This heuristic is based on "manhattan distance."
        """
        estimate = 0
        # print(self.blocks, "blocks\n")
        for index in range(len(self.board_blocks)):
            # print("index is:", index)
            # print("the goal tile is at position:", other.board_blocks[index],
            # "and the current tile is at position:", self.board_blocks[index])
            estimate += abs(
                other.board_blocks[index][0]
                - self.board_blocks[index][0]  # the distances in column
            ) + abs(
                other.board_blocks[index][1] - self.board_blocks[index][1]
            )  # the distances in rows

            #  Linear-conflict heuristic: when two tiles are in their goal column or row,
            #  but are reverse to their goal position, add two moves to the Manhattan distance
            if (
                other.board_blocks[index][0] - self.board_blocks[index][0] == 0
            ):  # if the index tile is in the goal column, check other tiles
                for jndex in range(index, len(self.board_blocks)):
                    # print("jndex is:", jndex)
                    if (
                        other.board_blocks[jndex][0] - self.board_blocks[jndex][0] == 0
                        and self.board_blocks[jndex][0] == self.board_blocks[index][0]
                    ):  # if jndex is in the goal column and that's same with the index tile
                        row_distance_between_goals = (
                            other.board_blocks[jndex][1] - other.board_blocks[index][1]
                        )
                        row_distance_between_tiles = (
                            self.board_blocks[jndex][1] - self.board_blocks[index][1]
                        )
                        if (
                            row_distance_between_goals * row_distance_between_tiles < 0
                        ):  # if the index tiles and jndex tile are in reverse order
                            # relative to their goal position, add 2 to the heuristics
                            estimate += 2

        # for i in range(4):
        #     for j in range(4):
        #         if m[i][j] == 0:
        #             continue
        #         estimate += abs(i - (m[i][j] / 4)) + abs(j - (m[i][j] % 4))

        return estimate

    def get_successors(self, former):
        successors = list()
        circular = False  # make this True to check circular for now

        moves = {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}
        location_of_zero = self.board_blocks[0]

        for direction, move in moves.items():
            # swap 0 and whatever
            new_board_blocks = copy.deepcopy(self.board_blocks)
            new_location_of_zero = (
                location_of_zero[0] + move[0],
                location_of_zero[1] + move[1],
            )

            if circular:
                # We're allowing circular
                if new_location_of_zero[0] < 0:  # on the first row
                    new_location_of_zero = (
                        new_location_of_zero[0] + self.height,
                        new_location_of_zero[1],
                    )
                elif new_location_of_zero[1] < 0:
                    new_location_of_zero = (
                        new_location_of_zero[0],
                        new_location_of_zero[1] + self.width,
                    )
                elif new_location_of_zero[0] > (self.width - 1):
                    new_location_of_zero = (
                        new_location_of_zero[0] - self.height,
                        new_location_of_zero[1],
                    )
                elif new_location_of_zero[1] > (self.height - 1):
                    new_location_of_zero = (
                        new_location_of_zero[0],
                        new_location_of_zero[1] - self.width,
                    )

            # skip this state if we've moved off the board
            if (
                any(
                    [
                        new_location_of_zero[0] < 0,
                        new_location_of_zero[1] < 0,
                        new_location_of_zero[0] > self.width - 1,
                        new_location_of_zero[1] > self.height - 1,
                    ]
                )
                and not circular
            ):
                # print("We're moving outside the bounds of board.")
                continue

            # skip this state if it's the same as the previous
            if former and former.board_blocks[0] == new_location_of_zero:
                # print("this is just the same!")
                continue

            # if not circular:
            swap_location(
                target=new_board_blocks,
                new_location_of_zero=new_location_of_zero,
                original_location_of_zero=location_of_zero,
            )

            # print(new_board_blocks, "new board blocks\n")
            neighbor = PuzzleBoard(
                new_board_blocks,
                former.path_taken_until_now + direction if former else direction,
            )
            successors.append(neighbor)
        # print(len(successors), "len")
        return successors


def solve(initial_board, goal_board):
    # The dictionary of states already evaluated
    evaluated_states = dict()

    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many start, origin will eventually contain the
    # most efficient previous step.
    origin = dict()

    # For each node, the cost of getting from the start node to that node.
    sttn_score = collections.defaultdict(
        lambda: float("inf")
    )  # sttn: start to that node

    # The cost of going from start to start is zero.
    sttn_score[initial_board] = 0

    # The heap of currently discovered state that are not evaluated yet.
    # Obviously, only the start state is known initially.
    fringe = [initial_board]
    heapq.heapify(fringe)

    # For the first node, that value is completely heuristic.
    stgptn_score[initial_board] = initial_board.calculate_manhattan_distance(goal_board)

    # While there are yet nodes to inspect,
    i = 0
    while len(fringe) > 0:

        # Pop the lowest f-score state off.
        current = heapq.heappop(fringe)
        print(current)
        i += 1
        print("moving..........", i)
        print("length of the fringe is:", len(fringe))
        if i > 100000:
            print(datetime.now() - startTime)

        # If we've reached the goal:
        if current == goal_board:
            # return the list of states it took to get there.
            path = [current]
            step = current
            actual_path = list()
            # print(step.to_string(), "step")
            while origin.get(step):
                actual_path.append(step.path_taken_until_now)
                path.append(origin[step])
                step = origin[step]
            path.reverse()
            actual_path.reverse()
            print(actual_path, "actual path")
            return path

        # make sure we won't visit this state again.
        evaluated_states[current] = True

        # For each possible neighbor of our current state,
        for neighbor in current.get_successors(origin.get(current)):

            # Skip it if it's already been evaluated
            if neighbor in evaluated_states:
                continue

            # Add it to our open heap
            heapq.heappush(fringe, neighbor)

            tentative_g_score = sttn_score[current] + 1

            # If it takes more to get here than another path to this state, skip it.
            if tentative_g_score >= sttn_score[neighbor]:
                continue

            # If we got to this point, add it!
            origin[neighbor] = current
            sttn_score[neighbor] = tentative_g_score
            stgptn_score[neighbor] = sttn_score[
                neighbor
            ] + neighbor.calculate_manhattan_distance(goal_board)

    return False


# test cases
if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     raise (Exception("Error: expected 2 arguments"))
    #
    # start_state = []
    # with open(sys.argv[1], "r") as file:
    #     for line in file:
    #         start_state += [int(i) for i in line.split()]
    #
    # if sys.argv[2] != "original":
    #     raise (
    #         Exception(
    #             "Error: only 'original' puzzle currently supported -- you need to implement the other two!"
    #         )
    #     )
    #
    # if len(start_state) != 16:
    #     raise (Exception("Error: couldn't parse start state file"))
    #
    # print("Start state: \n" + "\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    #
    # start = PuzzleBoard(
    #     [[1, 2, 3, 4], [5, 0, 6, 7], [9, 10, 11, 8], [13, 14, 15, 12]], ""
    # )  # board 4
    # start = PuzzleBoard(
    #     [[0, 2, 3, 4], [1, 5, 6, 7], [9, 10, 11, 8], [13, 14, 15, 12]], ""
    # )  # board 6
    start = PuzzleBoard(
        [[15, 2, 1, 12], [8, 5, 6, 11], [4, 9, 10, 7], [3, 14, 13, 0]], ""
    )  # board n
    # start = PuzzleBoard(
    #     [[1, 2, 3, 0], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 4]], ""
    # )  # To test circular
    goal = PuzzleBoard(
        [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]], ""
    )
    path = solve(start, goal)
    for state in path:
        print(state.to_string())
        print()

    print(datetime.now() - startTime)

    # route = solve(tuple(start_state))

    # print("Solution found in " + str(len(route)) + " moves:" + "\n" + route)
