"""Boss-related components."""
from dataclasses import dataclass


@dataclass
class Boss:
    """Boss entity marker and state."""
    boss_type: str  # "boss_a", "boss_b", "boss_c"
    current_phase: int = 1
    phase_2_threshold: float = 0.5  # 50% HP triggers phase 2
    has_transitioned: bool = False  # Prevent double-transition


@dataclass
class BossAI:
    """Boss-specific AI behavior."""
    pattern_name: str  # Current pattern: "spiral", "wave", "pulse", etc.
    pattern_timer: float = 0.0  # Time until next pattern execution
    pattern_cooldown: float = 2.0  # Time between patterns
    teleport_timer: float = 0.0  # Time until next teleport
    teleport_cooldown: float = 6.0  # Changes per phase


@dataclass
class Trapdoor:
    """Floor transition marker."""
    next_floor: int  # Which floor this leads to
