"""Currency-related components."""
from dataclasses import dataclass


@dataclass
class Coin:
    """Coin pickup component."""
    value: int = 1  # Coin worth (pennies=1, nickels=5, etc.)

    def __post_init__(self):
        """Validate coin value."""
        if self.value <= 0:
            raise ValueError("value must be positive")
