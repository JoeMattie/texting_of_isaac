"""Boss AI system for pattern execution, phase transitions, and teleportation."""
import esper
import random
import math
from src.components.core import Position, Health
from src.components.combat import Collider, Projectile
from src.components.boss import Boss, BossAI
from src.components.game import Player, Invincible
from src.components.core import Velocity, Sprite
from src.systems.boss_patterns import get_pattern_for_boss
from src.entities.bosses import BOSS_DATA
from src.config import Config


class BossAISystem(esper.Processor):
    """System for boss AI behavior including patterns, phases, and teleportation.

    Processes after AISystem (priority 1), before EnemyShootingSystem (priority 2).
    """

    def __init__(self):
        """Initialize the boss AI system."""
        self.dt = 0.0

    def process(self):
        """Process boss AI behavior for all bosses."""
        # Find player position for teleport distance checking
        player_pos = None
        for ent, (player, pos) in esper.get_components(Player, Position):
            player_pos = pos
            break

        # Process each boss
        for boss_ent, (boss, boss_ai, pos, health) in esper.get_components(
            Boss, BossAI, Position, Health
        ):
            # Check for phase transition
            self._check_phase_transition(boss_ent, boss, boss_ai, health)

            # Update and execute pattern
            self._update_pattern(boss_ent, boss, boss_ai, pos)

            # Update and execute teleport
            self._update_teleport(boss_ent, boss_ai, pos, player_pos)

    def _check_phase_transition(self, boss_ent: int, boss: Boss,
                               boss_ai: BossAI, health: Health):
        """Check if boss should transition to phase 2.

        Args:
            boss_ent: Boss entity ID
            boss: Boss component
            boss_ai: BossAI component
            health: Health component
        """
        # Only transition if not already transitioned
        if boss.has_transitioned:
            return

        # Check if HP is at or below threshold
        hp_ratio = health.current / health.max
        if hp_ratio <= boss.phase_2_threshold:
            # Transition to phase 2
            boss.current_phase = 2
            boss.has_transitioned = True

            # Get boss data
            data = BOSS_DATA[boss.boss_type]

            # Switch to phase 2 pattern
            if data["phase_2_patterns"]:
                boss_ai.pattern_name = data["phase_2_patterns"][0]

            # Update teleport cooldown to phase 2 speed
            boss_ai.teleport_cooldown = data["teleport_cooldowns"]["phase_2"]

            # Grant brief invulnerability
            esper.add_component(boss_ent, Invincible(
                Config.BOSS_PHASE_TRANSITION_INVULN
            ))

    def _update_pattern(self, boss_ent: int, boss: Boss,
                       boss_ai: BossAI, pos: Position):
        """Update pattern timer and execute pattern when ready.

        Args:
            boss_ent: Boss entity ID
            boss: Boss component
            boss_ai: BossAI component
            pos: Boss position
        """
        # Decrement pattern timer
        boss_ai.pattern_timer -= self.dt

        # Execute pattern when timer reaches 0
        if boss_ai.pattern_timer <= 0:
            self._execute_pattern(boss, boss_ai, pos)
            # Reset timer to cooldown
            boss_ai.pattern_timer = boss_ai.pattern_cooldown

    def _execute_pattern(self, boss: Boss, boss_ai: BossAI, pos: Position):
        """Execute boss attack pattern.

        Args:
            boss: Boss component
            boss_ai: BossAI component
            pos: Boss position
        """
        # Get pattern function
        pattern_func = get_pattern_for_boss(
            boss.boss_type,
            boss.current_phase,
            boss_ai.pattern_name
        )

        if pattern_func is None:
            return

        # Generate projectile data
        projectiles = pattern_func(pos.x, pos.y)

        # Create enemy projectiles
        for proj_data in projectiles:
            self._create_enemy_projectile(
                proj_data['x'],
                proj_data['y'],
                proj_data['vx'],
                proj_data['vy']
            )

    def _create_enemy_projectile(self, x: float, y: float, vx: float, vy: float):
        """Create an enemy projectile entity.

        Args:
            x, y: Starting position
            vx, vy: Velocity components
        """
        projectile = esper.create_entity()
        esper.add_component(projectile, Position(x, y))
        esper.add_component(projectile, Velocity(vx, vy))
        esper.add_component(projectile, Projectile(damage=1.0, owner=-1))
        esper.add_component(projectile, Collider(Config.PROJECTILE_HITBOX))
        esper.add_component(projectile, Sprite('*', 'yellow'))

    def _update_teleport(self, boss_ent: int, boss_ai: BossAI,
                        pos: Position, player_pos: Position | None):
        """Update teleport timer and teleport when ready.

        Args:
            boss_ent: Boss entity ID
            boss_ai: BossAI component
            pos: Boss position
            player_pos: Player position (if exists)
        """
        # Decrement teleport timer
        boss_ai.teleport_timer -= self.dt

        # Teleport when timer reaches 0
        if boss_ai.teleport_timer <= 0:
            self._teleport_boss(pos, player_pos)
            # Reset timer to cooldown
            boss_ai.teleport_timer = boss_ai.teleport_cooldown

    def _teleport_boss(self, pos: Position, player_pos: Position | None):
        """Teleport boss to a random safe position.

        Args:
            pos: Boss position to update
            player_pos: Player position (if exists)
        """
        # Get all teleport positions
        available_positions = list(Config.BOSS_TELEPORT_POSITIONS)

        # Filter positions that are too close to player
        if player_pos is not None:
            safe_positions = []
            for tp_x, tp_y in available_positions:
                distance = math.sqrt(
                    (tp_x - player_pos.x)**2 +
                    (tp_y - player_pos.y)**2
                )
                if distance >= Config.BOSS_TELEPORT_MIN_PLAYER_DISTANCE:
                    safe_positions.append((tp_x, tp_y))

            # Use safe positions if any exist, otherwise use all positions
            if safe_positions:
                available_positions = safe_positions

        # Select random position
        if available_positions:
            new_x, new_y = random.choice(available_positions)
            pos.x = new_x
            pos.y = new_y
