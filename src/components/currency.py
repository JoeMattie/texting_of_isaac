"""Currency-related components."""


class Coin:
    """Coin pickup component.

    Tracks the value of a coin pickup (pennies=1, nickels=5, etc.).
    """

    def __init__(self, value: int = 1):
        """Initialize coin component.

        Args:
            value: Coin worth (must be positive)

        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"value must be positive (got {value})")

        self.value: int = value

    def __repr__(self) -> str:
        """Return string representation of coin."""
        return f"Coin(value={self.value})"
