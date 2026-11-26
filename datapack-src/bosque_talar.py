"""Bosque Astral: mundo de tala con arboles que vuelven a crecer (ver docs/BOSQUE.md).

python bosque_talar.py  ->  build/bosque/astral_bosque.sk y build/bosque/instalacion.txt

Desde el 20/11/2026 el bosque es un recorte de 300 x 300 del mapa "Forested Plains" (terceros,
privado): tools/bosque_mapa.py lo recorta y limpia, tools/bosque_armar.py arma el mundo en un Paper
local y tools/bosque_arboles.py detecta los arboles. Todo el bosque tiene una copia identica 120
bloques mas abajo (el molde). Regenerar un arbol es un `clone ... masked` de su caja del molde a su
lugar, 3 minutos despues de talarlo. Las cajas salen de bosque_arboles.json (solo coordenadas).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/bosque"
WORLD = "astral_bosque"
DIM = "minecraft:astral_bosque"

SIZE = 300                     # el bosque ocupa x 0..299, z 0..299 (barreras en -1 y 300)
LIVE_BOTTOM, LIVE_TOP = 58, 165
MOLD_DY = -120                 # el molde de todo el bosque esta 120 bloques mas abajo (Y -62..45)
# Arboles de Minecraft que se suman en los claros (el mapa trae roble, abeto, abedul, acacia,
# roble oscuro y azalea).
EXTRA_TREES = [("mega_spruce", 24), ("mega_pine", 12), ("cherry", 16), ("mega_jungle_tree", 6),
               ("jungle_tree", 8), ("pale_oak", 8), ("super_birch_bees_0002", 10), ("fancy_oak", 8)]
CLONE_LIMIT = 32768            # bloques por comando clone (gamerule por defecto)
REGROW_MIN = 3                 # minutos hasta que vuelve a crecer
FALL_Y = 50

_DATA_FILE = Path(__file__).resolve().parent / 'bosque_arboles.json'
_DATA = json.loads(_DATA_FILE.read_text(encoding='utf-8')) if _DATA_FILE.exists() else {'spawn': [80, 87, 218], 'arboles': []}
ARBOLES = _DATA['arboles']
GROUND = _DATA['spawn'][1]     # piso de la plataforma del spawn
# Spawn mirando hacia el centro del bosque; venta y viajes a los costados, mirando al spawn.
SPAWN = (_DATA['spawn'][0] + 0.5, GROUND + 1, _DATA['spawn'][2] + 0.5, -135)
VENDOR = (SPAWN[0] + 3, GROUND + 1, SPAWN[2], 90)
TRAVEL = (SPAWN[0] - 3, GROUND + 1, SPAWN[2], -90)
# 21/11/2026: el dueno eligio donde aparecen los jugadores (mirando al sur). La plataforma de los NPC no cambia.
LLEGADA = (81.93, 87, 227.52, -1.6)
WOODS = ('oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'cherry', 'mangrove', 'pale_oak')


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


# Lo unico que se puede romper (texto del tipo de bloque en Skript, en ingles).
BREAKABLE = ("log", "wood", "leaves", "stem", "hyphae", "vine", "cocoa", "bee nest", "moss carpet", "hanging moss")


def clones(box):
    """Comandos clone (molde -> bosque) de la caja de un arbol, en tajadas si pasa el limite."""
    x1, y1, z1, x2, y2, z2 = box
    per = max(1, CLONE_LIMIT // ((x2 - x1 + 1) * (z2 - z1 + 1)))
    out, y = [], y1
    while y <= y2:
        ye = min(y2, y + per - 1)
        out.append(f"clone {x1} {y + MOLD_DY} {z1} {x2} {ye + MOLD_DY} {z2} {x1} {y} {z1} masked")
        y = ye + 1
    return out


def buckets():
    """Chunk 'cx_cz' -> numeros de arbol cuya caja lo toca."""
    out = {}
    for n, t in enumerate(ARBOLES, 1):
        x1, _, z1, x2, _, z2 = t['box']
        for cx in range(x1 >> 4, (x2 >> 4) + 1):
            for cz in range(z1 >> 4, (z2 >> 4) + 1):
                out.setdefault(f"{cx}_{cz}", []).append(n)
    return out


def tree_data():
    lines = ["on load:",
             "    delete {-ab.x::*}", "    delete {-ab.y::*}", "    delete {-ab.z::*}",
             "    delete {-ab.box::*}", "    delete {-ab.cl::*}", "    delete {-ab.k::*}",
             "    delete {-ab.cx::*}", "    delete {-ab.cy::*}", "    delete {-ab.cz::*}"]
    for n, t in enumerate(ARBOLES, 1):
        bx, by, bz = t['base']
        lines += [f"    set {{-ab.x::{n}}} to {bx}", f"    set {{-ab.y::{n}}} to {by}", f"    set {{-ab.z::{n}}} to {bz}",
                  f'    set {{-ab.box::{n}}} to "{" ".join(map(str, t["box"]))}"']
        # Puntos de control (troncos de abajo a arriba): la motosierra puede dejar la base.
        for i, (cx, cy, cz) in enumerate(t.get('checks') or [t['base']], 1):
            lines += [f"    set {{-ab.cx::{n}::{i}}} to {cx}", f"    set {{-ab.cy::{n}::{i}}} to {cy}",
                      f"    set {{-ab.cz::{n}::{i}}} to {cz}"]
        for i, c in enumerate(clones(t['box']), 1):
            lines.append(f'    set {{-ab.cl::{n}::{i}}} to "{c}"')
    for k, ns in sorted(buckets().items()):
        lines.append(f'    set {{-ab.k::{k}}} to "{",".join(map(str, ns))}"')
    return lines


def forceload(cmd):
    """forceload de todo el bosque en cuatro partes (el comando acepta 256 chunks)."""
    h = SIZE // 2
    return [f'execute console command "execute in {DIM} run forceload {cmd} {xa} {za} {xb} {zb}"'
            for xa, xb in ((0, h - 1), (h, SIZE - 1)) for za, zb in ((0, h - 1), (h, SIZE - 1))]


def script():
    lines = [
        "# AstralRPG / Bosque Astral. Generado por datapack-src/bosque_talar.py: no editar a mano.",
        f"# {len(ARBOLES)} arboles; molde de todo el bosque {-MOLD_DY} bloques mas abajo. Regeneran {REGROW_MIN} min",
        "# despues de talarlos (clone masked de su caja). Pendientes en memoria: {-ab.pend::N} = fecha en que se talo.",
        "",
        *tree_data(),
        "",
        "function ab_world() :: world:",
        f'    return world "{WORLD}"',
        "",
        "function ab_spawn() :: location:",
        f"    return location({LLEGADA[0]}, {LLEGADA[1]}, {LLEGADA[2]}, ab_world(), {LLEGADA[3]}, 0)",
        "",
        "function ab_inside(loc: location) :: boolean:",
        f"    if x-coordinate of {{_loc}} is between 0 and {SIZE}:",
        f"        if z-coordinate of {{_loc}} is between 0 and {SIZE}:",
        "            return true",
        "    return false",
        "",
        "function ab_breakable(b: block) :: boolean:",
        '    set {_t} to "%type of {_b}%"',
    ]
    lines += [f'    if {{_t}} contains "{w}":\n        return true' for w in BREAKABLE]
    lines += [
        "    return false",
        "",
        "# Marca como talados los arboles cuya caja contiene el bloque. Si no es de ningun arbol",
        "# (arbusto de hojas suelto), se anota el bloque solo y vuelve igual a los 3 minutos.",
        "function ab_mark(loc: location):",
        '    set {_ck} to "%floor(x-coordinate of {_loc} / 16)%_%floor(z-coordinate of {_loc} / 16)%"',
        "    if {-ab.k::%{_ck}%} is set:",
        '        loop split {-ab.k::%{_ck}%} at ",":',
        "            set {_n} to loop-value",
        '            set {_b::*} to split {-ab.box::%{_n}%} at " "',
        "            if x-coordinate of {_loc} is between ({_b::1} parsed as number) and ({_b::4} parsed as number) + 1:",
        "                if y-coordinate of {_loc} is between ({_b::2} parsed as number) and ({_b::5} parsed as number) + 1:",
        "                    if z-coordinate of {_loc} is between ({_b::3} parsed as number) and ({_b::6} parsed as number) + 1:",
        "                        set {_hit} to true",
        "                        if {-ab.pend::%{_n}%} is not set:",
        "                            set {-ab.pend::%{_n}%} to now",
        "    if {_hit} is not set:",
        '        set {-ab.suelto::%floor(x-coordinate of {_loc})% %floor(y-coordinate of {_loc})% %floor(z-coordinate of {_loc})%} to now',
        "",
        "# Copia el molde del arbol N sobre el. Devuelve true si el tronco volvio.",
        "function ab_regrow(n: text) :: boolean:",
        "    set {_c} to location({-ab.x::%{_n}%}, {-ab.y::%{_n}%}, {-ab.z::%{_n}%}, ab_world())",
        "    if chunk at {_c} is not loaded:",
        "        return false",
        "    loop {-ab.cl::%{_n}%::*}:",
        f'        execute console command "execute in {DIM} run %loop-value%"',
        "    if block at {_c} is air:",
        "        return false",
        "    loop indices of {-ab.cx::%{_n}%::*}:",
        "        set {_k} to location({-ab.cx::%{_n}%::%loop-value%}, {-ab.cy::%{_n}%::%loop-value%}, {-ab.cz::%{_n}%::%loop-value%}, ab_world())",
        "        if block at {_k} is air:",
        "            return false",
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
        "    if ab_inside(location of event-block) is false:",
        "        cancel event",
        "        stop",
        "    if ab_breakable(event-block) is false:",
        "        cancel event",
        "        stop",
        "    ab_mark(location of event-block)",
        "",
        "on uncancelled break with priority monitor:",
        f'    if name of world of event-block is not "{WORLD}":',
        "        stop",
        "    if player's gamemode is not survival:",
        "        stop",
        "    set {_d::*} to drops of event-block using player's tool",
        "    # Ranking semanal del Bosque (rankings.py): troncos sacados.",
        "    loop {_d::*}:",
        "        if \"%type of loop-value%\" contains \"log\" or \"stem\" or \"wood\":",
        "            rk_sumar(player, \"bosque\", item amount of loop-value)",
        "    # Ropa de Talador (oficios.py): con el set completo, 20% de tronco extra.",
        '    if scoreboard tags of player contains "astral.ofi_talador":',
        "        chance of 20%:",
        "            loop {_d::*}:",
        "                if \"%type of loop-value%\" contains \"log\" or \"stem\" or \"wood\":",
        "                    set {_extra} to loop-value",
        "            if {_extra} is set:",
        "                add {_extra} to {_d::*}",
        "                rk_sumar(player, \"bosque\", item amount of {_extra})",
        "    clear drops",
        "    am_give(player, {_d::*})",
        "",
        "# Solo loot de motosierra marcado por el datapack; no drops manuales.",
        "every 2 ticks:",
        "    loop all players in ab_world():",
        "        set {_p} to loop-player",
        "        loop all dropped items in radius 48 around {_p}:",
        '            if scoreboard tags of loop-dropped item contains "ab.saw":',
        "                # La madera sale donde estaba el tronco: marca ese arbol como talado.",
        "                ab_mark(location of loop-dropped item)",
        '                execute console command "minecraft:data remove entity %uuid of loop-dropped item% Item.components.minecraft:custom_data"',
        "                set {_it} to item of loop-dropped item",
        "                if \"%type of {_it}%\" contains \"log\" or \"stem\" or \"wood\":",
        "                    rk_sumar({_p}, \"bosque\", item amount of {_it})",
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
        "# La motosierra del datapack no dispara eventos de Skript: se revisan varios troncos de cada",
        "# arbol (de abajo a arriba). Si falta cualquiera, el arbol se talo, aunque quede la base.",
        "every 5 seconds:",
        "    if ab_world() is not set:",
        "        stop",
        "    loop indices of {-ab.x::*}:",
        "        set {_n} to loop-value",
        "        if {-ab.pend::%{_n}%} is not set:",
        "            set {_l} to location({-ab.x::%{_n}%}, {-ab.y::%{_n}%}, {-ab.z::%{_n}%}, ab_world())",
        "            if chunk at {_l} is loaded:",
        "                loop indices of {-ab.cx::%{_n}%::*}:",
        "                    set {_i} to loop-value-2",
        "                    set {_c} to location({-ab.cx::%{_n}%::%{_i}%}, {-ab.cy::%{_n}%::%{_i}%}, {-ab.cz::%{_n}%::%{_i}%}, ab_world())",
        "                    if block at {_c} is air:",
        "                        set {-ab.pend::%{_n}%} to now",
        "                        exit loop",
        "    loop indices of {-ab.pend::*}:",
        "        set {_k} to loop-value",
        f"        if difference between {{-ab.pend::%{{_k}}%}} and now >= {REGROW_MIN} minutes:",
        "            if ab_regrow({_k}) is true:",
        "                delete {-ab.pend::%{_k}%}",
        "    loop indices of {-ab.suelto::*}:",
        "        set {_k} to loop-value",
        f"        if difference between {{-ab.suelto::%{{_k}}%}} and now >= {REGROW_MIN} minutes:",
        '            set {_p::*} to split {_k} at " "',
        "            set {_l} to location(({_p::1} parsed as number), ({_p::2} parsed as number), ({_p::3} parsed as number), ab_world())",
        "            if chunk at {_l} is loaded:",
        f"                set {{_my}} to ({{_p::2}} parsed as number) + ({MOLD_DY})",
        f'                execute console command "execute in {DIM} run clone %{{_p::1}}% %{{_my}}% %{{_p::3}}% %{{_p::1}}% %{{_my}}% %{{_p::3}}% %{{_k}}% masked"',
        "                delete {-ab.suelto::%{_k}%}",
        "",
        "# Panel lateral (panel_mundos.py): arboles talados y cuanto falta para el proximo.",
        "on load:",
        '    execute console command "scoreboard objectives add ab.tal dummy"',
        '    execute console command "scoreboard objectives add ab.min dummy"',
        '    execute console command "scoreboard objectives add ab.seg dummy"',
        "",
        "every 1 second:",
        "    if ab_world() is not set:",
        "        stop",
        "    set {_t} to 0",
        f"    set {{_r}} to {REGROW_MIN * 60}",
        "    loop indices of {-ab.pend::*}:",
        "        add 1 to {_t}",
        f"        set {{_s}} to {REGROW_MIN * 60} - (unix timestamp of now - unix timestamp of {{-ab.pend::%loop-value%}})",
        "        if {_s} < {_r}:",
        "            set {_r} to {_s}",
        "    set {_r} to max(0, ceil({_r}))",
        "    loop all players in ab_world():",
        '        execute console command "scoreboard players set %name of loop-player% ab.tal %{_t}%"',
        '        execute console command "scoreboard players set %name of loop-player% ab.min %floor({_r} / 60)%"',
        '        execute console command "scoreboard players set %name of loop-player% ab.seg %mod({_r}, 60)%"',
        "",
        "# ---------------------------------------------------------------- admin",
        "",
        "command /bosquereset:",
        '    permission: astral.minas.admin',
        "    trigger:",
        '        send "&eRegenerando todos los arboles del Bosque Astral..." to command sender',
        *["        " + c for c in forceload("add")],
        "        wait 3 seconds",
        "        set {_i} to 0",
        "        loop indices of {-ab.x::*}:",
        "            ab_regrow(loop-value)",
        "            add 1 to {_i}",
        "            if mod({_i}, 20) is 0:",
        "                wait 1 tick",
        *["        " + c for c in forceload("remove")],
        "        delete {-ab.pend::*}",
        '        send "&aArboles regenerados: %{_i}%." to command sender',
    ]
    return services() + "\n".join(lines) + "\n"


def install():
    lines = [
        "# Bosque Astral (generado por datapack-src/bosque_talar.py). Ver docs/BOSQUE.md.",
        "# Bosque nuevo 300x300 (20/11/2026). El mundo astral_bosque ya existe en el server: no se crea de nuevo.",
        "# 1) Con el server APAGADO: borrar world/dimensions/minecraft/astral_bosque/{region,entities,poi}",
        "#    y subir las regiones de .local/bosque-mapas/entrega/region/ (privadas, nunca al repo).",
        "# 2) Subir build/bosque/astral_bosque.sk a plugins/Skript/scripts/ y prender el server.",
        "# 3) Desde la consola:",
        f"mv gamerule set minecraft:random_tick_speed 0 {WORLD}",
        f"rg flag -w {WORLD} __global__ mob-spawning allow",
    ]
    for name, pos in (("venta", VENDOR), ("viaje", TRAVEL)):
        x, y, z, yaw = pos
        lines += [f"mm mobs kill astral_npc_bosque_{name}",
                  f"mm mobs spawn astral_npc_bosque_{name} 1 {WORLD},{x},{y},{z},{yaw},0"]
    lines += [f"rg flag -w {WORLD} __global__ mob-spawning deny",
              "# Cartel del ranking del Bosque (rankings.py):",
              f"execute in {DIM} run summon text_display {SPAWN[0] - 3} {SPAWN[1] + 2.4} {SPAWN[2]} "
              "{Tags:['astral_rank','astral_rank_bosque'],billboard:'center',alignment:'center',line_width:240,"
              "background:1711276032,text:{text:'Ranking',color:'gold'}}",
              "# Con /bosquereset se vuelven a copiar todos los arboles desde el molde.",
              "# Precios sin referencia fija en services_catalog.json (pendientes; no se venden):",
              "# " + ", ".join(wood_prices()[1])]
    return "\n".join(lines) + "\n"


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "astral_bosque.sk").write_text(script(), encoding="utf-8")
    (OUT / "instalacion.txt").write_text(install(), encoding="utf-8")
    print(f"bosque: {len(ARBOLES)} arboles, spawn {SPAWN}")


if __name__ == "__main__":
    generate()
