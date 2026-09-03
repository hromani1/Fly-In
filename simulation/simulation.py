from scheduler import Scheduler
from models import Drone, ZoneType
from graph import Graph


class Simulator():
    """Simulate drone movement according to a generated schedule."""
    def __init__(self, graph: Graph, scheduler: Scheduler,
                 drones: list[Drone]) -> None:
        """Initialize the simulator and generate a drone schedule.
        Args:
            graph: Graph containing the zones and connections.
            scheduler: Scheduler used to generate drone paths.
            drones: List of drones to simulate.
        """
        self.scheduler = scheduler
        self.drones = drones
        self.graph = graph
        self.schedule: dict[int, list[tuple[int, str]]] = (
            self.scheduler.schedule_all(
                self.drones,
                self.graph.start.name,
                self.graph.end.name,
            )
        )

    def extract_moves(self) -> dict[int, str]:
        """Extract drone movements from the schedule.
        Returns:
            A dictionary mapping each turn to the movements that occur
            during that turn.
        """
        moves: dict[int, str] = {}
        for i in range(len(self.drones)):
            for res in self.schedule[i]:
                if self.graph.zones[res[1]].type == ZoneType.RESTRICTED:
                    turn = res[0] - 1
                    moves.setdefault(turn, "")
                    moves[turn] += f"D{i}-Cnc{res[1]} "
                moves.setdefault(res[0], "")
                moves[res[0]] += f"D{i}-{res[1]} "
        return moves
