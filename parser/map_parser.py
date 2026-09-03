from models import Zone, ZoneType, Connection, Drone
from graph import Graph


class MapError(Exception):
    """Raised when the Map file is invalid."""


class MapParser():
    """Parse and validate map files into graphs and drone lists.
    The parser reads map definitions, creates the corresponding zones,
    connections, and drones, and validates the resulting map structure.
    """
    _VALID_KEYS: set[str] = {
        "hub", "connection", "nb_drones", "color",
        "zone", "max_drones", "max_link_capacity",
        "start_hub", "end_hub"
    }

    _MANDATORY_KEYS: set[str] = {
        "hub", "connection", "start_hub", "end_hub", "nb_drones"
    }

    def __init__(self, path: str) -> None:
        """Initialize a map parser.
            Args:
                path: Path to the map file.
        """
        self.path = path
        self.graph = Graph()
        self.drones: list[Drone] = []
        self.raw_values: dict[str, str] = {}
        self.connected: list[set[str]] = []

    def _read_file(self) -> list[str]:
        """Initialize a map parser.

        Args:
            path: Path to the map file.
        """
        try:
            with open(self.path) as fd:
                return (fd.readlines())
        except FileNotFoundError as exc:
            msg = f"Map file not found: {self.path!r}"
            raise MapError(msg) from exc
        except PermissionError as exc:
            msg = f"Permission denied reading Map file: {self.path!r}"
            raise MapError(msg) from exc
        except IsADirectoryError as exc:
            msg = f"Map path is a directory, not a file: {self.path!r}"
            raise MapError(msg) from exc
        except OSError as exc:
            msg = f"Cannot read Map file {self.path!r}: {exc}"
            raise MapError(msg) from exc

    def parse(self) -> tuple[Graph, list[Drone]]:
        """Parse and validate the map file.
        Returns:
            A tuple containing the parsed graph and list of drones.
        Raises:
            MapError: If the map contains invalid or missing data.
        """
        lines = self._read_file()
        for line_no, line in enumerate(lines):
            self._parse_line(line, line_no + 1)
        self._validate_map()
        return self.graph, self.drones

    def _parse_line(self, line: str, line_no: int) -> None:
        """Parse a single line from the map file.
        Args:
            line: Line to parse.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the line contains invalid data.
        """
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return
        key, value = self._split_line(stripped, line_no)
        self._validate_key(key, line_no)
        if key == "nb_drones":
            self._parse_drones(value, line_no)
        elif key == "hub":
            self._parse_hub(value, line_no)
        elif key == "start_hub":
            self._parse_start_hub(value, line_no)
        elif key == "end_hub":
            self._parse_end_hub(value, line_no)
        elif key == "connection":
            self._parse_connection(value, line_no)
        self.raw_values[key] = value

    def _validate_map(self) -> None:
        """Validate that the map contains all mandatory keys.
        Raises:
            MapError: If the map is empty or a mandatory key is missing.
        """
        if not self.raw_values:
            msg = f"Map file {self.path!r} contains no valid key-value pairs"
            raise MapError(msg)
        missing = self._MANDATORY_KEYS - self.raw_values.keys()
        if missing:
            msg = f"Missing mandatory key(s): {', '.join(sorted(missing))}"
            raise MapError(msg)

    def _split_line(self, line: str, line_no: int) -> tuple[str, str]:
        """Split a line into its key and value.
        Args:
            line: Line to split.
            line_no: Line number used for error reporting.
        Returns:
            A tuple containing the key and value.
        Raises:
            MapError: If the line has an invalid key-value format.
        """
        if ":" not in line:
            msg = f"Line {line_no}: missing ':' in: {line!r}"
            raise MapError(msg)
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            msg = f"Line {line_no}: empty key before ':' in: {line!r}"
            raise MapError(msg)
        if not value:
            msg = f"Line {line_no}: empty value for key {key!r}"
            raise MapError(msg)
        return key, value

    def _validate_key(self, key: str, line_no: int) -> None:
        """Validate a map key and its position in the file.
        Args:
            key: Key to validate.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the key is invalid, duplicated, or out of order.
        """
        if key not in self._VALID_KEYS:
            msg = f"Line {line_no}: unknown key {key!r}"
            raise MapError(msg)
        if (key == "start_hub" or key == "end_hub") and key in self.raw_values:
            msg = f"Line {line_no}: duplicate endpoints {key!r}"
            raise MapError(msg)
        if key != "nb_drones" and ("nb_drones" not in self.raw_values):
            msg = f"Line {line_no}:First line must be: 'nb_drones'"
            raise MapError(msg)

    def _parse_drones(self, value: str, line_no: int) -> None:
        """Parse the number of drones and create the corresponding objects.
        Args:
            value: Number of drones as a string.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the number of drones is not a positive integer.
        """
        try:
            n_drones = int(value)
        except ValueError:
            raise MapError(
                f"Line {line_no}: nb_drones must be a positive integer."
            )
        if n_drones <= 0:
            raise MapError(
                f"Line {line_no}: nb_drones must be a positive integer."
            )
        for i in range(n_drones):
            self.drones.append(Drone(i))

    def _parse_hub(self, value: str, line_no: int) -> None:
        """Parse a hub and add it to the graph.
        Args:
            value: Hub definition to parse.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the hub definition is invalid or duplicated.
        """
        zone = self._parse_zone(value, line_no)

        if zone.name in self.graph.zones:
            raise MapError(
                f"Line {line_no}: duplicate zone name."
            )

        if " " in zone.name or "-" in zone.name:
            raise MapError(
                f"Line {line_no}: invalid characters "
                f"(' ' or '-') in zone name."
            )

        self.graph.zones[zone.name] = zone
        self.graph.adjacency[zone.name] = []

    def _parse_start_hub(self, value: str, line_no: int) -> None:
        """Parse and set the start hub of the graph.
        Args:
            value: Start hub definition to parse.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the hub definition is invalid.
        """
        zone = self._parse_zone(value, line_no)
        self.graph.set_start(zone)
        self.graph.adjacency[zone.name] = []

    def _parse_end_hub(self, value: str, line_no: int) -> None:
        """Parse and set the end hub of the graph.
        Args:
            value: End hub definition to parse.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the hub definition is invalid.
        """
        zone = self._parse_zone(value, line_no)
        self.graph.set_end(zone)
        self.graph.adjacency[zone.name] = []

    def _parse_connection(self, value: str, line_no: int) -> None:
        """Parse a connection and add it to the graph.
        Args:
            value: Connection definition to parse.
            line_no: Line number used for error reporting.
        Raises:
            MapError: If the connection is invalid, duplicated, references
                an unknown zone, or connects a zone to itself.
        """
        cnc = self._parse_connection_value(value, line_no)
        if cnc.z1 not in self.graph.adjacency:
            msg = f"Line {line_no}: {cnc.z1} doesn't exist."
            raise MapError(msg)
        if cnc.z2 not in self.graph.adjacency:
            msg = f"Line {line_no}: {cnc.z2} doesn't exist."
            raise MapError(msg)
        if {cnc.z1, cnc.z2} in self.connected:
            msg = f"Line {line_no}: duplicate connection."
            raise MapError(msg)
        if cnc.z1 == cnc.z2:
            msg = f"Line {line_no}: {cnc.z1} connects zone to itself."
            raise MapError(msg)
        self.graph.adjacency[cnc.z1].append(cnc)
        self.graph.adjacency[cnc.z2].append(cnc)
        self.graph.connections.append(cnc)
        self.connected.append({cnc.z1, cnc.z2})

    def _parse_connection_value(self, value: str, line_no: int) -> Connection:
        """Parse a connection definition into a Connection object.
        Args:
            value: Connection definition to parse.
            line_no: Line number used for error reporting.
        Returns:
            The parsed Connection object.
        Raises:
            MapError: If the connection format or capacity is invalid.
        """
        max_capacity = 1
        if "[" in value:
            zones, metadata = value.split("[", 1)
            metadata = metadata.rstrip("]")
            key, value = metadata.split("=")
            if key != "max_link_capacity":
                raise MapError(
                    f"Line {line_no}: invalid connection metadata."
                )
            if '.' in value or '-' in value:
                msg = f"Line {line_no}: max capacity must be positive integer."
                raise MapError(msg)
            max_capacity = int(value)
        else:
            zones = value
        try:
            zone1, zone2 = zones.strip().split("-", 1)
        except ValueError:
            raise MapError(
                f"Line {line_no}: invalid connection."
            )
        return Connection(zone1, zone2, max_capacity)

    def _parse_zone(self, text: str, line_no: int) -> Zone:
        """Parse a zone definition into a Zone object.
        Args:
            text: Zone definition to parse.
            line_no: Line number used for error reporting.
        Returns:
            The parsed Zone object.
        Raises:
            MapError: If the zone definition is invalid.
        """
        if "[" in text:
            return self._parse_zone_meta(text, line_no)
        else:
            try:
                name, sx, sy = text.strip().split(" ", 2)
                x = int(sx)
                y = int(sy)
            except ValueError:
                raise MapError(
                    f"Line {line_no}: invalid zone definition."
                )
        return Zone(name, x, y)

    def _parse_zone_meta(self, text: str, line_no: int) -> Zone:
        """Parse a zone definition containing metadata.
        Args:
            text: Zone definition and metadata to parse.
            line_no: Line number used for error reporting.
        Returns:
            The parsed Zone object with its metadata.
        Raises:
            MapError: If the zone definition or metadata is invalid.
        """
        ztype = ZoneType.NORMAL
        color = None
        max_drones = 1
        zone, metadata = text.split("[", 1)
        metadata = metadata.rstrip("]")
        for item in metadata.split():
            try:
                key, value = item.split("=", 1)
            except ValueError:
                raise MapError(
                    f"Line {line_no}: invalid metadata."
                )
            if key == "zone":
                try:
                    ztype = ZoneType(value)
                except ValueError:
                    raise MapError(
                        f"Line {line_no}: invalid zone type."
                    )
            elif key == "color":
                color = value
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    raise MapError(
                        f"Line {line_no}: max_drones "
                        f"must be an integer."
                    )
                if max_drones <= 0:
                    raise MapError(
                        f"Line {line_no}: max_drones "
                        f"must be positive."
                    )
        name, sx, sy = zone.split(" ", 2)
        x = int(sx)
        y = int(sy)
        return Zone(name, x, y, ztype, color, max_drones)
