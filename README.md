# a1 

## Overview

There are three parts in this assignment. All of them are implemented using A* search (or best-first search), that is, to estimate whether a node should be expanded, a function is used. This function consists of (1) a g-function as the actual cost function (cost that has already happened so far up to the current node) and (2) a h-function as heuristic function (estimating the future cost from the current node to goal). Each heuristic (h-function) will be explained in detail below

General structure:
1. Input: All the codes start with taking in arguments from keyboard inputs and parsing necessary files into desirable machine-readable format. 
2. Solving: For each search, a "solving" function is designed to take in the following parameters:
	* start state
	* goal state
	* choice of "game mode" or heuristics
And the solving function returns
	* the path if it finds a solution; 
	* 'Inf' if not.
3. Output: For each game, if the solution is found, a path is returned and printed. If not, 'Inf' is returned and printed.

## Heuristic Explanations
1. Part - 1 The 15-Puzzle
1.1 Checking solvability 
We check the solvability for the original problem following the explanation [here](https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
).
The legal moves in circular and luddy game mode do not preserve the polarity of the number of inversions as the original game does, thus the circular game and luddy game are not subjected to the solvability check. 
1.2 Heuristics
In the original and circular game, we choose the Manhattan distance between a tile and its goal position as the heruistics. For each board, we sum up all the Manhanttan distances as an estimation for that particular board (a state). 
In the luddy game, the Manhattan distance is not suitable because if a tile is right next to it's target position, the Manhanttan distance will estimate "1" step away when it's actually 3 hops away. It also overesitmate in other cases. But we choose a similar strategy of estimating the shortest distance using the following table to estimate the distance between a tile and its goal position. (Here, 0 represents a random tile, and other numbers represent how many hops are need to for "0" to get to that position.)
| 2 | 3 | 2 | 3 | 2 | 3 | 2 |
| 3 | 4 | 1 | 4 | 1 | 4 | 3 |
| 2 | 1 | 2 | 3 | 2 | 1 | 2 |
| 3 | 2 | 3 | 0 | 3 | 2 | 3 |
| 2 | 1 | 2 | 3 | 2 | 1 | 2 |
| 3 | 4 | 1 | 4 | 1 | 4 | 3 |
| 2 | 3 | 2 | 3 | 2 | 3 | 2 |

2. PART - 2 The navigation problem
2.1 Heuristics
There are four choices for the "best" route and each has a different heuristic:
* Segments: we take the geographical distance (converted from GPS coordinates from current node to goal city) and devide it by the Maximun of the segment distance (which we search and obtain in the main function as a global variable) and use the floor of this number as an estimation of how many road segments there will be from the current node to the goal city. 
* Distance: we simply take the geographical distance as an estimation
* Time: We take the geographical distance and divide it by the Maximum of the speed limit. 
* MPG: we take the geographical distance and devide it by 35. 