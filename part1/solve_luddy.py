#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: Bobby Rathore (brathore), James Mochizuki-Freeman (jmochizu), Dan Li (dli1)
#
# Based on skeleton code by D. Crandall, September 2019
#
import heapq
import sys
import time

HEURISTIC = None
GOAL_BOARD = None
SIZE = 4

_CHESS_CORNER = ((0, 3, 2, 5), (3, 4, 1, 2), (2, 1, 4, 3), (5, 2, 3, 2))
_CHESS_MID_EDGES = ((3, 0, 3, 2), (2, 3, 2, 1), (1, 2, 1, 4), (2, 3, 2, 3))
_CHESS_MID_EDGES_T = tuple(zip(*_CHESS_MID_EDGES))
_CHESS_MID_4 = ((4, 3, 2, 1), (3, 0, 3, 2), (2, 3, 2, 1), (1, 2, 1, 4))

_CHESS_COSTS_LISTS = {
    (0, 0): _CHESS_CORNER,
    (1, 0): _CHESS_MID_EDGES,
    (2, 0): [row[::-1] for row in _CHESS_MID_EDGES],
    (3, 0): [row[::-1] for row in _CHESS_CORNER],
    (0, 1): _CHESS_MID_EDGES_T,
    (1, 1): _CHESS_MID_4,
    (2, 1): [row[::-1] for row in _CHESS_MID_4],
    (3, 1): [row[::-1] for row in _CHESS_MID_EDGES_T],
    (0, 2): _CHESS_MID_EDGES_T[::-1],
    (1, 2): _CHESS_MID_4[::-1],
    (2, 2): [row[::-1] for row in _CHESS_MID_4][::-1],
    (3, 2): [row[::-1] for row in _CHESS_MID_EDGES_T][::-1],
    (0, 3): _CHESS_CORNER[::-1],
    (1, 3): _CHESS_MID_EDGES[::-1],
    (2, 3): [row[::-1] for row in _CHESS_MID_EDGES][::-1],
    (3, 3): [row[::-1] for row in _CHESS_CORNER][::-1],
}

CHESS_COSTS = dict()
for key, val in _CHESS_COSTS_LISTS.items():
    CHESS_COSTS[key] = dict()
    for y, row in enumerate(val):
        for x, item in enumerate(row):
            CHESS_COSTS[key][(x, y)] = item


def quantify_list_to_dict(board_blocks_list: list) -> dict:
    """
    Converts a 2D list of integers into a dictionary.
    :param board_blocks_list: A 2D list
    :return: Converted dictionary with coordinates of numbers
    """
    dictionary = dict()

    for row in range(len(board_blocks_list)):
        for col in range(len(board_blocks_list[0])):
            dictionary[board_blocks_list[row][col]] = (row, col)

    return dictionary


def swap_location(target: dict, new_location_of_zero: tuple):
    """
    A function to swap the location of zero and some other number
    :param target: the PuzzleBoard instance dictionary
    :param new_location_of_zero: coordinates of the intended location of zero
    """
    # Get number at target coordinates
    number = next(num for num, loc in target.items() if loc == new_location_of_zero)
    # Swap
    target[0], target[number] = target[number], target[0]


class PuzzleBoard:
    __slots__ = (
        "board_blocks",
        "valid",
        "path",
        "parent",
        "g_cost",
        "h_cost",
        "f_cost",
    )

    def __init__(self, board_blocks, path, parent, is_goal=False):
        """
        Constructor. Takes a dictionary of integer-tuple pairs that describe block positions.
        Alternatively, takes a 2D list array that is then converted to dict.
        :param board_blocks: can be either a list of a dict of a PuzzleBoard instance
        """
        if isinstance(board_blocks, list):
            self.board_blocks = quantify_list_to_dict(board_blocks)
        else:
            self.board_blocks = board_blocks
        self.valid = True
        self.path = path
        self.parent = parent
        self.g_cost = len(path)
        if is_goal:
            self.h_cost = 0
        else:
            self.h_cost = (
                self._estimate_chess_horse_dist(GOAL_BOARD)
                if HEURISTIC == "luddy"
                else self._calculate_manhattan_circular(GOAL_BOARD)
                if HEURISTIC == "circular"
                else self._calculate_manhattan_distance(GOAL_BOARD)
            )
        self.f_cost = self.g_cost + self.h_cost

    def __eq__(self, other: object) -> bool:
        """
        Equals function. Returns whether block dictionaries are equal.
        :param other: origin object
        :return: a bool indicating whether a PuzzleBoard instance
                 is the same as its origin
        """
        if not other:
            return False
        return self.board_blocks == other.board_blocks

    def __lt__(self, other: "PuzzleBoard") -> bool:
        """
        Less-than function. Compares stgptn-scores.
        :param other: origin object
        :return: a bool indicating whether new object's
                 stgptn-score is lower than its origin's
        """
        if not other:
            return False
        return self.f_cost < other.f_cost

    def __hash__(self):
        """
        Hash function. Hashes a frozenset of the blocks.
        :return: frozenset of PuzzleBoard instance
        """
        return hash(frozenset(self.board_blocks.items()))

    def to_string(self):
        """
        Returns the state in an easy-to-read fashion.
        :return: stringified PuzzleBoard instance
        """
        array = []
        for x in range(SIZE):
            # print("y:",y)
            row = []
            for y in range(SIZE):
                # print("x:",x)
                for block in self.board_blocks.items():
                    # print(block)
                    if block[1] == (x, y):
                        row.append(block[0])
                        break
            array.append(row)

        string = "\n".join("\t".join("%i" % x for x in y) for y in array)
        return string

    def _calculate_manhattan_distance(self, other: "PuzzleBoard") -> int:
        """
        Our go-to heuristic: manhattan distance, taking the sum of absolute differences
        :param other: the puzzle board instance to calculate manhattan distance from
        :return: the estimated distance
        """
        return sum(
            abs(other.board_blocks[i][0] - self.board_blocks[i][0])
            + abs(other.board_blocks[i][1] - self.board_blocks[i][1])
            for i in range(1, len(self.board_blocks))
        )

    def _calculate_manhattan_circular(self, other: "PuzzleBoard") -> int:
        """
        Regular manhattan distance with adjustments for circular tile movements
        :param other: Goal PuzzleBoard instance
        :return: the estimated distance
        """
        estimate = 0
        for i in range(1, len(self.board_blocks)):
            x = abs(self.board_blocks[i][0] - other.board_blocks[i][0])
            estimate += 4 - x if x > 2 else x
            y = abs(self.board_blocks[i][1] - other.board_blocks[i][1])
            estimate += 4 - y if y > 2 else y
        return estimate

    def _estimate_chess_horse_dist(self, other: "PuzzleBoard") -> int:
        """
        Function to return sum of L-shaped moves' distances across the PuzzleBoard
        :param other:
        :return: estimated distance
        """
        return sum(
            CHESS_COSTS[self.board_blocks[i]][other.board_blocks[i]]
            for i in range(1, len(self.board_blocks))
        )

    def get_successors(self) -> list:
        """
        Function to get all successors of a puzzle board instance,
        depending on the configuration: cirular or luddy (original is ON by default)
        :return: list of possible successors
        """
        successors = list()
        moves = (
            {
                "A": (-2, -1),
                "B": (-2, 1),
                "C": (2, -1),
                "D": (2, 1),
                "E": (-1, -2),
                "F": (-1, 2),
                "G": (1, -2),
                "H": (1, 2),
            }
            if HEURISTIC == "luddy"
            else {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}
        )

        location_of_zero = self.board_blocks[0]

        for direction, move in moves.items():
            # swap 0 and whatever
            new_board_blocks = self.board_blocks.copy()
            new_location_of_zero = (
                location_of_zero[0] + move[0],
                location_of_zero[1] + move[1],
            )

            if HEURISTIC == "circular":
                # We're allowing circular, move back onto board
                new_location_of_zero = (
                    new_location_of_zero[0] % SIZE,
                    new_location_of_zero[1] % SIZE,
                )

            # skip this state if we've moved off the board
            if (
                new_location_of_zero[0] < 0
                or new_location_of_zero[1] < 0
                or new_location_of_zero[0] > SIZE - 1
                or new_location_of_zero[1] > SIZE - 1
            ):
                continue

            # if not circular:
            swap_location(
                target=new_board_blocks, new_location_of_zero=new_location_of_zero
            )

            neighbor = PuzzleBoard(new_board_blocks, self.path + direction, self)
            successors.append(neighbor)

        return successors

    def invalidate(self):
        self.valid = False


def solve(initial_board: PuzzleBoard, goal_board: PuzzleBoard):
    """
    Function where the magic happens
    :param initial_board: Start instance
    :param goal_board: Goal instance
    :return: list of path taken or False if solution not found
    """
    # The dictionary of states already evaluated
    evaluated_states = dict()

    # The heap of currently discovered state that are not evaluated yet.
    # Obviously, only the start state is known initially.
    fringe = [initial_board]

    # Contains only valid fringe states, for fast membership tests
    fringe_map = {initial_board: initial_board}

    # While there are yet nodes to inspect,
    while len(fringe) > 0:
        current = heapq.heappop(fringe)  # Pop the lowest f-cost state off.

        if not current.valid:
            continue  # Skip if invalid

        del fringe_map[current]
        # If we've reached the goal:
        if current == goal_board:
            # return the list of states it took to get there.
            state_path = [current]
            step = current

            while step.parent:
                state_path.append(step.parent)
                step = step.parent

            state_path.reverse()
            return state_path

        # make sure we won't visit this state again.
        evaluated_states[current] = True

        # For each possible neighbor of our current state,
        for neighbor in current.get_successors():
            # Skip it if it's already been evaluated
            if neighbor in evaluated_states:
                continue

            if neighbor in fringe_map:
                # Find matching board state in fringe
                match = fringe_map[neighbor]
                if neighbor.g_cost < match.g_cost:
                    # Found a better path, remove old entry from fringe
                    match.invalidate()
                    del fringe_map[neighbor]

            if neighbor not in fringe_map:
                # Add it to our open heap
                heapq.heappush(fringe, neighbor)
                fringe_map[neighbor] = neighbor
    return False


def is_solvable(puzzle_board: list) -> bool:
    """
    Checks whether a puzzle grid is odd or even and if it solvable depending on
    the number of inversions as explained here:
    https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html

    :param puzzle_board: the puzzle board as a 1D list
    :return: a flag indicating whether the puzzle board instance is solvable
    """
    import math

    parity = 0
    width = math.sqrt(len(puzzle_board))
    row = 0
    row_with_zero = 0

    for i in range(len(puzzle_board)):
        if i % width == 0:  # Go to next row
            row += 1
        if puzzle_board[i] == 0:
            row_with_zero = row  # We found the row with zero
            continue
        for j in range(i + 1, len(puzzle_board)):
            if int(puzzle_board[i]) > int(puzzle_board[j]) and (
                int(puzzle_board[j]) != 0
            ):
                parity += 1

    return (
        (parity % 2 == 0 if row_with_zero % 2 == 0 else parity % 2 != 0)
        if width % 2 == 0  # even grid
        else parity % 2 == 0  # odd grid
    )


def two_d_to_one_d(arr: list) -> list:
    """
    A basic function to return a 2D list as a 1D
    :param arr: 2D list
    :return: 1D list, with rows attached
    """
    return [col for row in arr for col in row]


# Main event
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise (Exception("Error: expected 2 arguments"))

    if sys.argv[2] not in ["original", "circular", "luddy"]:
        raise (Exception("Error: only 'original', 'circular', and 'luddy' allowed"))

    HEURISTIC = sys.argv[2]

    with open(sys.argv[1], "r") as file:
        start_state = []
        for line in file:
            start_state += [[int(i) for i in line.split()]]

    # start_state = [
    #     [1, 2, 3, 4],
    #     [5, 0, 6, 7],
    #     [9, 10, 11, 8],
    #     [13, 14, 15, 12],
    # ]  # board 4
    # start_state = [
    #     [0, 2, 3, 4],
    #     [1, 5, 6, 7],
    #     [9, 10, 11, 8],
    #     [13, 14, 15, 12],
    # ]  # board 6
    # start_state = [
    #     [2, 5, 3, 4],
    #     [0, 10, 6, 7],
    #     [1, 9, 11, 8],
    #     [13, 14, 15, 12],
    # ]  # board 6 enhanced
    # start_state = [
    #     [1, 2, 3, 11],
    #     [12, 4, 9, 8],
    #     [15, 10, 5, 6],
    #     [13, 14, 0, 7],
    # ]  # To test chess-horse
    # start_state = [
    #     [15, 2, 1, 12],
    #     [8, 5, 6, 11],
    #     [4, 9, 10, 7],
    #     [3, 14, 13, 0],
    # ]  # board n
    # start_state = [
    #     [1, 2, 3, 0],
    #     [5, 6, 7, 8],
    #     [9, 10, 11, 12],
    #     [13, 14, 15, 4],
    # ]  # To test circular 1
    # start_state = [
    #     [0, 2, 3, 1],
    #     [5, 6, 7, 8],
    #     [9, 10, 11, 12],
    #     [13, 14, 15, 4],
    # ]  # To test circular 2

    goal_state = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 0],
    ]  # the requested goal state

    goal = PuzzleBoard(goal_state, "", None, True)
    GOAL_BOARD = goal
    start = PuzzleBoard(start_state, "", None)

    print("Solving...")

    if not is_solvable(puzzle_board=two_d_to_one_d(start_state)):
        print("Inf")

    else:
        tick = time.time()
        # the main thing
        states = solve(start, goal)

        # Found the solution, let's print the original puzzle first
        print("Original Board: \n{0}".format(states[0].to_string()))

        # Now the following intermediate steps
        for state in states[1:]:
            print("\t |\n\t |\n\t |\n\t\\./")
            print(state.to_string())

        print("\nTime taken: {0}s".format(round((time.time() - tick), 4)))
        print("Path taken: \n{0}".format(states[-1].path))
