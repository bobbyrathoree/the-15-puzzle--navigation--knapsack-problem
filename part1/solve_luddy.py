#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: [PLEASE PUT YOUR NAMES AND USER IDS HERE]
#
# Based on skeleton code by D. Crandall, September 2019
#
import heapq
import copy
import sys
import collections

# For each node, the total cost of getting from the start node to the goal
# by passing by that node. That value is partly known, partly heuristic.
# stgptn: start to goal passing that node
stgptn_score = collections.defaultdict(lambda: float("inf"))


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
    def __init__(self, board_blocks):
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
        estimate = 0
        # print(self.blocks, "blocks\n")
        for index in range(len(self.board_blocks)):
            estimate += abs(
                other.board_blocks[index][0] - self.board_blocks[index][0]
            ) + abs(other.board_blocks[index][1] - self.board_blocks[index][1])

        return estimate

    def get_successors(self, former, circular=False, luddy=False):
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
            if luddy
            else {"R": (0, -1), "L": (0, 1), "D": (-1, 0), "U": (1, 0)}
        )

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

            neighbor = PuzzleBoard(new_board_blocks)

            successors.append(neighbor)
        return successors


def solve(initial_board, goal_board, circular=False, luddy=False):

    # The dictionary of states already evaluated
    evaluated_states = dict()

    # For each node, which node it can most efficiently be reached from.
    # If a node can be reached from many start, origin will eventually contain the
    # most efficient previous step.
    origin = dict()

    # For each node, the cost of getting from the start node to that node.
    # sttn: start to that node
    sttn_score = collections.defaultdict(lambda: float("inf"))

    # The cost of going from start to start is zero.
    sttn_score[initial_board] = 0

    # The heap of currently discovered state that are not evaluated yet.
    # Obviously, only the start state is known initially.
    fringe = [initial_board]
    heapq.heapify(fringe)

    # For the first node, that value is completely heuristic.
    stgptn_score[initial_board] = initial_board.calculate_manhattan_distance(goal_board)

    # While there are yet nodes to inspect,
    while len(fringe) > 0:

        # Pop the lowest stgptn-score state off.
        current = heapq.heappop(fringe)

        # If we've reached the goal:
        if current == goal_board:
            # return the list of states it took to get there.
            state_path = [current]
            step = current

            while origin.get(step):
                state_path.append(origin[step])
                step = origin[step]

            state_path.reverse()
            return state_path

        # make sure we won't visit this state again.
        evaluated_states[current] = True

        # For each possible neighbor of our current state,
        for neighbor in current.get_successors(
            origin.get(current), circular=circular, luddy=luddy
        ):
            # Skip it if it's already been evaluated
            if neighbor in evaluated_states:
                continue

            # Add it to our open heap
            heapq.heappush(fringe, neighbor)

            tentative_sttn_score = sttn_score[current] + 1

            # If it takes more to get here than another path to this state, skip it.
            if tentative_sttn_score >= sttn_score[neighbor]:
                continue

            # If we got to this point, add it!
            origin[neighbor] = current
            sttn_score[neighbor] = tentative_sttn_score
            stgptn_score[neighbor] = sttn_score[
                neighbor
            ] + neighbor.calculate_manhattan_distance(goal_board)

    return False


def calculate_move(old_coordinate: tuple, new_coordinate: tuple, luddy=False):
    import numpy

    directions_map = (
        {
            "A": [(2, 1)],
            "B": [(2, -1)],
            "C": [(-2, 1)],
            "D": [(-2, -1)],
            "E": [(1, 2)],
            "F": [(1, -2)],
            "G": [(-1, 2)],
            "H": [(-1, -2)],
        }
        if luddy
        else {
            "L": [(-1, 0), (3, 0)],
            "R": [(1, 0), (-3, 0)],
            "U": [(0, -1), (0, 3)],
            "D": [(0, 1), (0, -3)],
        }
    )
    return [
        direction
        for direction, coordinate in directions_map.items()
        if tuple(
            numpy.subtract(
                tuple(reversed(old_coordinate)) if luddy else old_coordinate,
                tuple(reversed(new_coordinate)) if luddy else new_coordinate,
            )
        )
        in coordinate
    ][0]


# test cases
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise (Exception("Error: expected 2 arguments"))

    if sys.argv[2] not in ["original", "circular", "luddy"]:
        raise (Exception("Error: only 'original', 'circular', and 'luddy' allowed"))
    # start_state = list()
    # with open(sys.argv[1], "r") as file:
    #     for line in file:
    #         start_state += [[int(i) for i in line.split()]]
    #
    # start = PuzzleBoard(start_state)
    # start = PuzzleBoard(
    #     [[1, 2, 3, 4], [5, 0, 6, 7], [9, 10, 11, 8], [13, 14, 15, 12]]
    # )  # board 4
    # start = PuzzleBoard(
    #     [[0, 2, 3, 4], [1, 5, 6, 7], [9, 10, 11, 8], [13, 14, 15, 12]]
    # )  # board 6
    start = PuzzleBoard(
        [[1, 2, 3, 4], [5, 6, 14, 8], [9, 10, 11, 12], [13, 0, 15, 7]]
    )  # To test chess-horse
    # start = PuzzleBoard(
    #     [[15, 2, 1, 12], [8, 5, 6, 11], [4, 9, 10, 7], [3, 14, 13, 0]]
    # )  # board n
    # start = PuzzleBoard(
    #     [[1, 2, 3, 0], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 4]]
    # )  # To test circular 1
    # start = PuzzleBoard(
    #     [[0, 2, 3, 1], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 4]]
    # )  # To test circular 2
    goal = PuzzleBoard([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])

    print("Solving...")

    states = solve(start, goal, circular=False, luddy=False)

    initial_position_of_zero = states[0].board_blocks[0]
    actual_path = list()

    print("Original Board: \n{0}".format(states[0].to_string()))
    for state in states[1:]:
        print("\t |\n\t |\n\t |\n\t\\./")
        print(state.to_string())
        actual_path.append(
            calculate_move(
                old_coordinate=initial_position_of_zero,
                new_coordinate=state.board_blocks[0],
            )
        )
        initial_position_of_zero = state.board_blocks[0]

    print("\nPath taken: \n{0}".format("".join(actual_path)))
