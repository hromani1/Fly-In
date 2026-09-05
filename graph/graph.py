from models import Zone, Connection, ZoneType
from collections import deque


class Graph():
    """Represent the zones and connections that make up a graph."""
    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Connection]] = {}

    def get_cnc(self, z1: str, z2: str) -> Connection | None:
        """Find the connection between two zones.
        Args:
            z1: Name of the first zone.
            z2: Name of the second zone.
        Returns:
            The connection between the zones, or None if no connection exists.
        """
        for cnc in self.adjacency[z1]:
            if cnc.z1 == z1 and cnc.z2 == z2:
                return cnc
            if cnc.z1 == z2 and cnc.z2 == z1:
                return cnc
        return None

    def set_end(self, end: Zone) -> None:
        """Set the graph's destination zone.
        Args:
            end: Zone to use as the graph's destination.
        """
        self.zones[end.name] = end
        self.end = end

    def set_start(self, start: Zone) -> None:
        """Set the graph's starting zone.
        Args:
            start: Zone to use as the graph's starting point.
        """
        self.zones[start.name] = start
        self.start = start

    def neighbors_of(self, zone_name: str) -> list[tuple[Zone, Connection]]:
        """Get all zones directly connected to a given zone.
        Args:
            zone_name: Name of the zone whose neighbors are requested.
        Returns:
            A list of tuples containing each neighboring zone and the
            connection linking it to the given zone.
        """
        result: list[tuple[Zone, Connection]] = []
        for connection in self.adjacency[zone_name]:
            if connection.z1 == zone_name:
                other = connection.z2
            else:
                other = connection.z1
            result.append((self.zones[other], connection))
        return result

    def is_reachable(self) -> bool:
        """Check whether the end zone is reachable from the start zone.
        Blocked zones are excluded from the search.
        Returns:
            True if the end zone is reachable, otherwise False.
        """
        visited: list[str] = []
        visited.append(self.start.name)
        myque: deque[str] = deque()
        myque.append(self.start.name)
        while myque:
            neighbors = self.neighbors_of(myque[0])
            for n in neighbors:
                if n[0].type == ZoneType.BLOCKED:
                    continue
                else:
                    if n[0].name not in visited:
                        myque.append(n[0].name)
                        visited.append(n[0].name)
            myque.popleft()
            if self.end.name in visited:
                return True
        return False
