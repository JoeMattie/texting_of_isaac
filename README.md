# Texting of Isaac

A TUI (Terminal User Interface) roguelike game inspired by The Binding of Isaac, built with Python using an Entity Component System architecture.

![Version](https://img.shields.io/badge/version-0.3.0--alpha-orange)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Tests](https://img.shields.io/badge/tests-448%20passing-brightgreen)

## 🎮 What is This?

Texting of Isaac is a bullet-hell roguelike rendered entirely in ASCII/Unicode characters in your terminal. Fight enemies, dodge projectiles, and survive in a procedurally generated dungeon—all from the comfort of your command line.

**NEW: Web Frontend Available!** Play in your browser with real-time multiplayer support and sprite-based graphics powered by Pixi.js. See the [Web Frontend](#-web-frontend) section below.

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
- **Explosive Tears** - Special effect that creates explosions on projectile impact
- **Boss Fights** - Three unique bosses with multi-phase combat and geometric attack patterns
- **Multiple Floors** - Progress through 3 floors with increasing difficulty and scaling
- **Game State Management** - Victory and game over screens with proper terminal states
- **Win/Loss Conditions** - Beat all 3 floors to win, or lose when HP reaches 0
- **Comprehensive Tests** - 448 unit tests ensuring code quality
- **Web Frontend** - Play in browser with Pixi.js rendering and WebSocket multiplayer

### 🌐 Web Frontend Features
- **Real-time Multiplayer** - Player + spectator support via WebSocket
- **Pixi.js Rendering** - Hardware-accelerated WebGL graphics (60 FPS frontend)
- **Sprite System** - Placeholder colored sprites (ready for pixel art integration)
- **Network Client** - Automatic reconnection with exponential backoff
- **UI Overlay** - Health, coins, bombs, and items display
- **Keyboard Controls** - WASD for movement, arrow keys for shooting
- **Production Ready** - Full deployment configuration and documentation

### 🚧 In Progress / Planned
- Menu system and pause functionality
- Additional items and special effects
- Sound effects (if terminal audio is feasible)

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
Clear rooms filled with enemies, collect coins and items, purchase upgrades in shops, and navigate through the procedurally generated dungeon. Defeat all enemies in a room to unlock doors, defeat floor bosses to advance, and survive all 3 floors to achieve victory!

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
- Boss fights feature multi-phase combat - watch for pattern changes at 50% HP
- Defeat the floor boss to spawn a trapdoor (▼) that leads to the next floor

## 🌐 Web Frontend

Play Texting of Isaac in your browser with real-time multiplayer support!

### Setup

1. Install frontend dependencies:
```bash
cd web
npm install
```

### Running the Web Version

You'll need **two terminal windows**:

**Terminal 1 - Start the game server:**
```bash
# From project root
uv run python -m src.web.server
```

**Terminal 2 - Start the frontend:**
```bash
cd web
npm run dev
```

Then open your browser to `http://localhost:3000`

### Web Controls
- **WASD** - Move player
- **Arrow Keys** - Shoot projectiles
- **E** - Place bomb
- **Space** - Use item (if applicable)

### Features
- Real-time game state synchronization at 30 FPS
- Hardware-accelerated rendering with Pixi.js
- Spectator mode support (multiple viewers per game)
- Automatic reconnection on disconnect
- Production deployment ready

### Documentation
- **[RUN_DEMO.md](RUN_DEMO.md)** - Complete testing guide with 11 test scenarios
- **[DEPLOY.md](DEPLOY.md)** - Production deployment instructions
- **[ASSETS.md](ASSETS.md)** - Sprite asset pipeline documentation

## 🏗️ Project Structure

```
texting_of_isaac/
├── main.py                 # Terminal game entry point
├── src/
│   ├── web/                # Web frontend backend
│   │   ├── __main__.py    # WebSocket server entry point
│   │   ├── server.py      # WebSocket server and game loop
│   │   ├── session_manager.py # Multi-session management
│   │   └── protocol.py    # Message types and serialization
│   ├── components/         # ECS components (data containers)
│   │   ├── core.py        # Position, Velocity, Health, Sprite
│   │   ├── combat.py      # Stats, Collider, Projectile, Homing
│   │   ├── game.py        # Player, Enemy, Item, AI, Invincible, CollectedItems
│   │   ├── dungeon.py     # DungeonPosition, Door, Currency, ShopItem
│   │   ├── currency.py    # Coins, Bombs
│   │   └── boss.py        # Boss, BossAI, Trapdoor
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
│   │   ├── boss_ai.py     # Boss behavior and patterns
│   │   ├── boss_patterns.py # Geometric attack pattern generation
│   │   ├── boss_health_bar.py # Boss health bar rendering
│   │   ├── floor_transition.py # Floor progression system
│   │   ├── game_state.py  # Victory/defeat state management
│   │   └── render.py      # Grid-based rendering
│   ├── entities/          # Entity factory functions
│   │   ├── player.py      # Player entity creation
│   │   ├── enemies.py     # Enemy entity creation (5 types)
│   │   ├── bosses.py      # Boss entity creation (3 types)
│   │   ├── trapdoor.py    # Trapdoor (floor exit) creation
│   │   ├── items.py       # Item pickup creation
│   │   ├── shop.py        # Shop item creation
│   │   ├── currency.py    # Coin and bomb pickup creation
│   │   ├── doors.py       # Door entity creation
│   │   └── rewards.py     # Room clear reward spawning
│   ├── game/              # Game management
│   │   ├── engine.py      # Main game engine & ECS world
│   │   ├── state.py       # Game state enum (PLAYING, VICTORY, GAME_OVER)
│   │   ├── room.py        # Room generation & management
│   │   └── dungeon.py     # Procedural dungeon generation
│   ├── data/              # Game data and definitions
│   │   └── items.py       # Item definitions and effects
│   └── config.py          # Game constants and configuration
├── web/                   # Web frontend (Pixi.js + TypeScript)
│   ├── src/
│   │   ├── main.ts        # Frontend entry point
│   │   ├── network.ts     # WebSocket client
│   │   ├── sprites.ts     # Sprite manager
│   │   ├── renderer.ts    # Pixi.js game renderer
│   │   └── ui.ts          # UI overlay manager
│   ├── index.html         # HTML entry point
│   ├── package.json       # npm dependencies
│   ├── tsconfig.json      # TypeScript configuration
│   └── vite.config.js     # Vite build configuration
├── tests/                 # Unit tests (448 tests)
├── docs/
│   └── plans/             # Design documents
├── RUN_DEMO.md            # Web frontend testing guide
├── DEPLOY.md              # Production deployment guide
└── ASSETS.md              # Sprite asset pipeline docs
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

**Terminal Version:**
- **Python 3.12+** - Core language
- **Esper** - Entity Component System framework
- **Rich** - Terminal UI rendering and styling
- **Pytest** - Testing framework

**Web Version:**
- **Python WebSocket Server** - Real-time game state broadcasting
- **TypeScript** - Type-safe frontend code
- **Pixi.js v8** - Hardware-accelerated WebGL rendering
- **Vite** - Fast frontend build tool with HMR
- **WebSockets** - Real-time bidirectional communication

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
| `A/B/C` | Boss (unique per floor) |
| `.` | Projectile (yours) |
| `*` | Enemy projectile |
| `○` | Obstacle |
| `#` | Wall |
| `♥` | Health/Heart pickup |
| `$` | Coin |
| `B` | Bomb pickup |
| `I` | Item pickup |
| `D` | Door (locked/unlocked) |
| `▼` | Trapdoor (floor exit) |

## 🐛 Known Issues

- Projectiles can go off-screen indefinitely (limited to 200 max)
- No pause menu or settings menu yet

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

**Phase 3: Content** ✅ (Complete)
- [x] Boss fights with 3 unique bosses
- [x] Multiple floors (3 floors with scaling difficulty)
- [x] Explosive tears special effect
- [ ] More enemy types
- [ ] More items (targeting 12-15 total)

**Phase 4: Web Frontend** ✅ (Complete)
- [x] Python WebSocket server with session management
- [x] Pixi.js frontend with sprite rendering
- [x] Network client with reconnection
- [x] UI overlay (health, coins, items)
- [x] Keyboard input handling
- [x] Spectator mode support
- [x] Production deployment configuration
- [x] Comprehensive documentation
- [ ] Real pixel art sprites (placeholder colored rectangles)
- [ ] Sprite animations
- [ ] Visual effects (particles, screen shake)
- [ ] Sound integration

**Phase 5: Polish**
- [ ] Menu system
- [ ] Save/load
- [ ] High scores
- [ ] Leaderboards

---

**Status**: Alpha - Core gameplay complete with web frontend

**Play it now**:
- Terminal: `uv run python main.py`
- Web: See [Web Frontend](#-web-frontend) section
