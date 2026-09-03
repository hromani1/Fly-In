class Drone():
    """Represent a drone in the simulation."""
    def __init__(self, id: int):
        """Initialize a drone.
        Args:
            id: Unique identifier of the drone.
        """
        self.id = id

    def __str__(self) -> str:
        """Return a string representation of the drone.
        Returns:
            A string containing the drone's ID.
        """
        return (
            f"id:{self.id}"
        )
