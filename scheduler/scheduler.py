from models import ZoneType, Drone
from graph import Graph
from .table import ReservationTable, RTError
from heapq import heappop, heappush


class DroneScheduler():
    """Schedule drone paths while respecting graph and reservation
    constraints."""
    def __init__(self, graph: Graph, rt: ReservationTable,
                 ht: dict[str, int]) -> None:
        """Initialize a drone scheduler.
        Args:
            graph: Graph containing the zones and connections.
            rt: Reservation table used to track zone and connection capacity.
            ht: Heuristic table containing estimated costs to the destination.
        """
        self.graph = graph
        self.rt = rt
        self.ht = ht

    def plan_path(self, start_z: str, start_t: int,
                  end_z: str) -> list[tuple[int, str]]:
        """Find a valid path for a drone using A* search.
        The search accounts for zone costs, priorities, waiting, and existing
        reservations for zones and connections.
        Args:
            start_z: Name of the starting zone.
            start_t: Turn at which the drone starts.
            end_z: Name of the destination zone.
        Returns:
            A list of tuples containing the turn and zone for each step of
            the drone's path.
        Raises:
            ValueError: If the start or destination zone does not exist.
        """
        if start_z not in self.graph.zones:
            raise ValueError(f"given zone not found {start_z}")
        if end_z not in self.graph.zones:
            raise ValueError(f"given zone not found {end_z}")
        res: ZoneType = ZoneType.RESTRICTED
        pri: ZoneType = ZoneType.PRIORITY
        pq: list[tuple[int, int, int, str, int]] = []
        heappush(pq, (self.ht[start_z], 0, 0, start_z, start_t))
        g_score: dict[tuple[str, int], int] = {(start_z, start_t): 0}
        pred: dict[tuple[str, int], tuple[str, int]] = {}
        while pq:
            f_score, prio, cost, zone_name, turn = heappop(pq)
            state: tuple[str, int] = (zone_name, turn)
            if zone_name == end_z:
                path: list[tuple[int, str]] = []
                while state in pred:
                    path.append((state[1], state[0]))
                    self.rt.reserve_zone(state[0], state[1])
                    if state[0] != start_z and state[0] != pred[state][0]:
                        if self.graph.zones[state[0]].type != res:
                            self.rt.reserve_cnc(state[0],
                                                pred[state][0], state[1])
                        else:
                            self.rt.reserve_cnc(state[0],
                                                pred[state][0], state[1] - 1)
                    state = pred[state]
                path.append((start_t, start_z))
                path.reverse()
                return path
            for neighbor, _ in self.graph.neighbors_of(zone_name):
                if neighbor.type is ZoneType.BLOCKED:
                    continue
                next_turn = turn + neighbor.type.cost
                next_state = (neighbor.name, next_turn)
                transit_turn = turn + 1
                if not self.rt.zone_has_room(neighbor.name, next_turn):
                    continue
                if not self.rt.cnc_has_room(zone_name,
                                            neighbor.name, transit_turn):
                    continue
                new_cost = cost + neighbor.type.cost
                new_prio = prio + (0 if neighbor.type is pri else 1)
                if next_state not in g_score:
                    g_score[next_state] = new_cost
                    pred[next_state] = state
                    f_score = new_cost + self.ht[neighbor.name]
                    heappush(
                        pq,
                        (f_score, new_prio, new_cost, neighbor.name, next_turn)
                        )
            wait_turn = turn + 1
            wait_state = (zone_name, wait_turn)
            if self.rt.zone_has_room(zone_name, wait_turn):
                new_cost = cost + 1
                z = self.graph.zones[zone_name]
                new_prio = prio + (0 if z.type is pri else 1)
                if wait_state not in g_score:
                    g_score[wait_state] = new_cost
                    pred[wait_state] = state
                    heappush(pq, (new_cost + self.ht[zone_name],
                                  new_prio, new_cost, zone_name, wait_turn))
        return []


class Scheduler():
    """Schedule paths for multiple drones using a drone scheduler."""
    def __init__(self, dscheduler: DroneScheduler):
        """Initialize a scheduler.
        Args:
            dscheduler: Drone scheduler used to plan individual drone paths.
        """
        self.dscheduler = dscheduler

    def schedule_all(self, drones: list[Drone], start_z: str,
                     end_z: str) -> dict[int, list[tuple[int, str]]]:
        """Schedule paths for all drones from a start zone to an end zone.
        Args:
            drones: List of drones to schedule.
            start_z: Name of the starting zone.
            end_z: Name of the destination zone.
        Returns:
            A dictionary mapping each drone ID to its scheduled path.
        Raises:
            RTError: If no valid path can be found for a drone.
        """
        results: dict[int, list[tuple[int, str]]] = {}
        for drone in drones:
            path = self.dscheduler.plan_path(start_z, 0, end_z)
            if not path:
                raise RTError(f"Could not find a path for drone {drone.id}")
            results[drone.id] = path
        return results
