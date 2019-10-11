# a1 

Authors: 

James Mochizuki-Freeman (jmochizu); 
Bobby Rathore (brathore); 
Dan Li (dli1).

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


#### General structure:
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
In the original game, we use Manhattan distance as our heuristic. We also considered to combine it with another heuristic but eventually decided to drop it. (See section 1.3 Afterthought)
###### 1.2.1.1 Manhattan distance
In the original game, we choose the Manhattan distance between a tile and its goal position as the heuristics. For each board, we sum up all the Manhattan distances between a tile and its goal position as an estimation of distance between current board and the goal board. 
###### 1.2.1.2 The interaction between Manhattan distance and the Linear Conflict Heuristic
There is no interaction between the two. In other words, the existence of pairs with reverse ordering will not cause us to over estimate in Manhattan distance or in the overall estimation.
###### 1.2.1.3 Admissible and consistent
This combined heuristic is admissible because under no circumstance will we be overestimating the moves of a board state.
It is also consistent because the estimation of state (s) will be monotonous.

Let's start with analyzing Manhattan distance m(S).
In the current state (S), if we swap the blank tile with one of its neighbor (N), tile N will either be one step closer or away from its goal position, and we arrive in a new state (S'). This one-step is the actual cost of our move, and thus cost(S', S) = 1.

Ultimately, we have these equations:

(1) cost(S', S) + m(S) = 1 + m(S),

(2) m(S') = m(S) + 1 or m(S) -1,

(3) consistency requirement: m(S') <= m(S) + cost(S', S)

if we combine (1) and (2), it's easy to see (3) holds.



##### 1.2.2 Circular game
###### 1.2.2.1. Revised Manhattan distance
In the circular game, the linear-conflict heuristic will not apply because a tile can move outside of the board to restore the ordering. Thus, we follow the central idea of Manhattan distance and construct a set of rules to estimate the minimum distance between a tile and its goal position. We sum up this distance between a tile and its goal position over all tiles as an estimation of the distance between current board and the goal board.

Here are the matrices for the revised Manhattan distance. In these matrices "0" stands for the tile which we are looking at, the numbers on other positions represent "if the current tile wants to go there, how many hops or moves are needed at a minimum." 

* if the tile that we are look at is in the corner (represented by "0"), we use the following matrix to estimate this tile and its goal position. If this tile is not in the left up corner, but in the other three corners, because of the symmetry, we transpose the following matrix to suit the position of this tile. 

            0 1 2 1
            1 2 3 2  corners
            2 3 4 3
            1 2 3 2

* if the tile is in the middle edges, we use the following matrix and transpose or flip it if necessary:

            1 2 3 2 
            0 1 2 1  mid-edges
            1 2 3 2
            2 3 4 3
            
* if the tile is in the middle, we use the following matrix, (by the way, original Manhattan distance will apply):

            2 1 2 3
            1 0 1 2  mid-4
            2 1 2 3
            3 2 3 4


###### 1.2.2.2 Admissible and consistent
This heuristic for the circular game is admissible and also consistent.
The argument is similar to section 1.2.1.3. Whenever we move a tile, it's either one step closer to or away from its goal position. These matrices only allow +1 or -1 changes in the heuristic estimation. 
Thus, the revised Manhattan distance is admissible and also consistent (monotonous).  

In other words, 
h(S') = h(S) +1 or -1 <= h(S) + 1 = h(S) + cost(S', S), satisfying the consistency requirement.

##### 1.2.3 Luddy game
###### 1.2.3.1 Luddy distance 
In the luddy game, the original and revised Manhattan distance is not suitable because if a tile is right next to it's target position, the Manhattan distance will estimate "1" step away when it's actually 3 hops away. It also over-estimate in other cases. 

But we follow the idea of Manhattan distance and choose a similar strategy of estimating the shortest distance using the following lookup-table to estimate the distance between a tile and its goal position. (Here, 0 represents a random tile, and other numbers represent how many hops are need to for "0" to get to that position.)
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

###### 1.2.3.2 Linear-conflict for Luddy 
(tested, but not incooperated into the final version, please see section 1.3 Afterthought)
###### 1.2.3.3 Admissible and consistent
This Luddy-distance heuristic is admissible and also consistent. The argument is similar to section 1.2.2.2, because these matrices only allow +1 or -1 in the estimation as well. 

### 1.3 After-thought: Linear-conflict heuristic
We considered a heuristic called linear-conflict form Korf and Taylor (1996).

The linear conflict heuristic considers two tiles when they are in their goal row or column but in reverse order relative to their goal position. For example, if tile "1" and "2" are in their goal row, i.e. the upper most row, but in reverse order, i.e. ordered as ..."2"..."1"..., we add two moves to the estimation of the whole board, because we have to move one of them out of the current row, i.e. the goal row, to let the other pass through and thus restore the ideal ordering. 

Let's consider if there are more than one pair of linear conflict in the same goal row or column. For example, "3" "2" "1" in the upper most row. Based on the definition of "linear conflict", the algorithm will identify three pairs of linear conflict: "3" "2", "2" "1", and "3" "1". We add four moves to the estimation, because we have to temporarily move two tiles to let the third one pass to restore the order.  

Then we considered the consistency of this heuristic. In order to make it consistent, we decide to add 1 to the estimation. The argument is the following:

The linear-conflict heuristic is denoted as l(S):

In the current state (S), if we swap the blank tile with one of its neighbor, it either introduce a linear conflict or eliminate one conflict. Thus,

(1) cost(S', S) + l(S) = 1 + l(S),

(2) l(S') = l(S) + 1, or l(S) -1,

(3) consistency requirement: l(S') <= l(S) + cost(S', S)

However, although the Manhattan distance and the linear-conflict heuristic both are consistent independently, the combined heuristic is not consistent anymore because

m(S') + l(S') <= m(S) + l(S) + 2*cost(S', S). 

Besides, we also revised a Luddy-version linear-conflict case, that is, if two tiles are in each other's goal position and only one-hop away, we add two moves to the estimation because one of them has to be moved to let the other pass. However, the performance of the algorithm is not as good as the one with only Luddy-distance. We suspect it has to do with the inconsistency of the heuristic. 

Taking all the above points into consideration, we decided to take the linear-conflict heuristic out. 

### 2. PART - 2 The navigation problem
#### 2.1 Heuristics
There are four choices for the "best" route and each has a different heuristic:
* Segments: we take the geographical distance (converted from GPS coordinates from current city to goal city) and divide it by the length of the longest segment (which we search and obtain in the main function as a global variable). We use the floor of this number as an estimation of how many road segments there will be from the current city to the goal city. 
* Distance: we simply take the geographical distance as an estimation.
* Time: We take the geographical distance and divide it by the maximum speed limit. 
* MPG: we take the geographical distance and divide it by 35 (which is approaching maximum of the mpg-speed function)

Simply put, all these heuristics are based on the estimation of geographical distance converted from coordinates. If the GPS coordinates are accurate, this heuristic will not over-estimate and thus is admissible. However, an issue here is there are some cities without coordinates. Thus, the accuracy of our estimation of coordinates will influence whether the heuristic is admissible and whether it's consistent.
#### 2.2 Coordinates estimation
An intuitive idea is that the coordinates can be estimated by getting the mean of the neighboring cities' coordinates. However, this might not be optimal because if the estimated city is very close to the goal, and this coordinates-estimation strategy will be worse than simply searching all its neighbors. 

An improved idea is that we only initiate the coordinates estimation when the estimated city and its neighbors are clustering considerably together compared with their distances to the goal.

#### 2.3 Admissible and consistent
Whether the heuristic that we choose is admissible or consistent will influence the choice of algorithm. It mainly has to do with the completeness and optimality of the searching algorithm.
Needless to say, A* search is complete and optimal only if we use:

(1) Algorithm #2, that is, duplicated states are revisited, and;
(2) Admissible heuristic. 

If we do not want to revisit visited states, and also want A* search to be optimal, we have to use:

(1) Algorithm #3, that is, discard revisited states;
(2) Consistent heuristic. 

These hard requirement poses a difficult choice for us, because while using GPS coordinates to calculate estimated distance is a both admissible and consistent heuristic, the estimation of the coordinates of the cities with missing coordinates will introduce inconsistency into the heuristic.

Here's why:

##### 2.3.1 Heuristic with coordinates

Starting from the GPS distance. The estimation of distance from GPS coordinates is essentially a line distance on a sphere. Thus the current city, its successor, and the goal city will form a triangle (on a sphere, due to the actual shape of the Earth). 
Let's use h(c, g) as the **d**istance estimation between current **c**ity and the **g**oal city, h(c', g) as that between the successor city and the goal city. Then, because c, c', and g, form a triangle, we have:

h(c', g) <= h(c, g) + h(c, c')

further, because h(c, c')<= cost(c, c'), we have:

h(c', g) <= h(c, g) + cost(c, c').

##### 2.3.2 Estimation of coordinates introduces inconsistency
As mentioned, we use the average coordinates of neighboring cities when they are far enough from the goal city. 
This choice of estimation will influence whether or not our heuristic is admissible or not, consistent or not. 
We use the constant epsilon to control the estimation of coordinates. 
And we use this qualifier to make sure that the cluster of cities has to be close and small enough compared with the distance between their location and the goal city. 
Thus, we believe it to be admissible. In other words, at least it doesn't over estimate compared with the true cost. 
However, mathematically in the worst case scenario, it is not consistent. 

#### 2.3 Decision
Because the consistency requirement can be satisfied only if all coordinates are accurate in representing the locations of cities, we have to choose Algorithm #2 to preserve the optimality and sacrifice computing time and cost.




### 3. Part - 3 The Knapsack Problem
#### 3.1 Algorithm explanation
The Knapsack Problem is a famous Dynamic Programming Problem that falls in the **optimization** category.

It derives its name from a scenario where, given a set of items with specific weights and assigned values, the goal is to maximize the value in a knapsack while remaining within the weight constraint. Each item can only be selected once, as we don’t have multiple quantities of any item.

This problem can be solved by using either Dynamic Programming or by using a technique called **Branch and Bound** that is discussed below.

### 3.2 Branch & Bound

This famous algorithm is the driving force behind mixed integer programmming. For instance, here we're dealing with the cost of a robot **and** its skill level. In general, an optimization problem looks like this: 

min(f(x)) where x belongs to X.

The set X might be a set of all real numbers, or might be a set of integers… Or it might be also a set containing vectors of real numbers and integers (which is mostly the case with mixed integer programming). f is the cost function here.

The idea of the branch and bound algorithm is simple. It finds the bounds of the cost function f given certain subsets of X. The algorithm relies on the **bounding principle** from optimization, which is just a fancy term used to describe a very intuitive thing. Imagine subsets of the feasible set, S1 and S2. If the upper bound of the solutions from S1 is lower than the lower bound of the solutions in S2, then obviously it is not worth exploring the solutions in S2. This is the whole magic behind the branch and bound algorithm. From this point on, I will denote the upper bound with **UB**, lower bound with **LB** and global upper bound with **GUB** for brevity sake.

The way that we employ the algorithm is the following. We have a certain stack of open nodes, let us call it **OPEN**. Open just means that they are not yet fully explored. We also keep track of the global upper bound **GUB**. At each step we take a node from the open set and expand it, we also evaluate its value. If the value of the node is higher than the **GUB** then we update the **GUB** to be the value of the node.

Af that, we attempt to branch the node into two children. If the node has children, we look at the **UB** of the child nodes. If the **UB** of the child node is higher than the **GUB**, then we add it to the **OPEN** stack, otherwise we discard it as not worth exploring.

Primary takeaway from Branch and Bound algorithm can that also be implemented in other algorithms:

__*If the lower bound is greater than the global upper bound, it doesn’t pay off to look for solutions there!*__

# Reference:

Korf, Richard E., and Larry A. Taylor. “Finding Optimal Solutions to the Twenty-Four Puzzle.” In AAAI/IAAI, Vol. 2, 1996.
