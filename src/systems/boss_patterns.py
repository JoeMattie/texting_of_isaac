"""Boss attack pattern generation."""
import math
from typing import Optional, Callable


def generate_spiral_pattern(x: float, y: float, rotation: float = 0.0,
                            count: int = 8, speed: float = 4.0) -> list[dict]:
    """Generate spiral pattern projectiles.

    Args:
        x, y: Boss position
        rotation: Current rotation angle in degrees
        count: Number of projectiles
        speed: Projectile speed

    Returns:
        List of projectile data dicts with x, y, vx, vy
    """
    projectiles = []
    angle_step = 360.0 / count

    for i in range(count):
        angle_deg = (i * angle_step + rotation) % 360
        angle_rad = math.radians(angle_deg)

        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed

        projectiles.append({
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy
        })

    return projectiles


def generate_wave_pattern(x: float, y: float, sweep_angle: float = 0.0,
                         count: int = 5, arc_width: float = 60.0,
                         speed: float = 5.0) -> list[dict]:
    """Generate wave pattern projectiles.

    Args:
        x, y: Boss position
        sweep_angle: Current sweep angle offset
        count: Number of projectiles in wave
        arc_width: Arc width in degrees
        speed: Projectile speed

    Returns:
        List of projectile data dicts
    """
    projectiles = []
    start_angle = sweep_angle - (arc_width / 2)
    angle_step = arc_width / (count - 1) if count > 1 else 0

    for i in range(count):
        angle_deg = start_angle + (i * angle_step)
        angle_rad = math.radians(angle_deg)

        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed

        projectiles.append({
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy
        })

    return projectiles


def generate_pulse_pattern(x: float, y: float, count: int = 12,
                          speed: float = 3.5) -> list[dict]:
    """Generate pulse (complete ring) pattern projectiles.

    Args:
        x, y: Boss position
        count: Number of projectiles in ring
        speed: Projectile speed

    Returns:
        List of projectile data dicts
    """
    projectiles = []
    angle_step = 360.0 / count

    for i in range(count):
        angle_deg = i * angle_step
        angle_rad = math.radians(angle_deg)

        vx = math.cos(angle_rad) * speed
        vy = math.sin(angle_rad) * speed

        projectiles.append({
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy
        })

    return projectiles


def get_pattern_for_boss(boss_type: str, phase: int,
                        pattern_name: str) -> Optional[Callable]:
    """Get pattern generation function for boss, phase, and pattern name.

    Args:
        boss_type: "boss_a", "boss_b", "boss_c"
        phase: Current phase (1 or 2)
        pattern_name: Pattern identifier

    Returns:
        Pattern generation function or None if not found
    """
    # Pattern mapping
    patterns = {
        "spiral": generate_spiral_pattern,
        "wave": generate_wave_pattern,
        "pulse": generate_pulse_pattern,
        "double_spiral": lambda x, y: generate_spiral_pattern(x, y, count=16),
        "fast_wave": lambda x, y: generate_wave_pattern(x, y, arc_width=90.0, count=7, speed=6.0),
        "burst_pulse": lambda x, y: generate_pulse_pattern(x, y, count=16, speed=4.0)
    }

    return patterns.get(pattern_name)
