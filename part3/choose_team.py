#!/usr/local/bin/python3
#
# choose_team.py : Choose a team of maximum skill under a fixed budget
#
# Code by: Bobby Rathore (brathore), James Mochizuki-Freeman (jmochizu), Dan Li (dli1
#
# Based on skeleton code by D. Crandall, September 2019
#
import sys

BUDGET = None


class Person(object):
    __slots__ = ("name", "skill", "cost")

    def __init__(self, name, skill, cost):
        self.name = name
        self.skill = float(skill)
        self.cost = float(cost)

    def __lt__(self, other):
        return self.skill / self.cost < other.skill / other.cost

    def __repr__(self):
        return self.name


class State(object):
    __slots__ = ("fixed", "variable", "fixed_skill", "fixed_cost")

    def __init__(self, fixed, variable):
        self.fixed = tuple(fixed)
        self.variable = tuple(variable)
        self.fixed_skill = sum(p.skill for p in fixed)
        self.fixed_cost = sum(p.cost for p in fixed)


def load_people(filename):
    with open(filename, "r") as file:
        return [Person(*line.split()) for line in file]


def bound(state):
    """Returns a skill value that is guaranteed to not be less than that of any
    combination of people within the budget"""
    skill = state.fixed_skill
    rem_budget = BUDGET - state.fixed_cost
    for person in sorted(state.variable, reverse=True):
        if person.cost < rem_budget:
            skill += person.skill
            rem_budget -= person.cost
        else:
            skill += (rem_budget / person.cost) * person.skill
            break
    return skill


def branch(state):
    """Returns two (people, budget) pairs that subdivide the space in two"""
    people = list(state.variable)
    if len(people) == 0:
        return None, None
    person = people.pop()
    s1 = State(state.fixed, people)
    s1 = s1 if s1.fixed_cost < BUDGET else None
    s2 = State(state.fixed + (person,), people)
    s2 = s2 if s2.fixed_cost <= BUDGET else None
    return s1, s2


def solve(people):
    initial_state = State((), people)
    fringe = [initial_state]
    best = initial_state
    while len(fringe) > 0:
        state = fringe.pop()
        if state.fixed_skill > best.fixed_skill:
            best = state
        s1, s2 = branch(state)
        if s1:
            if bound(s1) > best.fixed_skill:
                fringe.append(s1)
        if s2:
            if bound(s2) > best.fixed_skill:
                fringe.append(s2)
    return best.fixed


def main():
    global BUDGET
    if len(sys.argv) != 3:
        raise Exception("Error: expected 2 command line arguments")

    BUDGET = float(sys.argv[2])
    people = load_people(sys.argv[1])
    solution = solve(people)
    print(
        "Found a group with %d people costing %f with total skill %f"
        % (len(solution), sum(p.cost for p in solution), sum(p.skill for p in solution))
    )

    for s in solution:
        print("%s %f" % (s.name, float(1)))


if __name__ == "__main__":
    main()
