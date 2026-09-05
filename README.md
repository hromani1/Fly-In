*This project has been created as part of the 42 curriculum by hromani.*

Fly-in
Description

Fly-in is a pathfinding and scheduling project developed as part of the 42 curriculum.

The goal of the project is to simulate a group of drones travelling through a network of connected zones from a starting hub to an ending hub. Each zone and connection can have different constraints, such as movement costs, maximum drone capacities, blocked zones, priority zones, and restricted zones.

The project is divided into several main components:

Map Parser — Reads and validates map files and converts them into a graph.
Graph — Represents zones and connections and provides graph traversal utilities.
Pathfinder — Uses Dijkstra's algorithm to calculate shortest paths and heuristic distances.
Reservation Table — Tracks the occupancy of zones and connections at each turn.
Drone Scheduler — Uses A* search to find paths while considering reservations and zone priorities.
Simulator — Generates the movements of all drones over time.
Visualizer — Provides a graphical representation of the simulation using Pygame.

The final result is a simulation in which multiple drones can navigate the same network while respecting its capacity and movement constraints.

Features
Parsing and validation of custom map files.
Support for multiple drones.
Graph-based representation of the map.
Blocked, normal, priority, and restricted zones.
Configurable zone capacity.
Configurable connection capacity.
Shortest-path calculation using Dijkstra's algorithm.
Time-aware pathfinding using A*.
Reservation system for preventing collisions and capacity violations.
Turn-based drone scheduling.
Real-time graphical visualization using Pygame.
Instructions
Requirements

The project requires Python 3 and the following Python packages:

pygame
matplotlib

Install the dependencies with:

pip install pygame matplotlib

Or, if your environment uses pip3:

pip3 install pygame matplotlib
Running the project

From the root directory of the repository, run the main program:

python3 main.py

For example:

python3 main.py

The program parses the map, creates the graph and drones, calculates their schedules, and launches the visualizer.

Map Format

A map file is composed of key-value definitions.

A basic example is:

nb_drones: 4

start_hub: start 0 0
hub: hub1 5 2
hub: hub2 10 0
end_hub: end 15 0

connection: start-hub1
connection: hub1-hub2
connection: hub2-end

Zones can also contain metadata:

hub: restricted1 5 5 [zone=restricted color=red max_drones=2]

Connections can specify their maximum capacity:

connection: hub1-hub2 [max_link_capacity=2]

Comments can be added using #.

Algorithm
Graph Representation

The map is represented as a graph consisting of:

Zones, which represent nodes.
Connections, which represent edges between zones.
Adjacency lists, which allow neighboring zones to be efficiently retrieved.

Each zone stores its coordinates, type, color, and maximum drone capacity.

Each connection stores the two connected zones and its maximum capacity.

Dijkstra's Algorithm

Dijkstra's algorithm is implemented in the Pathfinder class.

It is used for two purposes:

Finding the shortest path between two zones.
Precomputing distances from zones to the destination.

A priority queue implemented with Python's heapq module is used to efficiently select the next zone with the lowest known cost.

Blocked zones are ignored during traversal.

The cost of entering a zone depends on its type. Normal and priority zones have a cost of 1, while restricted zones have a higher cost.

The resulting distance table is used as a heuristic for the scheduler.

A* Pathfinding

The DroneScheduler uses an A*-based search to find paths for individual drones.

Each search state contains:

(zone, turn)

This is important because reaching the same zone at different turns represents different scheduling states.

The priority queue evaluates states using:

f(n) = g(n) + h(n)

where:

g(n) is the cost accumulated so far.
h(n) is the precomputed heuristic distance to the destination.

The scheduler also takes additional scheduling information into account, including:

Zone capacity.
Connection capacity.
Zone movement costs.
Priority zones.
Waiting when necessary.
Restricted-zone movement behavior.
Reservation Table

The reservation table keeps track of resource usage for every turn.

Two types of resources are reserved:

Zones — Prevents more drones from occupying a zone than its capacity allows.
Connections — Prevents more drones from using a connection simultaneously than its maximum capacity allows.

Before a drone moves, the scheduler checks whether both the destination zone and connection have available capacity.

Once a path is selected, its required resources are reserved so that subsequent drones can plan around the already scheduled drones.

Drone Scheduling

Drones are scheduled sequentially.

For every drone:

The scheduler searches for a valid path.
The path respects the reservations created by previously scheduled drones.
The selected path is added to the global schedule.
Its zones and connections are reserved.

This allows multiple drones to share the graph while respecting its constraints.

Visual Representation

The project includes a graphical visualizer implemented with Pygame.

The visualizer represents:

Zones as circles.
Connections as lines between zones.
Drones as smaller moving circles.
Zone names as labels.
Zone colors according to their map metadata.
Restricted-zone movement by displaying the drone on the connection while travelling through the restricted zone.

The graph coordinates from the map are automatically scaled to fit the Pygame window while preserving their relative positions.

The simulation advances turn by turn, allowing the user to observe how drones move through the network and how the scheduling algorithm handles congestion and restricted areas.

The visual representation makes the scheduling algorithm easier to understand than looking at the generated paths alone. It provides immediate feedback about drone positions, movement order, connections, and the overall behavior of the simulation.

Technical Choices
Python

Python was chosen for its standard-library support for data structures such as dictionaries, sets, and priority queues, as well as its suitability for implementing graph algorithms.

heapq

Python's heapq module is used to implement the priority queues required by Dijkstra's algorithm and A* search.

deque

collections.deque is used for breadth-first traversal when checking whether the graph's destination is reachable.

Pygame

Pygame is used to create the graphical simulation and display the movement of drones.

Matplotlib

Matplotlib's color utilities are used to convert user-defined color names into RGB values for the Pygame visualizer.

Project Structure

A simplified overview of the project is:

.
├── main.py
├── graph.py
├── models.py
├── parser/
│   └── map_parser.py
├── pathfinder.py
├── scheduler/
│   ├── scheduler.py
│   └── table.py
├── simulator.py
├── visualizer.py
└── test_maps/
Resources
Documentation and References
Python documentation — data structures, exceptions, classes, and standard library:
https://docs.python.org/3/
Python heapq documentation:
https://docs.python.org/3/library/heapq.html
Python collections.deque documentation:
https://docs.python.org/3/library/collections.html#collections.deque
Dijkstra's algorithm — Wikipedia:
https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
A* search algorithm — Wikipedia:
https://en.wikipedia.org/wiki/A*_search_algorithm
Breadth-first search — Wikipedia:
https://en.wikipedia.org/wiki/Breadth-first_search
Pygame documentation:
https://www.pygame.org/docs/
Matplotlib documentation:
https://matplotlib.org/stable/
AI Usage

AI tools were used as a supplementary development and learning resource during the project.

They were used for:

Explaining algorithms and data structures, particularly Dijkstra's algorithm, A* search, priority queues, and reservation tables.
Investigating bugs and unexpected behavior in the pathfinding and scheduling logic.
Improving code organization and readability.
Helping format code according to Python style conventions.
Assisting with the documentation and structure of this README.

The core project architecture, implementation decisions, algorithms, and final code were reviewed and adapted as part of the project's development. AI was used as a learning and assistance tool rather than as a replacement for understanding or testing the implementation.
