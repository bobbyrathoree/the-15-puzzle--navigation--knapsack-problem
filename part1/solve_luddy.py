#!/usr/local/bin/python3
# solve_luddy.py : Sliding tile puzzle solver
#
# Code by: Bobby Rathore (brathore), James Mochizuki-Freeman (jmochizu), Dan Li (dli1)
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
import time

stgptn_score = collections.defaultdict(lambda: float("inf"))


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


def swap_location(
    target: dict, new_location_of_zero: tuple, original_location_of_zero: tuple
):
    """
    A function to swap the location of zero and some other number
    :param target: the PuzzleBoard instance dictionary
    :param new_location_of_zero: coordinates of the intended location of zero
    :param original_location_of_zero: coordinates of the current location of zero
    """
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
        :param board_blocks: can be either a list of a dict of a PuzzleBoard instance
        """
        if isinstance(board_blocks, list):
            self.board_blocks = quantify_list_to_dict(board_blocks)
        else:
            self.board_blocks = board_blocks
        self.width = self.__get_width__()
        self.height = int(len(self.board_blocks) / self.width)

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

    def __lt__(self, other: object) -> bool:
        """
        Less-than function. Compares stgptn-scores.
        :param other: origin object
        :return: a bool indicating whether new object's
                 stgptn-score is lower than its origin's
        """
        if not other:
            return False
        return stgptn_score[self] < stgptn_score[other]

    def __hash__(self):
        """
        Hash function. Hashes a frozenset of the blocks.
        :return: frozenset of PuzzleBoard instance
        """
        return hash(frozenset(self.board_blocks.items()))

    def __get_width__(self):
        """
        Returns the width of this puzzle.
        :return: width of PuzzleBoard instance
        """
        max_width = 0
        for value in self.board_blocks.values():
            max_width = max(value[0], max_width)

        return max_width + 1

    def to_string(self):
        """
        Returns the state in an easy-to-read fashion.
        :return: stringified PuzzleBoard instance
        """
        array = []
        for x in range(self.height):
            # print("y:",y)
            row = []
            for y in range(self.width):
                # print("x:",x)
                for block in self.board_blocks.items():
                    # print(block)
                    if block[1] == (x, y):
                        row.append(block[0])
                        break
            array.append(row)

        string = "\n".join("\t".join("%i" % x for x in y) for y in array)
        return string

    def calculate_manhattan_distance(self, other: object) -> int:
        """
        Our go-to heuristic: manhattan distance
        :param other: the puzzle board instance to calculate manhattan distance from
        :return: the estimated distance
        """
        estimate = 0

        for index in range(len(self.board_blocks)):
            estimate += abs(
                other.board_blocks[index][0] - self.board_blocks[index][0]
            ) + abs(other.board_blocks[index][1] - self.board_blocks[index][1])

        return estimate

    def estimate_chess_horse_dist(self, other: object) -> int:
        """
        Heuristic for chess_horse distances, I'll explain in group meeting
        :param other:
        :return: estimated distance
        """
        estimate = 0
        for index in range(len(self.board_blocks)):
            x = abs(
                other.board_blocks[index][0] - self.board_blocks[index][0]
            )  # x is the column difference (on x axis)
            y = abs(other.board_blocks[index][1] - self.board_blocks[index][1])

            corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
            mid_edges = [(0, 1), (0, 2), (1, 0), (2, 0), (3, 1), (3, 2), (1, 3), (2, 3)]
            lookup_table = (
                {
                    "1": [(1, 2), (2, 1)],
                    "2": [(1, 3), (0, 2), (2, 0), (3, 1), (3, 3)],
                    "3": [(0, 1), (1, 0), (2, 3), (3, 2)],
                    "4": [(1, 1), (2, 2)],
                    "5": [(0, 3), (3, 0)],
                }
                if self.board_blocks[index] in corners
                else (
                    {
                        "1": [(1, 2), (2, 1)],
                        "2": [(0, 2), (1, 1), (2, 0), (3, 1)],
                        "3": [(0, 1), (1, 0), (3, 0), (3, 2)],
                        "4": [(2, 2)],
                    }
                    if self.board_blocks[index] in mid_edges
                    else {
                        "1": [(1, 2), (2, 1)],
                        "2": [(1, 1), (0, 2), (2, 0)],
                        "3": [(0, 1), (1, 0)],
                        "4": [(2, 2)],
                    }
                )
            )
            distance = [int(key) for key, val in lookup_table.items() if (x, y) in val]
            estimate += distance[0] if distance else 0
            """
            0 3 2 5
            3 4 1 2  corners
            2 1 4 3
            5 2 3 2
            """
            """
            3 0 3 2
            2 3 2 1  mid-edges
            1 2 1 4
            2 3 2 3
            """
            """
            4 3 2 1
            3 0 3 2  mid-4
            2 3 2 1
            1 2 1 4
            """

            # twos = [(3, 3), (1, 1), (3, 1), (1, 3), (2, 0)]
            # threes = [(0, 1), (0, 3), (1, 0), (2, 3), (3, 0), (3, 2)]
            #
            # if (x, y) == (2, 1) or (x, y) == (1, 2):
            #     estimate += 1
            # elif (x, y) in twos:
            #     estimate += 2
            # elif (x, y) in threes:
            #     estimate += 3
            # elif (x, y) == (2, 2) or (x, y) == (0, 2):
            #     estimate += 4
        return estimate

    def get_successors(
        self, former: object, circular: bool = False, luddy: bool = False
    ) -> list:
        """
        Function to get all successors of a puzzle board instance,
        depending on the configuration: cirular or luddy (original is ON by default)
        :param former: state from which current puzzle board instance comes from
        :param circular: flag whether circular configuration requested or not
        :param luddy: flag whether luddy configuration requested or not
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


def solve(
    initial_board: PuzzleBoard,
    goal_board: PuzzleBoard,
    circular: bool = False,
    luddy: bool = False,
):
    """
    Function where the magic happens
    :param initial_board: Start instance
    :param goal_board: Goal instance
    :param circular: flag whether circular configuration requested or not
    :param luddy: flag whether luddy configuration requested or not
    :return: list of path taken or False if solution not found
    """
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
    stgptn_score[initial_board] = (
        initial_board.estimate_chess_horse_dist(goal_board)
        if luddy
        else initial_board.calculate_manhattan_distance(goal_board)
    )

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
            stgptn_score[neighbor] = sttn_score[neighbor] + (
                neighbor.estimate_chess_horse_dist(goal_board)
                if luddy
                else neighbor.calculate_manhattan_distance(goal_board)
            )

    return False


def calculate_move(
    old_coordinate: tuple, new_coordinate: tuple, luddy: bool = False
) -> str:
    """
    Function to determine the move based on older and latest coordinates of zero
    :param old_coordinate: old coordinates of zero
    :param new_coordinate: new coordinates of zero
    :param luddy: a flag
    :return:
    """
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
            "L": [(0, -1), (0, 3)],
            "R": [(0, 1), (0, -3)],
            "U": [(-1, 0), (3, 0)],
            "D": [(1, 0), (-3, 0)],
        }
    )
    return [
        direction
        for direction, coordinate in directions_map.items()
        if tuple(numpy.subtract(old_coordinate, new_coordinate)) in coordinate
    ][0]


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

    circular = True if sys.argv[2] == "circular" else False
    luddy = True

    # with open(sys.argv[1], "r") as file:
    #     start_state = []
    #     for line in file:
    #         start_state += [[int(i) for i in line.split()]]

    start_state = [
        [1, 2, 3, 4],
        [5, 0, 6, 7],
        [9, 10, 11, 8],
        [13, 14, 15, 12],
    ]  # board 4
    # start_state = [
    #     [0, 2, 3, 4],
    #     [1, 5, 6, 7],
    #     [9, 10, 11, 8],
    #     [13, 14, 15, 12],
    # ]  # board 6
    # start_state = [
    #     [1, 2, 3, 4],
    #     [5, 0, 14, 8],
    #     [9, 10, 11, 6],
    #     [13, 12, 15, 7],
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

    start = PuzzleBoard(start_state)
    goal = PuzzleBoard(goal_state)

    print("Solving...")

    if not is_solvable(puzzle_board=two_d_to_one_d(start_state)):
        print("Inf")

    else:
        tick = time.time()
        # the main thing
        states = solve(start, goal, circular=circular, luddy=luddy)

        initial_position_of_zero = states[0].board_blocks[0]
        actual_path = list()

        # Found the solution, let's print the original puzzle first
        print("Original Board: \n{0}".format(states[0].to_string()))

        # Now the following intermediate steps
        for state in states[1:]:
            print("\t |\n\t |\n\t |\n\t\\./")
            print(state.to_string())
            actual_path.append(
                calculate_move(
                    old_coordinate=initial_position_of_zero,
                    new_coordinate=state.board_blocks[0],
                    luddy=luddy,
                )
            )
            initial_position_of_zero = state.board_blocks[0]

        print("Time taken: {0}".format(time.time() - tick))
        print("\nPath taken: \n{0}".format("".join(actual_path)))
