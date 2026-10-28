# -*- coding: utf-8 -*-
"""
Menus de cofre (DeluxeMenus) para que los jugadores no tengan que escribir comandos.

  /menu          menu principal (mascotas, mercado, subastas, guia, volver al lobby)
  /mascotas      tus mascotas: invocar o guardar (las que no tenes aparecen bloqueadas)
  gacha_*        lo abre el cofre de cada gacha: tirar x1 / x10 / x25 / x50 y ver premios
  bazar          lo abre el Administrador del Bazar: mercado (RoyalBazaar), subastas y ordenes (EzAuction)

Los menus que abren los vendedores se abren desde la consola con 'dm open <menu> <jugador>'.
Salida: ../build/menus/DeluxeMenus/  (gui_menus/*.yml + config-gui_menus.yml con la lista para config.yml)
"""
import os

from lobby import GACHAS, PITY, HOLO_COLOR, HOLO_NAME, HOLO_DESC, pity_obj, TIRADAS, money, RARITY_WEIGHT
from mobs.mascotas import MASCOTAS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "menus", "DeluxeMenus")
RULETA_TICKS = 140
# Puntaje de un jugador en un objetivo del scoreboard (expansion 'Objective' de PlaceholderAPI)
SCORE = "%objective_score_{{{}}}%"   # con llaves: los nombres llevan guion bajo

VIDRIO = {"gacha_rpg": "PURPLE_STAINED_GLASS_PANE", "gacha_monturas": "LIME_STAINED_GLASS_PANE",
          "gacha_cosmeticos": "PINK_STAINED_GLASS_PANE"}
ICONO = {"gacha_rpg": "AMETHYST_SHARD", "gacha_monturas": "SADDLE", "gacha_cosmeticos": "NAME_TAG"}
TIRADA_ICONO = {"gacha_rpg": "AMETHYST_SHARD", "gacha_monturas": "WHEAT", "gacha_cosmeticos": "PINK_DYE"}   # se apilan hasta 64
MASC_ICONO = {"lobo": "WOLF_SPAWN_EGG", "cuervo": "PARROT_SPAWN_EGG", "golem": "IRON_GOLEM_SPAWN_EGG",
              "zorro": "FOX_SPAWN_EGG", "dragon": "BLAZE_SPAWN_EGG", "fenix": "CHICKEN_SPAWN_EGG"}


def hexc(c):
    """#RRGGBB -> &#RRGGBB (formato de color de DeluxeMenus)."""
    return "&" + c


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def item(key, material, slot, name, lore=(), amount=1, extra=None, glow=False):
    L = [f"  {q(key)}:", f"    material: {material}", f"    slot: {slot}", f"    amount: {amount}",
         f"    display_name: {q(name)}"]
    flags = ["HIDE_ATTRIBUTES"] + (["HIDE_ENCHANTS"] if glow else [])
    if lore:
        L.append("    lore:")
        L += [f"    - {q(x)}" for x in lore]
    if glow:
        L += ["    enchantments:", "    - 'unbreaking;1'"]
    L += ["    item_flags:"] + [f"    - {f}" for f in flags]
    for k, v in (extra or {}).items():
        if isinstance(v, list):
            L.append(f"    {k}:")
            L += [f"    - {q(x)}" for x in v]
        elif isinstance(v, str) and v.startswith("\n"):
            L.append(f"    {k}:{v}")
        else:
            L.append(f"    {k}: {v}")
    return L


def relleno(material, size, ocupados):
    L = []
    for s in range(size):
        if s not in ocupados:
            L += item(f"vidrio_{s}", material, s, " ")
    return L


def menu(title, command, size, items, update=False):
    L = [f"menu_title: {q(title)}", f"open_command: {command}", f"size: {size}"]
    if update:
        L.append("update_interval: 1")
    return "\n".join(L + ["items:"] + items) + "\n"


def requisito_plata(costo):
    return ("\n      requirements:\n        plata:\n          type: has money\n          amount: " + str(costo) +
            "\n      deny_commands:\n      - " + q(f"[message] &cNo te alcanza: cuesta &e{money(costo)}&c. &7(/balance)") +
            "\n      - '[sound] ENTITY_VILLAGER_NO'")


def gacha_menu(gid, g):
    col, name, n, o = hexc(HOLO_COLOR[gid]), HOLO_NAME[gid], PITY[gid], pity_obj(gid)
    P = "%player_name%"
    items = item("info", ICONO[gid], 4, f"{col}&l✦ {name} ✦",
                 [f"&7{HOLO_DESC[gid]}", "", f"&7Precio: &e{money(g['cost'])} &7por tirada",
                  f"&7Epico garantizado cada &f{n} &7tiradas", f"&7Tu garantia: &e{SCORE.format(o)}&7/{n}"], glow=True,
                 extra={"update": "true"})
    slots = [10, 12, 14, 16]
    for slot, t in zip(slots, TIRADAS):
        costo = g["cost"] * t
        cmds = ["[close]", f"[takemoney] {costo}", "[sound] BLOCK_AMETHYST_BLOCK_CHIME",
                f"[console] scoreboard players add {P} {o} {t}",
                f"[console] scoreboard players set {P} gachaflag 0",
                f"[console] execute if score {P} {o} matches {n}.. run scoreboard players set {P} gachaflag 1",
                f"[console] execute if score {P} gachaflag matches 1 run minecraft:tellraw {P} "
                "{text:'Tirada garantizada! (Epico o Legendario seguro)',color:'light_purple',bold:true}",
                f"[console] execute if score {P} gachaflag matches 1 run crates forceopen {gid}_garantia {P}",
                f"[console] execute unless score {P} gachaflag matches 1 run crates forceopen {gid} {P}"]
        if t > 1:
            cmds += [f"[message] &7Gira la ruleta... cuando termine te llegan los otros &e{t - 1}&7 premios.",
                     f"[console] crates give virtual {gid} {t - 1} {P} -s<delay={RULETA_TICKS}>",
                     f"[console] sudo {P} crates mass-open {gid} virtual {t - 1}<delay={RULETA_TICKS + 1}>",
                     f"[message] &aListo: &f{t} tiradas &aen la {name}.<delay={RULETA_TICKS + 2}>"]
        items += item(f"x{t}", TIRADA_ICONO[gid] if t < 50 else "NETHER_STAR", slot,
                      f"{col}&lTirar x{t}",
                      ["", f"&7Precio: &e{money(costo)}", "&7Suma " + (f"{t} tiradas" if t > 1 else "1 tirada") + " a tu garantia",
                       "" if t == 1 else "&8Gira 1 ruleta y despues llegan los demas premios", "", "&eClic para tirar"],
                      amount=t, glow=t == 50,
                      extra={"click_requirement": requisito_plata(costo), "click_commands": cmds})
    items += item("premios", "CHEST", 22, "&6&lVer premios", ["&7Todos los premios y su probabilidad"],
                  extra={"click_commands": ["[close]", f"[console] sudo {P} crates preview {gid}"]})
    items += relleno(VIDRIO[gid], 27, [4, 10, 12, 14, 16, 22])
    return menu(f"&8{name}", f"astralmenu_{gid}", 27, items, update=True)


def mascotas_menu():
    P = "%player_name%"
    items = item("info", "BONE", 4, "&6&l✦ Mascotas ✦",
                 ["&7Una a la vez. Te siguen y te dan efectos.", "&7Suben de nivel con los mobs que matas:",
                  "&7nivel 10 y 20 = efecto extra, nivel 30 = evolucion.", "", "&8En el lobby no pueden salir."])
    for slot, (pid, d) in zip([10, 11, 12, 14, 15, 16], MASCOTAS.items()):
        col = hexc(d["color"])
        lore = ["", f"&7Nivel: &e{SCORE.format('plv_' + pid)}&7/30", "",
                f"&fNivel 1: &7{d['texto'][0]}", f"&fNivel 10: &7{d['texto'][1]}", f"&fNivel 20: &7{d['texto'][2]}", "",
                "&eClic para invocar"]
        items += item(f"m_{pid}", MASC_ICONO[pid], slot, f"{col}&l{d['nombre']}", lore, extra={
            "priority": 1,
            "view_requirement": f"\n      requirements:\n        tiene:\n          type: has permission\n          permission: astral.mascota.{pid}",
            "click_commands": ["[close]", f"[console] scoreboard players set {P} mascota {d['n']}"]})
        items += item(f"m_{pid}_no", "GRAY_DYE", slot, f"&8&l{d['nombre']} &7(bloqueada)",
                      ["", f"&7Se consigue en: &f{d['fuente']}", "", f"&8Nivel 1: {d['texto'][0]}"], extra={"priority": 2})
    items += item("guardar", "BARRIER", 22, "&c&lGuardar mascota", ["&7La mascota que tengas afuera vuelve a descansar"],
                  extra={"click_commands": ["[close]", f"[console] scoreboard players set {P} mascota 98"]})
    items += relleno("ORANGE_STAINED_GLASS_PANE", 27, [4, 10, 11, 12, 14, 15, 16, 22])
    return menu("&8Mascotas", "mascotas", 27, items)


def bazar_menu():
    items = item("info", "OAK_SIGN", 4, "&6&l✦ Bazar ✦", ["&7Compra y vende con otros jugadores", "&7o con el mercado del servidor."])
    items += item("mercado", "EMERALD", 11, "&a&lMercado",
                  ["&7Materiales comunes: vendes y compras al toque.", "&7Los precios suben si todos compran", "&7y bajan si todos venden.",
                   "", "&eClic para abrir"], extra={"click_commands": ["[close]", "[player] bazaar"]})
    items += item("subastas", "GOLD_INGOT", 13, "&e&lSubastas",
                  ["&7Items unicos entre jugadores (armas, armaduras...).", "&7Para publicar: agarra el item y usa", "&f/ah sell <precio>",
                   "", "&eClic para abrir"], extra={"click_commands": ["[close]", "[player] ah"]})
    items += item("ordenes", "PAPER", 15, "&b&lOrdenes de compra",
                  ["&7Pedi algo que buscas y paga por adelantado:", "&7cuando alguien te lo vende, te llega solo.", "",
                   "&eClic para ver tus ordenes"], extra={"click_commands": ["[close]", "[player] orders"]})
    items += relleno("YELLOW_STAINED_GLASS_PANE", 27, [4, 11, 13, 15])
    return menu("&8Bazar", "astralmenu_bazar", 27, items)


def principal_menu():
    items = item("info", "NETHER_STAR", 4, "&b&l✦ AstralRPG ✦", ["&7Todo lo del servidor, sin comandos."], glow=True)
    items += item("mascotas", "BONE", 10, "&6&lMascotas", ["&7Invoca o guarda tu mascota"],
                  extra={"click_commands": ["[openguimenu] mascotas"]})
    items += item("bazar", "EMERALD", 12, "&a&lBazar", ["&7Mercado, subastas y ordenes"],
                  extra={"click_commands": ["[openguimenu] bazar"]})
    items += item("guia", "WRITABLE_BOOK", 14, "&d&lGuia de AstralRPG", ["&7Clases, items, recetas y la Forja"],
                  extra={"click_commands": ["[close]", "[player] trigger astral.guia set 1"]})
    items += item("plata", "GOLD_NUGGET", 16, "&e&lTu plata", ["&7Tenes: &e%vault_eco_balance_formatted%$"], extra={"update": "true"})
    items += item("spawn", "COMPASS", 22, "&f&lVolver al lobby", ["&7Te lleva a la plaza"],
                  extra={"click_commands": ["[close]", "[player] spawn"]})
    items += relleno("LIGHT_BLUE_STAINED_GLASS_PANE", 27, [4, 10, 12, 14, 16, 22])
    return menu("&8Menu de AstralRPG", "menu", 27, items, update=True)


# ------------------------------------------------------------------ mercado del servidor (RoyalBazaar)
# Precio base de compra de cada material (el de venta es 5% menos). Suben si todos compran y bajan si todos venden
# (entre 40% y 300% del base) y despues vuelven solos hacia el base. Referencia: un mob hostil de AstralRPG da 15$.
MERCADO = {
    "mineria": ("&bMineria", "minecraft:iron_pickaxe", 2, 3, {
        "cobblestone": 1, "coal": 4, "copper_ingot": 3, "iron_ingot": 12, "gold_ingot": 18, "redstone": 3, "lapis_lazuli": 5,
        "quartz": 6, "amethyst_shard": 6, "obsidian": 15, "diamond": 120, "emerald": 80, "netherite_scrap": 400}),
    "cultivos": ("&aCultivos", "minecraft:wheat", 2, 5, {
        "wheat": 3, "carrot": 3, "potato": 3, "beetroot": 2, "sugar_cane": 4, "pumpkin": 6, "melon_slice": 1, "cocoa_beans": 3,
        "nether_wart": 4, "sweet_berries": 2, "cactus": 3, "bamboo": 1}),
    "mobs": ("&cDrops de mobs", "minecraft:bone", 2, 7, {
        "rotten_flesh": 1, "bone": 3, "string": 3, "spider_eye": 4, "gunpowder": 6, "leather": 6, "feather": 2,
        "slime_ball": 8, "ender_pearl": 25, "blaze_rod": 20, "phantom_membrane": 15, "ghast_tear": 40}),
    "madera": ("&6Madera", "minecraft:oak_log", 4, 5, {
        "oak_log": 3, "spruce_log": 3, "birch_log": 3, "jungle_log": 3, "acacia_log": 3, "dark_oak_log": 3,
        "mangrove_log": 3, "cherry_log": 4, "pale_oak_log": 4}),
}
MERCADO_LORE = {"mineria": "Minerales, lingotes y gemas.", "cultivos": "Cosechas y plantas.",
                "mobs": "Lo que sueltan los monstruos.", "madera": "Troncos de todos los arboles."}


def mercado_categoria(cid):
    name, icon, row, col, items = MERCADO[cid]
    L = [f"# Categoria del mercado (generado por datapack-src/menus.py, MERCADO)", f'name: "{name}"', f'icon: "{icon}"',
         f"slot: {(row - 1) * 9 + col - 1}", "", "defaults:", "  spread: 0.05", "  elasticity: 40000", "  reversion_rate: 0.02",
         "  floor_pct: 0.4", "  ceiling_pct: 3.0", "", "items:"]
    for it, price in items.items():
        L += [f"  {it}:", f'    item: "minecraft:{it}"', f"    base_price: {float(price)}"]
    return "\n".join(L) + "\n"


def mercado_menu():
    L = ["# Mercado: menu principal (generado por datapack-src/menus.py)", 'title: "&8Mercado"', "command: []", "rows: 4", "",
         "pages:", "  - page: 1", "    mask:", "      items:", "        - yellow_stained_glass_pane", "      pattern:",
         '        - "111111111"', '        - "100000001"', '        - "100000001"', '        - "111111111"', "", "slots:"]
    for cid, (name, icon, row, col, _) in MERCADO.items():
        L += [f'  - item: {icon.split(":")[1]} hide_attributes name:"{name}"', "    lore:", f'      - "&7{MERCADO_LORE[cid]}"',
              '      - ""', '      - "&eClic para ver"', "    location:", f"      row: {row}", f"      column: {col}", "      page: 1",
              "    left-click:", "      - id: open_menu", "        args:", "          menu: bazaar_category", f"          category: {cid}",
              "      - id: play_sound", "        args:", "          sound: ui_button_click", "          pitch: 1", "          volume: 1"]
    L += ['  - item: barrier name:"&cCerrar"', "    lore: []", "    location:", "      row: 4", "      column: 5", "      page: 1",
          "    left-click:", "      - id: close_inventory"]
    return "\n".join(L) + "\n"


def main():
    rb = os.path.join(OUT, "..", "RoyalBazaar")
    os.makedirs(os.path.join(rb, "categories"), exist_ok=True)
    os.makedirs(os.path.join(rb, "menus"), exist_ok=True)
    for cid in MERCADO:
        open(os.path.join(rb, "categories", f"{cid}.yml"), "w", encoding="utf-8").write(mercado_categoria(cid))
    open(os.path.join(rb, "menus", "bazaar_main.yml"), "w", encoding="utf-8").write(mercado_menu())
    os.makedirs(os.path.join(OUT, "gui_menus"), exist_ok=True)
    menus = {f"{gid}": gacha_menu(gid, g) for gid, g in GACHAS.items()}
    menus.update({"mascotas": mascotas_menu(), "bazar": bazar_menu(), "principal": principal_menu()})
    for k, txt in menus.items():
        open(os.path.join(OUT, "gui_menus", f"{k}.yml"), "w", encoding="utf-8").write(txt)
    lista = ["# Pegar dentro de plugins/DeluxeMenus/config.yml, en 'gui_menus:' (generado por datapack-src/menus.py)", "gui_menus:"]
    lista += [f"  {k}:\n    file: {k}.yml" for k in menus]
    open(os.path.join(OUT, "config-gui_menus.yml"), "w", encoding="utf-8").write("\n".join(lista) + "\n")
    print(f"menus: {len(menus)} -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
