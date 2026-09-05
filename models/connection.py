class Connection():
    """Represent a connection between two zones."""
    def __init__(self, z1: str, z2: str, max_cap: int = 1) -> None:
        """Initialize a connection.
        Args:
            z1: Name of the first connected zone.
            z2: Name of the second connected zone.
            max_cap: Maximum number of drones allowed on the connection.
        """
        self.z1 = z1
        self.z2 = z2
        self.max_cap = max_cap

    def __str__(self) -> str:
        """Return a string representation of the connection.
        Returns:
            A string containing the connection's zones and maximum capacity.
        """
        return (
            f"Connection(z1={self.z1!r}, "
            f"z2={self.z2!r}, "
            f"max_cap={self.max_cap})"
        )
