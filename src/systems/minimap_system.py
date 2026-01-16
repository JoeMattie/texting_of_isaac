"""Mini-map system for dungeon navigation overlay."""
import esper


class MiniMapSystem(esper.Processor):
    """Renders mini-map overlay showing explored rooms.

    The mini-map displays a 7x7 grid (±3 rooms from current position) with:
    - ◆ = Current room
    - ■ = Visited room
    - □ = Adjacent unvisited room (connected by door)
    - (space) = Unknown/unexplored
    """

    def __init__(self):
        """Initialize mini-map system."""
        super().__init__()

    def process(self):
        """Process is not used - minimap renders on demand."""
        pass

    def render(self, minimap, dungeon) -> list[str]:
        """Generate mini-map display lines.

        Args:
            minimap: MiniMap component with current position and visible rooms
            dungeon: Dungeon instance with room connections

        Returns:
            List of strings representing the mini-map display
        """
        lines = []

        # Top border
        lines.append("╔═══════╗")

        # Get display bounds (±3 from current position)
        min_x, min_y, max_x, max_y = minimap.get_display_bounds()

        # Render each row
        for y in range(min_y, max_y + 1):
            row = "║"
            for x in range(min_x, max_x + 1):
                position = (x, y)

                if position == minimap.current_position:
                    # Current room
                    row += "◆"
                elif position in minimap.visible_rooms:
                    # Visited room
                    row += "■"
                elif minimap.should_show_room(position, dungeon):
                    # Adjacent unvisited room
                    row += "□"
                else:
                    # Unknown
                    row += " "
            row += "║"
            lines.append(row)

        # Bottom border
        lines.append("╚═══════╝")

        return lines
