# a1 

## Overview

There are three parts in this assignment. 
The first two are implemented using A* search (or best-first search), 
that is, to estimate whether a node should be expanded, 
a combined function is used. 
This function consists of: 
(1) a g-function as the actual cost function 
(cost that has already happened so far up to the current node) and 
(2) a h-function as heuristic function 
(estimating the future cost from the current node to goal). 
Each heuristic (h-function) will be explained in detail below. 
The third problem is implemented with branch and bound algorithm. 
The branch and bound algorithm is designed for discrete and combinatorial optimization problems.


General structure:
1. Input: All the codes start with taking in arguments from keyboard inputs and parsing necessary files into desirable machine-readable format. 
2. Solving: 
    * For each search, a "solving" function is designed to take in the following parameters:
	    * start state
	    * goal state
	    * choice of "game mode" or heuristics
    * And the solving function returns:
	    * the path if it finds a solution; 
	    * 'Inf' if not.
3. Output: For each game, if the solution is found, a path is returned and printed. If not, 'Inf' is returned and printed.

## Heuristic Explanations
### 1. Part - 1 The 15-Puzzle
#### 1.1 Checking solvability 
We check the solvability for the original problem following the explanation [here](https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
).
The legal moves in circular and luddy game mode do not preserve the polarity of the number of inversions as the original game does, thus the circular game and luddy game are not subjected to the solvability check. 
#### 1.2 Heuristics
##### 1.2.1 Original game
In the orginal game, two heuristics are combined: (1) Manhattan distance; (2) Linear-conflict heuristic (Korf and Taylor, 1996).
###### 1.2.1.1 Manhattan distance
In the original game, we choose the Manhattan distance between a tile and its goal position as the heuristics. For each board, we sum up all the Manhattan distances between a tile and its goal position as an estimation of distance between current board and the goal board. 
###### 1.2.1.2 Linear Conflict heuristic
The linear conflict heuristic considers two tiles when they are in their goal row or column but in reverse order relative to their goal position. For example, if tile "1" and "2" are in their goal row, i.e. the upper most row, but in reverse order, i.e. ordered as ..."2"..."1"..., we add two moves to the estimation of the whole board, because we have to move one of them out of the current row, i.e. the goal row, to let the other pass through and thus restore the ideal ordering. 
Let's consider if there are more than one pair of linear conflict in the same goal row or column. For example, "3" "2" "1" in the upper most row. Based on the definition of "linear conflict", the algorithmn will identify three pairs of linear conflict: "3" "2", "2" "1", and "3" "1". We add four moves to the estimation, because we have to temporarily move two tiles to let the third one pass to restore the order.  
Generally for each pair of tiles with similar reverse ordering, we add two moves to the estimation. 
###### 1.2.1.3 The interaction between Manhattan distance and the Linear Conflict Heuristic
There is no interaction between the two. In other words, the existence of pairs with reverse ordering will not cause us to over estimate in Manhattan distance or in the overall estimation.
###### 1.2.1.4 Admissible and consistent
This combined heuristic is admissible because under no circumstance will we be overestimating the moves of a board state.
We don't think this heuristic is consistent.
##### 1.2.2 Circular game
###### 1.2.2.1. Revised Manhattan distance
In the circular game, the linear-conflict heuristic will not apply because a tile can move outside of the board to restore the ordering. Thus, we follow the central idea of Manhattan distance and construct a set of rules to estimate the minimum distance between a tile and its goal position. We sum up this distance between a tile and its goal position over all tiles as an estimation of the distance between current board and the goal board.
###### 1.2.2.2 Admissible and consistent
This heuristic for the circular game is admissible but not consistent. 
##### 1.2.3 Luddy game
###### 1.2.3.1 Luddy distance 
In the luddy game, the original and revised Manhattan distance is not suitable because if a tile is right next to it's target position, the Manhattan distance will estimate "1" step away when it's actually 3 hops away. It also over-estimate in other cases. But we follow the idea of Manhattan distance and choose a similar strategy of estimating the shortest distance using the following lookup-table to estimate the distance between a tile and its goal position. (Here, 0 represents a random tile, and other numbers represent how many hops are need to for "0" to get to that position.)
* if the tile that we are look at is in the corner (represented by "0"), we use the following matrix to estimate this tile and its goal position. If this tile is not in the left up corner, but in the other three corners, because of the symmetry, we transpose the following matrix to suit the position of this tile. 

            0 3 2 5
            3 4 1 2  corners
            2 1 4 3
            5 2 3 2

* if the tile is in the middle edges, we use the following matrix and transpose or flip it if necessary:

            3 0 3 2
            2 3 2 1  mid-edges
            1 2 1 4
            2 3 2 3
            
* if the tile is in the middle, we use the following matrix:

            4 3 2 1
            3 0 3 2  mid-4
            2 3 2 1
            1 2 1 4

###### 1.2.3.2 Linear-conflict for Luddy (tested, but not incooperated into the final version)
We implemented the linear-conflict heuristic for the Luddy puzzle, that is, if two tiles are in each other's goal position and only one-hop away, we add two moves to the estimation because one of them has to be moved to let the other pass. However, this heuristic is not ideal because it slows down the program drastically. Due to the running time concern, we dropped this heuristic eventually. 
###### 1.2.3.3 Admissible and consistent
This Luddy-distance heuristic is admissible but not consistent.


### 2. PART - 2 The navigation problem
#### 2.1 Heuristics
There are four choices for the "best" route and each has a different heuristic:
* Segments: we take the geographical distance (converted from GPS coordinates from current city to goal city) and devide it by the Maximun of the segment distance (which we search and obtain in the main function as a global variable) and use the floor of this number as an estimation of how many road segments there will be from the current city to the goal city. 
* Distance: we simply take the geographical distance as an estimation
* Time: We take the geographical distance and divide it by the Maximum of the speed limit. 
* MPG: we take the geographical distance and devide it by 35 (which is approaching maximum of the mpg-speed function)

Simply  put, all these heuristics are based on the estimation of geographical distance converted from coordinates. If the GPS coordinates are accurate, this heuristic will not over-estimate and thus is admissible. However, an issue here is there are some cities without coordinates. Thus, the accuracy of our estimation of coordinates will influence whether the heuristic is admissible and whether it's consistent.
#### 2.2 Coordinates estimation
An intuitive idea is that the coordinates can be estimated by getting the mean of the neighboring cities' coordinates. However, this might not be optimal because if the estimated city is very close to the goal, and this coordinates-estimation strategy will be worse than simply searching all its neighbors. 

An improved idea is that we only initiate the coordinates estimation when the estimated city and its neighbors are clustering considerably together compared with their distances to the goal.


Thus, we have:
only when the road segments that connect the estimated city and its neighbors are smaller than a fraction of their distances to the goal city, we average the coordinates of these cities to give the estimated city a pair of artificial coordinates. We use "epsilon" to control the how small the fraction should be. 

### 3. Part - 3 The Knapsack Problem
#### 3.1 Algorithm explanation
The Knapsack Problem is a famous Dynamic Programming Problem that falls in the **optimization** category.

It derives its name from a scenario where, given a set of items with specific weights and assigned values, the goal is to maximize the value in a knapsack while remaining within the weight constraint. Each item can only be selected once, as we don’t have multiple quantities of any item.

This problem can be solved by using either Dynamic Programming or by using a technique called **Branch and Bound** that is discussed below.

### 3.2 Branch & Bound

This famous algorithm is the driving force behind mixed integer programmming. For instance, here we're dealing with the cost of a robot **and** its skill level. In general, an optimization problem looks like this: 

min(f(x)) where x belongs to X.

The set X might be a set of all real numbers, might be a set of integers… Might be also a set containing vectors of real numbers and integers (which is mostly the case with mixed integer programming). f is the cost function here.

The idea of the branch and bound algorithm is simple. It finds the bounds of the cost function f given certain subsets of X. The algorithm relies on the **bounding principle** from optimization, which is just a fancy term used to describe a very intuitive thing. Imagine subsets of the feasible set, S1 and S2. If the upper bound of the solutions from S1 is lower than the lower bound of the solutions in S2, then obviously it is not worth exploring the solutions in S2. This is the whole magic behind the branch and bound algorithm. From this point on, I will denote the upper bound with **UB**, lower bound with **LB** and global upper bound with **GUB** for brevity sake.

The way that we employ the algorithm is the following. We have a certain stack of open nodes, let us call it **OPEN**. Open just means that they are not yet fully explored. We also keep track of the global upper bound **GUB**. At each step we take a node from the open set and expand it, we also evaluate it if it is a leaf node. If the node has children, we look at the **LB** and **UB** of the child nodes. If the **LB** of the child node is lower than the **GUB**, then we add it to the **OPEN** stack, if it is higher than the global **UB** then it is not worth exploring. Additionally, if the **UB** of the node if lower than the global **UB** then we update the global **UB** to the **UB** of the node.

Primary takeaway from Branch and Bound algorithm can that also be implemented in other algorithms:

__*If the lower bound is greater than the global upper bound, it doesn’t pay off to look for solutions there!*__

# Reference:

Korf, Richard E., and Larry A. Taylor. “Finding Optimal Solutions to the Twenty-Four Puzzle.” In AAAI/IAAI, Vol. 2, 1996.
