# Texting of Isaac

A TUI (Terminal User Interface) roguelike game inspired by The Binding of Isaac, built with Python using an Entity Component System architecture.

![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Tests](https://img.shields.io/badge/tests-328%20passing-brightgreen)

## 🎮 What is This?

Texting of Isaac is a bullet-hell roguelike rendered entirely in ASCII/Unicode characters in your terminal. Fight enemies, dodge projectiles, and survive in a procedurally generated dungeon—all from the comfort of your command line.

## ✨ Current Features

### ✅ Working
- **Entity Component System** - Clean ECS architecture powered by Esper
- **Real-time Gameplay** - 30 FPS game loop with smooth rendering
- **Player Controls** - WASD movement with twin-stick shooting (arrow keys)
- **Combat System** - Fire projectiles with cooldown-based fire rate
- **Enemy AI** - Multiple enemy types with different behaviors:
  - Chasers that pursue the player
  - Shooters that fire aimed shots and spread patterns
  - Orbiters that snipe and create radial bursts
  - Turrets that spray and create cross patterns
  - Tanks that fire shockwave patterns
- **Enemy Shooting** - Enemies fire back with varied attack patterns
- **Collision Detection** - Circle-based physics with bidirectional damage
- **Player Damage System** - Take damage from projectiles and contact
- **Invincibility Frames** - Brief immunity after taking damage with visual flash
- **Rich TUI Rendering** - Beautiful terminal interface with colors
- **Room Generation** - Procedural obstacle placement
- **5 Enemy Types** - Diverse enemy roster with unique stats and patterns
- **Item System** - Pickup items that modify player stats and grant special effects
- **Special Effects** - Homing shots, piercing tears, and multi-shot
- **Dungeon Progression** - Procedurally generated multi-room dungeons with multiple room types
- **Room Transitions** - Move between rooms through doors (locked during combat)
- **Door System** - Doors connect rooms and lock/unlock based on room state
- **Currency System** - Collect and spend coins, manage bomb inventory
- **Bomb System** - Place bombs to damage enemies and reveal secret rooms
- **Shop System** - Purchase items with coins in shop rooms
- **Minimap** - Track visited rooms and navigate the dungeon
- **Room Clear Rewards** - Earn coins, hearts, stat boosts, or bombs after clearing combat rooms
- **Comprehensive Tests** - 328 unit tests ensuring code quality

### 🚧 In Progress / Planned
- Boss fights and mini-boss encounters
- Game state management (menu, pause, game over)
- Win/loss conditions
- Additional special effects (explosive shots, etc.)

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JoeMattie/texting_of_isaac.git
cd texting_of_isaac
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Run the game:
```bash
uv run python main.py
```

## 🎯 How to Play

### Controls
- **WASD** - Move your character (`@`)
- **Arrow Keys** - Shoot projectiles in that direction
- **E** - Place bomb (if you have bombs)
- **Q** - Quit game

### Objective
Clear rooms filled with enemies, collect coins and items, purchase upgrades in shops, and navigate through the procedurally generated dungeon. Defeat all enemies in a room to unlock doors and progress deeper into the dungeon.

### Tips
- Keep moving! Enemies will chase you
- Shoot strategically - fire rate has cooldown
- Use obstacles for cover (the `○` characters)
- Collect coins ($) to buy items in shops
- Pick up hearts (♥) to restore health
- Items grant permanent stat upgrades and special effects
- Use bombs (E key) to damage multiple enemies or reveal secret rooms
- Check the minimap to navigate the dungeon
- Doors lock during combat - clear all enemies to proceed

## 🏗️ Project Structure

```
texting_of_isaac/
├── main.py                 # Game entry point and main loop
├── src/
│   ├── components/         # ECS components (data containers)
│   │   ├── core.py        # Position, Velocity, Health, Sprite
│   │   ├── combat.py      # Stats, Collider, Projectile, Homing
│   │   ├── game.py        # Player, Enemy, Item, AI, Invincible, CollectedItems
│   │   ├── dungeon.py     # DungeonPosition, Door, Currency, ShopItem
│   │   └── currency.py    # Coins, Bombs
│   ├── systems/           # ECS systems (game logic)
│   │   ├── input.py       # Player input handling
│   │   ├── movement.py    # Physics and movement
│   │   ├── shooting.py    # Player projectile creation
│   │   ├── ai.py          # Enemy AI behaviors
│   │   ├── enemy_shooting.py # Enemy projectile creation
│   │   ├── collision.py   # Collision detection & damage
│   │   ├── invincibility.py # Invincibility frame management
│   │   ├── homing.py      # Homing projectile guidance
│   │   ├── item_pickup.py # Item collection and shop purchases
│   │   ├── bomb.py        # Bomb placement and explosions
│   │   ├── room_manager.py # Room transitions and spawning
│   │   ├── minimap_system.py # Minimap rendering
│   │   └── render.py      # Grid-based rendering
│   ├── entities/          # Entity factory functions
│   │   ├── player.py      # Player entity creation
│   │   ├── enemies.py     # Enemy entity creation (5 types)
│   │   ├── items.py       # Item pickup creation
│   │   ├── shop.py        # Shop item creation
│   │   ├── currency.py    # Coin and bomb pickup creation
│   │   ├── doors.py       # Door entity creation
│   │   └── rewards.py     # Room clear reward spawning
│   ├── game/              # Game management
│   │   ├── engine.py      # Main game engine & ECS world
│   │   ├── room.py        # Room generation & management
│   │   └── dungeon.py     # Procedural dungeon generation
│   ├── data/              # Game data and definitions
│   │   └── items.py       # Item definitions and effects
│   └── config.py          # Game constants and configuration
├── tests/                 # Unit tests (328 tests)
└── docs/
    └── plans/             # Design documents
```

## 🛠️ Development

### Running Tests
```bash
uv run pytest
```

### Running Tests with Coverage
```bash
uv run pytest --cov=src --cov-report=html
```

### Code Quality
All code includes:
- Type hints for static analysis
- Comprehensive docstrings
- Input validation
- Unit test coverage

### Tech Stack
- **Python 3.12+** - Core language
- **Esper** - Entity Component System framework
- **Rich** - Terminal UI rendering and styling
- **Pytest** - Testing framework

## 📊 Architecture

This game uses an **Entity Component System (ECS)** architecture:

- **Entities** - Game objects (player, enemies, projectiles)
- **Components** - Pure data (Position, Health, Velocity, etc.)
- **Systems** - Logic that operates on components (Movement, Collision, AI)

Benefits:
- Clean separation of data and logic
- Easy to add new features
- Highly testable
- Performant for many entities

## 🎨 ASCII Art Guide

| Character | Meaning |
|-----------|---------|
| `@` | Player |
| `e` | Chaser enemy |
| `S` | Shooter enemy |
| `T` | Turret enemy |
| `O` | Orbiter enemy |
| `E` | Tank enemy |
| `.` | Projectile (yours) |
| `*` | Enemy projectile |
| `○` | Obstacle |
| `#` | Wall |
| `♥` | Health/Heart pickup |
| `$` | Coin |
| `B` | Bomb pickup |
| `I` | Item pickup |
| `D` | Door (locked/unlocked) |

## 🐛 Known Issues

- Projectiles can go off-screen indefinitely (limited to 200 max)
- No boss fights or mini-boss encounters yet
- No game over or win conditions

## 🤝 Contributing

This is a personal learning project, but feedback and suggestions are welcome! Feel free to:
- Open issues for bugs
- Suggest features
- Share your thoughts on the architecture

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by [The Binding of Isaac](https://bindingofisaac.com/) by Edmund McMillen
- Built with [Esper](https://github.com/benmoran56/esper) ECS framework
- Terminal rendering powered by [Rich](https://github.com/Textualize/rich)

## 📈 Roadmap

**Phase 1: Core Gameplay** ✅ (Complete)
- [x] ECS architecture
- [x] Player movement and shooting
- [x] Enemy AI
- [x] Collision detection
- [x] Enemy shooting patterns
- [x] Player damage system
- [x] Item pickup and stat modification system

**Phase 2: Progression** ✅ (Complete)
- [x] Multi-room dungeons
- [x] Room transitions with doors
- [x] Special item effects (homing, piercing, multi-shot)
- [x] Currency system (coins and bombs)
- [x] Shop system
- [x] Minimap navigation
- [x] Room clear rewards

**Phase 3: Content**
- [ ] Boss fights
- [ ] More enemy types
- [ ] More items (targeting 12-15)
- [ ] Multiple floors

**Phase 4: Polish**
- [ ] Sound effects
- [ ] Visual effects
- [ ] Menu system
- [ ] Save/load
- [ ] High scores

---

**Status**: Early Alpha - Core foundation complete, gameplay in progress

**Play it now**: `uv run python main.py`
