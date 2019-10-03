#!/usr/local/bin/python3

# from queue import PriorityQueue
from heapq import heappush, heappop
from math import inf, hypot, floor, radians, degrees, sin, cos, asin, acos, sqrt

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
            if not self.coords:
                return inf
            return floor(
                geo_distance(self.coords[1], self.coords[0], DEST_COORDS[1], DEST_COORDS[0])
                / MAX_DISTANCE
            )
        elif HEURISTIC == "distance":
            if not self.coords:
                return inf
            return geo_distance(self.coords[1], self.coords[0], DEST_COORDS[1], DEST_COORDS[0])
        elif HEURISTIC == "time":
            if not self.coords:
                return inf
            return (
                    geo_distance(self.coords[1], self.coords[0], DEST_COORDS[1], DEST_COORDS[0])
                    / MAX_SPEEDLIMIT
            )
        elif HEURISTIC == "mpg":
            if not self.coords:
                return inf
            return (
                    geo_distance(self.coords[1], self.coords[0], DEST_COORDS[1], DEST_COORDS[0])
                    / 35  ## FIX the 35 with some function???
            )
            ### I plotted out the mpg function,
            # and find the mpg decreases if speed is over 30 (min_speedlimit overall is 25),
        # I think it's safe to assume that within the range of possible speed, MPG_fun is monotonously deceasing

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
        self.g_cost = self._calc_g_cost()

    def _calc_g_cost(self):
        if HEURISTIC == "segments":
            return len(self.segments)
        elif HEURISTIC == "distance":
            return sum(seg.dist for seg in self.segments)
        elif HEURISTIC == "time":
            return sum(seg.dist / seg.speed for seg in self.segments)
        elif HEURISTIC == "mpg":
            # here it should be the sum of (distance of each segments divivded by MPG)
            # -> you get the total gallons
            return sum(
                seg.dist / mpg_fun(seg.speed)
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


# from gps coordinates return geo-circular distance
def geo_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 3958.7 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))


def mpg_fun(speed):
    return 400 * (speed / 150) * (1 - (speed / 150)) ** 4


def parse_segments(filepath):
    with open(filepath, "r") as file:
        segments = dict()
        for line in file:
            c1, c2, dist, speed, name = line.split()
            segments.setdefault(c1, []).append(
                Segment(c1, c2, float(dist), float(speed), name)
            )
            segments.setdefault(c2, []).append(
                Segment(c2, c1, float(dist), float(speed), name)
            )
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
        if not state.city:
            continue
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
print(segments["Ada,_Minnesota"])
gps = parse_gps("city-gps.txt")
MAX_DISTANCE = max(seg.dist for key, seglist in segments.items() for seg in seglist)
MAX_SPEEDLIMIT = max(seg.speed for key, seglist in segments.items() for seg in seglist)
MIN_SPEEDLIMIT = min(seg.speed for key, seglist in segments.items() for seg in seglist)
print(MAX_DISTANCE)
print(MAX_SPEEDLIMIT)
print(MIN_SPEEDLIMIT)

DEST_CITY = "Ada,_Minnesota"
HEURISTIC = "mpg"
DEST_COORDS = gps[DEST_CITY]
cities = {name: City(name, segments[name], gps.get(name, None)) for name in segments}
out = solve(cities["Abbot_Village,_Maine"])
print(out)
print("total segments", len(out.segments))
print("total distance:", sum(s.dist for s in out.segments))
print("total time (hours):", sum(s.dist / s.speed for s in out.segments))
print("total gas (gallons):", sum(s.dist / mpg_fun(s.speed) for s in out.segments))
