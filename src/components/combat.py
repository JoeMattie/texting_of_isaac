"""Combat-related ECS components."""


class Stats:
    """Combat statistics for entities."""

    def __init__(self, speed: float, damage: float, fire_rate: float, shot_speed: float) -> None:
        if speed < 0:
            raise ValueError("speed must be positive")
        if damage < 0:
            raise ValueError("damage must be positive")
        if fire_rate < 0:
            raise ValueError("fire_rate must be positive")
        if shot_speed < 0:
            raise ValueError("shot_speed must be positive")
        self.speed: float = speed
        self.damage: float = damage
        self.fire_rate: float = fire_rate
        self.shot_speed: float = shot_speed

    def __repr__(self) -> str:
        return f"Stats(speed={self.speed}, damage={self.damage}, fire_rate={self.fire_rate}, shot_speed={self.shot_speed})"


class Collider:
    """Circle collider for collision detection."""

    def __init__(self, radius: float) -> None:
        if radius < 0:
            raise ValueError("radius must be positive")
        self.radius: float = radius

    def __repr__(self) -> str:
        return f"Collider(radius={self.radius})"


class Projectile:
    """Marks entity as a projectile with damage."""

    def __init__(self, damage: float, owner: int) -> None:
        if damage < 0:
            raise ValueError("damage must be positive")
        self.damage: float = damage
        self.owner: int = owner  # Entity ID that fired this

    def __repr__(self) -> str:
        return f"Projectile(damage={self.damage}, owner={self.owner})"
