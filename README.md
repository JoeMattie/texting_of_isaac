# Texting of Isaac

A TUI (Terminal User Interface) roguelike game inspired by The Binding of Isaac, built with Python using an Entity Component System architecture.

![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Tests](https://img.shields.io/badge/tests-62%20passing-brightgreen)

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
  - Shooters that stay stationary
  - Tanks, Orbiters, and Turrets (basic implementation)
- **Collision Detection** - Circle-based physics with damage system
- **Rich TUI Rendering** - Beautiful terminal interface with colors
- **Room Generation** - Procedural obstacle placement
- **5 Enemy Types** - Diverse enemy roster with unique stats
- **Comprehensive Tests** - 62 unit tests ensuring code quality

### 🚧 In Progress / Planned
- Enemy shooting (enemies currently don't fire back)
- Player damage and health system integration
- Item pickup and stat modification system
- Multi-room dungeon progression
- Room transitions and door mechanics
- Boss fights
- Game state management (menu, pause, game over)
- Win/loss conditions
- Special effects (homing, piercing, explosive shots)

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
- **Q** - Quit game

### Objective
Currently: Survive and defeat enemies in the arena.

Coming soon: Clear rooms, collect items, defeat bosses, and escape the dungeon.

### Tips
- Keep moving! Enemies will chase you
- Shoot strategically - fire rate has cooldown
- Use obstacles for cover (the `○` characters)

## 🏗️ Project Structure

```
texting_of_isaac/
├── main.py                 # Game entry point and main loop
├── src/
│   ├── components/         # ECS components (data containers)
│   │   ├── core.py        # Position, Velocity, Health, Sprite
│   │   ├── combat.py      # Stats, Collider, Projectile
│   │   └── game.py        # Player, Enemy, Item, AI, Invincible
│   ├── systems/           # ECS systems (game logic)
│   │   ├── input.py       # Player input handling
│   │   ├── movement.py    # Physics and movement
│   │   ├── shooting.py    # Projectile creation
│   │   ├── ai.py          # Enemy AI behaviors
│   │   ├── collision.py   # Collision detection & damage
│   │   └── render.py      # Grid-based rendering
│   ├── entities/          # Entity factory functions
│   │   ├── player.py      # Player entity creation
│   │   └── enemies.py     # Enemy entity creation (5 types)
│   ├── game/              # Game management
│   │   ├── engine.py      # Main game engine & ECS world
│   │   └── room.py        # Room generation & management
│   └── config.py          # Game constants and configuration
├── tests/                 # Unit tests (62 tests)
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
| `♥` | Health/Heart |

## 🐛 Known Issues

- Player is currently invincible (damage system not fully integrated)
- Enemies don't shoot projectiles yet
- Single room only (no dungeon progression)
- No item pickups implemented
- Projectiles can go off-screen indefinitely

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

**Phase 1: Core Gameplay** (Current)
- [x] ECS architecture
- [x] Player movement and shooting
- [x] Enemy AI
- [x] Collision detection
- [ ] Enemy shooting patterns
- [ ] Player damage system

**Phase 2: Progression**
- [ ] Multi-room dungeons
- [ ] Room transitions
- [ ] Item pickups and stat modifications
- [ ] Special item effects

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
