from enum import Enum


class ZoneType(Enum):
    """Define the types of zones available in the graph."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    PRIORITY = "priority"
    RESTRICTED = "restricted"

    @property
    def cost(self) -> int:
        """Return the movement cost associated with the zone type.
        Returns:
            The cost of entering a zone of this type.
        """
        costs = {
            ZoneType.NORMAL: 1,
            ZoneType.PRIORITY: 1,
            ZoneType.RESTRICTED: 2
        }
        return costs[self]


class Zone():
    def __init__(self, name: str, x: int, y: int,
                 ztype: ZoneType = ZoneType.NORMAL, color: str | None = None,
                 max_drones: int = 1) -> None:
        """Represent a zone in the graph."""
        self.name = name
        self.x = x
        self.y = y
        self.type = ztype
        self.color = color
        self.max_drones = max_drones

    def __str__(self) -> str:
        """Return a string representation of the zone.
        Returns:
            A string containing the zone's properties.
        """
        return (
            f"Zone(name={self.name!r}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"type={self.type!r}, "
            f"color={self.color!r}, "
            f"max_drones={self.max_drones})"
        )
