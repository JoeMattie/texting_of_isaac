"""Game state management system for victory and game over detection."""
import esper
from src.game.state import GameState
from src.components.core import Health
from src.components.game import Player


class GameStateSystem(esper.Processor):
    """Manages game states and detects win/loss conditions.

    Monitors for:
    - Victory condition (floor_transition_system.victory flag)
    - Game over condition (player HP <= 0)

    Game states:
    - PLAYING: Normal gameplay
    - VICTORY: Player has won (defeated final boss)
    - GAME_OVER: Player has died

    When in VICTORY or GAME_OVER states, game processing is paused.
    """

    def __init__(self, floor_transition_system):
        """Initialize the game state system.

        Args:
            floor_transition_system: Reference to FloorTransitionSystem for victory detection
        """
        super().__init__()
        self.current_state = GameState.PLAYING
        self.floor_transition_system = floor_transition_system

    def process(self):
        """Check for victory and game over conditions.

        Updates current_state based on:
        1. Victory flag from floor_transition_system
        2. Player death (HP <= 0)

        Returns early if already in terminal state (VICTORY or GAME_OVER).
        """
        # If in terminal state, don't process further
        if self.current_state in (GameState.VICTORY, GameState.GAME_OVER):
            return

        # Check for victory condition (checked first)
        if self.floor_transition_system.victory:
            self.current_state = GameState.VICTORY
            return

        # Check for game over condition (player death)
        player_entities = list(esper.get_components(Player, Health))

        # If no player exists, can't check death
        if not player_entities:
            return

        # Get player health (should only be one player)
        player_ent, (player, health) = player_entities[0]

        # Check if player is dead
        if health.current <= 0:
            self.current_state = GameState.GAME_OVER
            return

    def get_state_screen_text(self) -> str:
        """Get the screen text for the current game state.

        Returns:
            Empty string for PLAYING state
            Victory message for VICTORY state
            Game over message for GAME_OVER state
        """
        if self.current_state == GameState.PLAYING:
            return ""

        if self.current_state == GameState.VICTORY:
            return """=== VICTORY ===

You defeated the final boss!
Floors completed: 3

Press R to restart
Press Q to quit"""

        if self.current_state == GameState.GAME_OVER:
            return """=== GAME OVER ===

You died!

Press R to restart
Press Q to quit"""

        return ""
