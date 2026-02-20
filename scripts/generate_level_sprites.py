#!/usr/bin/env python3
"""
Generate pixel art level/environment sprite sheet for Texting of Isaac.

Layout: 16 cols × 8 rows of 32×32 sprites (512×256 total)
Each sprite defined as a 16×16 char grid (chars → palette), scaled 2× to 32×32.

Row 0: floor variants      (plain, cracked, bloodstain, grate, dirt, mossy, decorated, shadow)
Row 1: directional walls   (top, bottom, left, right, corner TL/TR/BL/BR)
Row 2: inner corners + open doors (inner TL/TR/BL/BR, door N/S/E/W open)
Row 3: locked doors + obstacles   (door N/S/E/W locked, rock, barrel, skull, pillar)
Row 4: decorations         (torch, cobweb, bones, pot, chain, altar, pentagram, shopkeeper)
Row 5: special tiles       (boss/treasure/shop/secret markers, pit, pit edges, trapdoor)
Row 6: background fills + minimap  (bg_room_fill, bg_void, bg_wall_fill, shadows, minimap)
Row 7: spare
"""

import json
import os
from PIL import Image

# ---------------------------------------------------------------------------
# Colour palette  (char → RGBA or None = transparent)
# ---------------------------------------------------------------------------
P: dict[str, tuple[int, int, int, int] | None] = {
    '.': None,

    # ── Outline ──────────────────────────────────────────────────────────
    'K': (17,  17,  17,  255),   # hard outline / near-black

    # ── Stone / floor (dark dungeon) ─────────────────────────────────────
    '1': (18,  16,  22,  255),   # void / deepest shadow
    '2': (28,  26,  34,  255),   # floor very dark
    '3': (40,  38,  46,  255),   # floor medium
    '4': (32,  30,  40,  255),   # mortar joint (darker than stone body)
    '5': (50,  48,  58,  255),   # stone body
    '6': (64,  62,  72,  255),   # stone lighter
    '7': (80,  78,  90,  255),   # stone light
    '8': (98,  95,  108, 255),   # stone highlight
    '9': (120, 117, 130, 255),   # stone bright

    # ── Wall stone (brighter than floor) ─────────────────────────────────
    'a': (54,  52,  62,  255),   # wall mortar
    'b': (70,  68,  80,  255),   # wall dark
    'c': (88,  86,  98,  255),   # wall medium
    'd': (108, 105, 118, 255),   # wall light
    'e': (130, 127, 140, 255),   # wall bright (top-left highlight)

    # ── Blood ─────────────────────────────────────────────────────────────
    'J': (100, 0,   0,   255),   # blood dark
    'j': (140, 14,  14,  255),   # blood medium

    # ── Fire / torch ──────────────────────────────────────────────────────
    'F': (255, 140, 0,   255),   # fire orange
    'f': (255, 205, 55,  255),   # fire yellow
    'G': (200, 75,  0,   255),   # ember dark

    # ── Moss ──────────────────────────────────────────────────────────────
    'M': (36,  72,  30,  255),   # moss dark
    'm': (60,  104, 52,  255),   # moss medium

    # ── Wood ──────────────────────────────────────────────────────────────
    'W': (76,  46,  24,  255),   # wood dark
    'w': (108, 68,  36,  255),   # wood medium
    'V': (140, 90,  48,  255),   # wood light

    # ── Metal / grate / chain ─────────────────────────────────────────────
    'Z': (64,  62,  78,  255),   # metal dark
    'z': (92,  90,  108, 255),   # metal medium
    'A': (120, 126, 148, 255),   # metal light

    # ── Bone ──────────────────────────────────────────────────────────────
    'B': (185, 175, 160, 255),   # bone light
    'n': (150, 142, 128, 255),   # bone medium
    'N': (118, 110, 96,  255),   # bone shadow

    # ── Magic / boss ──────────────────────────────────────────────────────
    'P': (155, 18,  175, 255),   # magic purple
    'p': (88,  0,   108, 255),   # magic dark

    # ── Gold / treasure ───────────────────────────────────────────────────
    'Q': (220, 182, 0,   255),   # gold bright
    'q': (160, 132, 0,   255),   # gold dark

    # ── Rope / chain ──────────────────────────────────────────────────────
    'H': (88,  78,  68,  255),   # chain dark
    'h': (112, 102, 92,  255),   # chain light

    # ── Pit ───────────────────────────────────────────────────────────────
    'O': (4,   2,   8,   255),   # pit void
    'o': (18,  16,  24,  255),   # pit edge

    # ── Door passage (open arch interior) ────────────────────────────────
    'D': (20,  18,  26,  255),   # door dark
    'I': (30,  28,  38,  255),   # door slightly lighter

    # ── Locked door ───────────────────────────────────────────────────────
    'R': (96,  18,  18,  255),   # locked frame
    'r': (138, 46,  46,  255),   # locked lighter
    'x': (180, 60,  60,  255),   # locked bright

    # ── Shop teal ─────────────────────────────────────────────────────────
    'T': (0,   148, 168, 255),   # teal
    't': (0,   96,  118, 255),   # teal dark

    # ── Pillar ────────────────────────────────────────────────────────────
    'L': (62,  58,  72,  255),   # pillar body
    'l': (46,  42,  56,  255),   # pillar shadow

    # ── Boss warning ──────────────────────────────────────────────────────
    'X': (210, 0,   0,   255),   # boss warning red
    'Y': (220, 196, 0,   255),   # treasure gold

    # ── Cobweb ────────────────────────────────────────────────────────────
    'S': (160, 158, 172, 255),   # cobweb light
    's': (110, 108, 122, 255),   # cobweb shadow

    # ── Dirt ──────────────────────────────────────────────────────────────
    'E': (68,  52,  38,  255),   # dirt dark
    'i': (90,  72,  54,  255),   # dirt lighter

    # ── Clay / pot ────────────────────────────────────────────────────────
    'C': (148, 90,  56,  255),   # clay orange-brown
    'v': (116, 70,  42,  255),   # clay dark

    # ── Secret / barely visible ───────────────────────────────────────────
    'U': (44,  42,  52,  255),   # secret very faint
    'u': (50,  48,  58,  255),   # secret slightly visible

    # ── Minimap ───────────────────────────────────────────────────────────
    'k': (72,  62,  84,  255),   # minimap room fill
    'y': (138, 195, 252, 255),   # minimap current room highlight

    # ── Altar stone ───────────────────────────────────────────────────────
    'g': (200, 192, 180, 255),   # altar pale stone
    'Ğ': (160, 152, 140, 255),   # unused, reserved

    # ── Barrel ────────────────────────────────────────────────────────────
    # (reuse W/w/V for barrel wood)
}

# ---------------------------------------------------------------------------
# Sprite definitions  (16-string list × 16 chars each)
# ---------------------------------------------------------------------------
SPRITES: dict[str, list[str]] = {}


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 0 — FLOOR TILES
# ══════════════════════════════════════════════════════════════════════════════

# Stone body = '5', mortar = '4', highlights '6'/'7'/'8', shadow = '3'
# A 2×2 stone-tile grid with joints at col-7/col-8 and row-7/row-8.
# Light source: top-left → upper-left corner is brightest.

SPRITES['floor_plain'] = [
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
]

SPRITES['floor_cracked'] = [
    '8765555476555554',
    '7665544464555454',   # crack starts (4 darker line)
    '6645444564444445',
    '5534444453444445',   # crack diagonal
    '5442444554244445',
    '5444344554434444',
    '5444434454444344',
    '4444444444444444',
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544434555444445',   # small crack right side
    '5444444454343444',
    '5444444454444344',
    '4444444444444444',
]

SPRITES['floor_bloodstain'] = [
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544jJ4455444445',   # blood stain (j=medium, J=dark)
    '544jJJj454444444',
    '5444jj4454444444',
    '4444444444444444',
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
]

SPRITES['floor_grate'] = [
    'ZZZZZZZZZZZZZZZZ',   # horizontal metal bar
    'Z11Z1111Z1111Z1Z',   # holes between vertical bars
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'ZZZZZZZZZZZZZZZZ',   # bar
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'ZZZZZZZZZZZZZZZZ',   # bar
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'ZZZZZZZZZZZZZZZZ',   # bar
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
    'Z11Z1111Z1111Z1Z',
]

SPRITES['floor_dirt'] = [
    'EEEEEEEEiEEEEEEE',
    'EiEEEEEEEEEiEEEE',
    'EEEEiEEEEEEEEiEE',
    'EEEEEEEEiEEEEEEE',
    'EiEEEEEEEEEEEiEE',
    'EEEEiEEEEEiEEEEE',
    'EEEEEEEiEEEEEEEi',
    'iEEEEEEEEEiEEEEE',
    'EEiEEEEEEEEEEiEE',
    'EEEEEEiEEEEEEEEi',
    'EiEEEEEEEEiEEEEE',
    'EEEEiEEEEEEEiEEE',
    'EEEEEEEiEEEEEEEi',
    'iEEEEEEEEiEEEEEE',
    'EEiEEEEEEEEEiEEE',
    'EEEEEiEEEEEEEEEi',
]

SPRITES['floor_mossy'] = [
    '5555555455555554',
    '5Mm5554455m55454',
    '5mm5554465mm5445',
    '5M55444565554445',
    '5554444555444445',
    '5544444554m44445',
    '5444444Mm4444444',
    '4444444444444444',
    '5555555455555554',
    '5m55544466555454',
    '5mm5544565554445',
    '5M55444555444445',
    '5554444Mm5444445',
    '5544444554444444',
    '5444444454444444',
    '4444444444444444',
]

SPRITES['floor_decorated'] = [
    '5555555555555555',
    '5555655555655555',   # faint rune etching
    '5565755556575555',
    '5556555555655555',
    '5555566555555665',
    '5556657556565755',   # central cross motif
    '5565756556575655',
    '5556555555655565',
    '5555566555555665',
    '5556657556565755',
    '5565756556575655',
    '5556555555655565',
    '5555566655555666',
    '5565755556575555',
    '5556555555655555',
    '5555555555555555',
]

SPRITES['floor_shadow'] = [
    '2222222222222222',
    '2322222222222223',
    '2222222222222222',
    '2222232222232222',
    '2222222222222222',
    '2322222222222223',
    '2222222222222222',
    '2222222222222222',
    '3322222222222233',
    '2222222222222222',
    '2222232222232222',
    '2222222222222222',
    '2322222222222223',
    '2222222222222222',
    '2222232222232222',
    '2222222222222222',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 1 — DIRECTIONAL WALL TILES
# ══════════════════════════════════════════════════════════════════════════════
# Wall palette: 'a'=mortar(dark), 'b'=brick shadow, 'c'=brick body,
#               'd'=brick light, 'e'=brick highlight (top-left)
# Horizontal brick pattern: 4-row bricks (1 mortar + 3 brick), offset rows.

def _hbrick(offset: bool) -> list[str]:
    """Return 4 rows of a horizontal brick wall (1 mortar + 3 brick rows).
    offset=True staggers the brick joints by half a brick width (~4 chars)."""
    if not offset:
        #         0123456789012345
        mortar = 'aaaaaaaaaaaaaaaa'
        row1   = 'aeddddaeddddaedda'[:16]
        row2   = 'adddddadddddadcda'[:16]
        row3   = 'acddddacddddacdca'[:16]
    else:
        mortar = 'aaaaaaaaaaaaaaaa'
        row1   = 'edddddaeddddaedda'[:16]
        row2   = 'ddddddadddddadcda'[:16]
        row3   = 'cdddddacddddacdca'[:16]
    return [mortar, row1, row2, row3]

# wall_top — top border of room, horizontal bricks
SPRITES['wall_top'] = (
    _hbrick(False) + _hbrick(True) + _hbrick(False) + _hbrick(True)
)

# wall_bottom — same as top but with a darker cap at the bottom
SPRITES['wall_bottom'] = (
    _hbrick(True) + _hbrick(False) + _hbrick(True) +
    ['acccccccccccccca', 'aaaaaaaaaaaaaaa6', '6666666666666666', '3333333333333333']
)

def _vbrick(mirror: bool) -> list[str]:
    """Return 8 rows of a vertical brick wall (bricks stacked tall)."""
    rows = []
    for i in range(8):
        if i % 4 == 0:  # mortar column at fixed position
            if not mirror:
                rows.append('abbbbbabbbbbbabb')
            else:
                rows.append('bbabbbbbbabbbbba')
        else:
            if not mirror:
                rows.append('acddddacddddacdd')
            else:
                rows.append('ddcaddddddcadddd')
    return rows

SPRITES['wall_left']  = _vbrick(False) + _vbrick(False)
SPRITES['wall_right'] = _vbrick(True)  + _vbrick(True)

# wall_corner_tl — outer top-left corner
SPRITES['wall_corner_tl'] = [
    'aaaaaaaaaaaaaaaa',
    'aeddddaeddddaeea',
    'adddddadddddadda',
    'acddddacddddacca',
    'aaaaaaaaaaaaaaaa',
    'aecdddaecdddaeca',
    'addcddaddcddadda',
    'acddddacddddacca',
    'aaaaaaaaaaaaaaaa',
    'aeddddaeddddaeea',
    'adddddadddddadda',
    'acddddacddddacca',
    'aaaaaaaaaaaaaaaa',
    'aecdddaecdddaeca',
    'addcddaddcddadda',
    'acddddacddddacca',
]

# wall_corner_tr — outer top-right corner (mirror of tl)
SPRITES['wall_corner_tr'] = [
    'aaaaaaaaaaaaaaaa',
    'aeedddaeddddaeda',
    'adddddadddddadda',
    'accddaacddddadca',
    'aaaaaaaaaaaaaaaa',
    'aecdddaecdddaeca',
    'addddcaddddcadda',
    'adcdddadcdddadca',
    'aaaaaaaaaaaaaaaa',
    'aeedddaeddddaeda',
    'adddddadddddadda',
    'accddaacddddadca',
    'aaaaaaaaaaaaaaaa',
    'aecdddaecdddaeca',
    'addddcaddddcadda',
    'adcdddadcdddadca',
]

# wall_corner_bl — outer bottom-left corner
SPRITES['wall_corner_bl'] = [
    'acddddacddddacca',
    'adddddadddddadda',
    'aeddddaeddddaeea',
    'aaaaaaaaaaaaaaaa',
    'acddddacddddacca',
    'addcddaddcddadda',
    'aecdddaecdddaeca',
    'aaaaaaaaaaaaaaaa',
    'acddddacddddacca',
    'adddddadddddadda',
    'aeddddaeddddaeea',
    'aaaaaaaaaaaaaaaa',
    'acccccccccccccca',
    'aaaaaaaaaaaaaaa6',
    '6666666666666666',
    '4444444444444444',
]

# wall_corner_br — outer bottom-right corner
SPRITES['wall_corner_br'] = [
    'accddaacddddadca',
    'adddddadddddadda',
    'aeedddaeddddaeda',
    'aaaaaaaaaaaaaaaa',
    'adcdddadcdddadca',
    'addddcaddddcadda',
    'aecdddaecdddaeca',
    'aaaaaaaaaaaaaaaa',
    'accddaacddddadca',
    'adddddadddddadda',
    'aeedddaeddddaeda',
    'aaaaaaaaaaaaaaaa',
    'acccccccccccccca',
    'aaaaaaaaaaaaaaa6',
    '6666666666666666',
    '4444444444444444',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 2 — INNER CORNERS + OPEN DOORS
# ══════════════════════════════════════════════════════════════════════════════

# Inner concave corners (where wall meets floor on the inside of the room).
# Top portion = wall face, bottom/side = floor.

SPRITES['wall_inner_tl'] = [
    # wall section (left+top) meeting floor (bottom-right)
    'cccccccccccccccc',   # wall top
    'ceddddceddddcedd',
    'cddddddddddddcdd',
    'ccdddddddddddccd',
    'aaaaaaaaaaaaaaaa',   # mortar
    'ceddddceddddcedd',
    'cddddddddddddcdd',
    'ccdddddddddddccd',
    # transition to floor
    '5555555455555554',
    '5765544466555454',
    '6555444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
]

SPRITES['wall_inner_tr'] = [
    'cccccccccccccccc',
    'ddecddddceddddce',
    'dddcddddddddddcd',
    'dccddddddddddccd',
    'aaaaaaaaaaaaaaaa',
    'ddecddddceddddce',
    'dddcddddddddddcd',
    'dccddddddddddccd',
    '5555555455555554',
    '6455554466555454',
    '5554444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
]

SPRITES['wall_inner_bl'] = [
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
    'cccccccccccccccc',
    'ceddddceddddcedd',
    'cddddddddddddcdd',
    'ccdddddddddddccd',
    'aaaaaaaaaaaaaaaa',
    'ceddddceddddcedd',
    'cddddddddddddcdd',
    'ccdddddddddddccd',
]

SPRITES['wall_inner_br'] = [
    '8765555476555554',
    '7665544466555454',
    '6655444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '5444444454444444',
    '4444444444444444',
    'cccccccccccccccc',
    'ddecddddceddddce',
    'dddcddddddddddcd',
    'dccddddddddddccd',
    'aaaaaaaaaaaaaaaa',
    'ddecddddceddddce',
    'dddcddddddddddcd',
    'dccddddddddddccd',
]

# Open doors — stone arch frame with dark passage interior.
# North door: arch at top, passage going up (dark center, stone sides)
SPRITES['door_north_open'] = [
    'ccccDDDDDDDDcccc',   # top of arch, passage in middle
    'ccDDDDDDDDDDDDcc',
    'cDDDDDDDDDDDDDDc',
    'DDDDDDDDDDDDDDDD',   # full passage
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'ccDDDDDDDDDDDDcc',   # arch sides
    'cccDDDDDDDDDccc',
    'ccccIIIIIIIIcccc',   # arch base / threshold
    '5554555555545554',   # floor begins
    '5554444444445554',
    '4444444444444444',
    '5555555455555554',
    '5555555455555554',
]

SPRITES['door_south_open'] = [
    '5555555455555554',
    '5555555455555554',
    '4444444444444444',
    '5554444444445554',
    '5554555555545554',
    'ccccIIIIIIIIcccc',   # arch base
    'cccDDDDDDDDDccc',
    'ccDDDDDDDDDDDDcc',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'DDDDDDDDDDDDDDDD',
    'cDDDDDDDDDDDDDDc',
    'ccDDDDDDDDDDDDcc',
    'ccccDDDDDDDDcccc',
]

SPRITES['door_east_open'] = [
    'ccccccccc5555555',
    'cdddddDDD5555555',
    'cddddDDDD4444444',
    'cdddDDDDD5555555',
    'cddDDDDDD5555555',
    'cdDDDDDDD5555555',
    'DDDDDDDDD5555555',
    'DDDDDDDDD5555555',
    'DDDDDDDDD5555555',
    'DDDDDDDDD5555555',
    'cdDDDDDDD5555555',
    'cddDDDDDD5555555',
    'cdddDDDDD5555555',
    'cddddDDDD4444444',
    'cdddddDDD5555555',
    'ccccccccc5555555',
]

SPRITES['door_west_open'] = [
    '5555555ccccccccc',
    '5555555DDDdddddс',
    '4444444DDDDddddc',
    '5555555DDDDDdddc',
    '5555555DDDDDDddc',
    '5555555DDDDDDDdc',
    '5555555DDDDDDDDD',
    '5555555DDDDDDDDD',
    '5555555DDDDDDDDD',
    '5555555DDDDDDDDD',
    '5555555DDDDDDDdc',
    '5555555DDDDDDddc',
    '5555555DDDDDdddc',
    '4444444DDDDddddc',
    '5555555DDDdddddс',
    '5555555ccccccccc',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 3 — LOCKED DOORS + OBSTACLES
# ══════════════════════════════════════════════════════════════════════════════

# Locked doors — iron bars across the passage.
SPRITES['door_north_locked'] = [
    'ccccRRRRRRRRcccc',
    'ccRRrxxxxxxxrRcc',
    'cRRrxxxxxxxxrRRc',
    'RRrxrRRrRRrxrRR',   # bars
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'ccRRrxxxxxxxxrRcc',
    'cccRRrrrrrrRRccc',
    'ccccRRRRRRRRcccc',
    '5554555555545554',
    '5554444444445554',
    '4444444444444444',
    '5555555455555554',
    '5555555455555554',
]

SPRITES['door_south_locked'] = [
    '5555555455555554',
    '5555555455555554',
    '4444444444444444',
    '5554444444445554',
    '5554555555545554',
    'ccccRRRRRRRRcccc',
    'cccRRrrrrrrRRccc',
    'ccRRrxxxxxxxxrRcc',
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'RrxRRrxxxxxrRRrR',
    'RRrxrRRrRRrxrRR',
    'cRRrxxxxxxxxrRRc',
    'ccRRrxxxxxxxrRcc',
    'ccccRRRRRRRRcccc',
]

SPRITES['door_east_locked'] = [
    'ccccccccc5555555',
    'cdddddRRR5555555',
    'cddddRrxR4444444',
    'cdddRrxxR5555555',
    'cddRrxxxR5555555',
    'cdRrxxxxR5555555',
    'RrxxxxxrR5555555',
    'RrrrrrrRR5555555',
    'RrxxxxxrR5555555',
    'RrxxxxxrR5555555',
    'cdRrxxxxR5555555',
    'cddRrxxxR5555555',
    'cdddRrxxR5555555',
    'cddddRrxR4444444',
    'cdddddRRR5555555',
    'ccccccccc5555555',
]

SPRITES['door_west_locked'] = [
    '5555555ccccccccc',
    '5555555RRRdddddс',
    '4444444RxrRddddc',
    '5555555RxxrRdddc',
    '5555555RxxxrRddc',
    '5555555RxxxxrRdc',
    '5555555RrxxxxxrR',
    '5555555RRrrrrrRR',
    '5555555RrxxxxxrR',
    '5555555RrxxxxxrR',
    '5555555RxxxxrRdc',
    '5555555RxxxrRddc',
    '5555555RxxrRdddc',
    '4444444RxrRddddc',
    '5555555RRRdddddс',
    '5555555ccccccccc',
]

# Obstacles — on transparent background (placed over floor by renderer)
SPRITES['obstacle_rock'] = [
    '................',
    '................',
    '.....KKKK.......',
    '....K77888K.....',
    '...K787888bK....',
    '..K77888888bK...',
    '..K788888888K...',
    '..K88888888bK...',
    '..K888888bbbK...',
    '..K78888bbbKK...',
    '...K7788bKK.....',
    '....KKKKKK......',
    '................',
    '................',
    '................',
    '................',
]

SPRITES['obstacle_barrel'] = [
    '................',
    '....KKKKKKKK....',
    '...KVVVVVVVVKk..',
    '..KWwwwwwwwwWKk.',
    '..KVVWVVVVWVVKk.',
    '..KWWWWWWWWWWK..',
    '..KwwwwwwwwwwKk.',
    '..KVVWVVVVWVVKk.',
    '..KwwwwwwwwwwKk.',
    '..KVVWVVVVWVVKk.',
    '..KWWWWWWWWWWK..',
    '..KwwwwwwwwwwKk.',
    '...KVVVVVVVVKk..',
    '....KKKKKKKK....',
    '................',
    '................',
]

SPRITES['obstacle_skull'] = [
    '................',
    '................',
    '.....KKKKKK.....',
    '....KBBBBBBKk...',
    '...KBBgBBgBBKk..',
    '...KBKKBBKKBKk..',
    '...KBKKBBKKBKk..',
    '...KBBBBBBBBKk..',
    '...KBnnnnnBBKk..',
    '...KBBBnBBBBKk..',
    '....KBKnKBKKk...',
    '....KKKKKKKk....',
    '................',
    '................',
    '................',
    '................',
]

SPRITES['obstacle_pillar'] = [
    '....KLLLLLLK....',
    '...KLeeeeedLKk..',
    '..KLdddddddLLKk.',
    '..KLdLLLLLdLLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLllllLdLKk.',
    '..KLdLLLLLdLLKk.',
    '..KLdddddddLLKk.',
    '...KLeeeeedLKk..',
    '....KLLLLLLK....',
    '................',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 4 — DECORATIONS
# ══════════════════════════════════════════════════════════════════════════════

SPRITES['deco_torch'] = [
    '................',
    '......KfK.......',
    '.....KfFfK......',
    '....KfFFFFk.....',
    '.....KfGFK......',
    '......KGK.......',
    '.....KZZZKk.....',
    '....KZZZZZKk....',
    '....KZZZZZKk....',
    '.....KZZZZ......',
    '......KZK.......',
    '.....KZZZKk.....',
    '....KZZZZZKk....',
    '....KZZZZZKk....',
    '.....KZZZK......',
    '......KKK.......',
]

SPRITES['deco_cobweb_corner'] = [
    'SSSSSSSSSSSSSSSS',
    'KSSSSSSSSSSSSSsk',
    'sKSSSSSSSSSSssk.',
    '.sKSSSSSSSsssk..',
    '..sKSSSSsssk....',
    '...sKSsssk......',
    '....ssk.........',
    '.....k..........',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
    '................',
]

SPRITES['deco_bones'] = [
    '................',
    '................',
    '..KBBKk.........',
    '..KnBKk.........',
    '...KBKk.KBBKk...',
    '....Kk..KnBKk...',
    '........KBBKk...',
    '...KBBBBBBBBK...',
    '..KBBBBBBBBBKk..',
    '...KBBBBBBBBK...',
    '...KnBKk........',
    '....KBKk.KBBKk..',
    '....Kk...KnBKk..',
    '.........KBBKk..',
    '................',
    '................',
]

SPRITES['deco_pot'] = [
    '................',
    '................',
    '......KKK.......',
    '.....KCCC Kk....',
    '....KCCCCCCKk...',
    '...KvCCCCCCCKk..',
    '...KvCCCCCCCKk..',
    '...KvCCCCCCCKk..',
    '....KCCCCCCKk...',
    '.....KCCCCKk....',
    '......KKKKk.....',
    '...KKKKKKKKKk...',
    '..Kvvvvvvvvvkk..',
    '...KKKKKKKKKk...',
    '................',
    '................',
]

SPRITES['deco_chain'] = [
    '......KHHK......',
    '.....KHhhHKk....',
    '......KHHK......',
    '.....KKhhKK.....',
    '......KhhK......',
    '.....KHhhHKk....',
    '......KHHK......',
    '.....KKhhKK.....',
    '......KhhK......',
    '.....KHhhHKk....',
    '......KHHK......',
    '.....KKhhKK.....',
    '......KhhK......',
    '.....KHhhHKk....',
    '......KHHK......',
    '................',
]

SPRITES['deco_altar'] = [
    '................',
    '................',
    '....KKKKKKKK....',
    '...KgeeeeeegKk..',
    '...KeggggggeKk..',
    '...KgeeeeeegKk..',
    '..KKKKKKKKKKKK..',
    '..KggggggggggK..',
    '..KgeeeeeeeeK...',
    '..KKKKKKKKKKKK..',
    '.KKKKKKKKKKKKKk.',
    '.KggggggggggggK.',
    '.KggggggggggggK.',
    '.KKKKKKKKKKKKK..',
    '................',
    '................',
]

SPRITES['deco_pentagram'] = [
    '5555555555555555',
    '5555555X5555P555',   # boss warning X, magic P
    '5555555X555P5555',
    '555XXXXX555P5555',
    '5555555X5P5P5555',
    '5555555XPP5P5555',
    '555pPPPXPPPP5555',
    '5555555PPPPP5555',   # center of pentagram
    '555PppPXPPPp5555',
    '5555555XPP5P5555',
    '5555555XP55P5555',
    '5555555X55PpP555',
    '555XXXXXX555P555',
    '5555555X55555555',
    '5555555X55555555',
    '5555555555555555',
]

SPRITES['deco_shopkeeper'] = [
    '................',
    '....KKKKKKKK....',
    '...KddddddddKk..',
    '..KdTTTTTTTTKk..',
    '..KdTttTtttTKk..',
    '..KdTTTTTTTTKk..',
    '..KdTtttttTTKk..',
    '..KdTTTTTTTTKk..',
    '..KKKKKKKKKKKk..',
    '..KccccccccccK..',
    '..KcQcccccccQK..',
    '..KccccccccccK..',
    '..KccQcQcQcccK..',
    '..KccccccccccK..',
    '..KKKKKKKKKKKK..',
    '................',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 5 — SPECIAL TILES
# ══════════════════════════════════════════════════════════════════════════════

SPRITES['room_boss_marker'] = [
    '5555555555555555',
    '5555555555555555',
    '555XXXXXXXXXX555',
    '55X555555555X555',   # skull shape outline in red
    '55X5X5555X55X555',
    '55X5XKKKX55X555',
    '55X5555555X5X555',
    '55X5KKKKKK5XX555',
    '55X55555555X5555',
    '555XXXXXXXXXXXXX',
    '5555555555555555',
    '5555XXX5XXX55555',   # crossed bones
    '555555XXXXX55555',
    '5555XXX5XXX55555',
    '5555555555555555',
    '5555555555555555',
]

SPRITES['room_treasure_marker'] = [
    '5555555555555555',
    '55555YYYYYYY5555',   # treasure chest outline in gold
    '5555YQQQQQQQY555',
    '5555YQqqqqqQY555',
    '5555YQQQQQQQY555',
    '5555YYYYYYYYY555',
    '5555YQqQqQqQY555',
    '5555YYYYYYYYY555',
    '5555555555555555',
    '555555YYYYY55555',   # star
    '5555YYYYYYYYY555',
    '55YYYYYYYYYYY555',
    '5555YYYYYYYYY555',
    '555555YYYYY55555',
    '5555555555555555',
    '5555555555555555',
]

SPRITES['room_shop_marker'] = [
    '5555555555555555',
    '5555555555555555',
    '5555TTTTTTTTT555',
    '555TtttttttttT55',
    '555TtTTTTTTtTT55',
    '555TtTQQQQTtT555',
    '555TtTQqqqTtT555',
    '555TtTQQQQTtT555',
    '555TtTtttttTT555',
    '555TttttttttT555',
    '5555TTTTTTTTT555',
    '5555555555555555',
    '5555555T5T55T555',   # coin symbols
    '5555555TQT55T555',
    '5555555555555555',
    '5555555555555555',
]

SPRITES['room_secret_marker'] = [
    '5555555555555555',
    '5555555555555555',
    '5555555555555555',
    '55555UUUUUU55555',   # barely visible question mark
    '5555UUuuuuUU5555',
    '5555UuUUUuuU5555',
    '5555UuUUUuuU5555',
    '55555UUUUU55555.',
    '5555555UuU555555',
    '555555UUuU555555',
    '5555555555555555',
    '5555555UuU555555',
    '555555UUuUU55555',
    '5555555555555555',
    '5555555555555555',
    '5555555555555555',
]

SPRITES['pit'] = [
    'oooooooooooooooo',
    'oOOOOOOOOOOOOOoo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'ooOOOOOOOOOOOOoo',
    'oooooooooooooooo',
]

SPRITES['pit_edge_top'] = [
    '5555555455555554',   # floor above pit
    '5555555455555554',
    '4444444444444444',
    '3333333333333333',   # edge shadow
    '2222222222222222',
    '1111111111111111',
    'oooooooooooooooo',
    'oOOOOOOOOOOOOOoo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
    'oOOOOOOOOOOOOOOo',
]

SPRITES['pit_edge_side'] = [
    '5555554455555544',   # floor on left of pit
    '5555544455555444',
    '5555444355554443',
    '5554443355544433',
    '5554433255544322',
    '5554432155544321',
    'oooo1111oooo1111',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
    'oOOOOoOOoOOOOoOO',
]

SPRITES['trapdoor_open'] = [
    '5555555555555555',
    '5555KKKKKKKK5555',
    '555KwwwwwwwwK555',
    '555KwKKKKKKwK555',
    '555KwKWWWWKwK555',
    '555KwKWVWVKwK555',   # ladder rungs (V=wood light)
    '555KwKWVWVKwK555',
    '555KwKWVWVKwK555',
    '555KwKWVWVKwK555',
    '555KwKWKKKKwK555',
    '555KwwwwwwwwK555',
    '555K11111111K555',   # dark pit below
    '5555K111111K5555',
    '55555KKKKKK55555',
    '5555555555555555',
    '5555555555555555',
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 6 — BACKGROUND FILLS + MINIMAP
# ══════════════════════════════════════════════════════════════════════════════

# bg_room_fill — same as floor_plain but emphasised for tileable use
SPRITES['bg_room_fill'] = [
    '5555555455555554',
    '5665554466555454',
    '6555444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '4444444444444444',
    '5555555455555554',
    '5665554466555454',
    '6555444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
    '4444444444444444',
    '5555555455555554',
    '5665554466555454',
]

SPRITES['bg_void'] = [
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
    '1111111111111111',
]

SPRITES['bg_wall_fill'] = [
    'cccccccccccccccc',
    'ceddddceddddcedc',
    'cdddddcdddddcddc',
    'acddddacddddacdc',
    'aaaaaaaaaaaaaaaa',
    'eddddaeddddaedda',
    'dddddadddddaddda',
    'cddddacddddacdda',
    'aaaaaaaaaaaaaaaa',
    'ceddddceddddcedc',
    'cdddddcdddddcddc',
    'acddddacddddacdc',
    'aaaaaaaaaaaaaaaa',
    'eddddaeddddaedda',
    'dddddadddddaddda',
    'cddddacddddacdda',
]

# Shadow tiles (semi-transparent look using darker stone colors)
SPRITES['shadow_east'] = [
    '5555555455555554',
    '4555555444555544',
    '3455555433555443',
    '2345555423554433',
    '2234555422544332',
    '2223555422453322',
    '2222355422433222',
    '2222245422432222',
    '2222245422432222',
    '2222355422433222',
    '2223555422453322',
    '2234555423554433',
    '3455555433555443',
    '4555555444555544',
    '5555555455555554',
    '4444444444444444',
]

SPRITES['shadow_south'] = [
    '4444444444444444',
    '4333444433334444',
    '4332244433224444',
    '4321244432124444',
    '4321144432114444',
    '4321144432114444',
    '4321244432124444',
    '4332244433224444',
    '4333444433334444',
    '4444444444444444',
    '5555555455555554',
    '5665554466555454',
    '6555444565554445',
    '5554444555444445',
    '5544444555444445',
    '5444444454444444',
]

SPRITES['shadow_corner'] = [
    '4444444444444444',
    '4322222222222224',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4211111111111124',
    '4322222222222224',
    '4444444444444444',
]

# Minimap tiles (small colored squares)
SPRITES['minimap_room'] = [
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
    'kkkkkkkkkkkkkkkk',
]

SPRITES['minimap_current'] = [
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
    'yyyyyyyyyyyyyyyy',
]


# ---------------------------------------------------------------------------
# Layout — must be 16 columns wide × 8 rows
# ---------------------------------------------------------------------------
COLS = 16
ROWS = 8
TILE = 16      # source pixel size
SCALE = 2      # ×2 → 32×32 output
SPRITE_OUT = TILE * SCALE  # 32
SHEET_W = COLS * SPRITE_OUT  # 512
SHEET_H = ROWS * SPRITE_OUT  # 256

LAYOUT: list[list[str | None]] = [
    # Row 0 — floor variants
    ['floor_plain', 'floor_cracked', 'floor_bloodstain', 'floor_grate',
     'floor_dirt', 'floor_mossy', 'floor_decorated', 'floor_shadow',
     None, None, None, None, None, None, None, None],
    # Row 1 — directional walls
    ['wall_top', 'wall_bottom', 'wall_left', 'wall_right',
     'wall_corner_tl', 'wall_corner_tr', 'wall_corner_bl', 'wall_corner_br',
     None, None, None, None, None, None, None, None],
    # Row 2 — inner corners + open doors
    ['wall_inner_tl', 'wall_inner_tr', 'wall_inner_bl', 'wall_inner_br',
     'door_north_open', 'door_south_open', 'door_east_open', 'door_west_open',
     None, None, None, None, None, None, None, None],
    # Row 3 — locked doors + obstacles
    ['door_north_locked', 'door_south_locked', 'door_east_locked', 'door_west_locked',
     'obstacle_rock', 'obstacle_barrel', 'obstacle_skull', 'obstacle_pillar',
     None, None, None, None, None, None, None, None],
    # Row 4 — decorations
    ['deco_torch', 'deco_cobweb_corner', 'deco_bones', 'deco_pot',
     'deco_chain', 'deco_altar', 'deco_pentagram', 'deco_shopkeeper',
     None, None, None, None, None, None, None, None],
    # Row 5 — special tiles
    ['room_boss_marker', 'room_treasure_marker', 'room_shop_marker', 'room_secret_marker',
     'pit', 'pit_edge_top', 'pit_edge_side', 'trapdoor_open',
     None, None, None, None, None, None, None, None],
    # Row 6 — background fills + minimap
    ['bg_room_fill', 'bg_void', 'bg_wall_fill', 'shadow_east',
     'shadow_south', 'shadow_corner', 'minimap_room', 'minimap_current',
     None, None, None, None, None, None, None, None],
    # Row 7 — spare
    [None] * 16,
]


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def render_sprite(grid: list[str]) -> Image.Image:
    """Render a 16×16 string grid into a 32×32 RGBA image."""
    img = Image.new('RGBA', (TILE, TILE), (0, 0, 0, 0))
    pixels = img.load()
    for row_idx, row in enumerate(grid):
        for col_idx, ch in enumerate(row):
            if col_idx >= TILE or row_idx >= TILE:
                continue
            color = P.get(ch)
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
            print(f'  rendered {name:30s} → ({x:3d}, {y:3d})')

    # Pixi.js compatible atlas manifest
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
            'image': 'level-sprites.png',
            'size': {'w': SHEET_W, 'h': SHEET_H},
            'scale': '1',
        },
    }
    return sheet, manifest


def main() -> None:
    out_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'web', 'public', 'assets')
    )
    os.makedirs(out_dir, exist_ok=True)

    print(f'Building level sprite sheet ({SHEET_W}×{SHEET_H}) …')
    sheet, manifest = build_sheet()

    png_path = os.path.join(out_dir, 'level-sprites.png')
    sheet.save(png_path, 'PNG')
    print(f'\nSaved  {png_path}')

    json_path = os.path.join(out_dir, 'level-sprites.json')
    with open(json_path, 'w') as fh:
        json.dump(manifest, fh, indent=2)
    print(f'Saved  {json_path}')
    print('\nDone.')


if __name__ == '__main__':
    main()
