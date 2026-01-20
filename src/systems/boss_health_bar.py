"""Boss health bar display system."""
import esper
from src.components.boss import Boss
from src.components.core import Health
from src.entities.bosses import BOSS_DATA
from src.config import Config


class BossHealthBarSystem(esper.Processor):
    """System for generating boss health bar display text."""

    def __init__(self, world_name: str):
        """Initialize the boss health bar system.

        Args:
            world_name: Name of the ECS world
        """
        super().__init__()
        self.world_name = world_name

    def get_health_bar_text(self) -> str:
        """Generate boss health bar text.

        Returns:
            Formatted health bar string, or empty string if no boss exists.
            Format: "Boss Name HP: current/max [████████░░░░]"
        """
        esper.switch_world(self.world_name)

        # Query for boss entities (Boss + Health)
        boss_entities = esper.get_components(Boss, Health)

        # If no boss exists, return empty string
        if not boss_entities:
            return ""

        # Get the first boss (should only be one)
        entity, (boss, health) = boss_entities[0]

        # Get boss name from BOSS_DATA
        boss_name = BOSS_DATA[boss.boss_type]["name"]

        # Calculate HP percentage
        hp_percentage = health.current / health.max if health.max > 0 else 0.0

        # Generate visual bar
        filled_length = int(hp_percentage * Config.BOSS_HEALTH_BAR_WIDTH)
        empty_length = Config.BOSS_HEALTH_BAR_WIDTH - filled_length

        bar = '█' * filled_length + '░' * empty_length

        # Format and return the health bar string
        return f"{boss_name} HP: {health.current}/{health.max} [{bar}]"

    def process(self):
        """Process method (not used for this display-only system)."""
        pass
