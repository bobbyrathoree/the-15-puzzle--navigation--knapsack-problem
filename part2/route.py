#!/usr/local/bin/python3

from heapq import heappush, heappop
from math import floor, radians, sin, cos, acos
import sys

CITIES: dict = {}
DEST_CITY = None
DEST_COORDS = None
HEURISTIC = None

MAX_DISTANCE = None
MAX_SPEEDLIMIT = None
MIN_SPEEDLIMIT = None
MAX_MPG = 35


class Segment(object):
    __slots__ = ("from_city", "to_city", "dist", "speed", "name", "mpg")

    def __init__(self, from_city, to_city, dist, speed, name):
        self.from_city = from_city
        self.to_city = to_city
        self.dist = dist
        self.speed = speed
        self.mpg = 400 * (speed / 150) * (1 - (speed / 150)) ** 4
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

    def _calc_fake_coords(self):
        # FIXME: find some better way of calculating
        """
        calculate self's coordinates based on neighbors' coordinates
        only when the distance between the neighbor and goal city is 1/epsilon times longer than the segments
        :return:
        """

        lat = 0
        lon = 0
        EPSILON = 0.1
        coords_list = []
        for seg in self.segments:
            if not (
                not seg.to_city.coords
                or not (
                    seg.dist
                    < EPSILON
                    * seg.to_city.geo_distance(*seg.to_city.coords, *DEST_COORDS)
                )
            ):
                coords_list.append(seg.to_city.coords)
        if len(coords_list) != 0:
            for c in coords_list:
                lat += c[0]
                lon += c[1]
            lat = lat / len(coords_list)
            lon = lon / len(coords_list)
            self.coords = (lat, lon)
        else:
            self.coords = None
        return

    def _calc_heuristic(self):
        if not self.coords:
            return 0
        if HEURISTIC == "segments":
            return floor(self.geo_distance(*self.coords, *DEST_COORDS) / MAX_DISTANCE)
        elif HEURISTIC == "distance":
            return self.geo_distance(*self.coords, *DEST_COORDS)
        elif HEURISTIC == "time":
            return self.geo_distance(*self.coords, *DEST_COORDS) / MAX_SPEEDLIMIT
        elif HEURISTIC == "mpg":
            return self.geo_distance(*self.coords, *DEST_COORDS) / MAX_MPG

    def __repr__(self) -> object:
        return (
            f"{self.name} {self.coords} \n"
            f"segments: {list(s.to_city.name for s in self.segments)}\n"
            f"h_cost: {self.h_cost}"
        )

    @staticmethod
    def geo_distance(lat1, lon1, lat2, lon2):
        """from gps coordinates return geo-circular distance"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        return 3958.7 * (
            acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
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
            return sum(seg.dist / seg.mpg for seg in self.segments)  # gallons

    def __repr__(self):
        out = self.segments[0].from_city.name
        out += "".join(
            f"\n -> {seg.name}\n* {seg.to_city.name}" for seg in self.segments
        )
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
        State(seg.to_city, Route(state.route.segments + [seg]))
        for seg in state.city.segments
    ]


def solve(initial_city):
    print("solving")
    fringe = []
    heappush(fringe, State(initial_city, Route([])))
    closed = set()
    while len(fringe) > 0:
        state = heappop(fringe)
        # if not state.city:
        #    continue
        closed.add(state.city)
        if is_goal(state):
            return state.route
        for succ in successors(state):
            if succ.city in closed:
                continue
            # match = next((s for s in fringe if s.city == succ.city), None)
            # if not match:
            #    heappush(fringe, succ)
            #    continue
            # if match.route.g_cost <= succ.route.g_cost:
            #    continue
            # invalidate a heapq item instead of removing it, per
            # https://docs.python.org/3.6/library/heapq.html
            # match.invalidate()
            if not succ.city.coords:
                succ.city._calc_fake_coords()
                # print("CITIES WITHOUT COORDS:",succ.city, succ.city.coords)
            heappush(fringe, succ)
    return False


def setup():
    """
    Function to set up start city, destination city, and the heuristic that is to be used
    in this runtime. Followed by destination coordinates, speed limits and the maximum allowed
    distance between segments.
    """
    global MAX_DISTANCE, MAX_SPEEDLIMIT, MIN_SPEEDLIMIT, START_CITY, DEST_CITY, HEURISTIC
    global DEST_COORDS, CITIES

    if len(sys.argv) != 4:
        raise (
            Exception(
                "Error: expected 3 arguments: start city, end city, and cost function"
            )
        )

    if sys.argv[3] not in ["segments", "distance", "time", "mpg"]:
        raise (
            Exception(
                "Error: only 'segments', 'distance', 'time', 'mpg' allowed as cost function"
            )
        )

    START_CITY = sys.argv[1]
    DEST_CITY = sys.argv[2]
    HEURISTIC = sys.argv[3]

    segments = parse_segments("road-segments.txt")
    gps: dict = parse_gps("city-gps.txt")
    MAX_DISTANCE = max(seg.dist for segs in segments.values() for seg in segs)
    MAX_SPEEDLIMIT = max(seg.speed for segs in segments.values() for seg in segs)
    MIN_SPEEDLIMIT = min(seg.speed for segs in segments.values() for seg in segs)

    DEST_COORDS = gps[DEST_CITY]

    CITIES = {
        name: City(name, segments[name], gps.get(name, None)) for name in segments
    }
    for segs in segments.values():
        for seg in segs:
            seg.from_city = CITIES[seg.from_city]
            seg.to_city = CITIES[seg.to_city]


def last_line_output(solution):
    total_segments = len(solution.segments)
    total_miles = sum(s.dist for s in solution.segments)
    total_hours = sum(s.dist / s.speed for s in solution.segments)
    total_gas_gallons = sum(s.dist / s.mpg for s in solution.segments)
    cities_on_road = [START_CITY]
    for seg in solution.segments:
        cities_on_road.append(seg.to_city.name)
    print(
        total_segments,
        int(total_miles),
        total_hours,
        total_gas_gallons,
        *cities_on_road,
    )


if __name__ == "__main__":
    setup()
    result = solve(CITIES[START_CITY])
    print(result)
    print("total segments", len(result.segments))
    print("total distance:", sum(s.dist for s in result.segments))
    print("total time (hours):", sum(s.dist / s.speed for s in result.segments))
    print("total gas (gallons):", sum(s.dist / s.mpg for s in result.segments))
    last_line_output(solution=result)
