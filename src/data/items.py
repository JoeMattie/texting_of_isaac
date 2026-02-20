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
    },
    "explosive_tears": {
        "sprite": "E",
        "color": "orange",
        "stat_modifiers": {
            "damage": 0.3  # +0.3 damage bonus
        },
        "special_effects": ["explosive"]
    },
    # --- New items ---
    "soy_milk": {
        "sprite": "~",
        "color": "white",
        "stat_modifiers": {
            "fire_rate": 3.0,   # Much faster fire rate
            "damage": -1.5      # Less damage per tear
        },
        "special_effects": []
    },
    "polyphemus": {
        "sprite": "O",
        "color": "bright_red",
        "stat_modifiers": {
            "damage": 4.0,      # Massive damage boost
            "fire_rate": -1.0   # Much slower fire rate
        },
        "special_effects": []
    },
    "cricket_head": {
        "sprite": "C",
        "color": "bright_yellow",
        "stat_modifiers": {
            "damage": 0.8       # Solid damage boost
        },
        "special_effects": []
    },
    "spoon_bender": {
        "sprite": ")",
        "color": "magenta",
        "stat_modifiers": {
            "damage": 0.3
        },
        "special_effects": ["homing"]
    },
    "inner_eye": {
        "sprite": "I",
        "color": "cyan",
        "stat_modifiers": {
            "fire_rate": -0.5   # Slower fire rate (3-shot burst penalty)
        },
        "special_effects": ["multi_shot"]
    },
    "dead_cat": {
        "sprite": "9",
        "color": "bright_black",
        "stat_modifiers": {
            "damage": 3.5,      # Massive damage boost
            "max_hp": -8        # Reduces max HP to 1 heart
        },
        "special_effects": ["set_hp_1"]
    },
}
