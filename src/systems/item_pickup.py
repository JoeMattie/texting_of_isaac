"""Item pickup and stat modification system."""
from typing import Optional
import esper
import math
from src.components.core import Position
from src.components.combat import Stats, Collider
from src.components.game import Player, Item, CollectedItems


class ItemPickupSystem(esper.Processor):
    """Handles item pickup detection and stat application."""

    def __init__(self):
        super().__init__()
        self.notification: Optional[str] = None
        self.notification_timer: float = 0.0
        self.dt: float = 0.0

    def process(self):
        """Check for item pickups and apply effects."""
        # Decrement notification timer
        if self.notification_timer > 0:
            self.notification_timer -= self.dt
            if self.notification_timer <= 0:
                self.notification = None

        # Check for Player + Item collisions
        for player_ent, (player, player_pos, player_col) in esper.get_components(Player, Position, Collider):
            for item_ent, (item, item_pos, item_col) in esper.get_components(Item, Position, Collider):
                # Skip if entity was already deleted in this frame
                if not esper.entity_exists(item_ent):
                    continue
                if self._check_overlap(player_pos, player_col, item_pos, item_col):
                    self._pickup_item(player_ent, item_ent, item)

    def _check_overlap(self, pos1: Position, col1: Collider, pos2: Position, col2: Collider) -> bool:
        """Check if two circles overlap.

        Args:
            pos1: First position
            col1: First collider
            pos2: Second position
            col2: Second collider

        Returns:
            True if circles overlap
        """
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (col1.radius + col2.radius)

    def _pickup_item(self, player_ent: int, item_ent: int, item: Item):
        """Apply item effects and remove item entity.

        Args:
            player_ent: Player entity ID
            item_ent: Item entity ID
            item: Item component
        """
        from src.config import Config

        # Apply stat modifiers
        stats = esper.component_for_entity(player_ent, Stats)
        for stat_name, value in item.stat_modifiers.items():
            if stat_name in ["damage", "fire_rate"]:
                # Additive stats
                setattr(stats, stat_name, getattr(stats, stat_name) + value)
            elif stat_name in ["speed", "shot_speed"]:
                # Multiplicative stats
                setattr(stats, stat_name, getattr(stats, stat_name) * value)

        # Add to collected items
        if not esper.has_component(player_ent, CollectedItems):
            esper.add_component(player_ent, CollectedItems())
        collected = esper.component_for_entity(player_ent, CollectedItems)
        collected.items.append(item)

        # Show notification
        self.notification = f"Picked up: {item.name}"
        self.notification_timer = Config.NOTIFICATION_DURATION

        # Remove item entity
        esper.delete_entity(item_ent)
