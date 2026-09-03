from graph import Graph
from models import ZoneType
from heapq import heappop, heappush
from parser import MapError


class Pathfinder():
    """Find paths and calculate shortest distances in a graph."""
    def __init__(self, graph: Graph) -> None:
        """Initialize a pathfinder with a graph.
        Args:
            graph: Graph on which paths will be calculated.
        """
        self.graph = graph

    def _dijkstra(self, start: str,
                  stop: str | None = None) -> tuple[dict[str, int],
                                                    dict[str, str]]:
        """Calculate shortest-path distances using Dijkstra's algorithm.
        Args:
            start: Name of the starting zone.
            stop: Optional name of the destination zone. If provided, the
                search stops once the destination is reached.
        Returns:
            A tuple containing a dictionary of shortest distances and a
            dictionary of predecessor zones.
        Raises:
            MapError: If the graph's end zone is not reachable.
        """
        if not self.graph.is_reachable():
            msg = "End isn't reachable."
            raise MapError(msg)
        pq: list[tuple[int, str]] = []
        dist: dict[str, int] = {}
        dist[start] = 0
        pred: dict[str, str] = {}
        heappush(pq, (0, start))
        while pq:
            ccost, cname = heappop(pq)
            if ccost > dist[cname]:
                continue
            if stop is not None and cname == stop:
                break
            for nzone, _ in self.graph.neighbors_of(cname):
                if nzone.type == ZoneType.BLOCKED:
                    continue
                ncost = ccost + nzone.type.cost
                if nzone.name not in dist or ncost < dist[nzone.name]:
                    dist[nzone.name] = ncost
                    pred[nzone.name] = cname
                    heappush(pq, (ncost, nzone.name))
        return dist, pred

    def distances_to(self, target: str) -> dict[str, int]:
        """Calculate the shortest distances from a target zone.
        Args:
            target: Name of the target zone.
        Returns:
            A dictionary mapping each reachable zone name to its shortest
            distance from the target.
        """
        dist, _ = self._dijkstra(target, None)
        return dist

    def find_path(self, start: str, end: str) -> tuple[list[str], int]:
        """Find the shortest path between two zones.
        Args:
            start: Name of the starting zone.
            end: Name of the destination zone.
        Returns:
            A tuple containing the shortest path as a list of zone names and
            its total cost.
        """
        dist, pred = self._dijkstra(start, end)
        path: list[str] = []
        current = end
        while current != start:
            path.append(current)
            current = pred[current]
        path.append(start)
        path.reverse()
        return (path, dist[end])
