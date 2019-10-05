#!/usr/local/bin/python3
#
# choose_team.py : Choose a team of maximum skill under a fixed budget
#
# Code by: Bobby Rathore (brathore), James Mochizuki-Freeman (jmochizu), Dan Li (dli1
#
# Based on skeleton code by D. Crandall, September 2019
#
import sys


class Person(object):
    __slots__ = ("name", "skill", "cost")

    def __init__(self, name, skill, cost):
        self.name = name
        self.skill = float(skill)
        self.cost = float(cost)

    def __lt__(self, other):
        return self.skill / self.cost < other.skill / other.cost


def load_people(filename):
    with open(filename, "r") as file:
        return [Person(*line.split()) for line in file]


# This function implements a greedy solution to the problem:
#  It adds people in decreasing order of "skill per dollar,"
#  until the budget is exhausted.
def approx_solve(people, budget):
    solution = []
    for person in sorted(people, reverse=True):
        if budget >= person.cost:
            solution.append(person)
            budget -= person.cost
    return solution


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise Exception("Error: expected 2 command line arguments")

    budget = float(sys.argv[2])
    people = load_people(sys.argv[1])
    solution = approx_solve(people, budget)

    print(
        "Found a group with %d people costing %f with total skill %f"
        % (len(solution), sum(p.cost for p in solution), sum(p.skill for p in solution))
    )

    for s in solution:
        print("%s %f" % (s.name, float(1)))
