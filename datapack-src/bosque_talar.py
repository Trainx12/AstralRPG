"""Bosque Astral: mundo de tala con arboles que vuelven a crecer (ver docs/BOSQUE.md).

python bosque_talar.py  ->  build/bosque/astral_bosque.sk y build/bosque/instalacion.txt

Los arboles los genera Minecraft con `place feature` (formas naturales): no hay mapas de
terceros. Cada arbol tiene un molde identico debajo (Y -60) en los mismos chunks; regenerar
es un `clone ... masked` del molde a su lugar, 3 minutos despues de talarlo.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/bosque"
WORLD = "astral_bosque"
DIM = "minecraft:astral_bosque"

CELL = 14            # cada arbol ocupa una celda de 14 x 14
GRID = 8             # 8 x 8 = 64 arboles
X0, Z0 = 0, 0        # esquina de la grilla
GROUND = 64          # pasto del bosque; el arbol nace en Y 65
MOLD = -60           # pasto de los moldes; el molde nace en Y -59
HEIGHT = 41          # alto copiado (pasto + 40 de arbol)
REGROW_MIN = 3       # minutos hasta que vuelve a crecer
FALL_Y = 55
SPAWN = (X0 - 4.5, GROUND + 1, Z0 + GRID * CELL / 2 + 0.5, -90)
SEED = 87
# Pasto dentro del piso -8..119; fuera de la plataforma de piedra (-7..-3, 53..59).
VENDOR = (-1.5, 65, 56.5, 90)
TRAVEL = (-7.5, 65, 56.5, -90)
WOODS = ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'cherry', 'mangrove')


def wood_prices():
    catalog = json.loads((ROOT / 'datapack-src/services_catalog.json').read_text())
    prices, missing = {}, []
    for wood in WOODS:
        for material in (f'{wood}_log', f'stripped_{wood}_log', f'{wood}_wood', f'stripped_{wood}_wood', f'{wood}_planks'):
            entry = catalog.get(material.upper())
            if entry is None or entry['min'] != entry['max']:
                missing.append(material)
            else:
                prices[material] = entry['min']
    return prices, missing


def services():
    lines = ['on load:', '    delete {-ab.price::*}']
    for material, price in wood_prices()[0].items():
        lines += [f'    set {{_t}} to "minecraft:{material}" parsed as item type',
                  f'    set {{-ab.price::%{{_t}}%}} to {price}']
    lines += ['','command /bosqueventa <player>:', '    executable by: console', '    trigger:',
              f'        if name of world of arg-1 is "{WORLD}":', '            am_sale_menu(arg-1)', '']
    return '\n'.join(lines) + '\n'


# Pedido del dueno: muchos tipos, y los abetos gigantes son los que mas hay.
TREES = [("mega_spruce", 22), ("mega_pine", 12), ("spruce", 4), ("pine", 2), ("oak", 4),
         ("fancy_oak", 4), ("birch", 3), ("super_birch_bees_0002", 2), ("dark_oak", 3),
         ("jungle_tree", 2), ("mega_jungle_tree", 2), ("acacia", 2), ("cherry", 3)]
# Lo unico que se puede romper (texto del tipo de bloque en Skript, en ingles).
BREAKABLE = ("log", "wood", "leaves", "stem", "hyphae", "vine", "cocoa", "bee nest")


def layout():
    """Lista fija (semilla) de (i, j, feature): siempre el mismo bosque."""
    names = [n for n, w in TREES for _ in range(w)]
    rng = random.Random(SEED)
    rng.shuffle(names)
    while len(names) < GRID * GRID:
        names.append(rng.choice([n for n, w in TREES for _ in range(w)]))
    return [(i, j, names[i * GRID + j]) for i in range(GRID) for j in range(GRID)]


def center(i, j):
    return X0 + i * CELL + CELL // 2, Z0 + j * CELL + CELL // 2


def script():
    size = GRID * CELL
    lines = [
        "# AstralRPG / Bosque Astral. Generado por datapack-src/bosque_talar.py: no editar a mano.",
        f"# Arboles con molde en Y {MOLD}; regeneran {REGROW_MIN} min despues de talarlos (clone masked).",
        "# Pendientes en memoria: {-ab.pend::i_j} = fecha en que se talo.",
        "",
        "function ab_world() :: world:",
        f'    return world "{WORLD}"',
        "",
        "function ab_spawn() :: location:",
        f"    return location({SPAWN[0]}, {SPAWN[1]}, {SPAWN[2]}, ab_world(), {SPAWN[3]}, 0)",
        "",
        "# Celda del arbol (\"i_j\") o \"\" si esta fuera de la grilla.",
        "function ab_cell(loc: location) :: text:",
        f"    set {{_i}} to floor((x-coordinate of {{_loc}} - {X0}) / {CELL})",
        f"    set {{_j}} to floor((z-coordinate of {{_loc}} - {Z0}) / {CELL})",
        f"    if {{_i}} is between 0 and {GRID - 1}:",
        f"        if {{_j}} is between 0 and {GRID - 1}:",
        '            return "%{_i}%_%{_j}%"',
        '    return ""',
        "",
        "function ab_breakable(b: block) :: boolean:",
        '    set {_t} to "%type of {_b}%"',
    ]
    lines += [f'    if {{_t}} contains "{w}":\n        return true' for w in BREAKABLE]
    lines += [
        "    return false",
        "",
        "# Copia el molde de la celda sobre el arbol. Devuelve true si el tronco volvio.",
        "function ab_regrow(k: text) :: boolean:",
        '    set {_p::*} to {_k} split at "_"',
        "    set {_i} to {_p::1} parsed as integer",
        "    set {_j} to {_p::2} parsed as integer",
        f"    set {{_x}} to {X0} + {{_i}} * {CELL}",
        f"    set {{_z}} to {Z0} + {{_j}} * {CELL}",
        f"    set {{_x2}} to {{_x}} + {CELL - 1}",
        f"    set {{_z2}} to {{_z}} + {CELL - 1}",
        f'    execute console command "execute in {DIM} run clone %{{_x}}% {MOLD} %{{_z}}% %{{_x2}}% {MOLD + HEIGHT - 1} %{{_z2}}% %{{_x}}% {GROUND} %{{_z}}% masked"',
        f"    set {{_c}} to location({{_x}} + {CELL // 2}, {GROUND + 1}, {{_z}} + {CELL // 2}, ab_world())",
        "    if block at {_c} is air:",
        "        return false",
        "    return true",
        "",
        "command /bosque:",
        "    executable by: players",
        "    trigger:",
        f'        if name of world of player is "lobby" or "astral_minas" or "{WORLD}":',
        "            set velocity of player to vector(0, 0, 0)",
        "            teleport player to ab_spawn()",
        f'            send "&2Bosque Astral: &7solo se talan troncos y hojas. Cada arbol vuelve a crecer a los {REGROW_MIN} minutos." to player',
        "        else:",
        '            send "&eEl bosque se abre desde el lobby o desde las Minas Astrales (/minas)." to player',
        "",
        "on break with priority highest:",
        f'    if name of world of event-block is not "{WORLD}":',
        "        stop",
        "    if player's gamemode is creative:",
        '        if player has permission "astral.minas.admin":',
        "            stop",
        '    set {_k} to ab_cell(location of event-block)',
        '    if {_k} is "":',
        "        cancel event",
        "        stop",
        "    if ab_breakable(event-block) is false:",
        "        cancel event",
        "        stop",
        "    if {-ab.pend::%{_k}%} is not set:",
        "        set {-ab.pend::%{_k}%} to now",
        "",
        "on uncancelled break with priority monitor:",
        f'    if name of world of event-block is not "{WORLD}":',
        "        stop",
        "    if player's gamemode is not survival:",
        "        stop",
        "    set {_d::*} to drops of event-block using player's tool",
        "    clear drops",
        "    am_give(player, {_d::*})",
        "",
        "# Solo loot de motosierra marcado por el datapack; no drops manuales.",
        "every 2 ticks:",
        "    loop all players in ab_world():",
        "        set {_p} to loop-player",
        "        loop all dropped items in radius 48 around {_p}:",
        '            if scoreboard tags of loop-dropped item contains "ab.saw":',
        '                execute console command "minecraft:data remove entity %uuid of loop-dropped item% Item.components.minecraft:custom_data"',
        "                set {_it} to item of loop-dropped item",
        "                if {_p}'s inventory has enough space for {_it}:",
        "                    give {_it} to {_p}",
        "                    delete loop-dropped item",
        "                else:",
        "                    teleport loop-dropped item to {_p}",
        '                    execute console command "minecraft:tag %uuid of loop-dropped item% remove ab.saw"',
        '                    execute console command "minecraft:data merge entity %uuid of loop-dropped item% {PickupDelay:10s}"',
        "",
        "on place:",
        f'    if name of world of event-block is "{WORLD}":',
        "        if player's gamemode is not creative:",
        "            cancel event",
        "",
        "on bucket empty:",
        f'    if name of world of player is "{WORLD}":',
        "        if player's gamemode is not creative:",
        "            cancel event",
        "",
        "on explode:",
        f'    if name of world of event-location is "{WORLD}":',
        "        cancel event",
        "",
        "# Las hojas no se caen: el arbol vuelve entero con el molde.",
        "on leaves decay:",
        f'    if name of world of event-block is "{WORLD}":',
        "        cancel event",
        "",
        "on damage of player:",
        f'    if name of world of victim is "{WORLD}":',
        "        cancel event",
        "",
        "every 1 second:",
        "    loop all players in ab_world():",
        f"        if y-coordinate of loop-player < {FALL_Y}:",
        "            if loop-player's gamemode is not creative:",
        "                teleport loop-player to ab_spawn()",
        "",
        "# La motosierra del datapack no dispara eventos de Skript: se revisa el tronco de cada arbol.",
        "every 5 seconds:",
        "    if ab_world() is not set:",
        "        stop",
        "    set {_i} to 0",
        f"    while {{_i}} < {GRID}:",
        "        set {_j} to 0",
        f"        while {{_j}} < {GRID}:",
        '            set {_k} to "%{_i}%_%{_j}%"',
        "            if {-ab.pend::%{_k}%} is not set:",
        f"                set {{_x}} to {X0} + {{_i}} * {CELL} + {CELL // 2}",
        f"                set {{_z}} to {Z0} + {{_j}} * {CELL} + {CELL // 2}",
        f"                set {{_live}} to location({{_x}}, {GROUND + 1}, {{_z}}, ab_world())",
        f"                set {{_mold}} to location({{_x}}, {MOLD + 1}, {{_z}}, ab_world())",
        "                if chunk at {_live} is loaded:",
        "                    if block at {_live} is air:",
        "                        if block at {_mold} is not air:",
        "                            set {-ab.pend::%{_k}%} to now",
        "            add 1 to {_j}",
        "        add 1 to {_i}",
        "    loop indices of {-ab.pend::*}:",
        "        set {_k} to loop-value",
        f"        if difference between {{-ab.pend::%{{_k}}%}} and now >= {REGROW_MIN} minutes:",
        "            if ab_regrow({_k}) is true:",
        "                delete {-ab.pend::%{_k}%}",
        "",
        "# ---------------------------------------------------------------- admin",
        "",
        "command /bosquegenerar:",
        '    permission: astral.minas.admin',
        "    trigger:",
        f'        send "&eGenerando el Bosque Astral ({GRID * GRID} arboles)..." to command sender',
        f'        execute console command "execute in {DIM} run forceload add {X0 - 16} {Z0 - 16} {X0 + size + 15} {Z0 + size + 15}"',
        "        wait 3 seconds",
    ]
    # Piso del bosque y de los moldes (en partes para no pasar el limite de fill).
    lo, hi = X0 - 8, X0 + size + 7
    half = (lo + hi) // 2
    zl, zh = Z0 - 8, Z0 + size + 7
    zhalf = (zl + zh) // 2
    for xa, xb in ((lo, half), (half + 1, hi)):
        for za, zb in ((zl, zhalf), (zhalf + 1, zh)):
            lines += [f'        execute console command "execute in {DIM} run fill {xa} {GROUND - 3} {za} {xb} {GROUND - 1} {zb} minecraft:dirt"',
                      f'        execute console command "execute in {DIM} run fill {xa} {GROUND} {za} {xb} {GROUND} {zb} minecraft:grass_block"']
    sx, sy, sz, _ = SPAWN
    lines += [f'        execute console command "execute in {DIM} run fill {int(sx) - 3} {GROUND} {int(sz) - 3} {int(sx) + 1} {GROUND} {int(sz) + 3} minecraft:mossy_stone_bricks"',
              f'        execute console command "execute in {DIM} run fill {X0} {MOLD - 1} {Z0} {X0 + size - 1} {MOLD - 1} {Z0 + size - 1} minecraft:dirt"',
              f'        execute console command "execute in {DIM} run fill {X0} {MOLD} {Z0} {X0 + size - 1} {MOLD} {Z0 + size - 1} minecraft:grass_block"',
              "        wait 1 second"]
    for i, j, feature in layout():
        x, z = center(i, j)
        lines += [f'        execute console command "execute in {DIM} run place feature minecraft:{feature} {x} {MOLD + 1} {z}"',
                  "        wait 2 ticks"]
    lines += ["        wait 1 second",
              "        set {_i} to 0",
              f"        while {{_i}} < {GRID}:",
              "            set {_j} to 0",
              f"            while {{_j}} < {GRID}:",
              '                ab_regrow("%{_i}%_%{_j}%")',
              "                wait 2 ticks",
              "                add 1 to {_j}",
              "            add 1 to {_i}",
              f'        execute console command "execute in {DIM} run forceload remove {X0 - 16} {Z0 - 16} {X0 + size + 15} {Z0 + size + 15}"',
              "        delete {-ab.pend::*}",
              '        send "&aBosque generado. Revisar que no falten arboles (los que fallan quedan sin molde)." to command sender',
              "",
              "command /bosquereset:",
              '    permission: astral.minas.admin',
              "    trigger:",
              "        set {_i} to 0",
              f"        while {{_i}} < {GRID}:",
              "            set {_j} to 0",
              f"            while {{_j}} < {GRID}:",
              '                ab_regrow("%{_i}%_%{_j}%")',
              "                add 1 to {_j}",
              "            add 1 to {_i}",
              "        delete {-ab.pend::*}",
              '        send "&aArboles regenerados." to command sender']
    return services() + "\n".join(lines) + "\n"


def install():
    lines = [
        "# Bosque Astral (generado por datapack-src/bosque_talar.py). Ver docs/BOSQUE.md.",
        "# 1) Crear el mundo vacio una sola vez, desde la consola:",
        f'mv create {WORLD} normal --world-type FLAT --no-structures --no-adjust-spawn --generator-settings {{"layers":[{{"block":"minecraft:air","height":1}}],"biome":"minecraft:the_void"}}',
        f"mv modify {WORLD} set pvp false",
        f"mv modify {WORLD} set hunger false",
        f"mv modify {WORLD} set gamemode survival",
        f"mv modify {WORLD} set allow-weather false",
        f"mv gamerule set minecraft:spawn_mobs false {WORLD}",
        f"mv gamerule set minecraft:keep_inventory true {WORLD}",
        f"mv gamerule set minecraft:advance_time false {WORLD}",
        f"mv gamerule set minecraft:random_tick_speed 0 {WORLD}",
        f"rg flag -w {WORLD} __global__ chest-access deny",
        f"rg flag -w {WORLD} __global__ pistons deny",
        f"rg flag -w {WORLD} __global__ mob-spawning deny",
        "",
        "# 2) Subir build/bosque/astral_bosque.sk a plugins/Skript/scripts/ y el astral_minas.sk nuevo",
        "#    (boton Bosque en /minas). Despues:",
        "skript reload astral_bosque",
        "skript reload astral_minas",
        "# 3) Generar los arboles y sus moldes (unos 30 segundos):",
        "bosquegenerar",
        f"# 4) Revisar parado en el spawn ({SPAWN[0]} {SPAWN[1]} {SPAWN[2]}) que esten los {GRID * GRID} arboles.",
        "#    Con /bosquereset se vuelven a copiar todos los moldes.",
    ]
    lines += ["", "# Actualizacion: no regenerar el mundo ni los arboles existentes.",
              "# Subir tambien build/mythicmobs/mobs/astral.yml y recargar:", "mm reload",
              f"rg flag -w {WORLD} __global__ mob-spawning allow"]
    for name, pos in (("venta", VENDOR), ("viaje", TRAVEL)):
        x, y, z, yaw = pos
        lines += [f"mm mobs kill astral_npc_bosque_{name}",
                  f"mm mobs spawn astral_npc_bosque_{name} 1 {WORLD},{x},{y},{z},{yaw},0"]
    lines += [f"rg flag -w {WORLD} __global__ mob-spawning deny",
              "# Precios sin referencia fija en services_catalog.json (pendientes; no se venden):",
              "# " + ", ".join(wood_prices()[1])]
    return "\n".join(lines) + "\n"


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "astral_bosque.sk").write_text(script(), encoding="utf-8")
    (OUT / "instalacion.txt").write_text(install(), encoding="utf-8")
    counts = {}
    for _, _, f in layout():
        counts[f] = counts.get(f, 0) + 1
    print(f"bosque: {GRID * GRID} arboles {counts}")


if __name__ == "__main__":
    generate()
