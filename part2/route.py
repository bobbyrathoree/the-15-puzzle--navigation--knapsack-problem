#!/usr/local/bin/python3

# from queue import PriorityQueue
from heapq import heappush, heappop
from math import inf, hypot

DEST_CITY = None
DEST_COORDS = None
HEURISTIC = None


class Segment(object):
    __slots__ = ("from_city", "to_city", "dist", "speed", "name")

    def __init__(self, from_city, to_city, dist, speed, name):
        self.from_city = from_city
        self.to_city = to_city
        self.dist = dist
        self.speed = speed
        self.name = name

    def __repr__(self):
        return f"{self.from_city} {self.to_city} {self.dist} {self.speed} {self.name}"


class City(object):
    __slots__ = ("name", "segments", "coords", "h_cost")

    def __init__(self, name, segments, coords):
        self.name = name
        self.segments = segments
        self.coords = coords
        self.h_cost = self._calc_heuristic()

    def _calc_heuristic(self):
        if HEURISTIC == "segments":
            return 0  # FIXME: Implement
        elif HEURISTIC == "distance":
            if not self.coords:
                return inf
            return hypot(
                self.coords[0] - DEST_COORDS[0], self.coords[1] - DEST_COORDS[1]
            )
        elif HEURISTIC == "time":
            return 0  # FIXME: Implement
        elif HEURISTIC == "mpg":
            return 0  # FIXME: Implement

    def __repr__(self):
        return (
            f"{self.name} {self.coords} \n"
            f"segments: {list(s.to_city for s in self.segments)}\n"
            f"h_cost: {self.h_cost}"
        )


class Route(object):
    __slots__ = ("segments", "g_cost")

    def __init__(self, segments):
        self.segments = segments
        self.g_cost = self._calc_cost()

    def _calc_cost(self):
        if HEURISTIC == "segments":
            return len(segments)
        elif HEURISTIC == "distance":
            return sum(seg.dist for seg in self.segments)
        elif HEURISTIC == "time":
            return sum(seg.speed for seg in self.segments)
        elif HEURISTIC == "mpg":
            return sum(
                400 * (seg.speed / 150) * (1 - (seg.speed / 150)) ** 4
                for seg in self.segments
            )

    def __repr__(self):
        out = self.segments[0].from_city
        out += "".join(f"\n -> {seg.name}\n* {seg.to_city}" for seg in self.segments)
        return out


class State(object):
    __slots__ = ("city", "route", "cost")

    def __init__(self, city, route):
        self.city = city
        self.route = route
        self.cost = route.g_cost + city.h_cost

    def __eq__(self, other):
        return self.city == other.city and self.route == other.route

    def __lt__(self, other):
        return self.cost < other.cost

    def invalidate(self):
        self.city = None
        self.route = None


def parse_segments(filepath):
    with open(filepath, "r") as file:
        segments = dict()
        for line in file:
            c1, c2, dist, speed, name = line.split()
            segments.setdefault(c1, []).append(Segment(c1, c2, dist, speed, name))
            segments.setdefault(c2, []).append(Segment(c2, c1, dist, speed, name))
        return segments


def parse_gps(filepath):
    with open(filepath, "r") as file:
        return {
            name: tuple(map(float, coords))
            for name, *coords in (line.split() for line in file)
        }


def is_goal(state):
    return state.city.name == DEST_CITY


def successors(state):
    return [
        State(cities[seg.to_city], Route(state.route.segments + [seg]))
        for seg in state.city.segments
    ]


def solve(initial_city):
    fringe = []
    heappush(fringe, State(initial_city, Route([])))
    closed = set()
    while len(fringe) > 0:
        state = heappop(fringe)
        closed.add(state.city)
        if is_goal(state):
            return state.route
        for succ in successors(state):
            if succ.city in closed:
                continue
            match = next((s for s in fringe if s.city == succ.city), None)
            if not match:
                heappush(fringe, succ)
                continue
            if match.route.g_cost <= succ.route.g_cost:
                continue
            # invalidate a heapq item instead of removing it, per
            # https://docs.python.org/3.6/library/heapq.html
            match.invalidate()
            heappush(fringe, succ)
    return False


segments = parse_segments("road-segments.txt")
gps = parse_gps("city-gps.txt")

DEST_CITY = "Ada,_Minnesota"
HEURISTIC = "segments"
DEST_COORDS = gps[DEST_CITY]
cities = {name: City(name, segments[name], gps.get(name, None)) for name in segments}

out = solve(cities["Abbot_Village,_Maine"])
print(out)
print(len(out.segments))
