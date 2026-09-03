import pygame
from graph import Graph
from models import Zone, ZoneType
from matplotlib.colors import to_rgb


class Visualizer():
    """Display a visual simulation of drone movement on a graph."""
    def __init__(self, graph: Graph,
                 schedule: dict[int, list[tuple[int, str]]]) -> None:
        """Initialize the visualizer and configure the display.
        Args:
            graph: Graph containing the zones and connections to display.
            schedule: Mapping of drone IDs to their scheduled paths.
        """
        pygame.init()
        self.graph = graph
        self.schedule: dict[int, list[tuple[int, str]]] = schedule
        self.current_turn: int = 0
        self.turn_duration: int = 500
        self.last_turn_update: int = pygame.time.get_ticks()
        self.width: int = 1200
        self.height: int = 800
        self.padding: int = 50
        self.screen: pygame.Surface = (
            pygame.display.set_mode(
                (self.width, self.height)
                )
        )
        pygame.display.set_caption("Flyin Visualizer")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.min_x: int = min(zone.x for zone in self.graph.zones.values())
        self.max_x: int = max(zone.x for zone in self.graph.zones.values())
        self.min_y: int = min(zone.y for zone in self.graph.zones.values())
        self.max_y: int = max(zone.y for zone in self.graph.zones.values())
        map_width: int = self.max_x - self.min_x
        if map_width == 0:
            map_width += 1
        map_height: int = self.max_y - self.min_y
        if map_height == 0:
            map_height += 1
        available_width: int = self.width - 2 * self.padding
        available_height: int = self.height - 2 * self.padding
        scale_x: float = available_width / map_width
        scale_y: float = available_height / map_height
        self.scale: float = min(scale_x, scale_y)
        self.font: pygame.font.Font = pygame.font.Font(None, 12)
        self.max_turn: int = max(
            turn
            for path in self.schedule.values()
            for turn, _ in path
        )
        self.paused: bool = False
        self.ui_font: pygame.font.Font = pygame.font.Font(None, 28)

    def _to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert graph coordinates to screen coordinates.
        Args:
            x: X-coordinate in the graph.
            y: Y-coordinate in the graph.
        Returns:
            A tuple containing the corresponding screen coordinates.
        """
        n_x: float = float(x - self.min_x) * self.scale + self.padding
        n_y: float = float(y - self.min_y) * self.scale + self.padding
        return (float(n_x), float(n_y))

    def _update(self) -> None:
        """Update the current simulation turn based on elapsed time."""
        if self.paused:
            return
        current_time: int = pygame.time.get_ticks()
        if current_time - self.last_turn_update >= self.turn_duration:
            if self.current_turn < self.max_turn:
                self.current_turn += 1
            self.last_turn_update = current_time

    def run(self) -> None:
        """Run the visualization loop until the window is closed."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _handle_events(self) -> None:
        """Handle events received from the Pygame event queue."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

    def _draw(self) -> None:
        """Draw the current state of the simulation."""
        self.screen.fill((30, 30, 30))
        self._draw_connections()
        self._draw_zones()
        self._draw_drones(self.current_turn)
        self._draw_turn()

    def _draw_turn(self) -> None:
        """Draw the current simulation turn."""
        text: pygame.Surface = self.ui_font.render(
            f"Turn: {self.current_turn}",
            True,
            (255, 255, 255)
        )
        self.screen.blit(text, (20, 20))

    def _draw_connections(self) -> None:
        """Draw all graph connections on the screen."""
        for cnc in self.graph.connections:
            z1 = self.graph.zones[cnc.z1]
            z2 = self.graph.zones[cnc.z2]
            pygame.draw.line(self.screen,
                             (150, 150, 150),
                             (self._to_screen(z1.x, z1.y)),
                             (self._to_screen(z2.x, z2.y)),
                             3)

    def _draw_zones(self) -> None:
        """Draw all zones and their labels on the screen."""
        for zone in self.graph.zones.values():
            position: tuple[float, float] = self._to_screen(
                zone.x,
                zone.y
            )
            pygame.draw.circle(
                self.screen,
                self._get_zone_color(zone),
                position,
                15
            )
            label: pygame.Surface = self.font.render(
                zone.name,
                True,
                (255, 255, 255)
            )
            label_position: tuple[float, float] = (position[0] - 20,
                                                   position[1] + 20)
            self.screen.blit(label, label_position)

    def _get_zone_color(self, zone: Zone) -> tuple[int, ...]:
        """Get the display color for a zone.
        Args:
            zone: Zone whose display color is requested.
        Returns:
            A Pygame-compatible RGB color tuple.
        """
        if zone.color is None or zone.color == "rainbow":
            return (255, 255, 255)
        rgb: tuple[float, float, float] = to_rgb(zone.color)
        return tuple(int(value * 255) for value in rgb)

    def _get_drone_position(self, drone_id: int,
                            turn: int) -> tuple[float, float] | None:
        """Calculate a drone's screen position for a given turn.
        Args:
            drone_id: ID of the drone whose position is requested.
            turn: Simulation turn for which to calculate the position.
        Returns:
            The drone's screen coordinates, or None if the drone has not
            entered the simulation yet.
        """
        path: list[tuple[int, str]] = self.schedule[drone_id]
        current_zone: str = ""
        for path_turn, zone_name in path:
            if path_turn == turn + 1:
                if self.graph.zones[zone_name].type == ZoneType.RESTRICTED:
                    zone1 = self.graph.zones[current_zone]
                    zone2 = self.graph.zones[zone_name]
                    return self._to_screen((zone1.x + zone2.x) / 2,
                                           (zone1.y + zone2.y) / 2)
            if path_turn > turn + 1:
                break
            current_zone = zone_name
            if path_turn == turn:
                break
        if current_zone == "":
            return None
        zone: Zone = self.graph.zones[current_zone]
        return self._to_screen(zone.x, zone.y)

    def _draw_drones(self, turn: int) -> None:
        """Draw all drones at their positions for the current turn.
        Args:
            turn: Simulation turn to display.
        """
        white: tuple[int, int, int] = (255, 255, 255)
        for drone in self.schedule:
            pos = self._get_drone_position(drone, turn)
            if pos is None:
                continue
            pygame.draw.circle(self.screen, white, pos, 8)
            label: pygame.Surface = self.font.render(
                "D" + str(drone),
                True,
                (0, 0, 0)
                )
            label_position: tuple[float, float] = (pos[0] - 4, pos[1] - 2)
            self.screen.blit(label, label_position)
