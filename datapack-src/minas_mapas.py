"""Construcciones originales de Minas Astrales, en formato Sponge v2."""
from array import array
import gzip
from math import atan2, cos, hypot, sin
from pathlib import Path
from random import Random

# Las siete construcciones comparten las coordenadas del pozo y la plataforma.
W, H, L = 180, 84, 190
CENTER = (90, 91)
THEMES = {
    # terreno, estratos, caminos, arquitectura, acento, radio x/z, relieve, semilla
    "carbon": ("tuff", "stone", "cobbled_deepslate", "deepslate_bricks", "ochre_froglight", 66, 74, 18, 19),
    "cobre": ("red_sandstone", "orange_terracotta", "cut_red_sandstone", "cut_copper", "oxidized_copper", 72, 58, 15, 31),
    "oro": ("sandstone", "smooth_sandstone", "cut_sandstone", "chiseled_sandstone", "gold_block", 64, 67, 11, 67),
    "esmeralda": ("moss_block", "stone", "mossy_stone_bricks", "stone_bricks", "emerald_block", 71, 75, 13, 103),
    "diamante": ("snow_block", "packed_ice", "calcite", "polished_diorite", "blue_ice", 63, 73, 17, 157),
    "netherita": ("blackstone", "basalt", "polished_blackstone_bricks", "cracked_polished_blackstone_bricks", "shroomlight", 69, 66, 20, 197),
}


def terrain(theme):
    skin, strata, path, masonry, accent, rx, rz, relief, seed = THEMES[theme]
    random = Random(seed)
    palette = {"minecraft:air": 0}
    blocks = array("B", [0]) * (W * H * L)

    def material(name):
        return palette.setdefault("minecraft:" + name, len(palette))

    def set_block(x, y, z, name):
        if 0 <= x < W and 0 <= y < H and 0 <= z < L:
            blocks[x + W * (z + L * y)] = material(name)

    tops = {}
    cx, cz = CENTER
    core = material(strata)
    crust = material(skin)
    for z in range(L):
        for x in range(W):
            dx, dz = x - cx, z - cz
            theta = atan2(dz, dx)
            border = 1 + 0.08 * sin(3 * theta + seed) + 0.055 * cos(5 * theta)
            radius = hypot(dx / rx, dz / rz) / border
            if radius >= 1:
                continue
            ridge = max(0, (radius - 0.35) * 1.8)
            waves = (sin(x / 14 + seed) * cos(z / 17) + 1) / 2
            top = 28 + int(relief * ridge * waves)
            bottom = max(1, 24 - int(21 * (1 - radius ** 1.5)) + int(2 * sin(dx / 8 + dz / 10)))
            tops[x, z] = top
            offset = x + W * z
            for y in range(bottom, top + 1):
                blocks[offset + W * L * y] = crust if y == top else core

    # Paseo alrededor del pozo y conexiones hacia los cuatro puntos de la isla.
    for (x, z), top in tops.items():
        dx, dz = abs(x - cx), abs(z - cz)
        if (18 <= max(dx, dz) <= 22 and min(dx, dz) <= 22) or ((dx <= 2 or dz <= 2) and max(dx, dz) <= 54):
            set_block(x, top, z, path)
        if 73 <= x <= 107 and 74 <= z <= 108:
            for y in range(29, top + 1):
                set_block(x, y, z, "air")
            if 75 <= x <= 105 and 76 <= z <= 106:
                set_block(x, 8, z, "bedrock")
                for y in range(9, 29):
                    set_block(x, y, z, "air")
            elif x in (74, 106) or z in (75, 107):
                for y in range(8, 29):
                    set_block(x, y, z, masonry)
            else:
                set_block(x, 28, z, path)

    # Acceso norte, con luces en el perímetro y un pórtico visible desde el spawn.
    for x in (82, 98):
        for y in range(29, 38):
            set_block(x, y, 67, masonry if y != 35 else accent)
    for x in range(82, 99):
        set_block(x, 38, 67, masonry)
        if abs(x - 90) <= 4:
            set_block(x, 39, 67, path)
    for x, z in ((69, 70), (111, 70), (69, 112), (111, 112)):
        for y in range(29, 34):
            set_block(x, y, z, masonry)
        set_block(x, 34, z, "lantern")

    def tower(x, z, size, height, taper):
        base = tops.get((x, z), 28)
        for dy in range(height):
            span = max(1, size - int(dy * taper))
            for dz in range(-span, span + 1):
                for dx in range(-span, span + 1):
                    if max(abs(dx), abs(dz)) == span:
                        name = accent if dy % 5 == 4 and (dx == 0 or dz == 0) else masonry
                        set_block(x + dx, base + dy, z + dz, name)
        for dz in range(-span, span + 1):
            for dx in range(-span, span + 1):
                set_block(x + dx, base + height, z + dz, path)

    structures = {
        "carbon": [(61, 60, 7, 19, .13), (119, 117, 8, 15, .1), (52, 113, 5, 13, .2)],
        "cobre": [(55, 92, 8, 23, .17), (120, 56, 6, 18, .13), (119, 128, 9, 13, .3)],
        "oro": [(54, 65, 9, 15, .53), (124, 114, 12, 19, .55), (62, 123, 5, 12, .33)],
        "esmeralda": [(60, 55, 8, 13, .35), (126, 89, 10, 21, .32), (53, 112, 7, 13, .25)],
        "diamante": [(55, 106, 8, 22, .27), (125, 64, 7, 27, .21), (123, 125, 6, 16, .2)],
        "netherita": [(51, 91, 7, 28, .18), (126, 67, 8, 24, .21), (116, 131, 10, 16, .3)],
    }
    for structure in structures[theme]:
        tower(*structure)

    # Siluetas exteriores distintas por bioma.
    decor = {
        "carbon": ("spruce_log", "spruce_leaves[persistent=true]", 5, 29),
        "cobre": ("terracotta", "weathered_copper", 2, 20),
        "oro": ("stripped_jungle_log", "jungle_leaves[persistent=true]", 4, 20),
        "esmeralda": ("dark_oak_log", "azalea_leaves[persistent=true]", 7, 33),
        "diamante": ("packed_ice", "blue_ice", 2, 25),
        "netherita": ("basalt", "magma_block", 2, 36),
    }
    trunk, crown, spread, count = decor[theme]
    reserved = structures[theme]
    for _ in range(count):
        for _ in range(30):
            x, z = random.randrange(20, 160), random.randrange(20, 170)
            dx, dz = abs(x - cx), abs(z - cz)
            if ((x, z) in tops and max(dx, dz) > 26 and min(dx, dz) > 4
                    and all(hypot(x - a, z - b) > size + 7 for a, b, size, *_ in reserved)):
                break
        else:
            continue
        base = tops[x, z]
        height = random.randrange(5, 13)
        for dy in range(1, height + 1):
            set_block(x, base + dy, z, trunk)
        for dy in range(-2, 3):
            radius = max(0, spread - abs(dy))
            for dz in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + dz * dz <= radius * radius and (dx or dz or dy > 0):
                        set_block(x + dx, base + height + dy, z + dz, crown)
    return palette, blocks


def write_maps(directory: Path):
    from mapas import nbt_payload, nbt_string

    for theme in THEMES:
        palette, blocks = terrain(theme)
        # Las paletas de estas islas caben en un solo byte VarInt.
        assert len(palette) < 128
        root = {
            "Version": (3, 2), "DataVersion": (3, 3120),
            "Width": (2, W), "Height": (2, H), "Length": (2, L),
            "Offset": (11, [0, 0, 0]),
            "Metadata": (10, {f"WEOffset{axis}": (3, 0) for axis in "XYZ"}),
            "PaletteMax": (3, len(palette)),
            "Palette": (10, {name: (3, index) for name, index in palette.items()}),
            "BlockData": (7, bytes(blocks)),
            "BlockEntities": (9, []),
        }
        raw = b"\x0a" + nbt_string("Schematic") + nbt_payload((10, root))
        (directory / f"astral-mina-{theme}.schem").write_bytes(gzip.compress(raw, mtime=0))
