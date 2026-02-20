#!/usr/bin/env python3
"""
Generate pixel art sprite sheet for Texting of Isaac.

Layout: 12 cols × 4 rows of 32×32 sprites (384×128 total)
Each sprite is defined as a 16×16 grid (chars → palette), scaled 2× to 32×32.

Row 0: player, enemy_chaser, enemy_shooter, enemy_orbiter, enemy_turret, enemy_tank
Row 1: boss_A, boss_B, boss_C, projectile_player, projectile_enemy, trapdoor
Row 2: door_open, door_locked, wall, obstacle, floor, unknown
Row 3: heart, heart_half, coin, bomb, item, powerup
"""

import json
import os
from PIL import Image

# ---------------------------------------------------------------------------
# Color palette  (char → RGBA or None for transparent)
# ---------------------------------------------------------------------------
P = {
    '.': None,          # transparent
    'K': (17,  17,  17, 255),   # near-black outline
    'S': (244, 194, 161, 255),  # skin
    'k': (139,  90,  43, 255),  # dark brown / hair
    'B': ( 51, 102, 204, 255),  # blue shirt
    'b': ( 25,  50, 120, 255),  # dark blue
    'R': (210,  35,  35, 255),  # red
    'r': (140,  10,  10, 255),  # dark red
    'O': (255, 120,  20, 255),  # orange
    'o': (180,  80,   0, 255),  # dark orange
    'Y': (255, 215,   0, 255),  # gold/yellow
    'y': (200, 160,   0, 255),  # dark gold
    'G': ( 60, 180,  60, 255),  # green
    'g': ( 30, 110,  30, 255),  # dark green
    'C': (  0, 220, 255, 255),  # cyan
    'c': (  0, 140, 180, 255),  # dark cyan
    'M': (255,  60, 160, 255),  # magenta/pink
    'm': (180,  20, 100, 255),  # dark magenta
    'P': (140,  80, 210, 255),  # purple
    'p': ( 80,  40, 140, 255),  # dark purple
    'W': (200, 200, 200, 255),  # light gray
    'w': (140, 140, 140, 255),  # mid gray
    'D': ( 90,  90,  90, 255),  # dark gray
    'E': ( 50,  50,  50, 255),  # very dark gray
    'N': ( 28,  28,  28, 255),  # almost black
    'T': (139,  90,  43, 255),  # tan/wood brown
    't': ( 90,  55,  20, 255),  # dark wood
    'F': (210, 195, 175, 255),  # floor (warm light)
    'f': (180, 165, 145, 255),  # floor shadow
    'L': (255, 180, 180, 255),  # light pink
    'X': (255,  80,  80, 255),  # bright red highlight
    'Q': (255, 230,  80, 255),  # bright gold
    'V': (200, 130,  60, 255),  # warm medium brown
    'A': (100, 200, 160, 255),  # teal
    'a': ( 50, 140, 100, 255),  # dark teal
    'Z': (255, 230, 200, 255),  # very light skin / white
    'H': (255, 255, 255, 255),  # white
    'h': (230, 230, 230, 255),  # near white
}

# ---------------------------------------------------------------------------
# Sprite definitions  (each: list of 16 strings × 16 chars)
# ---------------------------------------------------------------------------
SPRITES: dict[str, list[str]] = {}

# ── Row 0 ──────────────────────────────────────────────────────────────────

# player  (Isaac-style: round skin head, blue shirt, short legs)
SPRITES['player'] = [
    '....KKKKKKKK....',
    '...KSSSSSSSSKk..',
    '..KSSSSSSSSSSKk.',
    '..KSSSSSSSSSSKk.',
    '..KSSKSSKSSKSK..',
    '..KSSSSSSSSSSKK.',
    '..KSSSSSSSSSSk..',
    '...KKKSSSSKKk...',
    '....KBBBBBBK....',
    '...KBBBBBBBBk...',
    '..KBBBBBBBBBBk..',
    '...KBBBBBBBBk...',
    '...KbbK..KbbK...',
    '..KbbKK..KKbbk..',
    '..KkkKK..KKkkk..',
    '..KKKK....KKKk..',
]

# enemy_chaser  (round red blob with angry V-brows and sharp teeth)
SPRITES['enemy_chaser'] = [
    '....KKKKKKKK....',
    '..KKRRRRRRRRKk..',
    '.KRRRRRRRRRRRKk.',
    'KRRrRRRRRRrRRKK.',
    'KRRrKKRRKKrRRRK.',
    'KRRRKKRRKKRRRRk.',
    'KRRRRRRRRRRRRRk.',
    'KRrRKKKKKKRrRRk.',
    'KRRRRRRRRRRRRRk.',
    'KRRKrrrrrrrKRRk.',
    '.KRRKKKKKKKKRKk.',
    '..KRRRRRRRRRKk..',
    '...KRRKRKRRKk...',
    '....KKrrrKKk....',
    '.....KKrKKk.....',
    '......KKKk......',
]

# enemy_shooter  (orange blob with single large eye/barrel on front)
SPRITES['enemy_shooter'] = [
    '....KKKKKKKK....',
    '..KKOOOOOOOOKk..',
    '.KOOOOOOOOOOOKk.',
    'KOOoOOOOOOoOOKK.',
    'KOOoKOOOOKoOOOK.',
    'KOOOKOOOOKOOOOk.',
    'KOOOKoooooKOOOk.',
    'KOOOKoKKKoKOOOk.',
    'KOOOKoCCCoKOOOk.',
    'KOOOKoooooKOOOk.',
    'KOOOOOOOOOOOOOk.',
    '.KOOOOOOOOOOOKk.',
    '..KKOOOOOOOKKk..',
    '....KoooooKk....',
    '....KKKKKKKk....',
    '................',
]

# enemy_orbiter  (halo/ring shape, yellow-orange glowing)
SPRITES['enemy_orbiter'] = [
    '....KKKKKKKK....',
    '..KKYYYYYYYYKk..',
    '.KYYOOOOOOOOYKk.',
    'KYYOooooooooOYKK',
    'KYYOoKKKKKKoOYOK',
    'KYYOoKYYYYKoOYOk',
    'KYOoKKYYYYKKoOYk',
    'KYOoKKYYYYKKoOYk',
    'KYYOoKYYYYKoOYOk',
    'KYYOoKKKKKKoOYOK',
    'KYYOooooooooOYKK',
    '.KYYOOOOOOOOYKk.',
    '..KKYYYYYYYYKk..',
    '....KKKKKKKk....',
    '................',
    '................',
]

# enemy_turret  (gray metal box with a barrel pointing right)
SPRITES['enemy_turret'] = [
    '....KKKKKKKK....',
    '...KDDDDDDDDKk..',
    '..KDDwwwwwwDDKk.',
    '.KDDwKKKKKwwDDKK',
    '.KDDwKEEEKwwDDEK',
    '.KDDwKEEEKwwDDEk',
    '.KDDwKEEEKwwKKKKKKKK',
    '.KDDwKEEEKwwKDDDDDDk',
    '.KDDwKEEEKwwKKKKKKKK',
    '.KDDwKEEEKwwDDEk....',
    '.KDDwKKKKKwwDDEK....',
    '.KDDwwwwwwwwDDKK....',
    '..KDDwwwwwwDDKk.....',
    '...KDDDDDDDDKk......',
    '....KKKKKKKKk.......',
    '................',
]

# enemy_tank  (large armored dark-red slow enemy, chunky shape)
SPRITES['enemy_tank'] = [
    '..KKKKKKKKKKK...',
    '.KrrrrrrrrrrrKk.',
    'KrrRRRRRRRRrrKK.',
    'KrRRRRRRRRRRrKK.',
    'KrRRrKKKKrRRrKK.',
    'KrRRrKKKKrRRrKK.',
    'KrRRRRRRRRRRrKK.',
    'KrRRRRRRRRRRrKK.',
    'KrRRrrrrrrrRrKK.',
    'KrRRRRRRRRRRrKK.',
    'KrrRRRRRRRRrrKK.',
    '.KrrrrrrrrrrrKk.',
    'KKKKKKKKKKKKKKk.',
    'KwwwwwwwwwwwwKk.',
    'KwwwwwwwwwwwwKk.',
    '.KKKKKKKKKKKKk..',
]

# ── Row 1 ──────────────────────────────────────────────────────────────────

# boss_A  (large pale skull with hollow eye sockets, cracks)
SPRITES['boss_A'] = [
    '.....KKKKKK.....',
    '...KKhhhhhKKK...',
    '..KhhhhhhhhhKK..',
    '.KhhhhhhhhhhhhK.',
    'KhhhKKKhhKKKhhhK',
    'KhhhKEEKhhKEEKhhK',
    'KhhhKEEKhhKEEKhhK',
    'KhhhKKKhhKKKhhhK',
    'KhhhhhhhhhhhhhhK',
    'KhhhKKKKKKKKhhhK',
    'KhhKhKhKhKhKhhhK',
    '.KhKKKKKKKKKhKK.',
    '..KhhhKKKKhhhK..',
    '...KKKhhhKKKK...',
    '....KKhKhKK.....',
    '.....KKKKK......',
]

# boss_B  (spider-like boss: round body with spindly legs)
SPRITES['boss_B'] = [
    'K..............K',
    '.K....KKKK....K.',
    '..K..KPPPPKk.K..',
    'K..KKPpppppKKK.K',
    '.K.KPppPPpppPK.K',
    'KKKPppPKKPppPKKK',
    '.KKKppPKKPppKKK.',
    '.KKKppppppppKKK.',
    'KKKKpppppppppKKK',
    '.KKKppppppppKKK.',
    '.KKPpppppppppPKK',
    'K.KPpppKKKpppPKK',
    'K..KKPPKKKPPKKk.',
    'K...KKKKKKKKKk..',
    '.....KKKKKKk....',
    '................',
]

# boss_C  (big beholder eye with tentacles)
SPRITES['boss_C'] = [
    '....KKKKKKKK....',
    '..KKMMMMMMMmKK..',
    '.KMMMmmmmmmmMmK.',
    'KMMMmKKKKKKmMMK.',
    'KMMmKCCCCCCKmMmK',
    'KMMmKCccccCKmMMK',
    'KMMmKCcKKcCKmMMK',
    'KMMmKCcKKcCKmMMK',
    'KMMmKCccccCKmMMK',
    'KMMmKCCCCCCKmMmK',
    'KMMMmKKKKKKmMMK.',
    '.KMMMmmmmmmmMmK.',
    '..KKMMMMMMMmKK..',
    '....KKKKKKKK....',
    'K..KKmKmKmKK..K.',
    '.KK...KmK...KK..',
]

# projectile_player  (small cyan teardrop, center of sprite)
SPRITES['projectile_player'] = [
    '................',
    '................',
    '................',
    '................',
    '......KKK.......',
    '.....KCCCKk.....',
    '....KCcCCCKk....',
    '....KCcCCCKk....',
    '....KCCCCCKk....',
    '.....KCCC Kk....',
    '......KKKKk.....',
    '................',
    '................',
    '................',
    '................',
    '................',
]

# projectile_enemy  (small red/magenta bullet)
SPRITES['projectile_enemy'] = [
    '................',
    '................',
    '................',
    '................',
    '......KKK.......',
    '.....KMMMKk.....',
    '....KMmMMMKk....',
    '....KMmMMMKk....',
    '....KMMMMMKk....',
    '.....KMMMmKk....',
    '......KKKKk.....',
    '................',
    '................',
    '................',
    '................',
    '................',
]

# trapdoor  (wooden brown trap door with iron ring handle, dark opening)
SPRITES['trapdoor'] = [
    'KKKKKKKKKKKKKKKK',
    'KttttttttttttttK',
    'KtTTTTTTTTTTTtK',
    'KtTKKKKKKKKTTtK',
    'KtTKNNNNNNKTTtK',
    'KtTKNKKKKNKTTtK',
    'KtTKNKYYKNKTTtK',
    'KtTKNKYYKNKTTtK',
    'KtTKNKKKKNKTTtK',
    'KtTKNNNNNNKTTtK',
    'KtTKKKKKKKKTTtK',
    'KtTTTTTTTTTTTtK',
    'KttttttttttttttK',
    'KtttTTTTTTTtttK',
    'KKKtttttttttKKK',
    'KKKKKKKKKKKKKKKK',
]

# ── Row 2 ──────────────────────────────────────────────────────────────────

# door_open  (open archway, stone frame, dark interior)
SPRITES['door_open'] = [
    'KKKKKKKKKKKKKKKK',
    'KwwwwwwwwwwwwwwK',
    'KwKKKKKKKKKKKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKNNNNNNNNNKwK',
    'KwKwwwKKKwwwKwK',
    'KwwwwwKKKwwwwwK',
    'KwwwwwKKKwwwwwK',
    'KKKKKKKKKKKKKKKK',
]

# door_locked  (closed door with iron lock symbol)
SPRITES['door_locked'] = [
    'KKKKKKKKKKKKKKKK',
    'KwwwwwwwwwwwwwwK',
    'KwKKKKKKKKKKKwK',
    'KwKTTTTTTTTTKwK',
    'KwKTtTTTTTtTKwK',
    'KwKTTTTTTTTTKwK',
    'KwKTTKKKKKTTKwK',
    'KwKTKwwwwwKTKwK',
    'KwKTKwYYwwKTKwK',
    'KwKTKwwwwwKTKwK',
    'KwKTTKKKKKTTKwK',
    'KwKTTTTTTTTTKwK',
    'KwKTtTTTTTtTKwK',
    'KwKKKKKKKKKKKwK',
    'KwwwwwwwwwwwwwK',
    'KKKKKKKKKKKKKKKK',
]

# wall  (stone bricks pattern, gray tones)
SPRITES['wall'] = [
    'KKKKKKKKKKKKKKKK',
    'KWWWwKWWWWwKWWwK',
    'KWwwwKWWwwwKWwwK',
    'KWwwwKWWwwwKWwwK',
    'KKKKKKKKKKKKKKkK',
    'KWWWWwKWWwKWWwwK',
    'KWWwwwKWwwKWwwwK',
    'KWWwwwKWwwKWwwwK',
    'KKKKKKKKKKKKKKkK',
    'KWwwKWWWwKWWwwwK',
    'KWwwKWWwwKWWwwwK',
    'KWwwKWWwwKWWwwwK',
    'KKKKKKKKKKKKKKkK',
    'KWWWwwwKWwwKWwwK',
    'KWWWwwwKWwwKWwwK',
    'KKKKKKKKKKKKKKKK',
]

# obstacle  (rounded stone/rock, gray)
SPRITES['obstacle'] = [
    '................',
    '....KKKKKK......',
    '..KKwwwwwwKK....',
    '.KwwwwwwwwwwK...',
    'KwwwWwwwwwwwwK..',
    'KwwWWwwwwwwwwK..',
    'KwwwwwwwwwwwwK..',
    'KwwwwwwwwDDwwK..',
    'KwwwwwwwwDDwwK..',
    'KwwwwwwwwwwwwK..',
    '.KwwwwwwwwwwK...',
    '..KKwwwwwwKK....',
    '....KKKKKK......',
    '................',
    '................',
    '................',
]

# floor  (plain flat floor tile, warm light gray)
SPRITES['floor'] = [
    'FFFFFFFFFFFFFFFF',
    'FfFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FFFFFFFFFFFFFFfF',
    'FfFFFFFFFFFFFFFf',
    'FfFFFFFFFFFFFFFf',
]

# unknown  (dark tile with ? mark)
SPRITES['unknown'] = [
    'KKKKKKKKKKKKKKKK',
    'KPPPPPPPPPPPPPPK',
    'KPPPpppppppppPPK',
    'KPPpPPPPPPPPpPPK',
    'KPpPPpPPPPpPPpPK',
    'KPpPpPHHHPpPPpPK',
    'KPpPpPHHHPpPPpPK',
    'KPPpPPHHHPPpPPK ',
    'KPPPpPPHPPpPPPPK',
    'KPPPPpPHPpPPPPPK',
    'KPPPPpPHPpPPPPPK',
    'KPPPPppppPPPPPPK',
    'KPPPPpPPPpPPPPPK',
    'KPPPpPPHPPpPPPPK',
    'KPPppppppppppPPK',
    'KKKKKKKKKKKKKKKK',
]

# ── Row 3 ──────────────────────────────────────────────────────────────────

# heart  (full red heart with highlight)
SPRITES['heart'] = [
    '................',
    '....KKKK.KKKK...',
    '...KRRRKKRRRKk..',
    '..KRRRRRRRRRRKk.',
    '..KRRXRRRRRRRKk.',
    '..KRRXRRRRRRRKk.',
    '..KRRRRRRRRRRKk.',
    '...KRRRRRRRRKk..',
    '....KRRRRRRKk...',
    '.....KRRRRKk....',
    '......KRRKk.....',
    '.......KKk......',
    '................',
    '................',
    '................',
    '................',
]

# heart_half  (left half red, right half gray/empty)
SPRITES['heart_half'] = [
    '................',
    '....KKKK.KKKK...',
    '...KRRRKKwwwKk..',
    '..KRRRRRwwwwwKk.',
    '..KRRXRRwwwwwKk.',
    '..KRRXRRwwwwwKk.',
    '..KRRRRRwwwwwKk.',
    '...KRRRRwwwwKk..',
    '....KRRRwwwKk...',
    '.....KRRwwKk....',
    '......KRwKk.....',
    '.......KKk......',
    '................',
    '................',
    '................',
    '................',
]

# coin  (shiny gold coin, circular)
SPRITES['coin'] = [
    '................',
    '.....KKKKK......',
    '....KYYYYYKk....',
    '...KYYQQQYYKk...',
    '...KYQQQQQYYKk..',
    '..KYYQYYYQQYKk..',
    '..KYYQYYYQYYKk..',
    '..KYYQQQQQYYKk..',
    '..KYYQYYYYYYKk..',
    '..KYYYQQQQYYKk..',
    '...KYYYYYYYKk...',
    '....KYYYYYKk....',
    '.....KKKKKk.....',
    '................',
    '................',
    '................',
]

# bomb  (gray sphere with black fuse, flame at top)
SPRITES['bomb'] = [
    '........KK......',
    '.......KYKk.....',
    '......KYYKk.....',
    '.....KKwKk......',
    '....KKwwwwKK....',
    '...KwwwwwwwwKk..',
    '..KwwwwwwwwwwKk.',
    '.KwwwWwwwwwwwKk.',
    '.KwwWWwwwwwwwKk.',
    '.KwwwwwwwwDwwKk.',
    '.KwwwwwwwwDwwKk.',
    '.KwwwwwwwwwwwKk.',
    '..KwwwwwwwwwKk..',
    '...KwwwwwwwKk...',
    '....KKwwwKKk....',
    '......KKKk......',
]

# item  (item pedestal on a small platform)
SPRITES['item'] = [
    '................',
    '......KKK.......',
    '.....KPPPKk.....',
    '....KPpppPKk....',
    '....KPpPpPKk....',
    '....KPpppPKk....',
    '.....KKKKKk.....',
    '.....KwwwwK.....',
    '.....KwwwwK.....',
    '....KwwwwwwK....',
    '...KwwwwwwwwK...',
    '..KKKwwwwwwKKK..',
    '..KFFFFFFFFFFF..',
    '..KFFFFFFFFFF...',
    '................',
    '................',
]

# powerup  (glowing star/orb with rays)
SPRITES['powerup'] = [
    '................',
    '........K.......',
    '.......KGKk.....',
    '...K..KGGGKk..K.',
    '..KGK.KGgGKk.KGK',
    '...KKKKKgKKKKKK.',
    '....KGKKgKKGKK..',
    '.....KKggggKK...',
    '.....KGggggGKk..',
    '.....KKKggKKK...',
    '....KGKKgKKGKk..',
    '...KKKKKgKKKKKK.',
    '..KGK.KGgGKk.KGK',
    '...K..KGGGKk..K.',
    '.......KGKk.....',
    '........K.......',
]

# ---------------------------------------------------------------------------
# Ordered list matching the spritesheet layout
# ---------------------------------------------------------------------------
LAYOUT = [
    # Row 0
    ['player', 'enemy_chaser', 'enemy_shooter', 'enemy_orbiter', 'enemy_turret', 'enemy_tank',
     None, None, None, None, None, None],
    # Row 1
    ['boss_A', 'boss_B', 'boss_C', 'projectile_player', 'projectile_enemy', 'trapdoor',
     None, None, None, None, None, None],
    # Row 2
    ['door_open', 'door_locked', 'wall', 'obstacle', 'floor', 'unknown',
     None, None, None, None, None, None],
    # Row 3
    ['heart', 'heart_half', 'coin', 'bomb', 'item', 'powerup',
     None, None, None, None, None, None],
]

COLS = 12
ROWS = 4
TILE = 16    # source pixel size
SCALE = 2    # ×2 → 32×32 output tiles
SPRITE_OUT = TILE * SCALE  # 32
SHEET_W = COLS * SPRITE_OUT  # 384
SHEET_H = ROWS * SPRITE_OUT  # 128


def render_sprite(grid: list[str]) -> Image.Image:
    """Render a 16×16 string grid into a 32×32 RGBA image."""
    img = Image.new('RGBA', (TILE, TILE), (0, 0, 0, 0))
    pixels = img.load()
    for row_idx, row in enumerate(grid):
        for col_idx, ch in enumerate(row):
            if col_idx >= TILE or row_idx >= TILE:
                continue
            color = P.get(ch, None)
            if color is not None:
                pixels[col_idx, row_idx] = color
    return img.resize((SPRITE_OUT, SPRITE_OUT), Image.NEAREST)


def build_sheet() -> tuple[Image.Image, dict]:
    sheet = Image.new('RGBA', (SHEET_W, SHEET_H), (0, 0, 0, 0))
    frames: dict[str, dict] = {}

    for row_idx, row in enumerate(LAYOUT):
        for col_idx, name in enumerate(row):
            x = col_idx * SPRITE_OUT
            y = row_idx * SPRITE_OUT
            if name is None:
                continue
            grid = SPRITES.get(name)
            if grid is None:
                print(f'  WARNING: no sprite data for "{name}"')
                continue
            sprite_img = render_sprite(grid)
            sheet.paste(sprite_img, (x, y))
            frames[name] = {'x': x, 'y': y, 'w': SPRITE_OUT, 'h': SPRITE_OUT}
            print(f'  rendered {name:25s} → ({x:3d}, {y:3d})')

    # Build Pixi.js compatible atlas format
    pixi_frames: dict = {}
    for name, f in frames.items():
        pixi_frames[name] = {
            'frame': {'x': f['x'], 'y': f['y'], 'w': f['w'], 'h': f['h']},
            'rotated': False,
            'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': f['w'], 'h': f['h']},
            'sourceSize': {'w': f['w'], 'h': f['h']},
        }

    manifest = {
        'frames': pixi_frames,
        'meta': {
            'image': 'sprites.png',
            'size': {'w': SHEET_W, 'h': SHEET_H},
            'scale': '1',
        }
    }
    return sheet, manifest


def main():
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'public', 'assets')
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    print(f'Building sprite sheet ({SHEET_W}×{SHEET_H}) ...')
    sheet, manifest = build_sheet()

    png_path = os.path.join(out_dir, 'sprites.png')
    sheet.save(png_path, 'PNG')
    print(f'\nSaved  {png_path}')

    json_path = os.path.join(out_dir, 'sprites.json')
    with open(json_path, 'w') as fh:
        json.dump(manifest, fh, indent=2)
    print(f'Saved  {json_path}')
    print('\nDone.')


if __name__ == '__main__':
    main()
