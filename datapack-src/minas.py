"""Minas Astrales: genera el Skript (sin skript-reflect), la instalacion y el panel de TAB.

Uso:  python minas.py                          -> build/minas/ y build/lobby/TAB/secciones-config.yml
      python minas.py --schematic <mina.schem> -> prepara el mapa común en .local/minas (no se publican)

Progresion (pedido del duenio): Tier I piedra + mineral, Tier II mineral + bloque compacto, y la
ultima mina es Netherrack con restos ancestrales. Cada mina paga mas por bloque que la anterior.
"""
import argparse
import gzip
from pathlib import Path

from tools import AREA_NAMES, FACING, area_ranges

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/minas"
LOCAL = ROOT / ".local/minas"
WORLD = "astral_minas"
DIM = "minecraft:astral_minas"
SPACING = 512                     # cada mina esta 512 bloques en X despues de la anterior
MAP = "astral-mina-hierro.schem"
PASTE_X, PASTE_Z = 7, 2
PIT = dict(x1=82, x2=112, y1=73, y2=92, z1=78, z2=108)  # Hierro I: X 1106..1136
SPAWN = (89.5, 93, 70.5)          # plataforma junto al pozo
VENDOR = (94.5, 93, 70.5, 0)      # aldeano de venta rapida, mirando al pozo
TRAVEL = (84.5, 93, 70.5, 0)      # aldeano de viajes (lobby u otra mina), del otro lado de la plataforma
MOLD_Y, MOLD_STEP = -20, 25       # moldes de regeneracion debajo del pozo (y -20..-1 y -45..-26)
RESET_MIN = 9                     # minutos entre regeneraciones de una mina con gente
FALL_Y = 66
LOBBY_NPC = (174.636, 100, 225.735, 180)   # 4 bloques al oeste de Expediciones Astrales

ORES = [  # nombre, mena, bloque, mapa
    ("Carbón", "coal_ore", "coal_block", "carbon"),
    ("Cobre", "copper_ore", "copper_block", "cobre"),
    ("Hierro", "iron_ore", "iron_block", "hierro"),
    ("Oro", "gold_ore", "gold_block", "oro"),
    ("Esmeralda", "emerald_ore", "emerald_block", "esmeralda"),
    ("Diamante", "diamond_ore", "diamond_block", "diamante"),
]
# (nombre, base, mineral, % de mineral, mapa, descripcion)
MIXES = [(f"I · {n}", "stone", ore, 22, m, f"Piedra con mena de {n.lower()}.") for n, ore, _, m in ORES]
MIXES += [(f"II · {n}", ore, block, 30, m, f"Mena y bloques de {n.lower()}.") for n, ore, block, m in ORES]
MIXES += [("II · Restos ancestrales", "netherrack", "ancient_debris", 8, "netherita",
           "Netherrack con restos ancestrales.")]
MIXES += [(f"III · {n}", block, block, 0, m, f"Solo bloques de {n.lower()}.") for n, _, block, m in ORES]
MIXES += [("III · Netherita", "netherite_block", "netherite_block", 0, "netherita", "Solo bloques de netherita.")]
# Para abrir la mina N: bloques picados en la mina N-1 y oro (cerca del 80 % de lo que se gana
# vendiendo esos bloques picados a mano, para que alcance con picar y vender).
# Netherita III ademas pide FINAL_MINUTES de mineria activa en Diamante III.
GOALS = [0, 400, 600, 800, 1000, 1300, 1700, 2200, 2700, 3200, 3700, 4500, 5500,
         7000, 8000, 9500, 12000, 15000, 20000, 500000]
COSTS = [0, 80, 150, 300, 550, 1300, 2500, 4000, 7000, 13000, 25000, 60000, 120000,
         250000, 40000, 70000, 135000, 260000, 700000, 25000000]
FINAL_MINUTES = 25 * 60
MINES = [(*mix, goal, cost) for mix, goal, cost in zip(MIXES, GOALS, COSTS, strict=True)]

# Precio de venta por unidad (oro). Incluye lo que suelta cada bloque (la piedra suelta roca, las
# menas sueltan el mineral) y los bloques en si, por si se pican con Toque de seda.
PRICES = {
    "stone": 0.1, "cobblestone": 0.1, "netherrack": 0.2,
    "coal": 0.6, "coal_ore": 0.6, "deepslate_coal_ore": 0.6, "coal_block": 6,
    "raw_copper": 0.25, "copper_ingot": 0.25, "copper_ore": 0.9, "deepslate_copper_ore": 0.9,
    "copper_block": 9, "raw_copper_block": 2.25,
    "raw_iron": 1.5, "iron_ingot": 1.5, "iron_ore": 1.5, "deepslate_iron_ore": 1.5,
    "iron_block": 14, "raw_iron_block": 13.5,
    "raw_gold": 2.5, "gold_ingot": 2.5, "gold_ore": 2.5, "deepslate_gold_ore": 2.5,
    "gold_block": 22, "raw_gold_block": 22.5,
    "emerald": 5, "emerald_ore": 5, "deepslate_emerald_ore": 5, "emerald_block": 45,
    "diamond": 8, "diamond_ore": 8, "deepslate_diamond_ore": 8, "diamond_block": 72,
    "ancient_debris": 600, "netherite_scrap": 600, "netherite_block": 4000,
    "redstone": 0.3, "lapis_lazuli": 0.3, "quartz": 0.4, "nether_quartz_ore": 0.4,
}
DROPS = {"stone": ("cobblestone", 1), "coal_ore": ("coal", 1), "copper_ore": ("raw_copper", 3.5),
         "iron_ore": ("raw_iron", 1), "gold_ore": ("raw_gold", 1), "emerald_ore": ("emerald", 1),
         "diamond_ore": ("diamond", 1)}


def value(material):
    drop, amount = DROPS.get(material, (material, 1))
    return PRICES[drop] * amount


def mine_value(base, ore, chance):
    return round(value(base) * (100 - chance) / 100 + value(ore) * chance / 100, 2)


def slot(i):
    """Tier I (6 minas), II (7) y III (7) en las filas 2, 3 y 4 del menu."""
    if i <= 6:
        return 9 + i
    return 19 + (i - 7) if i <= 13 else 28 + (i - 14)


def config():
    lines = [f"    set {{-am.count}} to {len(MINES)}", f"    set {{-am.finalMinutes}} to {FINAL_MINUTES}"]
    for i, (name, base, ore, chance, _map, desc, goal, cost) in enumerate(MINES, 1):
        s = slot(i)
        lines += [f"    set {{-am.slot::{i}}} to {s}", f"    set {{-am.dest::{s}}} to {i}",
                  f'    set {{-am.name::{i}}} to "{name}"', f'    set {{-am.desc::{i}}} to "{desc}"',
                  f'    set {{-am.base::{i}}} to "minecraft:{base}" parsed as item type',
                  f'    set {{-am.ore::{i}}} to "minecraft:{ore}" parsed as item type',
                  f'    set {{-am.icon::{i}}} to "minecraft:{ore}" parsed as item type',
                  f'    set {{-am.baseid::{i}}} to "minecraft:{base}"',
                  f"    set {{-am.chance::{i}}} to {chance}", f"    set {{-am.goal::{i}}} to {goal}",
                  f"    set {{-am.cost::{i}}} to {cost}",
                  f"    set {{-am.value::{i}}} to {mine_value(base, ore, chance)}"]
    lines.append("    delete {-am.price::*}")
    for material, price in PRICES.items():
        lines.append(f'    set {{_t}} to "minecraft:{material}" parsed as item type')
        lines.append(f"    set {{-am.price::%{{_t}}%}} to {price}")
    # El script reconoce el area por la descripcion "Rompe en area NxM" (ver AREA_NAMES).
    assert AREA_NAMES == {1: "1x1", 2: "2x1", 3: "2x2", 4: "3x3", 5: "4x4"}, "actualizar am_tool_area en minas.sk"
    lines.append("    delete {-am.off::*}")
    for area in range(2, 6):
        offsets = {}
        for face, (forward, right) in FACING.items():
            # Piso o techo: cuadrado horizontal (a lo ancho y hacia adelante) alrededor del bloque.
            horizontal, depth = area_ranges(area, 0, True)
            offsets[f"v{face}"] = [(u * right[0] + v * forward[0], 0, u * right[2] + v * forward[2])
                                   for u in horizontal for v in depth if (u, v) != (0, 0)]
            for up in (0, 1):
                horizontal, vertical = area_ranges(area, up, False)
                offsets[f"{face}{up}"] = [(u * right[0], v, u * right[2])
                                         for u in horizontal for v in vertical if (u, v) != (0, 0)]
        for direction, entries in offsets.items():
            for index, (x, y, z) in enumerate(entries, 1):
                lines.append(f"    set {{-am.off::{area}::{direction}::{index}}} to vector({x}, {y}, {z})")
    return "\n".join(lines)


def script(world=WORLD, dim=DIM):
    text = Path(__file__).with_suffix(".sk").read_text(encoding="utf-8")
    values = {"WORLD": world, "DIM": dim, "SPACING": SPACING, "SPAWN_X": SPAWN[0], "SPAWN_Y": SPAWN[1],
              "SPAWN_Z": SPAWN[2], "MOLD_Y": MOLD_Y, "MOLD_STEP": MOLD_STEP, "RESET_MIN": RESET_MIN,
              "FALL_Y": FALL_Y, "PIT_H": PIT["y2"] - PIT["y1"] + 1, "PIT_W": PIT["x2"] - PIT["x1"] + 1}
    for key, v in PIT.items():
        values[f"PIT_{key.upper()}"] = v
        if key.endswith("2"):
            values[f"PIT_{key.upper()}E"] = v + 0.999
    for key in sorted(values, key=len, reverse=True):
        text = text.replace(f"@{key}@", str(values[key]))
    leftover = [w for w in text.split("@")[1::2] if w.isupper()]
    assert not leftover, f"quedaron valores sin reemplazar: {leftover}"
    return text.replace("    # CATALOGO", config())


def sidebar(original):
    """Agrega al TAB un panel para el mundo de minas: igual al normal, pero en lugar de las
    misiones diarias muestra la mina actual y lo que falta para abrir la siguiente."""
    start = original.index("    astral:\n")
    end = original.index("conditions:\n", start)
    block = original[start:end]
    daily = block.index('        - "<aqua><bold>Misiones diarias')
    mine = block[:daily].replace("    astral:\n", f'    minas:\n      display-condition: "%world%={WORLD}"\n')
    mine += """        - "<aqua><bold>⛏ Minas Astrales</bold>"
        - "<gray>Estás en||%condition:am_here%"
        - "<gray>Siguiente||%condition:am_next%"
        - "<gray>Picar en||%condition:am_current%"
        - "<gray>Bloques||%condition:am_need%"
        - "<gray>Costo||%condition:am_pay%"
        - "%condition:am_time%"
        - "%animation:astral_ip%"
"""
    last = len(MINES)
    conditions = [
        "  am_need:", "    conditions:", f'      - "%objective_score_{{am_rank}}%<{last}"',
        '    true: "<white>%objective_score_{am_blocks}%<gray>/<white>%objective_score_{am_goal}%"',
        '    false: "<green>¡Todas abiertas!"',
        "  am_pay:", "    conditions:", f'      - "%objective_score_{{am_rank}}%<{last}"',
        '    true: "<gold>%objective_score_{am_cost}% oro"', '    false: "<gray>—"',
        "  am_time:", "    conditions:", f'      - "%objective_score_{{am_rank}}%={last - 1}"',
        f'    true: "<gray>Minería activa: <white>%objective_score_{{am_minutes}}%<gray>/{FINAL_MINUTES} min"',
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
                                     ("next", "am_rank", labels[1:] + ["—"])):
        label_tree(key, objective, options, 1, len(options))
    return original[:start] + mine + block + "conditions:\n" + "\n".join(conditions) + "\n" + original[end+len("conditions:\n"):]


def prepare_schematic(source):
    """Arma los 7 mapas en .local/minas a partir del mina.schem que mando el duenio. Quedan solo
    en esta PC: el de Hierro sale de un mapa de terceros y el repo es publico."""
    from mapas import NBT, nbt_payload, nbt_string

    tree = NBT(gzip.decompress(source.read_bytes()), typed=True).root()
    root = tree[1]
    signature = tuple(root[key][1] for key in ("Version", "Width", "Height", "Length"))
    if signature != (2, 180, 124, 190) or root["Offset"][1] != [-436, 134, -209]:
        raise ValueError("No se reconoce el adjunto mina.schem")
    root["Offset"] = (11, [0, 0, 0])
    for axis in "XYZ":
        root["Metadata"][1]["WEOffset" + axis] = (3, 0)

    # Quita la logica del minijuego original antes de importar la construccion.
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
    val = shift = 0
    for byte in root["BlockData"][1]:
        val |= (byte & 127) << shift
        if byte >= 128:
            shift += 7
            continue
        index = indexes[val]
        while index >= 128:
            packed.append((index & 127) | 128)
            index >>= 7
        packed.append(index)
        val = shift = 0
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
    LOCAL.mkdir(parents=True, exist_ok=True)
    (LOCAL / "astral-mina-hierro.schem").write_bytes(gzip.compress(raw, mtime=0))


def install_commands():
    c = [
        "# Minas Astrales: armado inicial (generado por datapack-src/minas.py).",
        "# 1) Crear el mundo vacio (una sola vez), desde la consola:",
        f'mv create {WORLD} normal --world-type FLAT --no-structures --no-adjust-spawn --generator-settings {{"layers":[{{"block":"minecraft:air","height":1}}],"biome":"minecraft:the_void"}}',
        f"mv modify {WORLD} set pvp false",
        f"mv modify {WORLD} set hunger false",
        f"mv modify {WORLD} set gamemode survival",
        f"mv modify {WORLD} set allow-weather false",
        f"mv gamerule set minecraft:spawn_mobs false {WORLD}",
        f"mv gamerule set minecraft:keep_inventory true {WORLD}",
        f"mv gamerule set minecraft:advance_time false {WORLD}",
        f"minecraft:execute in {DIM} run time set noon",
        f"rg flag -w {WORLD} __global__ block-place deny",
        f"rg flag -w {WORLD} __global__ chest-access deny",
        f"rg flag -w {WORLD} __global__ pistons deny",
        f"rg flag -w {WORLD} __global__ mob-spawning allow",
        "",
        "# 2) Subir astral-mina-hierro.schem a plugins/WorldEdit/schematics/ (ya estan en Aternos).",
        "#    Pegar EN EL JUEGO, en creativo y con OP, mina por mina (esperar que termine cada //paste):",
    ]
    for i, mine in enumerate(MINES, 1):
        x = (i - 1) * SPACING
        c += [f"# Mina {i}: {mine[0]}",
              f"/execute in {DIM} run minecraft:tp @s {x + PASTE_X + 0.5} 64 {PASTE_Z + 0.5}",
              f"//schem load {MAP}",
              "//paste -a",
              f"/fill {x+84} 92 67 {x+96} 92 74 polished_deepslate",
              f"/fill {x+84} 93 67 {x+96} 96 74 air"]
    c += ["",
          "# 3) Subir build/mythicmobs/mobs/astral.yml (trae los aldeanos nuevos) y recargar:",
          "mm reload",
          "#    Aldeanos de venta rapida y de viajes (dos por mina) desde la consola:"]
    for i in range(1, len(MINES) + 1):
        x = (i - 1) * SPACING + VENDOR[0]
        c.append(f"mm mobs spawn astral_npc_mina_venta 1 {WORLD},{x},{VENDOR[1]},{VENDOR[2]},{VENDOR[3]},0")
        t = (i - 1) * SPACING + TRAVEL[0]
        c.append(f"mm mobs spawn astral_npc_mina_viaje 1 {WORLD},{t},{TRAVEL[1]},{TRAVEL[2]},{TRAVEL[3]},0")
    lx, ly, lz, lyaw = LOBBY_NPC
    c += ["",
          "# 4) Aldeano del lobby (al lado de Expediciones). WorldGuard bloquea mobs en el lobby:",
          "rg flag -w lobby __global__ mob-spawning allow",
          f"mm mobs spawn astral_npc_minas 1 lobby,{lx},{ly},{lz},{lyaw},0",
          "rg flag -w lobby __global__ mob-spawning deny",
          "",
          "# 5) Script y panel. Subir astral_minas.sk a plugins/Skript/scripts/ y la seccion de TAB.",
          "skript reload astral_minas",
          "tab reload",
          "# 6) Rellenar los moldes (tarda ~1 minuto por mina; se puede hacer de a una: /minasmoldes 3)",
          "minasmoldes",
          "minasactivar",
          ]
    return "\n".join(c) + "\n"


def migration_commands():
    commands = [
        "# Mantener una copia del mundo y cerrar el acceso a jugadores durante el reemplazo.",
        "# Deshabilitar astral_minas antes de limpiar y conservar variables.csv y los aldeanos.",
        "# Ejecutar en astral_minas, como OP en creativo. Esperar después de cada comando WorldEdit.",
    ]
    for i, mine in enumerate(MINES):
        x = i * SPACING
        commands += [
            f"# Mina {i + 1}: {mine[0]}",
            f"/execute in {DIM} run minecraft:tp @s {x + PASTE_X + 0.5} 64 {PASTE_Z + 0.5}",
            f"//schem load {MAP}",
            "//paste",  # Con aire, para borrar la construccion anterior dentro de la huella.
            f"/fill {x + 84} 92 67 {x + 96} 92 74 polished_deepslate",
            f"/fill {x + 84} 93 67 {x + 96} 96 74 air",
            f"/execute if block {x + PIT['x1']} 72 {PIT['z1']} bedrock",
            f"/execute if block {x + PIT['x2']} 72 {PIT['z2']} bedrock",
        ]
    commands += ["# Habilitar el script actualizado y comprobar que cargue sin errores.",
                 "# Ejecutar minasmoldes y esperar Moldes listos antes de reabrir el acceso."]
    return "\n".join(commands) + "\n"


def sign_commands():
    commands = []
    tier_numbers = {"I": 1, "II": 2, "III": 3}
    colors = {1: "gold", 2: "aqua", 3: "light_purple"}
    y = PIT["y2"] + 5  # cuatro bloques sobre la cara superior del último bloque
    z = (PIT["z1"] + PIT["z2"] + 1) / 2
    for i, mine in enumerate(MINES):
        roman, material = mine[0].split(" · ", 1)
        tier = tier_numbers[roman]
        x = i * SPACING + (PIT["x1"] + PIT["x2"] + 1) / 2
        tag = f"astral.mina.rotulo.{i + 1}"
        target = f"@e[type=minecraft:text_display,tag={tag},distance=..2,limit=1]"
        text = f'[{{text:"Tier {tier}",color:"{colors[tier]}",bold:1b}},{{text:"\\nMina de {material}",color:"white",bold:1b}}]'
        transform = (
            "{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],"
            "scale:[2f,2f,2f],right_rotation:[0f,0f,0f,1f]}"
        )
        settings = (
            f'{{billboard:"center",shadow:1b,background:1073741824,'
            f'transformation:{transform},text:{text}}}'
        )
        position = f"execute in {DIM} positioned {x} {y} {z}"
        commands.extend([
            f'{position} unless entity {target} run summon minecraft:text_display ~ ~ ~ '
            f'{{Tags:["{tag}"],{settings[1:]}',
            f'{position} run data merge entity {target} {settings}',
        ])
    return "\n".join(commands) + "\n"


def generate():
    from lobby import TAB_SECTIONS
    outputs = {OUT / "Skript/scripts/astral_minas.sk": script(),
               OUT / "instalacion.txt": install_commands(),
               OUT / "reemplazar-mapas.txt": migration_commands(),
               OUT / "carteles.txt": sign_commands(),
               ROOT / "build/lobby/TAB/secciones-config.yml": TAB_SECTIONS}
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    old = OUT / "Skript/scripts/astral_minas_instalar.sk"
    if old.exists():
        old.unlink()
    print(f"minas: {len(MINES)} minas, {len(PRICES)} precios -> {OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schematic", type=Path, help="copia original de mina.schem")
    parser.add_argument("--test-world", help="genera una copia para el server de prueba en otro mundo")
    args = parser.parse_args()
    if args.test_world:
        print(script(args.test_world, "minecraft:overworld"))
    else:
        generate()
    if args.schematic:
        prepare_schematic(args.schematic)
