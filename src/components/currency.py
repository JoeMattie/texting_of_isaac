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


class BombPickup:
    """Bomb pickup component.

    Tracks the number of bombs in this pickup.
    """

    def __init__(self, quantity: int = 1):
        """Initialize bomb pickup component.

        Args:
            quantity: Number of bombs (must be positive)

        Raises:
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError(f"quantity must be positive (got {quantity})")

        self.quantity: int = quantity

    def __repr__(self) -> str:
        """Return string representation of bomb pickup."""
        return f"BombPickup(quantity={self.quantity})"


class HeartPickup:
    """Heart pickup component.

    Tracks the amount of health restored by this pickup.
    """

    def __init__(self, heal_amount: int = 1):
        """Initialize heart pickup component.

        Args:
            heal_amount: Amount of health restored (must be positive)

        Raises:
            ValueError: If heal_amount is not positive
        """
        if heal_amount <= 0:
            raise ValueError(f"heal_amount must be positive (got {heal_amount})")

        self.heal_amount: int = heal_amount

    def __repr__(self) -> str:
        """Return string representation of heart pickup."""
        return f"HeartPickup(heal_amount={self.heal_amount})"
