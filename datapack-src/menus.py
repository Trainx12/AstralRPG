# -*- coding: utf-8 -*-
"""
Menus de cofre (DeluxeMenus) para que los jugadores no tengan que escribir comandos.

  /menu          menu principal (mascotas, mercado, subastas, guia, volver al lobby)
  /mascotas      tus mascotas: invocar o guardar (las que no tenes aparecen bloqueadas)
  gacha_*        lo abre el cofre de cada gacha: tirar x1 / x10 / x25 / x50 y ver premios
  bazar          lo abre el aldeano Bazar: mercado y venta rapida (EconomyShopGUI), subastas (CrazyAuctions), ordenes (DonutOrders)

Los menus que abren los vendedores se abren desde la consola con 'dm open <menu> <jugador>'.
Salida: ../build/menus/DeluxeMenus/  (gui_menus/*.yml + config-gui_menus.yml con la lista para config.yml)
"""
import os
import textwrap

from lobby import GACHAS, PITY, HOLO_COLOR, HOLO_NAME, HOLO_DESC, pity_obj, TIRADAS, money, RARITY_WEIGHT
from mobs.mascotas import MASCOTAS
from misiones import CHAPTERS, DAILIES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "menus", "DeluxeMenus")
RULETA_TICKS = 140
# Puntaje del jugador (expansion 'ScoreboardObjectives' de PlaceholderAPI).
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
                  "&7nivel 10 y 20 = efecto extra, nivel 30 = evolucion.", "", "&7Te acompanan en todos los mundos.", "&8Bonus solo dentro de las mazmorras."])
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
    items = item("info", "OAK_SIGN", 4, "&6&l✦ Bazar ✦", ["&7Compra y vende con el servidor", "&7o con otros jugadores."])
    items += item("mercado", "EMERALD", 10, "&a&lMercado",
                  ["&7Compra y vende materiales al servidor.", "", "&eClic para abrir"],
                  extra={"click_commands": ["[close]", "[player] shop"]})
    items += item("venta", "HOPPER", 12, "&2&lVenta rapida",
                  ["&7Pone lo que quieras vender y listo.", "", "&eClic para abrir"],
                  extra={"click_commands": ["[close]", "[player] sellgui"]})
    items += item("subastas", "GOLD_INGOT", 14, "&e&lSubastas",
                  ["&7Items unicos entre jugadores (armas, armaduras...).", "&7Para publicar: agarra el item y usa",
                   "&f/ah sell <precio>", "", "&eClic para abrir"], extra={"click_commands": ["[close]", "[player] ah"]})
    items += item("ordenes", "PAPER", 16, "&b&lOrdenes de compra",
                  ["&7Pedi algo que buscas y paga por adelantado:", "&7cuando alguien te lo entrega, te llega solo.",
                   "&7Tambien podes entregar lo que otros piden.", "", "&eClic para abrir"],
                  extra={"click_commands": ["[close]", "[player] orders"]})
    items += relleno("YELLOW_STAINED_GLASS_PANE", 27, [4, 10, 12, 14, 16])
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
    items += item("misiones", "BOOK", 20, "&b&lMisiones e historia", ["&7Consulta tu capitulo y las diarias", "&7El Cronista entrega los premios"],
                  extra={"click_commands": ["[console] execute as %player_name% at @s run function astral:quest/gui/page/0", "[openguimenu] misiones"]})
    items += relleno("LIGHT_BLUE_STAINED_GLASS_PANE", 27, [4, 10, 12, 14, 16, 20, 22])
    return menu("&8Menu de AstralRPG", "menu", 27, items, update=True)


def misiones_menu(current_page=0):
    """Una mision por pantalla, con acciones que validan el progreso en el datapack."""
    P = "%player_name%"

    def req(page, **scores):
        # Cada seccion es un menu real: navegar no depende de leer aq.page.
        return "\n      requirements:" + "".join(
            f"\n        r{i}:\n          type: string equals\n          input: {q(SCORE.format('aq.' + key))}\n          output: {q(value)}"
            for i, (key, value) in enumerate(scores.items()))

    def action(function):
        if function.startswith("gui/details/"):
            return ["[close]", f"[console] execute as {P} at @s run function astral:quest/{function}",
                    f"[message] &7Volve al detalle con /{mission_menu_id(current_page)}."]
        if function.startswith("gui/page/"):
            page = int(function.rsplit("/", 1)[1])
            return [f"[console] execute as {P} at @s run function astral:quest/{function}",
                    f"[openguimenu] {mission_menu_id(page)}"]
        return [f"[console] execute as {P} at @s run function astral:quest/{function}",
                f"[openguimenu] {mission_menu_id(current_page)}<delay=2>"]

    def button(key, material, slot, name, lore, page, function=None, **scores):
        if page != current_page:
            return []
        extra = {"priority": 1, "update": "true"}
        if scores:
            extra["view_requirement"] = req(page, **scores)
        if function:
            extra["click_commands"] = action(function)
        return item(key, material, slot, name, lore, extra=extra)

    icons = ["COMPASS", "WHEAT", "NAUTILUS_SHELL", "OAK_SAPLING", "SANDSTONE", "IRON_PICKAXE", "SNOWBALL", "BLAZE_POWDER", "NETHER_STAR"]
    rewards = [300, 500, 1000, 1500, 2000, 2500, 3000, 5000, 10000]
    progress = {
        1: ["&7Herrero: &f" + SCORE.format("aq.herrero") + "/1", "&7Forja tier I: &f" + SCORE.format("aq.forge1") + "/1"],
        2: ["&7Espantapajaros: &f" + SCORE.format("aq.scare") + "/10", "&7Abejorros: &f" + SCORE.format("aq.bee") + "/10", "&7Elites: &f" + SCORE.format("aq.helite") + "/1"],
        3: ["&7Cangrejo: &f" + SCORE.format("aq.f1") + "/1"],
        4: ["&7Caras: &f" + SCORE.format("aq.face") + "/15", "&7Chaman: &f" + SCORE.format("aq.f2") + "/1"],
        5: ["&7Momia: &f" + SCORE.format("aq.f3") + "/1"],
        6: ["&7Minas completadas: &f" + SCORE.format("aq.f4") + "/1"],
        7: ["&7Yeti: &f" + SCORE.format("aq.f5") + "/1"],
        8: ["&7Forja tier V: &f" + SCORE.format("aq.forge5") + "/1", "&7Golem: &f" + SCORE.format("aq.f6") + "/1"],
    }
    L = []
    for page, label, icon in [(0, "Historia", "BOOK"), (1, "Diaria facil", "PAPER"), (2, "Diaria media", "MAP"), (3, "Diaria dificil", "ENCHANTED_BOOK")]:
        L += item(f"tab_{page}", icon, page, f"&b&l{label}", ["&eClic para ver una mision"], extra={"click_commands": action(f"gui/page/{page}")})
    for state in range(10):
        chapter = max(1, state)
        lore = ["&7" + line for line in textwrap.wrap(CHAPTERS[chapter - 1], 43)]
        lore += ["", f"&6Premio: {rewards[chapter - 1]}$"]
        if chapter == 2: lore += ["&6+ una pieza de armadura tier I a eleccion"]
        if chapter in (5, 7): lore += ["&6+ material astral"]
        if chapter == 9: lore += ["&6+ titulo Portador de la Estrella"]
        lore += [""] + progress.get(chapter, []) + ["", "&eClic: ver el objetivo en el chat.", "&eVerde: aceptar o comprobar y cobrar.", "&cRojo: rechazar o abandonar."]
        L += button(f"historia_{state}", icons[chapter - 1], 13, f"&b&lCapitulo {chapter}/9", lore, 0, f"gui/details/story/{state}", state=state)
        if state == 0:
            L += button("empezar", "LIME_DYE", 22, "&a&lAceptar mision", ["&7Empieza tu historia en el Refugio."], 0, "gui/accept", state=0)
        else:
            L += button(f"aceptar_{state}", "LIME_DYE", 22, "&a&lAceptar mision", ["&7Los objetivos cuentan desde que aceptas."], 0, "gui/accept", state=state, accepted=0)
            L += button(f"cobrar_{state}", "EMERALD", 22, "&a&lComprobar y cobrar", ["&7Comprueba los objetivos y entrega", "&7los materiales de esta mision.", "&7Si falta algo, no consume ni paga."], 0, "viajero", state=state, accepted=1)
            L += button(f"pausar_{state}", "RED_DYE", 20, "&c&lAbandonar mision", ["&7Pausa los objetivos sin borrar avances.", "&7Podes aceptarla otra vez mas tarde.", "&eClic para abandonar."], 0, "gui/reject", state=state, accepted=1)
        L += button(f"rechazar_{state}", "RED_DYE", 20, "&c&lRechazar por ahora", ["&7No inicia la mision ni entrega premios.", "&7Podes volver a aceptarla mas tarde."], 0, "gui/reject", state=state, accepted=0)
    L += button("historia_fin", "NETHER_STAR", 13, "&6&lHistoria completada", ["&7La Estrella vuelve a brillar.", "&7El Santuario Celestial te espera."], 0, state=10)
    L += button("premio_pendiente", "CHEST", 24, "&6Elegir premio de armadura", ["&7Se desbloquea al cobrar el capitulo 2.", "&7Elegis una sola pieza, una sola vez."], 0, "gui/page/4")
    for did, tier, name, counter, goal, desc in DAILIES:
        page = tier + 1
        lore = ["&7" + line for line in textwrap.wrap(desc, 43)] + ["", f"&6Premio: {[300,750,1500][tier]}$"]
        extras = {11: "&6+ Alma Corrupta", 12: "&6+ Alma Corrupta", 13: "&6+ 25% de Chispa Astral", 14: "&6+ 2 Esencias de Elite"}
        if did in extras: lore += [extras[did]]
        if counter:
            lore += ["", f"&7Progreso: &f{SCORE.format('aq.' + counter)}/{goal}" + (" cm" if counter == "ride" else "")]
        else:
            lore += ["", "&7Para entregar: acercate al NPC indicado", "&7y usa Comprobar y cobrar."]
        lore += ["", "&eClic: ver el objetivo en el chat.", "&eVerde: aceptar o comprobar y cobrar.", "&cRojo: rechazar o abandonar."]
        L += button(f"diaria_{did}", "PAPER", 13, f"&b&l{name}", lore, page, f"gui/details/daily/{tier}", **{f"d{tier}": did})
    for tier in range(3):
        page = tier + 1
        L += button(f"diaria_aceptar_{tier}", "LIME_DYE", 22, "&a&lAceptar mision", ["&7Empieza a contar tu progreso."], page, f"gui/daily/accept/{tier}", **{f"active{tier}": 0, f"done{tier}": 0})
        L += button(f"diaria_rechazar_{tier}", "RED_DYE", 20, "&c&lRechazar por ahora", ["&7No inicia la mision ni entrega premios.", "&7Podes aceptarla mas tarde hoy."], page, f"gui/daily/reject/{tier}", **{f"active{tier}": 0, f"done{tier}": 0})
        L += button(f"diaria_abandonar_{tier}", "RED_DYE", 20, "&c&lAbandonar mision", ["&7Pausa los objetivos sin borrar avances.", "&7Podes retomarla antes de medianoche.", "&eClic para abandonar."], page, f"gui/daily/reject/{tier}", **{f"active{tier}": 1, f"done{tier}": 0})
        L += button(f"diaria_cobrar_{tier}", "EMERALD", 22, "&a&lComprobar y cobrar", ["&7Valida solo esta mision."], page, f"gui/daily/claim/{tier}", **{f"active{tier}": 1, f"done{tier}": 0})
        L += button(f"diaria_fin_{tier}", "GRAY_DYE", 22, "&7&lMision cobrada", ["&7Volve manana para una mision nueva."], page, **{f"done{tier}": 1})
    for n, (cls, piece, material) in enumerate(((c, p, m) for c in ("Berserker", "Mago", "Arquero") for p, m in (("Casco", "IRON_HELMET"), ("Pechera", "IRON_CHESTPLATE"), ("Grebas", "IRON_LEGGINGS"), ("Botas", "IRON_BOOTS"))), 1):
        L += button(f"premio_{n}", material, [9,10,11,12,13,14,15,16,18,19,20,21][n-1], f"&6{cls} - {piece}", ["&7Premio del capitulo 2: una sola pieza.", "&eClic para elegir y recibirla."], 4, f"gui/choice/{n}")
    if current_page != 4:
        L += item("sin_datos", "BARRIER", 13, "&e&lMisiones sin cargar", ["&7Todavia no se pudieron leer tus misiones.", "&7Volve a abrir el menu en unos segundos.", "&7Si sigue igual, avisa al administrador.", "&7Falta revisar el reloj o ScoreboardObjectives."], extra={"priority": 99})
        L += item("sin_accion", "CLOCK", 22, "&eEsperando los datos de la mision", ["&7Usa Actualizar; si sigue igual,", "&7avisa al administrador."], extra={"priority": 99})
    L += item("ayuda", "OAK_SIGN", 8, "&b&lComo funcionan las misiones", ["&71. Elegi historia o una diaria arriba.", "&72. Pasa el cursor por el objeto central:", "&7   muestra objetivo, premio y progreso.", "&73. Acepta con el boton verde.", "&74. Completa y usa Comprobar y cobrar.", "&7Rojo: rechazar o pausar sin cobrar.", "&7Las diarias cambian a las 00:00 (Argentina)."])
    L += item("actualizar", "SUNFLOWER", 25, "&eActualizar misiones", extra={"click_commands": action(f"gui/page/{current_page}")})
    L += item("volver", "ARROW", 26, "&fVolver al menu", extra={"click_commands": ["[openguimenu] principal"]})
    L += relleno("BLUE_STAINED_GLASS_PANE", 27, [0,1,2,3,8,9,10,11,12,13,14,15,16,18,19,20,21,22,24,25,26])
    titles = ["Historia", "Diaria facil - 300$", "Diaria media - 750$", "Diaria dificil - 1500$", "Premio de historia"]
    result = menu("&8" + titles[current_page], mission_menu_id(current_page), 27, L, update=True)
    return result.replace("items:\n", f"open_commands:\n- '[console] execute as {P} at @s run function astral:quest/sync'\n- '[refresh]<delay=2>'\nitems:\n", 1)


def mission_menu_id(page):
    return "misiones" if page == 0 else f"misiones_{page}"


def main():
    os.makedirs(os.path.join(OUT, "gui_menus"), exist_ok=True)
    menus = {f"{gid}": gacha_menu(gid, g) for gid, g in GACHAS.items()}
    menus.update({"mascotas": mascotas_menu(), "bazar": bazar_menu(), "principal": principal_menu(), "misiones": misiones_menu()})
    menus.update({mission_menu_id(page): misiones_menu(page) for page in range(1, 5)})
    for k, txt in menus.items():
        open(os.path.join(OUT, "gui_menus", f"{k}.yml"), "w", encoding="utf-8").write(txt)
    lista = ["# Pegar dentro de plugins/DeluxeMenus/config.yml, en 'gui_menus:' (generado por datapack-src/menus.py)", "gui_menus:"]
    lista += [f"  {k}:\n    file: {k}.yml" for k in menus]
    open(os.path.join(OUT, "config-gui_menus.yml"), "w", encoding="utf-8").write("\n".join(lista) + "\n")
    print(f"menus: {len(menus)} -> {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
