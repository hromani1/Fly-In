from graph import Graph


class RTError(Exception):
    """Raised when there is an error in reservation."""


class ReservationTable():
    """Track zone and connection reservations for each turn."""
    def __init__(self, graph: Graph) -> None:
        """Initialize a reservation table for a graph.
        Args:
            graph: Graph whose zones and connections are being reserved.
        """
        self.graph = graph
        self._zone_occupancy: dict[int, dict[str, int]] = {}
        self._cnc_usg: dict[int, dict[str, int]] = {}

    def _connection_key(self, z1: str, z2: str) -> str:
        """Create a consistent key for a connection.
        Args:
            z1: Name of the first zone.
            z2: Name of the second zone.
        Returns:
            A normalized connection key independent of zone order.
        """
        return "-".join(sorted((z1, z2)))

    def cnc_has_room(self, cz1: str, cz2: str, turn: int) -> bool:
        """Check whether a connection has available capacity at a turn.
        Args:
            cz1: Name of the first zone.
            cz2: Name of the second zone.
            turn: Turn at which the connection is being checked.
        Returns:
            True if the connection has available capacity, otherwise False.
        Raises:
            RTError: If the connection does not exist.
        """
        cncname = self._connection_key(cz1, cz2)
        n: int = self._cnc_usg.get(turn, {}).get(cncname, 0)
        cnc = self.graph.get_cnc(cz1, cz2)
        if not cnc:
            raise RTError("Connection doesnt exist!")
        if n < cnc.max_cap:
            return True
        else:
            return False

    def reserve_cnc(self, cz1: str, cz2: str, turn: int) -> None:
        """Reserve one unit of connection capacity for a turn.
        Args:
            cz1: Name of the first zone.
            cz2: Name of the second zone.
            turn: Turn for which the connection is reserved.
        Raises:
            RTError: If the connection is full.
        """
        if not self.cnc_has_room(cz1, cz2, turn):
            msg = f"Connection {cz1}-{cz2} is full"
            raise RTError(msg)
        cnc = self._connection_key(cz1, cz2)
        cncu = self._cnc_usg
        cncu.setdefault(turn, {})
        cncu[turn][cnc] = cncu[turn].get(cnc, 0) + 1

    def zone_has_room(self, zone_name: str, turn: int) -> bool:
        """Check whether a zone has available capacity at a turn.
        Args:
            zone_name: Name of the zone to check.
            turn: Turn at which the zone is being checked.
        Returns:
            True if the zone has available capacity, otherwise False.
        """
        n: int = self._zone_occupancy.get(turn, {}).get(zone_name, 0)
        if self.graph.zones[zone_name] in (self.graph.start, self.graph.end):
            return True
        if n < self.graph.zones[zone_name].max_drones:
            return True
        else:
            return False

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """Reserve one unit of zone capacity for a turn.
        Args:
            zone_name: Name of the zone to reserve.
            turn: Turn for which the zone is reserved.
        Raises:
            RTError: If the zone is full.
        """
        if not self.zone_has_room(zone_name, turn):
            msg = f"Zone({zone_name}) is full"
            raise RTError(msg)
        zone = self._zone_occupancy
        zone.setdefault(turn, {})
        zone[turn][zone_name] = zone[turn].get(zone_name, 0) + 1
