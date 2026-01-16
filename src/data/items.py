"""Item database definitions."""

ITEM_DEFINITIONS = {
    "magic_mushroom": {
        "sprite": "M",
        "color": "red",
        "stat_modifiers": {
            "damage": 1.0,      # +1.0 damage
            "speed": 1.2        # 20% speed increase
        },
        "special_effects": []
    },
    "triple_shot": {
        "sprite": "3",
        "color": "yellow",
        "stat_modifiers": {
            "fire_rate": 0.1    # Slightly slower fire rate
        },
        "special_effects": ["multi_shot"]
    },
    "piercing_tears": {
        "sprite": "P",
        "color": "cyan",
        "stat_modifiers": {
            "damage": 0.5       # +0.5 damage
        },
        "special_effects": ["piercing"]
    },
    "homing_shots": {
        "sprite": "H",
        "color": "magenta",
        "stat_modifiers": {},
        "special_effects": ["homing"]
    },
    "speed_boost": {
        "sprite": "S",
        "color": "green",
        "stat_modifiers": {
            "speed": 1.3        # 30% speed increase
        },
        "special_effects": []
    },
    "damage_up": {
        "sprite": "D",
        "color": "red",
        "stat_modifiers": {
            "damage": 1.5       # +1.5 damage
        },
        "special_effects": []
    },
    "mini_mushroom": {
        "sprite": "m",
        "color": "red",
        "stat_modifiers": {
            "damage": 0.3       # Small +0.3 damage boost
        },
        "special_effects": []
    },
    "fire_rate_up": {
        "sprite": "F",
        "color": "yellow",
        "stat_modifiers": {
            "fire_rate": 0.5    # +0.5 fire rate boost
        },
        "special_effects": []
    }
}
