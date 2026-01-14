"""AI system for enemy behavior."""
import esper
import math
from src.components.core import Position, Velocity
from src.components.game import Enemy, Player, AIBehavior


class AISystem(esper.Processor):
    """Handles enemy AI behavior."""

    def __init__(self):
        self.dt = 0.0

    def process(self):
        """Process AI for all enemies."""
        # Find player position
        player_pos = None
        for ent, (player, pos) in esper.get_components(Player, Position):
            player_pos = pos
            break

        if not player_pos:
            return

        # Process each enemy
        for ent, (enemy, pos, vel) in esper.get_components(Enemy, Position, Velocity):
            # Decrement pattern cooldowns if enemy has AI
            if esper.has_component(ent, AIBehavior):
                ai = esper.component_for_entity(ent, AIBehavior)
                for pattern_name in ai.pattern_cooldowns:
                    ai.pattern_cooldowns[pattern_name] -= self.dt

            # Process movement AI
            if enemy.type == "chaser":
                self._ai_chaser(pos, vel, player_pos)
            elif enemy.type == "shooter":
                self._ai_shooter(pos, vel, player_pos)
            elif enemy.type == "orbiter":
                self._ai_orbiter(pos, vel, player_pos)
            elif enemy.type == "turret":
                self._ai_turret(pos, vel, player_pos)
            elif enemy.type == "tank":
                self._ai_tank(pos, vel, player_pos)

    def _ai_chaser(self, pos: Position, vel: Velocity, player_pos: Position):
        """Chaser AI: move toward player."""
        dx = player_pos.x - pos.x
        dy = player_pos.y - pos.y

        # Normalize
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # Move at chaser speed (3.0)
        vel.dx = dx * 3.0
        vel.dy = dy * 3.0

    def _ai_shooter(self, pos: Position, vel: Velocity, player_pos: Position):
        """Shooter AI: stay mostly still."""
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_orbiter(self, pos: Position, vel: Velocity, player_pos: Position):
        """Orbiter AI: circle around player."""
        # TODO: Implement circular movement
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_turret(self, pos: Position, vel: Velocity, player_pos: Position):
        """Turret AI: stationary."""
        vel.dx = 0.0
        vel.dy = 0.0

    def _ai_tank(self, pos: Position, vel: Velocity, player_pos: Position):
        """Tank AI: slow movement toward player."""
        dx = player_pos.x - pos.x
        dy = player_pos.y - pos.y

        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        vel.dx = dx * 2.0
        vel.dy = dy * 2.0
