"""Room generation and management."""
import esper
import random
from typing import List, Tuple, Dict, Set
from src.entities.enemies import create_enemy


class Room:
    """Represents a single room in the dungeon."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: List[Tuple[int, int]] = []
        self.doors: Set[str] = set()  # "top", "bottom", "left", "right"
        self.cleared = False

    def add_door(self, direction: str):
        """Add a door in the specified direction.

        Args:
            direction: "top", "bottom", "left", or "right"
        """
        if direction not in ["top", "bottom", "left", "right"]:
            raise ValueError(f"Invalid door direction: {direction}")
        self.doors.add(direction)

    def generate_obstacles(self, seed: int = None):
        """Generate obstacles using simple random placement.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

        # Place 3-8 obstacle clusters
        num_clusters = random.randint(3, 8)

        for _ in range(num_clusters):
            # Pick random seed position (avoid edges and center)
            cx = random.randint(5, self.width - 5)
            cy = random.randint(5, self.height - 5)

            # Avoid center spawn area
            if abs(cx - self.width // 2) < 10 and abs(cy - self.height // 2) < 5:
                continue

            # Grow cluster (2-4 tiles)
            cluster_size = random.randint(2, 4)
            for _ in range(cluster_size):
                ox = cx + random.randint(-1, 1)
                oy = cy + random.randint(-1, 1)

                if 1 < ox < self.width - 1 and 1 < oy < self.height - 1:
                    self.obstacles.append((ox, oy))

    def spawn_enemies(self, world_name: str, enemy_config: List[Dict]) -> List[int]:
        """Spawn enemies in the room.

        Args:
            world_name: ECS world name
            enemy_config: List of dicts with "type" and "count"

        Returns:
            List of spawned enemy entity IDs
        """
        spawned = []

        for config in enemy_config:
            enemy_type = config["type"]
            count = config["count"]

            for _ in range(count):
                # Random spawn position (avoid edges and center)
                x = random.uniform(10, self.width - 10)
                y = random.uniform(5, self.height - 5)

                # Avoid center spawn
                if abs(x - self.width // 2) < 10:
                    x += 15

                enemy_id = create_enemy(world_name, enemy_type, x, y)
                spawned.append(enemy_id)

        return spawned
