"""Genera Skript, instalación y la variante del marcador para las minas."""
import argparse
import gzip
from pathlib import Path
from zipfile import ZipFile

from tools import DRILLS, FACING, area_ranges

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/minas"
ORES = [
    ("Carbón", "coal", "coal_block"),
    ("Cobre", "copper", "copper_block"),
    ("Hierro", "iron", "iron_block"),
    ("Oro", "gold", "gold_block"),
    ("Esmeralda", "emerald", "emerald_block"),
    ("Diamante", "diamond", "diamond_block"),
]
# Cada requisito se cumple en el destino inmediatamente anterior.
GOALS = [0, 350, 550, 750, 1000, 1250, 1600, 2100, 2600, 3200, 3800, 4500, 5500,
         6500, 8000, 9500, 12000, 15000, 20000, 500000]
COSTS = [0, 55, 150, 240, 350, 600, 1000, 2000, 3500, 4800, 6500, 10000, 17000,
         26000, 40000, 60000, 95000, 160000, 300000, 25000000]
FINAL_MINUTES = 25 * 60
DIAMOND_III = 19
MINERAL_MAPS = ("carbon", "cobre", "hierro", "oro", "esmeralda", "diamante")
MAPS_BY_MINE = MINERAL_MAPS * 2 + ("netherita",) + MINERAL_MAPS + ("netherita",)
MIXES = [
    *[(f"I · {label}", "stone", f"{ore}_ore", 24) for label, ore, _ in ORES],
    *[(f"II · {label}", f"{ore}_ore", block, 30) for label, ore, block in ORES],
    ("II · Restos ancestrales", "netherrack", "ancient_debris", 23),
    *[(f"III · {label}", block, block, 0) for label, _, block in ORES],
    ("III · Netherita", "netherite_block", "netherite_block", 0),
]
MINES = [(*mix, goal, cost) for mix, goal, cost in zip(MIXES, GOALS, COSTS, strict=True)]
PRICES = {
    "stone": 0.16, "cobblestone": 0.16,
    "coal": 1, "coal_ore": 1, "deepslate_coal_ore": 1, "coal_block": 9,
    "raw_iron": 1.3, "iron_ingot": 1.3, "iron_ore": 1.3, "deepslate_iron_ore": 1.3,
    "iron_block": 11.7, "raw_iron_block": 11.7,
    "raw_gold": 1.95, "gold_ingot": 1.95, "gold_ore": 1.95, "deepslate_gold_ore": 1.95,
    "gold_block": 17.55, "raw_gold_block": 17.55, "nether_gold_ore": 0.8, "gold_nugget": 0.21,
    "diamond": 4, "diamond_ore": 4, "deepslate_diamond_ore": 4, "diamond_block": 36,
    "raw_copper": 0.2, "copper_ingot": 0.2, "copper_ore": 0.2, "deepslate_copper_ore": 0.2,
    "copper_block": 1.8, "raw_copper_block": 1.8, "netherite_block": 4390.2,
    "redstone": 1, "redstone_block": 9, "redstone_ore": 4, "deepslate_redstone_ore": 4,
    "lapis_lazuli": 1, "lapis_block": 9, "lapis_ore": 4, "deepslate_lapis_ore": 4,
    "emerald": 4, "emerald_block": 36, "emerald_ore": 4, "deepslate_emerald_ore": 4,
    "quartz": 1, "nether_quartz_ore": 1, "amethyst_shard": 0.5,
    "netherrack": 0.04, "ancient_debris": 120, "netherite_scrap": 120, "netherite_ingot": 487.8,
}


def config():
    lines = [f"    set {{-am.finalMinutes}} to {FINAL_MINUTES}"]
    for i, (name, base, ore, chance, goal, cost) in enumerate(MINES, 1):
        slot = 9 + i if i <= 6 else 12 + i if i <= 13 else 14 + i
        lines.append(f"    set {{-am.slot::{i}}} to {slot}")
        lines.append(f"    set {{-am.destination::{slot}}} to {i}")
        for key, value in dict(name=f'"{name}"', base=f'Material.{base.upper()}',
                               ore=f'Material.{ore.upper()}', chance=chance, goal=goal, cost=cost).items():
            lines.append(f"    set {{-am.{key}::{i}}} to {value}")
    for material, price in PRICES.items():
        lines.append(f"    set {{-am.price::{material.upper()}}} to {price}")
    for drill in DRILLS:
        lines.append(f'    set {{-am.drill::{drill["id"]}}} to {drill["area"]}')
    for area in range(2, 6):
        offsets = {direction: [(0, sign * depth, 0) for depth, minimum in ((1, 2), (2, 4), (3, 5)) if area >= minimum]
                   for direction, sign in (("down", -1), ("up", 1))}
        for face, (_, right) in FACING.items():
            for up in (0, 1):
                horizontal, vertical = area_ranges(area, up, False)
                offsets[f"{face}{up}"] = [(u * right[0], v, u * right[2])
                                         for u in horizontal for v in vertical if (u, v) != (0, 0)]
        for direction, entries in offsets.items():
            for index, (x, y, z) in enumerate(entries, 1):
                lines.append(f'    set {{-am.offset::{area}::{direction}::{index}}} to "{x},{y},{z}"')
    return "\n".join(lines)


def sidebar(original):
    start = original.index("    astral:\n")
    end = original.index("conditions:\n", start)
    block = original[start:end]
    daily = block.index('        - "<aqua><bold>Misiones diarias')
    mine = block[:daily].replace("    astral:\n", '    minas:\n      display-condition: "%world%=astral_minas"\n')
    mine += """        - "<aqua><bold>Progresión de minas</bold>"
        - "<gray>Mina actual||%condition:am_here%"
        - "<gray>Siguiente||%condition:am_next%"
        - "<gray>Avanza en||%condition:am_current%"
        - "<gray>Bloques||<white>%objective_score_{am_blocks}%<gray>/%objective_score_{am_goal}%"
        - "<gray>Costo||<gold>%objective_score_{am_cost}%"
        - "%condition:am_time%"
        - "%animation:astral_ip%"
"""
    conditions = [
        "  am_time:", "    conditions:",
        f'      - "%objective_score_{{am_rank}}%={DIAMOND_III}"',
        f'    true: "<gray>Minería activa||<white>%objective_score_{{am_minutes}}%/{FINAL_MINUTES} min"',
        '    false: ""',
    ]

    def label_tree(key, objective, labels, lo, hi):
        identifier = f"am_{key}" if (lo, hi) == (1, len(labels)) else f"am_{key}{lo}_{hi}"
        if lo == hi:
            return f"<white>{labels[lo-1]}"
        mid = (lo + hi) // 2
        yes = label_tree(key, objective, labels, lo, mid)
        no = label_tree(key, objective, labels, mid + 1, hi)
        conditions.extend([f"  {identifier}:", "    conditions:",
                           f'      - "%objective_score_{{{objective}}}%<={mid}"',
                           f'    true: "{yes}"', f'    false: "{no}"'])
        return f"%condition:{identifier}%"

    labels = [row[0] for row in MINES]
    for key, objective, options in (("here", "am_here", labels), ("current", "am_rank", labels),
                                     ("next", "am_rank", labels[1:] + ["Completada"])):
        label_tree(key, objective, options, 1, len(options))
    return original[:start] + mine + block + "conditions:\n" + "\n".join(conditions) + "\n" + original[end+len("conditions:\n"):]


def prepare_schematic(source):
    from mapas import NBT, nbt_payload, nbt_string

    tree = NBT(gzip.decompress(source.read_bytes()), typed=True).root()
    root = tree[1]
    signature = tuple(root[key][1] for key in ("Version", "Width", "Height", "Length"))
    if signature != (2, 180, 124, 190) or root["Offset"][1] != [-436, 134, -209]:
        raise ValueError("No se reconoce el adjunto mina.schem")
    root["Offset"] = (11, [0, 0, 0])
    for axis in "XYZ":
        root["Metadata"][1]["WEOffset" + axis] = (3, 0)

    # Quita la lógica del minijuego original antes de importar la construcción.
    forbidden = {"command_block", "chain_command_block", "repeating_command_block",
                 "structure_block", "jigsaw", "spawner", "trial_spawner"}
    palette = root["Palette"][1]
    unsafe = {tag[1] for name, tag in palette.items()
              if name.partition("[")[0].removeprefix("minecraft:") in forbidden}
    safe = {name: tag for name, tag in palette.items() if tag[1] not in unsafe}
    indexes = {tag[1]: index for index, tag in enumerate(safe.values())}
    air = indexes[palette["minecraft:air"][1]]
    indexes.update(dict.fromkeys(unsafe, air))
    root["Palette"] = (10, {name: (3, indexes[tag[1]]) for name, tag in safe.items()})
    root["PaletteMax"] = (3, len(safe))
    packed = bytearray()
    value = shift = 0
    for byte in root["BlockData"][1]:
        value |= (byte & 127) << shift
        if byte >= 128:
            shift += 7
            continue
        index = indexes[value]
        while index >= 128:
            packed.append((index & 127) | 128)
            index >>= 7
        packed.append(index)
        value = shift = 0
    root["BlockData"] = (7, packed)

    entities = []
    for entry in root["BlockEntities"][1]:
        data = entry[1]
        kind = data["Id"][1].removeprefix("minecraft:")
        if kind in forbidden | {"mob_spawner", "sign", "hanging_sign", "lectern"} or "Command" in data:
            continue
        for field in ("Items", "LootTable", "LootTableSeed"):
            data.pop(field, None)
        entities.append(entry)
    root["BlockEntities"] = (9, entities)
    root.pop("Entities", None)
    raw = bytes([tree[0]]) + nbt_string("Schematic") + nbt_payload(tree)
    target = ROOT / ".local/minas/astral-mina-hierro.schem"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(raw, mtime=0))
    from minas_mapas import write_maps
    write_maps(target.parent)
    with ZipFile(OUT / "Mapas-Minas-Astrales.zip", "w") as archive:
        for theme in (*MINERAL_MAPS, "netherita"):
            name = f"astral-mina-{theme}.schem"
            archive.write(target.parent / name, name)


def generate():
    from lobby import TAB_SECTIONS
    script = Path(__file__).with_suffix(".sk").read_text(encoding="utf-8")
    script = script.replace("    # CATALOGO", config())
    outputs = {OUT / "Skript/scripts/astral_minas.sk": script,
               ROOT / "build/lobby/TAB/secciones-config.yml": TAB_SECTIONS}
    commands = [
        '# Ejecutar la creación una sola vez. Confirmar que la dimensión es minecraft:astral_minas.',
        '/mv create astral_minas normal --world-type FLAT --no-structures --no-adjust-spawn --generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
        '/mv modify astral_minas set pvp false',
        '/mv modify astral_minas set hunger false',
        '/mv modify astral_minas set gamemode survival',
        '/mv modify astral_minas set allow-weather false',
        '/mv gamerule set minecraft:spawn_mobs false astral_minas',
        '/mv gamerule set minecraft:keep_inventory true astral_minas',
        '/mv gamerule set minecraft:advance_time false astral_minas',
        '/minecraft:execute in minecraft:astral_minas run time set noon',
        '/rg flag -w astral_minas __global__ block-place deny',
        '/rg flag -w astral_minas __global__ chest-access deny',
        '/rg flag -w astral_minas __global__ pistons deny',
        "# Subir los siete .schem del ZIP a WorldEdit/schematics antes de pegar.",
        "# Pegar en creativo como administrador. Confirmar cada paste antes de seguir.",
    ]
    for i, theme in enumerate(MAPS_BY_MINE):
        x = i * 512
        commands.extend([
            f"/minecraft:execute in minecraft:astral_minas run minecraft:tp @s {x} 64 0",
            f"//schem load astral-mina-{theme}",
            "//paste -a",
            f"/minecraft:fill {x+84} 92 67 {x+96} 92 74 polished_deepslate",
            f"/minecraft:fill {x+84} 93 67 {x+96} 96 74 air",
            f"/minecraft:summon villager {x+94.5} 93 70.5 {{Tags:[\"astral_mina_venta\"],NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,CustomName:{{text:\"Venta rápida\",color:\"gold\"}},CustomNameVisible:1b}}",
        ])
    commands.extend([
        "/minecraft:execute in minecraft:lobby run minecraft:summon villager 174.636 100 225.735 {Tags:[\"astral_minas_lobby\"],NoAI:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,CustomName:{text:\"Minas Astrales\",color:\"aqua\"},CustomNameVisible:1b}",
        "# La expansión ScoreboardObjectives ya se usa para las diarias. Instalarla si falta.",
        "/papi ecloud download ScoreboardObjectives",
        "/papi reload",
        "/skript reload astral_minas",
        "/tab reload",
        "# Habilitar después de comprobar los nueve pegados y el suelo del aldeano del lobby.",
        "/minasactivar",
    ])
    outputs[OUT / "instalacion.txt"] = "\n".join(commands) + "\n"
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schematic", type=Path, help="copia original de mina.schem")
    args = parser.parse_args()
    generate()
    if args.schematic:
        prepare_schematic(args.schematic)
