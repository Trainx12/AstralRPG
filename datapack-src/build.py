# -*- coding: utf-8 -*-
"""
Genera el datapack AstralRPG-Items para Paper / Minecraft 26.1.2.
Uso:  python build.py
Salida: ../build/AstralRPG-Items/ y ../build/AstralRPG-Items.zip
"""
import json
import os
import shutil
import zipfile

from escala import VIDA_PIEZA, VIDA_JUGADOR_BASE, defensa_pieza, TIER_MAX
from items_t6_10 import ARCO_AUTO, PUNTERIA, ARMA_MODELO, BALLESTAS, CARGA_VANILLA, VISUAL as ARMOR_VISUAL, SIN_CASCO as ARMOR_SIN_CASCO, CASCO_PLANO as ARMOR_CASCO_PLANO
from escala import (FACTOR_ARMA, FACTOR_MOSTRADO, TIER_ESPECIAL, MANA_BASTON, MANA_HECHIZO, HECHIZO, HECHIZO_PERFORA,
                    REGEN_POR_MANA, fmt)
from items import (SKILLS, MATERIALS, HISTORY_ITEMS, MOB_DROPS, MAT_RECIPES, PIECES, PIECE_SLOT, ARMOR_VALUES,
                   TOUGHNESS, ARMOR_SETS, ROMAN, SWORDS, AXES, STAFFS, SCYTHES, BOWS,
                   SET_BONUS, MEJORAS, MEJORA_DANO, MEJORA_VIDA, ARMOR_DURABILITY)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "AstralRPG-Items")
NS = "astral"
DATA_FORMAT = 101  # Minecraft 26.1.x
# Subir este numero cuando cambian los items: los jugadores reciben la version nueva sola
STACK_VERSION_BASE = 31  # NO CAMBIAR: version inicial de los apilables (25/11); despues cada uno sube solo si cambia (item_versions.json)
ITEM_VERSION = 31  # 24/11: armadura = nivel del arma de su clase; Carnivora/Agua/oficios con requisito. 30: 23/11: armaduras piden la skill de su clase. 29: requisitos del tier 1 bajados. Antes 28: 23/11: sin sangrado, nivel minimo en armas especiales, mago/berserker T5<->T6.

files = {}


def put(path, content):
    if not isinstance(content, str):
        content = json.dumps(content, indent=1, ensure_ascii=False)
    files[path] = content


def fn(name, lines):
    put(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) + "\n")


def txt(text, color="gray", **kw):
    d = {"text": text, "color": color, "italic": False}
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# Helpers de items
# ---------------------------------------------------------------------------
ITEMS = {}      # id -> {"base":..., "components": {...}, "name":..., "kind":...}
FICHAS = {}
REQUIREMENTS = {}
RECIPES = []    # (out_id, count, ingredients, group)


def snbt(value):
    """Convierte un dict/list/valor de Python a SNBT."""
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            key = k if k.replace("_", "").isalnum() else '"' + k + '"'
            parts.append(f"{key}:{snbt(v)}")
        return "{" + ",".join(parts) + "}"
    if isinstance(value, list):
        return "[" + ",".join(snbt(v) for v in value) + "]"
    if isinstance(value, bool):
        return "1b" if value else "0b"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(round(value, 4)) + "d"
    if isinstance(value, Dbl):
        return repr(round(value.v, 4)) + "d"
    return '"' + str(value).replace('"', '\\"') + '"'


class Dbl:
    def __init__(self, v):
        self.v = float(v)


def aura_pdc(kind, skill=None, level=None, traits=None):
    """kind: 'armor' o 'item'. traits: lista de (trait, valor, operacion)."""
    pdc = {}
    if skill:   # nivel 0 tambien se guarda: AstralProgression lo usa para saber que skill recibe la XP del arma
        pdc[f"auraskills:{kind}_requirements"] = {f"auraskills:{skill}": int(level)}
    if traits:
        pdc[f"auraskills:{kind}_trait_modifiers"] = [
            {"auraskills:trait": f"auraskills/{t}", "auraskills:value": Dbl(v), "auraskills:operation": op}
            for (t, v, op) in traits]
    return pdc


def add_item(item_id, base, name, color, lore, astral_data, extra=None, pdc=None, model=None,
             glint=None, kind="item"):
    REQUIREMENTS[item_id] = {s: n for key, value in (pdc or {}).items()
                             if key.endswith('_requirements') for s, n in value.items()}
    custom = {NS: dict({"id": item_id, "v": ITEM_VERSION}, **astral_data)}
    if pdc:
        custom["PublicBukkitValues"] = pdc
    comps = {
        "minecraft:item_name": txt(name, color),
        "minecraft:lore": lore,
        "minecraft:custom_data": snbt(custom),
    }
    if model:
        comps["minecraft:item_model"] = model
    if glint is not None:
        comps["minecraft:enchantment_glint_override"] = glint
    if extra:
        comps.update(extra)
    if kind in ("weapon", "armor") and astral_data.get("type") in ("weapon", "staff", "armor", "tool"):
        from ficha import prepare, render
        source = prepare(item_id, name, base, lore, astral_data, comps, pdc)
        FICHAS[item_id] = source
        comps.update(render(source))
        hidden = comps.setdefault("minecraft:tooltip_display", {}).setdefault("hidden_components", [])
        if "minecraft:attribute_modifiers" not in hidden:
            hidden.append("minecraft:attribute_modifiers")
    elif astral_data.get("type") == "utility" and "tier" in astral_data and any(
            k in base for k in ("pickaxe", "shovel", "hoe", "fishing_rod", "shield")):
        from ficha import utility_render
        comps.update(utility_render(item_id, name, color, base, lore, astral_data, comps))
    ITEMS[item_id] = {"base": base, "components": comps, "name": name, "color": color, "kind": kind,
                      "ficha": item_id in FICHAS,
                      "mejorable": item_id in FICHAS and FICHAS[item_id]["kind"] not in ("drill", "saw")}


def req_line(skill, level):
    if not level:
        return txt("Requiere: sin nivel", "red")   # mismo texto que usa ficha.py
    return txt(f"Requiere: {SKILLS[skill]} {level}", "red")


# ---------------------------------------------------------------------------
# MATERIALES
# ---------------------------------------------------------------------------
for mid, (name, color, model, glint, desc) in MATERIALS.items():
    add_item(mid, "minecraft:paper", name, color,
             [txt(desc), txt("Material de AstralRPG", "dark_gray")],
             {"type": "material"}, model=model, glint=glint, kind="material")

from tanda_xp import register as register_xp
register_xp(add_item, txt)
from manzanas import register as register_manzanas
register_manzanas(add_item, txt)  # Manzanas de Mazmorra T2-T10

# Reforja de gemas (7d, 19/11/2026): items, encantamientos astral:gema_* y funciones gemas/* (fuente: gemas.py)
import gemas as GEMAS
GEMAS.register(put, fn, add_item, txt)
# Cavernas de Cristal (7e): Cristal, Geoda, Polvo y funciones cavernas/* (fuente: cavernas.py)
import cavernas as CAVERNAS
CAVERNAS.register(put, fn, add_item, txt)
# Vacio Estelar (7f, 23/11): Fragmento Estelar, Nucleo de Meteorito y vacio/jefe (fuente: vacio.py)
import vacio as VACIO
VACIO.register(put, fn, add_item, txt)

# Gancho de escalada
for mid, (name, color, model, glint, desc) in HISTORY_ITEMS.items():
    add_item(mid, "minecraft:paper", name, color, [txt(desc), txt("Recuerdo de la Estrella Astral", "dark_gray")],
             {"type": "quest"}, model=model, glint=glint, kind="quest")

# Items del Modo Historia (Gomera y premios de capitulo; solo los da el Cronista)
from historia_items import register as register_historia
register_historia(add_item, txt)

add_item("gancho", "minecraft:carrot_on_a_stick", "Saltador", "#d0d0d0",
         [txt("Click derecho: impulso hacia donde miras"), txt("Salto elevado sin dano de caida."),
          txt("Enfriamiento: 2 segundos.", "dark_gray")],
         {"type": "hook", "tier": 1},
         extra={"minecraft:enchantments": {f"{NS}:gancho": 1},
                "minecraft:tooltip_display": {"hidden_components": ["minecraft:enchantments"]},
                "minecraft:max_stack_size": 1})
RECIPES.append(("gancho", 1, [("v", "minecraft:fishing_rod", 1), ("v", "minecraft:iron_ingot", 2),
                              ("v", "minecraft:string", 2)], "Especiales"))

# Variante de prueba: caña vanilla con sedal y colision reales, sin receta por ahora.
add_item("gancho_realista", "minecraft:fishing_rod", "Gancho", "#D6B4FF",
         [txt("Click derecho: lanza el anzuelo (mano principal)."),
          txt("Vuelve a pulsar al enganchar un bloque o entidad."),
          txt("El tiron te lleva hacia el anzuelo, no hacia la mirada."),
          txt("Anclaje fijo · alcance 32 bloques · sin recarga", "dark_gray")],
         {"type": "realistic_hook", "tier": 1})

for (out, n, ings) in MAT_RECIPES:
    RECIPES.append((out, n, ings, "Materiales"))


# ---------------------------------------------------------------------------
# ARMADURAS
# ---------------------------------------------------------------------------
def armor_attrs(item_id, piece, mat, stats, extra_armor=0, tough_extra=0, vida=0):
    # Sin dureza vanilla: la proteccion es la DEFENSA de escala.py (astral.def), la aplica Skript.
    slot = PIECE_SLOT[piece]
    mods = []

    def m(attr, amount, op, suffix):
        mods.append({"type": f"minecraft:{attr}", "id": f"{NS}:{item_id}.{suffix}", "amount": round(amount, 4),
                     "operation": op, "slot": slot})

    # Barra de armadura vanilla completa con el set (3/8/6/3 = 20, pedido del dueno 13/11/2026).
    # Es solo el indicador: AstralDecor anula la reduccion vanilla en jugadores.
    m("armor", {"helmet": 3, "chestplate": 8, "leggings": 6, "boots": 3}[piece], "add_value", "barra")
    if vida:
        # Vida fija de la pieza (escala.VIDA_PIEZA); los % de vida del set van aparte.
        m("max_health", vida, "add_value", "vida")
    if mat == "netherite":
        m("knockback_resistance", 0.1, "add_value", "kbn")
    q = 4.0
    if "hp" in stats:
        m("max_health", stats["hp"] / 100 / q, "add_multiplied_total", "hp")
    if "dmg" in stats:
        m("attack_damage", stats["dmg"] / 100 / q, "add_multiplied_total", "dmg")
    if "fire" in stats:
        m("burning_time", -stats["fire"] / 100 / q, "add_multiplied_total", "fire")
    if "kb" in stats:
        m("knockback_resistance", stats["kb"] / 100 / q, "add_value", "kb")
    if "spd" in stats:
        m("movement_speed", stats["spd"] / 100 / q, "add_multiplied_base", "spd")
    return mods


def stat_lines(stats, per_piece=True):
    names = {"hp": "vida maxima", "dmg": "dano cuerpo a cuerpo", "def": "defensa", "fire": "tiempo en llamas",
             "kb": "resistencia al empuje", "mana": "mana maximo", "mregen": "regeneracion de mana",
             "mdmg": "dano magico", "cdr": "enfriamiento de hechizos", "rdmg": "dano a distancia",
             "crit": "probabilidad de critico", "spd": "velocidad", "draw": "velocidad de disparo"}
    out = []
    for k, v in stats.items():
        if k == "fire":
            out.append(txt(f"-{v}% {names[k]}", "gold"))
        elif k == "cdr":
            out.append(txt(f"-{v}% {names[k]}", "aqua"))
        elif k == "mana":
            out.append(txt(f"+{v} {names[k]}", "aqua"))
        else:
            sign = "+" if v >= 0 else ""
            out.append(txt(f"{sign}{v}% {names[k]}", "green" if v >= 0 else "red"))
    return out


for set_id, sdef in ARMOR_SETS.items():
    for ti, tier in enumerate(sdef["tiers"]):
        tnum = ti + 1
        for piece in PIECES:
            iid = f"{set_id}_{tnum}_{piece}"
            mat = tier["mat"]
            base = f"minecraft:{mat}_{piece}"
            pname = f"{sdef['piece_names'][piece]} {tier['name']}"
            stats = tier["stats"]
            per_piece = {k: v for k, v in stats.items()}
            # stats que van completos en la pechera
            chest_only = {"draw"}
            lore = [txt(f"{sdef['clase']} {ROMAN[ti]}", sdef["color"]),
                    txt("Bonus del set completo:", "gray")]
            lore += stat_lines({k: v for k, v in stats.items()})
            if tier.get("lifesteal"):
                lore.append(txt("Robo de vida (pechera)", "dark_red"))
            if tier.get("furia"):
                lore.append(txt("Mas dano cuanto menos vida tenes (pechera)", "dark_red"))
            lore.append(txt("Cada pieza da 1/4 del bonus", "dark_gray"))
            lore.append(txt(f"Piezas {sdef['clase']} (cualquier tier):", "gray"))
            for npz, (desc, _) in SET_BONUS[set_id].items():
                lore.append(txt(f" ({npz}) {desc}", sdef["color"]))
            lore.append(req_line(sdef["skill"], tier["lvl"]))
            extra = {"minecraft:max_damage": int(ARMOR_DURABILITY[ti] * {'helmet':0.8,'chestplate':1,'leggings':0.95,'boots':0.85}[piece]),
                     "minecraft:attribute_modifiers":
                     armor_attrs(iid, piece, mat, {k: v for k, v in stats.items() if k not in chest_only},
                                 tier.get("extra_armor", 0), tier.get("tough", 0), vida=VIDA_PIEZA[tnum])}
            if mat == "leather":
                extra["minecraft:dyed_color"] = sdef["dye"][ti]
                extra["minecraft:tooltip_display"] = {"hidden_components": ["minecraft:dyed_color"]}
            ench = {}
            if piece == "chestplate":
                if tier.get("lifesteal"):
                    ench[f"{NS}:robo_vida"] = tier["lifesteal"]
                if tier.get("furia"):
                    ench[f"{NS}:furia"] = tier["furia"]
                if set_id == "arquero":
                    ench[f"{NS}:punteria_set"] = tnum
            if ench:
                extra["minecraft:enchantments"] = ench
            traits = []
            if "mana" in stats:
                traits.append(("max_mana", stats["mana"] / 4, "add"))
                # Regeneracion (mana por segundo): 2% del mana de la pieza, +mregen% (escala.py).
                regen = stats["mana"] / 4 * REGEN_POR_MANA * (1 + stats.get("mregen", 0) / 100)
                traits.append(("mana_regen", round(regen, 3), "add"))
            if "crit" in stats:
                traits.append(("crit_chance", stats["crit"] / 4, "add"))
            pdc = aura_pdc("armor", sdef["skill"], tier["lvl"], traits)
            astral = {"type": "armor", "set": set_id, "tier": tnum, "piece": piece,
                      "def": defensa_pieza(tnum, piece, stats.get("def", 0), tier.get("extra_armor", 0))}
            if "mdmg" in stats:
                astral["mdmg"] = int(round(stats["mdmg"] * 100 / 4))
            if "cdr" in stats:
                astral["cdr"] = int(round(stats["cdr"] * 100 / 4))
            if "draw" in stats and piece == "chestplate":
                astral["draw"] = stats["draw"]
            add_item(iid, base, pname, sdef["color"], lore, astral, extra=extra, pdc=pdc,
                     glint=(tnum >= 3) if not ench else None, kind="armor")
            if tnum == 1:
                ings = [("v", f"minecraft:leather_{piece}", 1)] + tier["cost"]
            else:
                ings = [("c", f"{set_id}_{tnum - 1}_{piece}", 1)] + tier["cost"]
            RECIPES.append((iid, 1, ings, f"Armaduras {sdef['clase']}"))


# ---------------------------------------------------------------------------
# ARMAS
# ---------------------------------------------------------------------------
def weapon_mods(iid, dmg_total, speed, extra=None):
    mods = [{"type": "minecraft:attack_damage", "id": "minecraft:base_attack_damage", "amount": round(dmg_total - 1, 3),
             "operation": "add_value", "slot": "mainhand"},
            {"type": "minecraft:attack_speed", "id": "minecraft:base_attack_speed", "amount": round(speed - 4, 3),
             "operation": "add_value", "slot": "mainhand"}]
    for e in (extra or []):
        mods.append(e)
    return mods


def weapon_item(iid, base, name, color, clase, tier, desc, skill, lvl, mods, ench, astral, model=None,
                traits=None, more_lore=None, extra_pdc=None):
    lore = [txt(f"{clase} {ROMAN[tier - 1]}", color)]
    real = next((m["amount"] + 1 for m in (mods or []) if m["type"] == "minecraft:attack_damage"), None)
    if real is not None:
        lore.append(txt(f"Dano: {fmt(real * FACTOR_MOSTRADO[tier])}", "red"))
    lore += [txt(d, "gray") for d in desc]
    if more_lore:
        lore += more_lore
    lore.append(req_line(skill, lvl))
    extra = {}
    if mods is not None:
        extra["minecraft:attribute_modifiers"] = mods
        if real is not None:
            extra["minecraft:tooltip_display"] = {"hidden_components": ["minecraft:attribute_modifiers"]}
    if ench:
        extra["minecraft:enchantments"] = ench
    pdc = aura_pdc("item", skill, lvl, traits)
    pdc.update(extra_pdc or {})
    add_item(iid, base, name, color, lore, dict({"type": "weapon", "tier": tier}, **astral), extra=extra,
             pdc=pdc, model=model, kind="weapon")


FX_ENCH = {"lifesteal": "robo_vida", "furia": "furia", "remate": "remate", "verdugo": "verdugo",
           "sangrado": "sangrado", "hendidura": "hendidura", "maldicion": "maldicion", "cono": "cono"}


def fx_to_ench(fx, exec_kind=None):
    e = {}
    for k, v in fx.items():
        if k == "sangrado":   # 23/11: sangrado retirado por pedido del dueno (ni mobs ni jugadores sangran)
            continue
        if k == "ejecucion":
            e[f"{NS}:ejecucion" if v == 1 else f"{NS}:ejecucion_astral"] = 1
        else:
            e[f"{NS}:{FX_ENCH[k]}"] = v
    return e


BERS = ARMOR_SETS["berserker"]["color"]
for i, s in enumerate(SWORDS):
    t = i + 1
    iid = f"espada_{t}"
    dmg = s["dmg"] * (1 + s["bonus"] / 100)
    extra = []
    if s.get("kb_res"):
        extra.append({"type": "minecraft:knockback_resistance", "id": f"{NS}:{iid}.kb", "amount": s["kb_res"],
                      "operation": "add_value", "slot": "mainhand"})
    if s.get("kb_out"):
        extra.append({"type": "minecraft:attack_knockback", "id": f"{NS}:{iid}.kbo", "amount": s["kb_out"],
                      "operation": "add_value", "slot": "mainhand"})
    dmg *= FACTOR_ARMA[t]
    weapon_item(iid, s["base"], s["name"], BERS, "Espada Berserker", t, [f"+{s['bonus']}% de dano"] + s["desc"],
                "fighting", s["lvl"], weapon_mods(iid, dmg, 1.6, extra), fx_to_ench(s["fx"]), {"w": "sword"})
    ings = list(s["cost"]) if t == 1 else [("c", f"espada_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas Berserker"))

from escala import DANO
weapon_item("espada_heroe_errante", "minecraft:diamond_sword", "Espada del Heroe Errante", BERS,
            "Espada Berserker", 2, ["Se forja con materiales de tier II"], "fighting", SWORDS[1]["lvl"],
            weapon_mods("espada_heroe_errante", DANO[2], 1.6), {}, {"w": "sword", "special": "espada_heroe_errante"})
ITEMS["espada_heroe_errante"]["components"]["minecraft:item_model"] = "astral:espada_heroe_errante"
RECIPES.append(("espada_heroe_errante", 1, [("c", "espada_1", 1)] + list(SWORDS[1]["cost"]), "Armas Berserker"))

from items import CUCHILLOS
from escala import DANO, CUCHILLO_DANO, CUCHILLO_VELOCIDAD
for t,s in enumerate(CUCHILLOS,1):
    iid=f'cuchillo_{t}'
    # 22/11: los cuchillos son del Asesino (clases.py): espalda, veneno e invisibilidad en AstralClases.
    from clases import SETS as _CL
    weapon_item(iid, 'minecraft:iron_sword', s['name'], _CL['asesino']['color'], 'Cuchillo de Asesino', t,
                ['Ataque rapido: 3 golpes por segundo', 'Por la espalda: +50% de dano', 'Envenena: 8% del golpe por segundo, 3 s',
                 'Agachado + clic derecho: invisible 2 s (no en PvP)'], 'fighting', s['lvl'],
                weapon_mods(iid,DANO[t]*CUCHILLO_DANO,CUCHILLO_VELOCIDAD), {}, {'w':'knife'}, model=f'astral:{iid}',
                extra_pdc={'astral:clase_arma': 'cuchillo', 'astral:clase_tier': t})
    RECIPES.append((iid,1, ([] if t==1 else [('c',f'cuchillo_{t-1}',1)])+s['cost'],'Armas Asesino'))

for i, s in enumerate(AXES):
    t = i + 1
    iid = f"hacha_{t}"
    dmg = s["dmg"] * (1 + s["bonus"] / 100) * FACTOR_ARMA[t]
    weapon_item(iid, s["base"], s["name"], BERS, "Hacha Berserker", t, [f"+{s['bonus']}% de dano"] + s["desc"],
                "fighting", s["lvl"], weapon_mods(iid, dmg, s["spd"]), fx_to_ench(s["fx"]), {"w": "axe"})
    ings = list(s["cost"]) if t == 1 else [("c", f"hacha_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas Berserker"))

MAGO = ARMOR_SETS["mago"]["color"]
for i, s in enumerate(STAFFS):
    t = i + 1
    iid = f"baston_{t}"
    mana = MANA_BASTON[t]
    # Regeneracion (mana por segundo): 2% del mana del baston, +mregen% (escala.py).
    traits = [("max_mana", mana, "add"),
              ("mana_regen", round(mana * REGEN_POR_MANA * (1 + s.get("mregen", 0) / 100), 3), "add")]
    desc = [f"+{mana} mana", f"+{s['mdmg']}% dano magico", "Click derecho: proyectil arcano"] + s["desc"]
    # Dano del hechizo en la escala de tiers (escala.HECHIZO = espada del tier x 1,2).
    spell = HECHIZO[t]
    astral = {"w": "staff", "type": "staff", "tier": t, "spell": spell, "mdmg": s["mdmg"] * 100,
              "cd": s["cd"], "cdr": s.get("cdr", 0) * 100}
    # Lo que pega spell/cast sin bonus de armadura: base x (100 + mdmg + pierce)%.
    astral["spell_display"] = spell * (100 + s['mdmg'] + s.get('pierce', 0)) // 100
    astral["cd_display"] = (s['cd'] - int(s['cd']*s.get('cdr',0)/100))/20
    astral["mana_display"] = MANA_HECHIZO[t]
    lore_extra = [txt(f"Dano del hechizo: {fmt(spell * FACTOR_MOSTRADO[t])}", "light_purple"),
                  txt(f"Costo del hechizo: {MANA_HECHIZO[t]} mana", "aqua")]
    add_item(iid, "minecraft:carrot_on_a_stick", s["name"], MAGO,
             [txt(f"Baston de Mago {ROMAN[i]}", MAGO)] + [txt(d) for d in desc] + lore_extra + [req_line("sorcery", s["lvl"])],
             astral, pdc=aura_pdc("item", "sorcery", s["lvl"], traits), model=s["model"], glint=t >= 2,
             extra={"minecraft:max_stack_size": 1}, kind="weapon")
    ings = list(s["cost"]) if t == 1 else [("c", f"baston_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas de Mago"))

for i, s in enumerate(SCYTHES):
    t = i + 1
    iid = f"guadana_{t}"
    # 22/11: las guadanas son del Segador (clases.py). El area es el barrido en semicirculo de AstralClases,
    # asi que el "golpe en cono" del datapack ya no va (serian dos areas juntas).
    from clases import SETS as _CL
    ench = fx_to_ench({k: v for k, v in s["fx"].items() if k != "cono"})
    ench[f"{NS}:filo_arcano"] = t
    astral = {"w": "scythe"}
    if s.get("reset_cd"):
        astral["reset_cd"] = 1
    desc = ["Tajo en area: 60% del golpe a hasta 8 mobs adelante", "Cada baja te cura 0,5% de vida"] + [d for d in s["desc"] if "cono" not in d.lower()]
    weapon_item(iid, s["base"], s["name"], _CL['segador']['color'], "Guadana del Segador", t, desc, "fighting", s["lvl"],
                weapon_mods(iid, s["dmg"] * FACTOR_ARMA[t], 1.3), ench, astral,
                extra_pdc={'astral:clase_arma': 'guadana', 'astral:clase_tier': t})
    ings = list(s["cost"]) if t == 1 else [("c", f"guadana_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas Segador"))

ARQ = ARMOR_SETS["arquero"]["color"]
for i, s in enumerate(BOWS):
    t = i + 1
    iid = f"arco_{t}"
    desc = ([f"+{s['bonus']}% de dano"] if s["bonus"] else []) + [f"Dano de flecha cargada: ~{fmt(9 * FACTOR_ARMA[t])}"] + [f"Mantene click derecho: dispara solo cada {ARCO_AUTO[i] / 20:.2f}s".replace(".", ",")] + s["desc"]
    mods = None
    if s.get("spd"):
        mods = [{"type": "minecraft:movement_speed", "id": f"{NS}:{iid}.spd", "amount": s["spd"] / 100,
                 "operation": "add_multiplied_base", "slot": "mainhand"}]
    # Ficha: dano real de la flecha cargada (9 x Punteria del tier) y disparo automatico.
    arrow = round(9 * PUNTERIA[i] * FACTOR_ARMA[t])
    weapon_item(iid, "minecraft:bow", s["name"], ARQ, "Arco de Arquero", t, desc, "archery", s["lvl"], mods,
                {f"{NS}:punteria": t}, {"w": "bow", "draw": s["draw"], "arrow": arrow,
                                        "auto": ARCO_AUTO[i] / 20})
    ings = list(s["cost"]) if t == 1 else [("c", f"arco_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Arcos"))

# Ballestas de Arquero (items_t6_10.BALLESTAS): cargan mas rapido que la vanilla y pegan con Punteria del tier.
# En el pack publico se ven como la ballesta vanilla; el modelo elegido esta en el FINAL privado (armas_mod.py).
for t, s in BALLESTAS.items():
    iid = f"ballesta_{t}"
    arrow = round(9 * PUNTERIA[t - 1] * FACTOR_ARMA[t])
    ench = {f"{NS}:punteria": t, f"{NS}:carga_rapida": sorted(BALLESTAS).index(t) + 1}
    if s["piercing"]:
        ench["minecraft:piercing"] = s["piercing"]
    if s["multishot"]:
        ench["minecraft:multishot"] = s["multishot"]
    desc = [f"Dano de flecha: ~{fmt(9 * FACTOR_ARMA[t])}", f"Carga en {s['carga']:.2f}s".replace(".", ",")] + s["desc"]
    weapon_item(iid, "minecraft:crossbow", s["name"], ARQ, "Ballesta de Arquero", t, desc, "archery", s["lvl"], None,
                ench, {"w": "crossbow", "arrow": arrow}, model=f"{NS}:{iid}")
    RECIPES.append((iid, 1, list(s["cost"]), "Arcos"))

# Especiales
from special_weapons import WEAPONS as SPECIAL_WEAPONS, register as register_special_weapons
register_special_weapons(add_item, RECIPES, txt, weapon_mods)
add_item("guadana_umbria", "minecraft:netherite_hoe", "Guadana Umbria", "#7d3cff",
         [txt("Clase Segador", "#7d3cff"), txt("Dano en area en cono"), txt("Roba vida"), req_line("sorcery", 16)],
         {"type": "weapon", "w": "scythe", "tier": TIER_ESPECIAL},
         extra={"minecraft:attribute_modifiers": weapon_mods("guadana_umbria", 9 * FACTOR_ARMA[TIER_ESPECIAL], 1.2),
                "minecraft:enchantments": {f"{NS}:cono": 1, f"{NS}:robo_vida": 3}},
         pdc=aura_pdc("item", "sorcery", 16), kind="weapon")
RECIPES.append(("guadana_umbria", 1, [("c", "gema_umbria", 3), ("c", "shadowsteel", 2), ("c", "palo_reforzado", 1)], "Especiales"))

add_item("guantes_meteoro", "minecraft:paper", "Nudillos de Rubi", "#ff8c1a",
         [txt("Clase Monje", "#ff8c1a"), txt("Tus golpes queman"), txt("Mucho mas dano que a mano limpia"),
          req_line("fighting", 12)],
         {"type": "weapon", "w": "gloves", "tier": TIER_ESPECIAL}, model="minecraft:blaze_powder", glint=True,
         extra={"minecraft:attribute_modifiers": weapon_mods("guantes_meteoro", 7 * FACTOR_ARMA[TIER_ESPECIAL], 2.2),
                "minecraft:enchantments": {f"{NS}:igneo": 1}, "minecraft:max_stack_size": 1},
         pdc=aura_pdc("item", "fighting", 12), kind="weapon")
RECIPES.append(("guantes_meteoro", 1, [("c", "netherita_reforzada", 2), ("v", "minecraft:blaze_powder", 2),
                                        ("c", "gema_luminica", 1)], "Especiales"))

# ---------------------------------------------------------------------------
# TALADROS (Mineria) y MOTOSIERRAS (Deforestacion)
# ---------------------------------------------------------------------------
from tools import DRILLS, CHAINSAWS, AREA_NAMES, ROMAN_EXT

for i, d in enumerate(DRILLS):
    t = i + 1
    iid = d["id"]
    rules = [{"blocks": "#minecraft:incorrect_for_netherite_tool", "correct_for_drops": False},
             {"blocks": "#minecraft:mineable/pickaxe", "speed": d["speed"], "correct_for_drops": True},
             {"blocks": "#minecraft:mineable/shovel", "speed": d["speed"], "correct_for_drops": True}]
    # 24/11 (dueno): el taladro no golpea como pico; la broca gira (herramientas3d.py)
    extra = {"minecraft:tool": {"rules": rules, "default_mining_speed": 1.0, "damage_per_block": 1},
             "minecraft:swing_animation": {"type": "none"}}
    lore = [txt(f"Taladro {ROMAN_EXT[i]}", d["color"]),
            txt("Mas rapido que un pico de netherita" if d["area"] == 1 else f"Rompe en area {AREA_NAMES[d['area']]}", "gold"),
            txt(f"Velocidad: {d['speed']} (pico de netherita: 9)", "gray"),
            txt("Pica piedra, menas y tierra", "dark_gray"),txt("Shift: rompe solo el bloque apuntado.", "yellow")]
    if t >= 3:
        extra["minecraft:unbreakable"] = {}
        lore.append(txt("Indestructible", "aqua"))
    else:
        extra["minecraft:max_damage"] = d["dur"]
    if d.get("ench"):
        extra["minecraft:enchantments"] = d["ench"]
    lore.append(req_line("mining", d["lvl"]))
    add_item(iid, "minecraft:netherite_pickaxe", d["name"], d["color"], lore,
             {"type": "tool", "tool": "drill", "tier": t, "area": d["area"]}, extra=extra,
             pdc=aura_pdc("item", "mining", d["lvl"]), glint=False, kind="weapon")
    ings = list(d["cost"]) if t == 1 else [("c", DRILLS[i - 1]["id"], 1)] + d["cost"]
    RECIPES.append((iid, 1, ings, "Taladros"))

for i, c in enumerate(CHAINSAWS):
    t = i + 1
    iid = c["id"]
    rules = [{"blocks": "#minecraft:mineable/axe", "speed": c["speed"], "correct_for_drops": True}]
    extra = {"minecraft:tool": {"rules": rules, "default_mining_speed": 1.0, "damage_per_block": 1}}
    if c["chain"] == 0:
        what = "Mas rapida que un hacha de netherita"
    elif c["chain"] >= 100:
        what = "Tala el arbol entero de un corte"
    else:
        what = f"Corta {c['chain'] + 1} troncos de un corte"
    lore = [txt(f"Motosierra {ROMAN_EXT[i]}", c["color"]), txt(what, "gold"),
            txt(f"Velocidad: {c['speed']} (hacha de netherita: 9)", "gray"),txt("Shift: corta un solo bloque.", "yellow")]
    if c["chain"]:
        lore.append(txt("Solo en arboles naturales (con hojas)", "dark_gray"))
    if t >= 3:
        extra["minecraft:unbreakable"] = {}
        lore.append(txt("Indestructible", "aqua"))
    else:
        extra["minecraft:max_damage"] = c["dur"]
    lore.append(req_line("foraging", c["lvl"]))
    add_item(iid, "minecraft:netherite_axe", c["name"], c["color"], lore,
             {"type": "tool", "tool": "saw", "tier": t, "chain": c["chain"]}, extra=extra,
             pdc=aura_pdc("item", "foraging", c["lvl"]), glint=False, kind="weapon")
    ings = list(c["cost"]) if t == 1 else [("c", CHAINSAWS[i - 1]["id"], 1)] + c["cost"]
    RECIPES.append((iid, 1, ings, "Motosierras"))


# ---------------------------------------------------------------------------
# Enfriamiento de los arcos (evita disparar sin parar con carga casi instantanea)
# ---------------------------------------------------------------------------
from items import TALISMANS, TALISMAN_COST, SPEARS, ELITE_TIERS, ELITE_DROPS, HOSTILE

# ---------------------------------------------------------------------------
# Talismanes (mano secundaria)
# ---------------------------------------------------------------------------
for tid, t in TALISMANS.items():
    for lv in range(3):
        iid = f"talisman_{tid}_{lv + 1}"
        v = t["vals"][lv]
        line = t["fmt"].format(v=v, p=int(round(v * 100)))
        add_item(iid, "minecraft:paper", f"{t['name']} {ROMAN[lv]}", t["color"],
                 [txt("Llevalo en la mano secundaria", "dark_gray"), txt(line, "green")],
                 {"type": "talisman", "tier": lv + 1}, model=t["model"], glint=True, kind="weapon",
                 extra={"minecraft:max_stack_size": 1, "minecraft:attribute_modifiers": [
                     {"type": f"minecraft:{t['attr']}", "id": f"{NS}:{iid}", "amount": v,
                      "operation": t["op"], "slot": "offhand"}]})
        ings = list(TALISMAN_COST[lv]) if lv == 0 else [("c", f"talisman_{tid}_{lv}", 1)] + TALISMAN_COST[lv]
        if lv == 0:
            extra_ing = {"vida": ("v", "minecraft:golden_apple", 1), "furia": ("v", "minecraft:blaze_rod", 2),
                         "viento": ("v", "minecraft:feather", 4), "roca": ("v", "minecraft:iron_block", 1)}[tid]
            ings.append(extra_ing)
        RECIPES.append((iid, 1, ings, "Talismanes"))

# ---------------------------------------------------------------------------
# Lanzas (Combate)
# ---------------------------------------------------------------------------
for i, s in enumerate(SPEARS):
    t = i + 1
    iid = f"lanza_{t}"
    ench = fx_to_ench(s["fx"])
    # Dano explicito por tier, sin multiplicador duplicado de encantamientos.
    weapon_item(iid, s["base"], s["name"], "#ffb347", "Lanza de Combate", t,
                s["desc"], "fighting", s["lvl"], weapon_mods(iid, DANO[t] * __import__('balance_equipo').LANZA_DANO, __import__('balance_equipo').LANZA_VELOCIDAD), ench, {"w": "spear", "spear_balance": 1})
    ings = list(s["cost"]) if t == 1 else [("c", f"lanza_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Lanzas"))

# ---------------------------------------------------------------------------
# Texturas del resource pack (si el item tiene una, usa su modelo)
# ---------------------------------------------------------------------------
from textures import MATERIAL_TEX, BLOCK_ITEMS, WEAPON_TEX, BOW_TEX, GEN_WEAPON, GEN_ITEM, ARMOR_ITEMS
for _iid in list(MATERIAL_TEX) + list(BLOCK_ITEMS) + list(WEAPON_TEX) + list(BOW_TEX) + GEN_WEAPON + GEN_ITEM + ARMOR_ITEMS:
    ITEMS[_iid]["components"]["minecraft:item_model"] = f"{NS}:{_iid}"
from item_redesign import IDS as REDESIGN_IDS
for _iid in REDESIGN_IDS:
    ITEMS[_iid]["components"]["minecraft:item_model"] = f"{NS}:{_iid}"
for _t in DRILLS + CHAINSAWS:
    ITEMS[_t["id"]]["components"]["minecraft:item_model"] = f"{NS}:{_t['id']}"
# Saltador con arte propio; conservar el modelo existente del Gancho real.
ITEMS["gancho"]["components"]["minecraft:item_model"] = "astral:saltador"
ITEMS["gancho_realista"]["components"]["minecraft:item_model"] = f"{NS}:gancho"
# Armaduras: textura propia al tenerlas puestas
_SOUND = {"leather": "leather", "chainmail": "chain", "iron": "iron", "diamond": "diamond", "netherite": "netherite"}
for _iid in ARMOR_ITEMS:
    _set, _t, _piece = _iid.split("_")
    _c = ITEMS[_iid]["components"]
    _c.pop("minecraft:dyed_color", None)
    _c.pop("minecraft:tooltip_display", None)
    _mat = ITEMS[_iid]["base"].split(":")[1].split("_")[0]
    _c["minecraft:equippable"] = {"slot": PIECE_SLOT[_piece], "asset_id": f"{NS}:{_set}_{_t}",
                                  "equip_sound": f"minecraft:item.armor.equip_{_SOUND[_mat]}"}
    # Tiers 6-10 con modelo elegido: el casco se dibuja en 3D (item en la cabeza SIN asset_id; el pack FINAL
    # privado trae el modelo). Sin modelo, se ve como el T5 de su clase (pack publico).
    if _piece == "helmet" and ARMOR_VISUAL[_set].get(int(_t)) not in (None, *ARMOR_SIN_CASCO, *ARMOR_CASCO_PLANO):
        del _c["minecraft:equippable"]["asset_id"]
# Armas T6-T10: cada una con su item_model (items_t6_10.ARMA_MODELO); el modelo elegido esta en el FINAL privado.
for _iid, _it in ITEMS.items():
    _fam, _, _t = _iid.rpartition("_")
    if _fam in ("espada", "hacha", "baston", "guadana", "arco", "lanza") and _t.isdigit() and int(_t) >= 6:
        _model = ARMA_MODELO.get(_iid) or ITEMS[f"{_fam}_5"]["components"].get("minecraft:item_model")
        if _model:
            _it["components"]["minecraft:item_model"] = _model

# ---------------------------------------------------------------------------
# Loot tables de items (sirven para /loot y para el altar)
# ---------------------------------------------------------------------------
from tanda4b import register as register_tanda4b
register_tanda4b(ITEMS, FICHAS, RECIPES, add_item, txt, armor_attrs)
from oceano_items import register as register_oceano
register_oceano(ITEMS, FICHAS, RECIPES, add_item, txt, armor_attrs)
from oficios import register as register_oficios
register_oficios(ITEMS, FICHAS, RECIPES, add_item, txt, armor_attrs)
# Clases nuevas (22/11): Segador, Invocador y Asesino (armaduras y libros; habilidades en AstralClases).
from clases import register as register_clases
from escala import VIDA_PIEZA as _VIDA_PIEZA, defensa_pieza as _defensa_pieza
register_clases(add_item, RECIPES, txt, armor_attrs, aura_pdc, _defensa_pieza, req_line, ARMOR_SETS, ARMOR_DURABILITY,
                _VIDA_PIEZA, STAFFS)
from mesa import prepare as prepare_mesa, export as export_mesa
from balance_equipo import finalize as finalize_balance
finalize_balance(ITEMS, FICHAS)
# 25/11 (dueno: "no se juntan los items iguales"): los items que se APILAN (materiales, manzanas, frascos...)
# llevan SU PROPIA version: solo cambia si cambia ese item. Antes todos llevaban ITEM_VERSION y cada subida
# dejaba los del cofre (v viejo) sin juntarse con los del inventario (actualizados). Ver item_versions.json.
# El chequeo separa por minecraft:max_stack_size=1 (armas/armaduras/talismanes: ITEM_VERSION de siempre)
# y apilables (su version), asi pueden compartir numeros sin confundirse.
import hashlib as _hl
_VER_FILE = os.path.join(HERE, "item_versions.json")
_vers = json.load(open(_VER_FILE, encoding="utf-8")) if os.path.exists(_VER_FILE) else {}
_vtag = lambda v: f'id:"{{}}",v:{v}'
_NO_APILA = ("minecraft:fishing_rod", "minecraft:carrot_on_a_stick", "minecraft:warped_fungus_on_a_stick",
             "minecraft:book", "minecraft:potion", "minecraft:shield", "minecraft:bow", "minecraft:crossbow")
for _iid, _it in ITEMS.items():
    _c = _it["components"]
    _cd = _c.get("minecraft:custom_data", "")
    _cur = _vtag(ITEM_VERSION).format(_iid)
    if (_iid in FICHAS or _it["kind"] in ("weapon", "armor") or "minecraft:max_damage" in _c or _cur not in _cd
            or _c.get("minecraft:max_stack_size", 2) == 1 or _it["base"] in _NO_APILA):
        continue
    _h = _hl.sha1(json.dumps(dict(_c, **{"minecraft:custom_data": _cd.replace(_cur, f'id:"{_iid}"')}),
                             sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]
    _old = _vers.get(_iid)
    _v = STACK_VERSION_BASE if not _old else (_old["v"] if _old["h"] == _h else _old["v"] + 1)
    _vers[_iid] = {"v": _v, "h": _h}
    _c["minecraft:custom_data"] = _cd.replace(_cur, _vtag(_v).format(_iid))
_vers = {k: v for k, v in _vers.items() if k in ITEMS}
with open(_VER_FILE, "w", encoding="utf-8") as _f:
    json.dump(dict(sorted(_vers.items())), _f, indent=1)
ITEM_VERSIONS = {_iid: (_vers[_iid]["v"] if _iid in _vers else ITEM_VERSION) for _iid in ITEMS}
_ASTRAL = "minecraft:custom_data~{astral:{}}"
_UNO = "minecraft:max_stack_size=1"
# Selectores de "item viejo": no apilables, apilables en general y uno por apilable que ya cambio (lista corta).
OLD_PREDS = [f"*[{_ASTRAL},{_UNO},!minecraft:custom_data~{{astral:{{v:{ITEM_VERSION}}}}}]",
             f"*[{_ASTRAL},!{_UNO}" + "".join(f",!minecraft:custom_data~{{astral:{{v:{_v}}}}}"
                                              for _v in sorted({_vers[_i]["v"] for _i in _vers})) + "]"] + [
    f'*[minecraft:custom_data~{{astral:{{id:"{_i}"}}}},!minecraft:custom_data~{{astral:{{v:{_vers[_i]["v"]}}}}}]'
    for _i in sorted(_vers) if _vers[_i]["v"] != STACK_VERSION_BASE]
if len(OLD_PREDS) == 2 and {_vers[_i]["v"] for _i in _vers} <= {ITEM_VERSION}:
    # Mientras apilables y no apilables compartan la misma version alcanza un solo chequeo por casilla (menos CPU).
    OLD_PREDS = [f"*[{_ASTRAL},!minecraft:custom_data~{{astral:{{v:{ITEM_VERSION}}}}}]"]
MESA = prepare_mesa(ITEMS, FICHAS, RECIPES, txt)
# Armas clonadas (Carnivora, Asura, Agua): no pasan por add_item; la mesa toma el requisito real del item.
import re as _re
for _iid, _it in ITEMS.items():
    if not REQUIREMENTS.get(_iid):
        _m = _re.search(r'auraskills:(?:item|armor)_requirements"?:\{([^}]*)\}', _it['components']['minecraft:custom_data'])
        if _m:
            REQUIREMENTS[_iid] = {k: int(v) for k, v in _re.findall(r'"?(auraskills:\w+)"?:(\d+)', _m.group(1))}
export_mesa(ITEMS, REQUIREMENTS, RECIPES, os.path.dirname(HERE))
for iid, it in ITEMS.items():
    put(f"data/{NS}/loot_table/item/{iid}.json", {
        "type": "minecraft:command",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": it["base"], "functions": [
            {"function": "minecraft:set_components", "components": it["components"]}]}]}]})

# ---------------------------------------------------------------------------
# Actualizacion automatica de items viejos (version distinta a ITEM_VERSION)
# ---------------------------------------------------------------------------
def comp_arg(k, v):
    if k == "minecraft:custom_data":
        return f"{k}={v}"
    return f"{k}={snbt(v)}"


OLD = OLD_PREDS[0]
upd = []
for iid, it in ITEMS.items():
    sel = (f"*[minecraft:custom_data~{{{NS}:{{id:\"{iid}\"}}}},"
           f"!minecraft:custom_data~{{{NS}:{{v:{ITEM_VERSIONS[iid]}}}}}]")
    keep = []
    if it["kind"] in ("armor", "weapon"):
        mej = "mejora_armadura" if it["kind"] == "armor" else "mejora_arma"
        for L in range(1, 11):
            selL = sel[:-1] + f',minecraft:enchantments~[{{enchantments:"{NS}:{mej}",levels:{L}}}]]'
            keep += [f"execute store result score #c astral.tmp run clear @s {selL}",
                     f"execute if score #c astral.tmp matches 1.. store result storage {NS}:tmp up.n int 1 "
                     f"run scoreboard players get #c astral.tmp",
                     f"execute if score #c astral.tmp matches 1.. run function {NS}:upgrade/gm{L}/{iid} with storage {NS}:tmp up"]
            ench = dict(it["components"].get("minecraft:enchantments", {}))
            ench[f"{NS}:{mej}"] = L
            comps = dict(it["components"], **{"minecraft:enchantments": ench})
            if iid in FICHAS:
                from ficha import render
                comps.update(render(FICHAS[iid], L))
            comps.pop("minecraft:enchantment_glint_override", None)
            argsL = ",".join(comp_arg(k, v) for k, v in comps.items())
            fn(f"upgrade/gm{L}/{iid}", [f"$give @s {it['base']}[{argsL}] $(n)"])
    fn(f"upgrade/i/{iid}", keep + [
        f"execute store result score #c astral.tmp run clear @s {sel}",
        "execute if score #c astral.tmp matches ..0 run return 0",
        f"execute store result storage {NS}:tmp up.n int 1 run scoreboard players get #c astral.tmp",
        f"function {NS}:upgrade/g/{iid} with storage {NS}:tmp up",
    ])
    args = ",".join(comp_arg(k, v) for k, v in it["components"].items())
    fn(f"upgrade/g/{iid}", [f"$give @s {it['base']}[{args}] $(n)"])
    upd.append(f"function {NS}:upgrade/i/{iid}")
fn("upgrade/check", [
    f"execute unless items entity @s container.* {OLD} unless items entity @s armor.* {OLD} "
    f"unless items entity @s weapon.offhand {OLD} run return 0",
] + upd + [
    "# la guia vieja en libro ya no se usa (ahora es un menu) y cualquier item que ya no existe",
    f"clear @s {OLD}",
    "tellraw @s " + json.dumps(txt("Tus items de AstralRPG se actualizaron a la version nueva.", "light_purple"))])

# Netherita Fundida: horno y alto horno (entrada vanilla, salida custom)
nf = ITEMS["netherita_fundida"]
for rtype, t in (("smelting", 400), ("blasting", 200)):
    put(f"data/{NS}/recipe/netherita_fundida_{rtype}.json", {
        "type": f"minecraft:{rtype}", "category": "misc", "cookingtime": t, "experience": 2.0,
        "ingredient": "minecraft:netherite_ingot",
        "result": {"id": nf["base"], "count": 1, "components": nf["components"]}})


# ---------------------------------------------------------------------------
# Predicados
# ---------------------------------------------------------------------------
CHANCES = set()


def chance(p):
    key = str(int(round(p * 1000)))
    CHANCES.add((key, p))
    return f"{NS}:chance/{key}"


ING_PRED = {}


def ing_key(kind, ident, count):
    short = ident.split(":")[-1]
    key = f"{kind}_{short}_{count}"
    if key in ING_PRED:
        return key
    if kind == "c":
        base = ITEMS[ident]["base"]
        pred = {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {
            "type": "minecraft:item", "slots": {"contents": {
                "items": base, "count": {"min": count},
                "predicates": {"minecraft:custom_data": f'{{{NS}:{{id:"{ident}"}}}}'}}}}}
    else:
        if ident == "water_bottle":
            item_pred = {"items": "minecraft:potion", "count": {"min": count},
                         "components": {"minecraft:potion_contents": {"potion": "minecraft:water"}}}
        else:
            item_pred = {"items": ident, "count": {"min": count}}
        pred = {"condition": "minecraft:all_of", "terms": [
            {"condition": "minecraft:entity_properties", "entity": "this", "predicate": {
                "type": "minecraft:item", "slots": {"contents": item_pred}}},
            {"condition": "minecraft:inverted", "term": {
                "condition": "minecraft:entity_properties", "entity": "this", "predicate": {
                    "slots": {"contents": {"predicates": {"minecraft:custom_data": f"{{{NS}:{{}}}}"}}}}}}]}
    ING_PRED[key] = pred
    return key


# ---------------------------------------------------------------------------
# Mejora en el lugar (24/11, dueno): al forjar el tier siguiente (taladro, arma, armadura...) la pieza vieja
# se transforma en la nueva en vez de borrarse; conserva encantamientos, gemas, mejora del Herrero y nombre.
# ---------------------------------------------------------------------------
CHAIN = set()  # (resultado, pieza anterior que se transforma)
INPLACE_SLOTS = (["weapon.mainhand"] + [f"container.{n}" for n in range(36)]
                 + ["armor.head", "armor.chest", "armor.legs", "armor.feet", "weapon.offhand"])


def chain_prev(out, n, ings):
    kind, prev, count = ings[0]
    if n != 1 or kind != "c" or count != 1 or prev == out:
        return None
    if ITEMS[prev]["kind"] not in ("weapon", "armor") or ITEMS[out]["kind"] != ITEMS[prev]["kind"]:
        return None
    return prev


def inplace_fn(out, prev):
    """forge/ip/<out>: busca la pieza anterior y la transforma; forge/ipl/<out> (macro) elige el nivel de mejora."""
    CHAIN.add((out, prev))
    sel = f'*[minecraft:custom_data~{{{NS}:{{id:"{prev}"}}}}]'
    fn(f"forge/ip/{out}/{prev}", [f"execute if items entity @s {slot} {sel} run return run function {NS}:forge/ipl/{out}/{prev} "
                           f'{{slot:"{slot}"}}' for slot in INPLACE_SLOTS] + ["return 0"])
    lines = []
    if ITEMS[out]["mejorable"]:
        mej = "mejora_armadura" if ITEMS[out]["kind"] == "armor" else "mejora_arma"
        for L in range(10, 0, -1):
            lines.append(f"$execute if items entity @s $(slot) *[minecraft:enchantments~[{{enchantments:\"{NS}:{mej}\","
                         f"levels:{L}}}]] run return run item modify entity @s $(slot) {NS}:forja/{out}/{prev}/{L}")
    lines.append(f"$return run item modify entity @s $(slot) {NS}:forja/{out}/{prev}/0")
    fn(f"forge/ipl/{out}/{prev}", lines)


# ---------------------------------------------------------------------------
# ALTAR (Forja Astral)
# ---------------------------------------------------------------------------
SUBS = set()
recipe_fns = []
for (out, n, ings, group) in RECIPES:
    keys = []
    for (kind, ident, count) in ings:
        keys.append((ing_key(kind, ident, count), count, ident))
    total = sum(c for (_, c, _) in keys)
    rid = f"{out}"
    lines = []
    for (k, c, _) in keys:
        lines.append(f"execute unless entity @e[type=minecraft:item,distance=..1.2,predicate={NS}:ing/{k}] run return 0")
    prev = chain_prev(out, n, ings)
    if prev:
        inplace_fn(out, prev)
    for i, (k, c, ident) in enumerate(keys):
        if prev and i == 0:
            # La pieza anterior se transforma en el lugar (no se borra ni aparece una nueva).
            lines.append(f"execute as @e[type=minecraft:item,distance=..1.2,predicate={NS}:ing/{k},limit=1,sort=nearest] "
                         f"run function {NS}:forge/ipl/{out}/{prev} {{slot:\"contents\"}}")
            continue
        SUBS.add(c)
        lines.append(f"execute as @e[type=minecraft:item,distance=..1.2,predicate={NS}:ing/{k},limit=1,sort=nearest] "
                     f"run item modify entity @s contents {NS}:sub/{c}")
        if ident == "minecraft:lava_bucket":
            lines.append("summon minecraft:item ~ ~0.3 ~ {Item:{id:\"minecraft:bucket\",count:1}}")
    for _ in range(0 if prev else n):
        lines.append(f"loot spawn ~ ~0.3 ~ loot {NS}:item/{out}")
    it = ITEMS[out]
    # Las misiones registran la fabricacion real, no la mera posesion de equipo.
    for _tier in (1, 5):
        if f'tier:{_tier},' in it['components']['minecraft:custom_data'] or f'tier:{_tier}}}' in it['components']['minecraft:custom_data']:
            lines.append(f"function {NS}:quest/event/forge{_tier}")
    lines += [
        "particle minecraft:enchant ~ ~0.5 ~ 0.3 0.3 0.3 1 40",
        "particle minecraft:end_rod ~ ~0.5 ~ 0.2 0.2 0.2 0.02 12",
        "playsound minecraft:block.smithing_table.use block @a[distance=..12] ~ ~ ~ 1 1",
        "playsound minecraft:block.enchantment_table.use block @a[distance=..12] ~ ~ ~ 0.8 1.4",
        "title @a[distance=..6] actionbar " + json.dumps(
            [txt("Forjaste: ", "gray"), txt(it["name"] + (f" x{n}" if n > 1 else ""), it["color"])], ensure_ascii=False),
        "return 1",
    ]
    fn(f"altar/r/{rid}", lines)
    recipe_fns.append((total, len(keys), rid))

recipe_fns.sort(key=lambda r: (-r[0], -r[1]))
fn("altar/try", [f"execute if function {NS}:altar/r/{rid} run return 1" for (_, _, rid) in recipe_fns] + ["return 0"])
fn("altar/scan", [
    "# Cada jugador agachado busca items arriba de una mesa de herreria cercana",
    f"execute as @a[gamemode=!spectator,predicate={NS}:sneaking] at @s as @e[type=minecraft:item,distance=..4] at @s "
    f"if block ~ ~-0.2 ~ minecraft:smithing_table positioned ~ ~-0.2 ~ align xyz positioned ~0.5 ~1 ~0.5 "
    f"run function {NS}:altar/try",
])

for key, pred in ING_PRED.items():
    put(f"data/{NS}/predicate/ing/{key}.json", pred)
for c in SUBS:
    put(f"data/{NS}/item_modifier/sub/{c}.json", {"function": "minecraft:set_count", "count": -c, "add": True})

put(f"data/{NS}/predicate/in_sanctuary.json", {"condition":"minecraft:any_of", "terms":[
    {"condition":"minecraft:location_check", "predicate":{"dimension":"minecraft:"+world}}
    for world in ("santuario","santuario_interstellar",*__import__('instancias').copias("santuario_azeroth"))]})
put(f"data/{NS}/predicate/sneaking.json", {"condition": "minecraft:entity_properties", "entity": "this",
                                           "predicate": {"flags": {"is_sneaking": True}}})


# ---------------------------------------------------------------------------
# ENCANTAMIENTOS (efectos especiales de las armas y armaduras)
# ---------------------------------------------------------------------------
NOHIT = {"condition": "minecraft:inverted", "term": {"condition": "minecraft:entity_properties", "entity": "this",
                                                     "predicate": {"nbt": "{Tags:[\"astral.nohit\"]}"}}}
DIRECT = {"condition": "minecraft:damage_source_properties", "predicate": {"is_direct": True}}
# Ningun objeto "acepta" nuestros encantamientos para el juego: asi la mesa de LynExp, yunques y /enchant
# no los ofrecen (la mesa vendia Mejora +10 por XP, 12/11/2026). Los efectos no dependen de esto y
# nuestros comandos (set_enchantments) los ponen igual.
ENCH_ITEMS = f"#{NS}:sin_mesa"
put(f"data/{NS}/tags/item/sin_mesa.json", {"values": []})


def enchant(eid, name, color, max_level, slots, effects, supported=ENCH_ITEMS):
    put(f"data/{NS}/enchantment/{eid}.json", {
        "description": {"text": name, "color": color},
        "supported_items": supported,
        "weight": 1, "max_level": max_level,
        "min_cost": {"base": 999, "per_level_above_first": 0},
        "max_cost": {"base": 999, "per_level_above_first": 0},
        "anvil_cost": 8, "slots": slots, "effects": effects})


def all_of(*terms):
    return {"condition": "minecraft:all_of", "terms": list(terms)}


def run_fn_victim(func, extra_req=None):
    req = [NOHIT, DIRECT] + ([extra_req] if extra_req else [])
    return {"enchanted": "attacker", "affected": "victim",
            "effect": {"type": "minecraft:run_function", "function": f"{NS}:{func}"},
            "requirements": all_of(*req)}


enchant("robo_vida", "Robo de vida", "dark_red", 5, ["mainhand", "chest"], {
    "minecraft:post_attack": [{
        "enchanted": "attacker", "affected": "attacker",
        "effect": {"type": "minecraft:apply_mob_effect", "to_apply": "minecraft:regeneration",
                   "min_duration": 1.5, "max_duration": 2.0, "min_amplifier": 2.0, "max_amplifier": 2.0},
        "requirements": all_of(NOHIT, DIRECT, {
            "condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": f"{NS}:robo_vida",
            "unenchanted_chance": 0.0,
            "enchanted_chance": {"type": "minecraft:lookup", "values": [0.1, 0.15, 0.25, 0.3, 0.4], "fallback": 0.4}})}]})

# Furia: multiplicador segun % de vida del atacante (score astral.hp)
furia_effects = []
lvl1 = [1.15, 1.15, 1.12, 1.10, 1.08, 1.06, 1.04, 1.02, 1.0]
lvl2 = [1.45, 1.40, 1.35, 1.30, 1.25, 1.20, 1.15, 1.10, 1.05]
for b in range(9):
    lo, hi = b * 10, b * 10 + 9
    if b == 0:
        lo = -1000
    furia_effects.append({
        "effect": {"type": "minecraft:multiply",
                   "factor": {"type": "minecraft:lookup", "values": [lvl1[b], lvl2[b]], "fallback": lvl2[b]}},
        "requirements": all_of(DIRECT, {"condition": "minecraft:entity_scores", "entity": "attacker",
                                        "scores": {"astral.hp": {"min": lo, "max": hi}}})})
enchant("furia", "Furia", "red", 2, ["mainhand", "chest"], {"minecraft:damage": furia_effects})

enchant("remate", "Remate", "gold", 1, ["mainhand"], {"minecraft:post_attack": [run_fn_victim("fx/remate")]})
enchant("verdugo", "Verdugo", "gold", 1, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:multiply", "factor": 1.10},
    "requirements": all_of(DIRECT, {"condition": "minecraft:entity_properties", "entity": "this",
                                    "predicate": {"equipment": {"chest": {"count": {"min": 1}}}}})}]})
enchant("sangrado", "Sangrado", "dark_red", 1, ["mainhand"], {"minecraft:post_attack": [
    run_fn_victim("fx/bleed_start", {"condition": "minecraft:random_chance", "chance": 0.10})]})
enchant("hendidura", "Hendidura", "gold", 1, ["mainhand"], {"minecraft:post_attack": [run_fn_victim("fx/cleave")]})
enchant("ejecucion", "Ejecucion", "dark_red", 1, ["mainhand"], {"minecraft:post_attack": [run_fn_victim("fx/exec_15")]})
enchant("ejecucion_astral", "Ejecucion Astral", "dark_purple", 1, ["mainhand"],
        {"minecraft:post_attack": [run_fn_victim("fx/exec_20")]})
enchant("cono", "Golpe en Cono", "dark_purple", 1, ["mainhand"], {"minecraft:post_attack": [run_fn_victim("fx/cone")]})
enchant("maldicion", "Maldicion", "dark_purple", 1, ["mainhand"], {"minecraft:post_attack": [{
    "enchanted": "attacker", "affected": "victim",
    "effect": {"type": "minecraft:apply_mob_effect", "to_apply": ["minecraft:slowness", "minecraft:weakness"],
               "min_duration": 2.0, "max_duration": 3.0, "min_amplifier": 0.0, "max_amplifier": 0.0},
    "requirements": all_of(NOHIT, DIRECT)}]})
enchant("filo_arcano", "Filo Arcano", "light_purple", TIER_MAX, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:add",
               "value": {"type": "minecraft:lookup", "values": [0.5, 1.0, 1.8, 3.0, 4.5, 6.0, 7.5, 9.0, 11.0, 13.0], "fallback": 13.0}},
    "requirements": DIRECT}]})
enchant("igneo", "Puno Igneo", "gold", 1, ["mainhand"], {"minecraft:post_attack": [{
    "enchanted": "attacker", "affected": "victim",
    "effect": {"type": "minecraft:ignite", "duration": 4.0}, "requirements": all_of(NOHIT, DIRECT)}]})

ARROW_REQ = {"condition": "minecraft:entity_properties", "entity": "direct_attacker",
             "predicate": {"type": "#minecraft:arrows"}}
enchant("punteria", "Punteria", "green", TIER_MAX, ["mainhand", "offhand"], {
    "minecraft:damage": [{"effect": {"type": "minecraft:multiply", "factor": {
        "type": "minecraft:lookup", "values": [round(m * FACTOR_ARMA[i + 1], 3) for i, m in enumerate(PUNTERIA)],
        "fallback": round(PUNTERIA[-1] * FACTOR_ARMA[TIER_MAX], 3)}},
        "requirements": ARROW_REQ}],
    "minecraft:projectile_spawned": [{"effect": {"type": "minecraft:run_function", "function": f"{NS}:bow/tag"}}],
    "minecraft:ammo_use": [{"effect": {"type": "minecraft:set", "value": {
        "type": "minecraft:lookup", "values": [1, 1, 1, 1] + [0] * (TIER_MAX - 4), "fallback": 0}},
        "requirements": {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:arrow"}}}],
})
# Ballestas: tiempo de carga propio por nivel (la vanilla tarda 1,25 s).
enchant("carga_rapida", "Carga Rapida", "green", len(BALLESTAS), ["mainhand", "offhand"], {
    # crossbow_charge_time es un efecto de valor UNICO (como Carga Rapida vanilla), no una lista: con lista no arranca el server.
    "minecraft:crossbow_charge_time": {"type": "minecraft:add", "value": {
        "type": "minecraft:lookup", "values": [round(BALLESTAS[t]["carga"] - CARGA_VANILLA, 3) for t in sorted(BALLESTAS)],
        "fallback": round(min(b["carga"] for b in BALLESTAS.values()) - CARGA_VANILLA, 3)}}})
enchant("punteria_set", "Punteria del Set", "green", TIER_MAX, ["chest"], {
    "minecraft:damage": [{"effect": {"type": "minecraft:multiply", "factor": {
        "type": "minecraft:lookup", "values": [1.04, 1.08, 1.12, 1.18, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50], "fallback": 1.50}},
        "requirements": ARROW_REQ}]})
enchant("gancho", "Gancho", "gray", 1, ["mainhand"], {"minecraft:tick": [{
    "effect": {"type": "minecraft:apply_impulse", "direction": [0.0, 0.0, 1.0],
               "coordinate_scale": [1.0, 1.0, 1.0], "magnitude": 0.16},
    "requirements": {"condition": "minecraft:entity_scores", "entity": "this", "scores": {"astral.grap": {"min": 1}}}}]})

# Encantamientos originales de lanzas quedan conservados al migrar, pero no duplican
# el dano del nuevo atributo. En lanzas antiguas aun sin migrar funcionan como antes.
LEGACY_SPEAR = {"condition":"minecraft:all_of","terms":[DIRECT,
    {"condition":"minecraft:inverted","term":{"condition":"minecraft:entity_properties","entity":"attacker",
     "predicate":{"equipment":{"mainhand":{"predicates":{"minecraft:custom_data":"{astral:{spear_balance:1}}"}}}}}}]}
enchant("empalar", "Empalar", "gold", TIER_MAX, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:add",
               "value": {"type": "minecraft:lookup", "values": [1.0, 2.0, 3.0, 4.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0], "fallback": 12.0}},
    "requirements": LEGACY_SPEAR}]})

# Poder Astral: multiplica el dano de las lanzas segun su tier (escala.py).
enchant("poder_astral", "Poder Astral", "light_purple", TIER_MAX, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:multiply", "factor": {"type": "minecraft:lookup",
               "values": [round(FACTOR_ARMA[t], 3) for t in range(1, TIER_MAX + 1)], "fallback": round(FACTOR_ARMA[TIER_MAX], 3)}},
    "requirements": LEGACY_SPEAR}]})

# Mejora +1..+10 del Herrero (el nivel del encantamiento es el +N)
put(f"data/{NS}/enchantment/mejora_arma.json", {
    "description": {"text": "Mejora", "color": "gold"}, "supported_items": ENCH_ITEMS,
    "weight": 1, "max_level": 10, "min_cost": {"base": 999, "per_level_above_first": 0},
    "max_cost": {"base": 999, "per_level_above_first": 0}, "anvil_cost": 40, "slots": ["mainhand"],
    "effects": {"minecraft:damage": [{"effect": {"type": "minecraft:multiply", "factor": {
        "type": "minecraft:lookup", "values": MEJORA_DANO, "fallback": MEJORA_DANO[-1]}}}]}})
put(f"data/{NS}/enchantment/mejora_armadura.json", {
    "description": {"text": "Mejora", "color": "gold"}, "supported_items": ENCH_ITEMS,
    "weight": 1, "max_level": 10, "min_cost": {"base": 999, "per_level_above_first": 0},
    "max_cost": {"base": 999, "per_level_above_first": 0}, "anvil_cost": 40, "slots": ["armor"],
    "effects": {"minecraft:attributes": [{"id": f"{NS}:mejora_armadura", "attribute": "minecraft:max_health",
                                          "operation": "add_multiplied_total", "amount": {
        "type": "minecraft:lookup", "values": [v / 100 for v in MEJORA_VIDA], "fallback": MEJORA_VIDA[-1] / 100}}]}})

ench_items = sorted({it["base"] for it in ITEMS.values() if it["kind"] in ("armor", "weapon")} | {"minecraft:carrot_on_a_stick"})
put(f"data/{NS}/tags/item/enchantable.json", {"values": ench_items})


# ---------------------------------------------------------------------------
# Efectos (funciones)
# ---------------------------------------------------------------------------
IGNORE = ["minecraft:item", "minecraft:experience_orb", "minecraft:arrow", "minecraft:spectral_arrow",
          "minecraft:trident", "minecraft:marker", "minecraft:armor_stand", "minecraft:item_frame",
          "minecraft:glow_item_frame", "minecraft:painting", "minecraft:interaction", "minecraft:block_display",
          "minecraft:item_display", "minecraft:text_display", "minecraft:falling_block", "minecraft:tnt",
          "minecraft:area_effect_cloud", "minecraft:fishing_bobber", "minecraft:ender_pearl", "minecraft:snowball",
          "minecraft:egg", "minecraft:splash_potion", "minecraft:lingering_potion", "minecraft:experience_bottle",
          "minecraft:firework_rocket", "minecraft:leash_knot", "minecraft:end_crystal", "minecraft:minecart",
          "minecraft:chest_minecart", "minecraft:furnace_minecart", "minecraft:hopper_minecart",
          "minecraft:tnt_minecart", "minecraft:spawner_minecart", "minecraft:command_block_minecart",
          "minecraft:evoker_fangs", "minecraft:eye_of_ender", "minecraft:fireball", "minecraft:small_fireball",
          "minecraft:dragon_fireball", "minecraft:wither_skull", "minecraft:shulker_bullet", "minecraft:llama_spit",
          "minecraft:wind_charge", "minecraft:breeze_wind_charge", "minecraft:lightning_bolt",
          "minecraft:ominous_item_spawner", "#minecraft:boat",
          # Aldeanos: los NPC del lobby (MythicMobs) son aldeanos; ningun golpe de area ni hechizo los toca.
          "minecraft:villager", "minecraft:wandering_trader"]
put(f"data/{NS}/tags/entity_type/ignore.json", {"values": IGNORE})
put(f"data/{NS}/tags/entity_type/bosses.json", {"values": ["minecraft:wither", "minecraft:ender_dragon",
                                                           "minecraft:warden", "minecraft:elder_guardian"]})
put(f"data/{NS}/tags/block/passable.json", {"values": ["#minecraft:air", "#minecraft:replaceable"]})

MOB = f"type=!minecraft:player,type=!#{NS}:ignore,tag=!astral.pet,nbt=!{{Invulnerable:1b}}"

# porcentaje de vida de la victima en #pct (0-100)
fn("fx/victim_pct", [
    # Mobs de mas de 20 millones (T8+): Health x100 no entra en un puntaje; se calcula en otra escala.
    "execute store result score #m astral.tmp run attribute @s minecraft:max_health get 0.00001",
    f"execute if score #m astral.tmp matches 200.. run return run function {NS}:fx/victim_pct_g",
    "execute store result score #h astral.tmp run data get entity @s Health 100",
    "execute store result score #m astral.tmp run attribute @s minecraft:max_health get 1",
    "execute if score #m astral.tmp matches ..0 run scoreboard players set #m astral.tmp 1",
    "scoreboard players operation #h astral.tmp /= #m astral.tmp",
    "scoreboard players operation #pct astral.tmp = #h astral.tmp",
])
fn("fx/victim_pct_g", [
    "execute store result score #h astral.tmp run data get entity @s Health 0.001",
    "scoreboard players operation #h astral.tmp /= #m astral.tmp",
    "scoreboard players operation #pct astral.tmp = #h astral.tmp",
])
# #ht = tier del arma en la mano del atacante (score astral.ht, lo calcula player/lvl).
fn("fx/attacker_tier", [
    "scoreboard players set #ht astral.tmp 0",
    "execute on attacker run scoreboard players operation #ht astral.tmp = @s astral.ht",
    "# contra jugadores (arena) el sangrado y el remate quedan como antes",
    "execute if entity @s[type=minecraft:player] run scoreboard players set #ht astral.tmp 0",
])
fn("fx/remate", [
    f"function {NS}:fx/victim_pct",
    "execute if score #pct astral.tmp matches 50.. run return 0",
    "execute if score #pct astral.tmp matches ..0 run return 0",
    "# se aplica un rato despues para que no lo absorba la invulnerabilidad del golpe",
    "scoreboard players set @s astral.rem 2",
    f"function {NS}:fx/attacker_tier",
    *[f"execute if score #ht astral.tmp matches {t} run scoreboard players set @s astral.remd {round(15 * FACTOR_ARMA[t])}"
      for t in range(0, TIER_MAX + 1)],
])
fn("fx/remate_tick", [
    "scoreboard players remove @s astral.rem 1",
    "execute if score @s astral.rem matches 1.. run return 0",
    "tag @s add astral.nohit",
    f"execute store result storage {NS}:tmp hit.dmg float 0.1 run scoreboard players get @s astral.remd",
    f"function {NS}:fx/generic_hit with storage {NS}:tmp hit",
    "particle minecraft:crit ~ ~1 ~ 0.3 0.4 0.3 0.1 8",
    "tag @s remove astral.nohit",
])
# golpe extra al @s (victima) atribuido al atacante, sin volver a disparar efectos
fn("fx/extra_hit", [
    "tag @s add astral.nohit",
    "execute on attacker run tag @s add astral.atk",
    "$execute if entity @e[tag=astral.atk,limit=1] run damage @s $(dmg) minecraft:player_attack by @e[tag=astral.atk,limit=1]",
    "$execute unless entity @e[tag=astral.atk,limit=1] run damage @s $(dmg) minecraft:generic",
    "tag @e[tag=astral.atk] remove astral.atk",
    "tag @s remove astral.nohit",
])
for thr in (15, 20):
    fn(f"fx/exec_{thr}", [
        f"execute if entity @s[type=#{NS}:bosses] run return 0",
        f"function {NS}:fx/victim_pct",
        f"execute if score #pct astral.tmp matches {thr}.. run return 0",
        "execute if score #pct astral.tmp matches ..0 run return 0",
        "particle minecraft:damage_indicator ~ ~1 ~ 0.3 0.3 0.3 0.1 10",
        "playsound minecraft:entity.player.attack.crit player @a[distance=..16] ~ ~ ~ 1 0.6",
        f"function {NS}:fx/extra_hit {{dmg:1.0E9}}",
    ])
fn("fx/bleed_start", [
    # 23/11: sin sangrado. Las armas viejas que todavia tengan el encantamiento no hacen nada.
    "scoreboard players reset @s astral.bleed",
])
fn("fx/bleed_tick", ["scoreboard players reset @s astral.bleed"])
fn("fx/generic_hit", ["$damage @s $(dmg) minecraft:generic"])
fn("fx/cleave", [
    "tag @s add astral.src",
    "execute on attacker run tag @s add astral.atk",
    # 26/11: area por caja (toca el cuerpo, sirve para golems y mobs grandes) alrededor del golpeado
    # y otra caja detras de el, en la direccion en que mira el atacante.
    f"execute positioned ~-2.5 ~-1 ~-2.5 run tag @e[{MOB},dx=4,dy=3,dz=4,tag=!astral.src,tag=!astral.atk] add astral.tgt",
    f"execute rotated as @e[tag=astral.atk,limit=1] rotated ~ 0 positioned ^ ^ ^3 positioned ~-2 ~-1 ~-2 run tag @e[{MOB},dx=3,dy=3,dz=3,tag=!astral.src,tag=!astral.atk] add astral.tgt",
    "tag @e[tag=astral.tgt] add astral.nohit",
    "scoreboard players set #ht astral.tmp 0",
    "scoreboard players operation #ht astral.tmp = @e[tag=astral.atk,limit=1] astral.ht",
    *[f"execute if score #ht astral.tmp matches {t} as @e[tag=astral.tgt] at @s run damage @s {round(5 * FACTOR_ARMA[t], 2)} minecraft:player_attack by @e[tag=astral.atk,limit=1]"
      for t in range(0, TIER_MAX + 1)],
    "particle minecraft:sweep_attack ~ ~1 ~ 1 0.2 1 0 5",
    "tag @e[tag=astral.tgt] remove astral.nohit",
    "tag @e[tag=astral.tgt] remove astral.tgt",
    "tag @e[tag=astral.atk] remove astral.atk",
    "tag @s remove astral.src",
])
fn("fx/cone", [
    "tag @s add astral.src",
    "execute on attacker run tag @s add astral.atk",
    f"execute as @e[tag=astral.atk,limit=1] at @s anchored eyes positioned ^ ^-0.6 ^2 run tag @e[{MOB},distance=..2,tag=!astral.src,tag=!astral.atk] add astral.tgt",
    f"execute as @e[tag=astral.atk,limit=1] at @s anchored eyes positioned ^ ^-0.6 ^3.5 run tag @e[{MOB},distance=..1.8,tag=!astral.src,tag=!astral.atk] add astral.tgt",
    "execute as @e[tag=astral.atk,limit=1] at @s anchored eyes positioned ^ ^-0.4 ^2 run particle minecraft:sweep_attack ~ ~ ~ 0.8 0.2 0.8 0 4",
    "tag @e[tag=astral.tgt] add astral.nohit",
    "scoreboard players set #ht astral.tmp 0",
    "scoreboard players operation #ht astral.tmp = @e[tag=astral.atk,limit=1] astral.ht",
    *[f"execute if score #ht astral.tmp matches {t} as @e[tag=astral.tgt] at @s run damage @s {round(4 * FACTOR_ARMA[t], 2)} minecraft:player_attack by @e[tag=astral.atk,limit=1]"
      for t in range(0, TIER_MAX + 1)],
    "tag @e[tag=astral.tgt] remove astral.nohit",
    "tag @e[tag=astral.tgt] remove astral.tgt",
    "tag @e[tag=astral.atk] remove astral.atk",
    "tag @s remove astral.src",
])


# ---------------------------------------------------------------------------
# Hechizos de baston
# ---------------------------------------------------------------------------
cast = [
    "execute if score @s astral.cd matches 1.. run return run title @s actionbar " +
    json.dumps(txt("El hechizo se esta recargando...", "gray")),
    "scoreboard players set #base astral.tmp 0",
    "scoreboard players set #pct astral.tmp 10000",
    "scoreboard players set #cd astral.tmp 20",
    "scoreboard players set #cdr astral.tmp 0",
]
from escala import COLOR_TIER as _CT
cast.append(f'data modify storage {NS}:tmp spell.fxh set value "c070ff"')
cast.append(f'data modify storage {NS}:tmp spell.fxc set value "[0.75,0.44,1.0]"')
cast.append(f'data modify storage {NS}:tmp spell.fxe set value "arcano"')
cast.append(f'data modify storage {NS}:tmp spell.fxp set value "witch"')
for i, s in enumerate(STAFFS):
    t = i + 1
    sel = f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"baston_{t}"}}}}]'
    from efectos import COLOR_BASTON as _CB
    _h = _CB[t].lstrip('#')
    _rgb = ','.join(f"{int(_h[k:k + 2], 16) / 255:.2f}" for k in (0, 2, 4))
    cast.append(f'{sel} run data modify storage {NS}:tmp spell.fxh set value "{_h}"')
    cast.append(f'{sel} run data modify storage {NS}:tmp spell.fxc set value "[{_rgb}]"')
    from efectos import ELEM_BASTON as _EB
    cast.append(f'{sel} run data modify storage {NS}:tmp spell.fxe set value "{_EB[t][0]}"')
    cast.append(f'{sel} run data modify storage {NS}:tmp spell.fxp set value "{_EB[t][1]}"')
    cast.append(f"{sel} run scoreboard players set #base astral.tmp {HECHIZO[t]}")
    cast.append(f"{sel} run scoreboard players add #pct astral.tmp {s['mdmg'] * 100}")
    cast.append(f"{sel} run scoreboard players set #cd astral.tmp {s['cd']}")
    if s.get("cdr"):
        cast.append(f"{sel} run scoreboard players add #cdr astral.tmp {s['cdr']}")
    if s.get("pierce"):
        cast.append(f"{sel} run scoreboard players add #pct astral.tmp {s['pierce'] * 100}")
sl = {"helmet": "armor.head", "chestplate": "armor.chest", "leggings": "armor.legs", "boots": "armor.feet"}
for ti, tier in enumerate(ARMOR_SETS["mago"]["tiers"]):
    st = tier["stats"]
    for piece in PIECES:
        sel = f'execute if items entity @s {sl[piece]} *[minecraft:custom_data~{{{NS}:{{id:"mago_{ti + 1}_{piece}"}}}}]'
        if "mdmg" in st:
            cast.append(f"{sel} run scoreboard players add #pct astral.tmp {int(round(st['mdmg'] * 100 / 4))}")
        if "cdr" in st:
            cast.append(f"{sel} run scoreboard players add #cdr astral.tmp {int(round(st['cdr'] / 4))}")
# Mejora del Herrero en el baston: mismo % que el dano de un arma (MEJORA_DANO).
cast.append("scoreboard players set #mej astral.tmp 100")
for _lvl, _f in enumerate(MEJORA_DANO, 1):
    cast.append(f'execute if items entity @s weapon.mainhand *[minecraft:enchantments~[{{enchantments:"{NS}:mejora_arma",levels:{_lvl}}}]] '
                f"run scoreboard players set #mej astral.tmp {round(_f * 100)}")
cast += [
    "execute if score #base astral.tmp matches ..0 run return 0",
    # Tiers 7-10: el hechizo pasa el millon; se calcula en miles para no pasar el tope del scoreboard.
    "scoreboard players set #sk astral.tmp 1",
    "execute if score #base astral.tmp matches 1000000.. run scoreboard players set #sk astral.tmp 1000",
    "scoreboard players operation #base astral.tmp /= #sk astral.tmp",
    "scoreboard players operation #base astral.tmp *= #mej astral.tmp",
    "scoreboard players operation #base astral.tmp /= #100 astral.const",
    # #base en puntos de vida enteros (hasta 75.000) y #pct en centesimas de %: se pasa #pct a %
    # antes de multiplicar para no pasar el limite de los numeros del scoreboard.
    "scoreboard players operation #pct astral.tmp /= #100 astral.const",
    "scoreboard players operation #base astral.tmp *= #pct astral.tmp",
    "scoreboard players operation #base astral.tmp /= #100 astral.const",
    f"execute if score #sk astral.tmp matches 1 store result storage {NS}:tmp spell.dmg float 1 run scoreboard players get #base astral.tmp",
    f"execute if score #sk astral.tmp matches 1000 store result storage {NS}:tmp spell.dmg float 1000 run scoreboard players get #base astral.tmp",
    "scoreboard players operation #cdr astral.tmp *= #cd astral.tmp",
    "scoreboard players operation #cdr astral.tmp /= #100 astral.const",
    "scoreboard players operation #cd astral.tmp -= #cdr astral.tmp",
    "scoreboard players operation @s astral.cd = #cd astral.tmp",
    "tag @s add astral.caster",
    "scoreboard players set #steps astral.tmp 0",
    "playsound minecraft:entity.evoker.cast_spell player @a[distance=..16] ~ ~ ~ 0.8 1.6",
    # Medio/Alto: el plugin AstralEfectos dibuja el rayo laser o la bola de fuego (marcador fx.rayo frente a los ojos).
    f"execute anchored eyes positioned ^ ^ ^0.8 run function {NS}:spell/fx_rayo with storage {NS}:tmp spell",
    f"execute anchored eyes positioned ^ ^ ^0.8 run function {NS}:spell/trace with storage {NS}:tmp spell",
    "tag @s remove astral.caster",
]
fn("spell/cast", cast)
fn("spell/trace", [
    'summon minecraft:marker ~ ~ ~ {Tags:["astral.spell.trace"]}',
    'kill @e[type=minecraft:marker,tag=astral.spell.trace,distance=0..]',
    f"execute as @e[tag=astral.spell.model,distance=0..,limit=1] run return run function {NS}:spell/hit with storage {NS}:tmp spell",
    f"function {NS}:spell/ray with storage {NS}:tmp spell",
])
from minijuegos import arena_worlds as _arena_worlds
ARENA_WORLDS = _arena_worlds()
# Efectos (16/11/2026): Bajo ve lo de siempre (witch + end_rod). En Medio y Alto el plugin AstralEfectos dibuja el
# rayo laser / bola de fuego (marcador fx.rayo al lanzar) y la explosion del impacto (marcador fx.estallido).
FX_MEDIO = "@a[scores={astral.fx=1..,astral.fx.bastones=1..},distance=..96]"
FX_ALTO = "@a[scores={astral.fx=2..,astral.fx.bastones=1..},distance=..96]"
FX_IMPACTO = ("$execute if entity " + FX_MEDIO + " run summon marker ~ ~ ~ "
              "{Tags:[\"astral.fx\",\"fx.estallido\",\"fxc.$(fxh)\",\"fxe.$(fxe)\"]}")
fn("spell/fx_rayo", [
    "$execute if entity " + FX_MEDIO + " run summon marker ~ ~ ~ "
    "{Tags:[\"astral.fx\",\"fx.rayo\",\"fxc.$(fxh)\",\"fxe.$(fxe)\"]}",
])
fn("spell/ray", [
    "particle minecraft:witch ~ ~ ~ 0.05 0.05 0.05 0 2 force",
    "particle minecraft:end_rod ~ ~ ~ 0 0 0 0 1 force",
    # particula del elemento del baston (fuego, hielo, arcano...) acompanando al rayo del plugin
    f"$particle minecraft:$(fxp) ~ ~ ~ 0.08 0.08 0.08 0.01 1 force {FX_MEDIO}",
    f"$particle minecraft:$(fxp) ~ ~ ~ 0.18 0.18 0.18 0.02 1 force {FX_ALTO}",
    # nbt=!{NoAI:1b}: los NPC de MythicMobs (vendedores, gachas) estan quietos y no se pueden lastimar.
    # dx/dy/dz intersectan la caja, distance solo mide al origen (los pies).
    # dx=0 es un cubo de UN bloque en Java; centrado da tolerancia .5 sin huecos.
    f"execute positioned ~-0.5 ~-0.5 ~-0.5 as @e[{MOB},dx=0,dy=0,dz=0,tag=!astral.caster,nbt=!{{NoAI:1b}},limit=1,sort=nearest] run return run function {NS}:spell/hit with storage {NS}:tmp spell",
    # Arenas PvP: el hechizo tambien pega a jugadores en survival/aventura (pedido 12/11/2026).
    *[f"execute if dimension minecraft:{w} positioned ~-0.5 ~-0.5 ~-0.5 as @a[gamemode=!creative,gamemode=!spectator,dx=0,dy=0,dz=0,tag=!astral.caster,limit=1,sort=nearest] run return run function {NS}:spell/hit with storage {NS}:tmp spell"
      for w in ARENA_WORLDS],
    f"execute unless block ~ ~ ~ #{NS}:passable run return run function {NS}:spell/pared with storage {NS}:tmp spell",
    "scoreboard players add #steps astral.tmp 1",
    "execute if score #steps astral.tmp matches 50.. run return 0",
    f"execute positioned ^ ^ ^0.5 run function {NS}:spell/ray with storage {NS}:tmp spell",
])
fn("spell/pared", [
    "particle minecraft:large_smoke ~ ~ ~ 0.1 0.1 0.1 0.01 6",
    FX_IMPACTO,
])
fn("spell/hit", [
    "$damage @s $(dmg) minecraft:magic by @a[tag=astral.caster,limit=1]",
    FX_IMPACTO.replace("summon marker ~ ~ ~", "summon marker ~ ~1 ~"),
    "particle minecraft:dragon_breath ~ ~1 ~ 0.3 0.4 0.3 0.02 25",
    "playsound minecraft:entity.illusioner.cast_spell player @a[distance=..16] ~ ~ ~ 0.7 1.8",
    "return 1",
])

# ---------------------------------------------------------------------------
from tanda_xp import register as register_xp
register_xp(add_item, txt)

# Gancho de escalada
# ---------------------------------------------------------------------------
fn("grapple/use", [
    "execute if score @s astral.grap matches 1.. run return run scoreboard players set @s astral.grap 1",
    "scoreboard players set #steps astral.tmp 0",
    f"execute anchored eyes positioned ^ ^ ^1 run function {NS}:grapple/ray",
    "execute if score #steps astral.tmp matches ..0 run return run title @s actionbar " +
    json.dumps(txt("No hay nada donde engancharse", "gray")),
    "scoreboard players operation @s astral.grap = #steps astral.tmp",
    "scoreboard players operation @s astral.grap /= #3 astral.const",
    "scoreboard players add @s astral.grap 6",
    "execute if score @s astral.grap matches 30.. run scoreboard players set @s astral.grap 30",
    "playsound minecraft:entity.fishing_bobber.throw player @a[distance=..16] ~ ~ ~ 1 0.6",
])
fn("grapple/ray", [
    f"execute unless block ~ ~ ~ #{NS}:passable run return run particle minecraft:crit ~ ~ ~ 0.2 0.2 0.2 0.1 12",
    "scoreboard players add #steps astral.tmp 1",
    "particle minecraft:crit ~ ~ ~ 0 0 0 0 1",
    "execute if score #steps astral.tmp matches 64.. run return run scoreboard players set #steps astral.tmp 0",
    f"execute positioned ^ ^ ^0.5 run function {NS}:grapple/ray",
])
fn("grapple/tick", [
    "scoreboard players remove @s astral.grap 1",
    f"execute if entity @s[predicate={NS}:sneaking] run scoreboard players set @s astral.grap 0",
    f'execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"gancho"}}}}] run scoreboard players set @s astral.grap 0',
    "execute if score @s astral.grap matches ..0 run effect give @s minecraft:slow_falling 2 0 true",
    "execute if score @s astral.grap matches ..0 run scoreboard players reset @s astral.grap",
])

# ---------------------------------------------------------------------------
# Arcos: carga rapida (normaliza la velocidad de la flecha)
# t = 1 - reduccion ; potencia f = (t^2 + 2t) / 3 ; velocidad minima = 3f
# ---------------------------------------------------------------------------
def thr2(red):
    red = min(red, 97)
    t = 1 - red / 100
    f = (t * t + 2 * t) / 3
    v = 3 * f * 100  # en centesimas
    return int(v * v)


# #flechas avisa al tick que hay flechas nuevas: sin eso no recorre todas las entidades cada tick (24/11).
fn("bow/tag", ["tag @s add astral.bowshot", "scoreboard players set #flechas astral.tmp 1"])
bow = [
    "tag @s remove astral.bowshot",
    "execute on origin run tag @s add astral.shooter",
    "scoreboard players set #red astral.tmp -1",
]
for i, b in enumerate(BOWS):
    for slot in ("weapon.mainhand", "weapon.offhand"):
        bow.append(f'execute if entity @a[tag=astral.shooter,limit=1] as @a[tag=astral.shooter,limit=1] if items entity @s {slot} '
                   f'*[minecraft:custom_data~{{{NS}:{{id:"arco_{i + 1}"}}}}] run scoreboard players set #red astral.tmp {b["draw"]}')
for ti, tier in enumerate(ARMOR_SETS["arquero"]["tiers"]):
    d = tier["stats"].get("draw")
    if d:
        bow.append(f'execute as @a[tag=astral.shooter,limit=1] if items entity @s armor.chest '
                   f'*[minecraft:custom_data~{{{NS}:{{id:"arquero_{ti + 1}_chestplate"}}}}] '
                   f'if score #red astral.tmp matches 0.. run scoreboard players add #red astral.tmp {d}')
bow.append("execute if score #red astral.tmp matches ..-1 run return run tag @a remove astral.shooter")
for red in range(0, 200, 5):
    lo = red
    hi = red + 4
    bow.append(f"execute if score #red astral.tmp matches {lo}..{hi} run scoreboard players set #thr astral.tmp {thr2(red)}")
bow += [
    "execute store result score #x astral.tmp run data get entity @s Motion[0] 100",
    "execute store result score #y astral.tmp run data get entity @s Motion[1] 100",
    "execute store result score #z astral.tmp run data get entity @s Motion[2] 100",
    "scoreboard players operation #x astral.tmp *= #x astral.tmp",
    "scoreboard players operation #y astral.tmp *= #y astral.tmp",
    "scoreboard players operation #z astral.tmp *= #z astral.tmp",
    "scoreboard players operation #x astral.tmp += #y astral.tmp",
    "scoreboard players operation #x astral.tmp += #z astral.tmp",
    f"execute if score #x astral.tmp >= #thr astral.tmp at @s rotated as @a[tag=astral.shooter,limit=1] summon minecraft:marker run function {NS}:bow/vec",
    "tag @a remove astral.shooter",
]
fn("bow/norm", bow)
fn("bow/vec", [
    "execute store result score #ox astral.tmp run data get entity @s Pos[0] 1000",
    "execute store result score #oy astral.tmp run data get entity @s Pos[1] 1000",
    "execute store result score #oz astral.tmp run data get entity @s Pos[2] 1000",
    "tp @s ^ ^ ^3",
    "execute store result score #nx astral.tmp run data get entity @s Pos[0] 1000",
    "execute store result score #ny astral.tmp run data get entity @s Pos[1] 1000",
    "execute store result score #nz astral.tmp run data get entity @s Pos[2] 1000",
    "scoreboard players operation #nx astral.tmp -= #ox astral.tmp",
    "scoreboard players operation #ny astral.tmp -= #oy astral.tmp",
    "scoreboard players operation #nz astral.tmp -= #oz astral.tmp",
    "kill @s",
    "execute as @e[type=#minecraft:arrows,distance=..0.5,limit=1,sort=nearest] run function astral:bow/apply",
])
fn("bow/apply", [
    "execute store result entity @s Motion[0] double 0.001 run scoreboard players get #nx astral.tmp",
    "execute store result entity @s Motion[1] double 0.001 run scoreboard players get #ny astral.tmp",
    "execute store result entity @s Motion[2] double 0.001 run scoreboard players get #nz astral.tmp",
    "data modify entity @s crit set value 1b",
])

# ---------------------------------------------------------------------------
# Arcos: disparo automatico al mantener click derecho.
# Cada tier dispara una flecha a maxima potencia cada N ticks (vanilla = 20).
# ---------------------------------------------------------------------------
BOW_TICKS = ARCO_AUTO   # 23/11: los 10 tiers (antes solo I-V; VI-X tiraban cada 20 ticks)
put(f"data/{NS}/advancement/bow/hold.json", {
    "criteria": {"hold": {"trigger": "minecraft:using_item", "conditions": {"item": {
        "items": "minecraft:bow", "predicates": {"minecraft:custom_data": f"{{{NS}:{{w:\"bow\"}}}}"}}}}},
    "rewards": {"function": f"{NS}:bow/hold"}})
hold = [f"advancement revoke @s only {NS}:bow/hold",
        "tag @s add astral.drew",
        "scoreboard players add @s astral.draw 1",
        "scoreboard players set #need astral.tmp 20"]
for i, n in enumerate(BOW_TICKS):
    hold.append(f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"arco_{i + 1}"}}}}] '
                f'run scoreboard players set #need astral.tmp {n}')
for ti, tier in enumerate(ARMOR_SETS["arquero"]["tiers"]):
    d = tier["stats"].get("draw")
    if d:
        hold.append(f'execute if items entity @s armor.chest *[minecraft:custom_data~{{{NS}:{{id:"arquero_{ti + 1}_chestplate"}}}}] '
                    f'run scoreboard players remove #need astral.tmp {d // 20}')
hold += ["execute if score #need astral.tmp matches ..2 run scoreboard players set #need astral.tmp 3",
         "execute if score @s astral.draw < #need astral.tmp run return 0",
         "scoreboard players set @s astral.draw 0",
         f"function {NS}:bow/fire"]
fn("bow/hold", hold)
fn("bow/fire", [
    "# necesita flechas (salvo creativo o Arco Astral)",
    "scoreboard players set #free astral.tmp 0",
    "execute if entity @s[gamemode=creative] run scoreboard players set #free astral.tmp 1",
    *[f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"arco_{t}"}}}}] run scoreboard players set #free astral.tmp 1'
      for t in range(5, len(ARCO_AUTO) + 1)],
    "execute if score #free astral.tmp matches 0 unless items entity @s container.* minecraft:arrow unless items entity @s weapon.offhand minecraft:arrow run return 0",
    "execute if score #free astral.tmp matches 0 run clear @s minecraft:arrow 1",
    "tag @s add astral.archer",
    f"execute anchored eyes positioned ^ ^ ^0.6 summon minecraft:arrow run function {NS}:bow/setup",
    "tag @s remove astral.archer",
    "playsound minecraft:entity.arrow.shoot player @a[distance=..16] ~ ~ ~ 1 1.2",
])
fn("bow/setup", [
    "tag @s add astral.newarrow",
    "data modify entity @s Owner set from entity @a[tag=astral.archer,limit=1] UUID",
    "data modify entity @s crit set value 1b",
    "data modify entity @s damage set value 2.0d",
    # 23/11: el arco viaja con la flecha: asi aplica Punteria del tier (sin esto pegaba como flecha vanilla).
    "data modify entity @s weapon set from entity @a[tag=astral.archer,limit=1] SelectedItem",
    "execute if score #free astral.tmp matches 1 run data modify entity @s pickup set value 2b",
    "execute if score #free astral.tmp matches 0 run data modify entity @s pickup set value 1b",
    f"execute summon minecraft:marker run function {NS}:bow/vec2",
    "tag @s remove astral.newarrow",
])
fn("bow/vec2", [
    "execute store result score #ox astral.tmp run data get entity @s Pos[0] 1000",
    "execute store result score #oy astral.tmp run data get entity @s Pos[1] 1000",
    "execute store result score #oz astral.tmp run data get entity @s Pos[2] 1000",
    "tp @s ^ ^ ^3",
    "execute store result score #nx astral.tmp run data get entity @s Pos[0] 1000",
    "execute store result score #ny astral.tmp run data get entity @s Pos[1] 1000",
    "execute store result score #nz astral.tmp run data get entity @s Pos[2] 1000",
    "scoreboard players operation #nx astral.tmp -= #ox astral.tmp",
    "scoreboard players operation #ny astral.tmp -= #oy astral.tmp",
    "scoreboard players operation #nz astral.tmp -= #oz astral.tmp",
    "kill @s",
    f"execute as @e[type=minecraft:arrow,tag=astral.newarrow,limit=1] run function {NS}:bow/apply",
])

# ---------------------------------------------------------------------------
# Uso de items con click derecho (zanahoria con palo como base)
# ---------------------------------------------------------------------------
fn("use/main", [
    "scoreboard players reset @s astral.use",
    # Bastones: el clic lo maneja Skript (special_weapons.sk), que cobra el mana y llama a spell/cast.
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{type:"hook"}}}}] run return run function {NS}:grapple/use',
])

# ---------------------------------------------------------------------------
# Drops de mobs (advancement al matar)
# ---------------------------------------------------------------------------
for group, (mobs, drops) in MOB_DROPS.items():
    put(f"data/{NS}/advancement/kill/{group}.json", {
        "criteria": {"kill": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": [
            {"condition": "minecraft:entity_properties", "entity": "this",
             "predicate": {"type": mobs if len(mobs) > 1 else mobs[0]}}]}}},
        "rewards": {"function": f"{NS}:drop/{group}"}})
    lines = [f"advancement revoke @s only {NS}:kill/{group}"]
    for (mat, p, cond) in drops:
        pre = "execute "
        if cond == "end":
            pre += "if dimension minecraft:the_end "
        name = MATERIALS[mat][0]
        lines.append(f"{pre}if predicate {chance(p)} run function {NS}:drop/give {{id:\"{mat}\",name:\"{name}\"}}")
    fn(f"drop/{group}", lines)
fn("drop/give", [
    f"$loot give @s loot {NS}:item/$(id)",
    "$title @s actionbar " + json.dumps([txt("Conseguiste: ", "gray"), txt("$(name)", "light_purple")]),
    "playsound minecraft:entity.experience_orb.pickup player @s ~ ~ ~ 0.6 0.7",
    # Topacio engarzado (gemas.py): chance de duplicar el drop.
    GEMAS.SUERTE_HOOK,
])
# Cualquier muerte: guadanas que reinician el enfriamiento
put(f"data/{NS}/advancement/kill/any.json", {
    "criteria": {"kill": {"trigger": "minecraft:player_killed_entity"}},
    "rewards": {"function": f"{NS}:drop/any"}})
fn("drop/any", [
    f"advancement revoke @s only {NS}:kill/any",
    f"execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{reset_cd:1}}}}] run scoreboard players set @s astral.cd 0",
])

# Gemas Luminicas en cofres del Overworld
chests = []
with open(os.path.join(HERE, "dnt_chests.txt"), encoding="utf-8") as f:
    chests += [l.strip() for l in f if l.strip()]
chests += ["minecraft:" + c for c in [
    "chests/abandoned_mineshaft", "chests/ancient_city", "chests/buried_treasure", "chests/desert_pyramid",
    "chests/igloo_chest", "chests/jungle_temple", "chests/pillager_outpost", "chests/ruined_portal",
    "chests/shipwreck_supply", "chests/shipwreck_treasure", "chests/simple_dungeon", "chests/stronghold_corridor",
    "chests/stronghold_crossing", "chests/stronghold_library", "chests/woodland_mansion",
    "chests/underwater_ruin_big", "chests/underwater_ruin_small", "chests/trial_chambers/corridor",
    "chests/trial_chambers/supply", "chests/trial_chambers/intersection"]]
put(f"data/{NS}/advancement/loot/chest.json", {
    "criteria": {f"c{i}": {"trigger": "minecraft:player_generates_container_loot", "conditions": {"loot_table": c}}
                 for i, c in enumerate(chests)},
    "requirements": [[f"c{i}" for i in range(len(chests))]],
    "rewards": {"function": f"{NS}:drop/chest"}})
fn("drop/chest", [
    f"advancement revoke @s only {NS}:loot/chest",
    f"execute if dimension minecraft:overworld if predicate {chance(0.25)} run function {NS}:drop/give {{id:\"gema_luminica\",name:\"Gema Luminica\"}}",
])

# Mineria / tala en el End
LOGS = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak"]
log_objs = []
for l in LOGS:
    for v in (f"{l}_log", f"stripped_{l}_log", f"{l}_wood", f"stripped_{l}_wood"):
        log_objs.append((f"astral.m_{v}", f"minecraft.mined:minecraft.{v}"))
# 23/11: lo que el jugador pone en el End no cuenta (poner y romper el mismo bloque era una granja infinita).
# astral.p_* = bloques colocados (stat used); en el End suman a la "deuda" astral.dlog / astral.des.
place_objs = [(f"astral.p_{v}", f"minecraft.used:minecraft.{v}", "astral.dlog") for (_o, c) in log_objs
              for v in [c.split(".")[-1]]] + [("astral.p_es", "minecraft.used:minecraft.end_stone", "astral.des")]
fn("mine/placed", [f"execute if dimension minecraft:the_end run scoreboard players operation @s {d} += @s {o}" for (o, _c, d) in place_objs]
   + [f"scoreboard players reset @s {o}" for (o, _c, _d) in place_objs])
fn("mine/endstone", [
    "scoreboard players reset @s astral.m_es",
    "execute if score @s astral.des matches 1.. run return run scoreboard players remove @s astral.des 1",
    f"execute if dimension minecraft:the_end if entity @s[y=-64,dy=114] if predicate {chance(0.04)} run function {NS}:drop/give {{id:\"fragmento_cristal\",name:\"Fragmento de Cristal Arcano\"}}",
])
fn("mine/chorus", [
    "scoreboard players reset @s astral.m_ch",
    f"execute if dimension minecraft:the_end if predicate {chance(0.08)} run function {NS}:drop/give {{id:\"madera_estelar\",name:\"Madera Estelar\"}}",
])
fn("mine/log", [f"scoreboard players reset @s {o}" for (o, _) in log_objs] + [
    "execute if score @s astral.dlog matches 1.. run return run scoreboard players remove @s astral.dlog 1",
    f"execute if dimension minecraft:the_end if predicate {chance(0.35)} run function {NS}:drop/give {{id:\"madera_estelar\",name:\"Madera Estelar\"}}",
])

# ---------------------------------------------------------------------------
# DIFICULTAD PROGRESIVA: mobs elite
# ---------------------------------------------------------------------------
put(f"data/{NS}/tags/entity_type/hostile.json", {"values": HOSTILE})

# Nivel de equipo del jugador (0-5): el mejor tier Astral que lleva puesto o en la mano (sin taladros ni motosierras)
lvl = ["scoreboard players set @s astral.lvl 0"]
for t in range(1, TIER_MAX + 1):
    for slot in ("armor.head", "armor.chest", "armor.legs", "armor.feet", "weapon.mainhand", "weapon.offhand"):
        lvl.append(f"execute if score @s astral.lvl matches ..{t - 1} if items entity @s {slot} "
                   f"*[minecraft:custom_data~{{{NS}:{{tier:{t}}}}},!minecraft:custom_data~{{{NS}:{{type:\"tool\"}}}}] "
                   f"run scoreboard players set @s astral.lvl {t}")
# Escala por tier (escala.py):
#   astral.ht = tier del arma en la mano; astral.wt = mejor arma Astral del inventario
#   (los mobs se adaptan a esta); astral.at = mejor armadura puesta (vida mostrada).
ARMA_TIER = lambda t: (f"*[minecraft:custom_data~{{{NS}:{{type:\"weapon\",tier:{t}}}}}]",
                       f"*[minecraft:custom_data~{{{NS}:{{type:\"staff\",tier:{t}}}}}]")
lvl += ["scoreboard players set @s astral.ht 0", "scoreboard players set @s astral.wt 0",
        "scoreboard players set @s astral.at 0"]
for t in range(1, TIER_MAX + 1):
    for sel in ARMA_TIER(t):
        lvl.append(f"execute if items entity @s weapon.mainhand {sel} run scoreboard players set @s astral.ht {t}")
        for slot in ("container.*", "weapon.offhand"):
            lvl.append(f"execute if score @s astral.wt matches ..{t - 1} if items entity @s {slot} {sel} "
                       f"run scoreboard players set @s astral.wt {t}")
    # Pedido 12/11/2026: los mobs del mundo se adaptan al MEJOR tier del inventario (armas, bastones,
    # armaduras y herramientas Astral, puestas o guardadas), no solo a las armas.
    # 25/11 (dueno): taladros y motosierras (type "tool") NO cuentan: un taladro T5 no sube el tier de los mobs.
    for kind in ("armor",):
        for slot in ("container.*", "armor.*", "weapon.offhand"):
            lvl.append(f"execute if score @s astral.wt matches ..{t - 1} if items entity @s {slot} "
                       f"*[minecraft:custom_data~{{{NS}:{{type:\"{kind}\",tier:{t}}}}}] run scoreboard players set @s astral.wt {t}")
    for slot in ("armor.head", "armor.chest", "armor.legs", "armor.feet"):
        lvl.append(f"execute if score @s astral.at matches ..{t - 1} if items entity @s {slot} "
                   f"*[minecraft:custom_data~{{{NS}:{{type:\"armor\",tier:{t}}}}}] run scoreboard players set @s astral.at {t}")
# Etiquetas para Skript (PvP en la arena divide el dano segun el arma del atacante)
lvl += [f"tag @s remove astral.ht{t}" for t in range(TIER_MAX + 1)]
lvl += [f"execute if score @s astral.ht matches {t} run tag @s add astral.ht{t}" for t in range(TIER_MAX + 1)]
fn("player/lvl", lvl)
# Defensa (escala.DEFENSA_SET): suma astral.def de las 4 piezas puestas. astraldef = lo que muestra la barra
# (Defensa Astral + armadura vanilla x5); las etiquetas astral.db0..db11 son la Defensa Astral en binario
# para que Skript calcule la reduccion de dano (Skript no lee puntajes).
fn("player/def", [
    "scoreboard players set #d astral.tmp 0",
    f"data modify storage {NS}:tmp eq set value {{}}",
    f"data modify storage {NS}:tmp eq set from entity @s equipment",
    "scoreboard players set #cien astral.tmp 100",
    # #pub astral.protdef: 1 = todos, 0 (por defecto) = solo ByTrainx, -1 = apagado.
    "execute if score #pub astral.protdef matches 1 run tag @s add astral.protdef",
    "execute if score #pub astral.protdef matches 0 if entity @s[name=ByTrainx] run tag @s add astral.protdef",
    "execute if score #pub astral.protdef matches -1 run tag @s remove astral.protdef",
    # #pub astral.filo: lo mismo para el Filo en porcentaje (escala.FILO_PCT).
    "execute if score #pub astral.filo matches 1 run tag @s add astral.filo",
    "execute if score #pub astral.filo matches 0 if entity @s[name=ByTrainx] run tag @s add astral.filo",
    "execute if score #pub astral.filo matches 0 unless entity @s[name=ByTrainx] run tag @s remove astral.filo",
    "execute if score #pub astral.filo matches -1 run tag @s remove astral.filo",
] + [f'execute store result score #p astral.tmp run data get storage {NS}:tmp eq.{slot}.components."minecraft:custom_data".astral.def\n'
     f"scoreboard players operation #d astral.tmp += #p astral.tmp\n"
     # Proteccion (escala.PROT_DEF_PCT): nivel x % de la Defensa de esta pieza, solo con astral.protdef.
     f"execute if entity @s[tag=astral.protdef] if score #p astral.tmp matches 1.. run function {NS}:player/def_prot_{slot}"
     for slot in ("head", "chest", "legs", "feet")] + [
    # Armadura vanilla como Defensa (escala.VANILLA_PIEZAS), solo piezas sin atributos propios ni astral.def.
    "execute if score #pub astral.vandef matches 1 run tag @s add astral.vandef",
    "execute if score #pub astral.vandef matches 0 if entity @s[name=ByTrainx] run tag @s add astral.vandef",
    "execute if score #pub astral.vandef matches -1 run tag @s remove astral.vandef",
    "scoreboard players set #vp astral.tmp 0",
] + [f'execute if entity @s[tag=astral.vandef] unless data storage {NS}:tmp eq.{slot}.components."minecraft:custom_data".astral.def '
     f'unless data storage {NS}:tmp eq.{slot}.components."minecraft:attribute_modifiers" run function {NS}:player/def_van_{slot}'
     for slot in ("head", "chest", "legs", "feet")] + [
    # Anula la reduccion de Minecraft de esos puntos (modificador negativo); solo se toca cuando cambia.
    f"execute unless score @s astral.vanp = #vp astral.tmp run function {NS}:player/def_van_mod",
    "execute store result score #v astral.tmp run attribute @s minecraft:armor get 5",
] + [f'execute if data storage {NS}:tmp eq.{slot}.components."minecraft:custom_data".astral.def '
     f'run scoreboard players remove #v astral.tmp {bar * 5}'
     # La barra de armadura de las piezas Astral (3/8/6/3) es solo visual: no se suma a la Defensa.
     for slot, bar in (("head", 3), ("chest", 8), ("legs", 6), ("feet", 3))] + [
    "scoreboard players set #pct astral.tmp 100",
    *[f'execute if items entity @s weapon.offhand *[minecraft:custom_data~{{astral:{{id:"talisman_roca_{lv}"}}}}] run scoreboard players set #pct astral.tmp {100+int(pct*100)}' for lv,pct in enumerate(__import__('balance_equipo').TALISMAN_PCT,1)],
    f'execute if items entity @s weapon.offhand *[minecraft:custom_data~{{astral:{{id:"eco_estrella"}}}}] run scoreboard players set #pct astral.tmp {100+round(__import__("historia_items").ECO_DEFENSA*100)}',
    "scoreboard players operation #d astral.tmp *= #pct astral.tmp",
    "scoreboard players set #base astral.tmp 100",
    "scoreboard players operation #d astral.tmp /= #base astral.tmp",
    # Roca tambien multiplica la barra visual: descontar ese extra, no contarlo como defensa real.
    "scoreboard players set #bar astral.tmp 0",
    *[f'execute if data storage {NS}:tmp eq.{slot}.components."minecraft:custom_data".astral.def run scoreboard players add #bar astral.tmp {bar*5}'
      for slot,bar in (("head",3),("chest",8),("legs",6),("feet",3))],
    "scoreboard players remove #pct astral.tmp 100",
    "scoreboard players operation #bar astral.tmp *= #pct astral.tmp",
    "scoreboard players operation #bar astral.tmp /= #base astral.tmp",
    "scoreboard players operation #v astral.tmp -= #bar astral.tmp",
    # Opalo engarzado (gemas.py): % de la Defensa de cada pieza, despues del Talisman de Roca.
    GEMAS.DEFENSA_HOOK,
    "scoreboard players operation @s astraldef = #d astral.tmp",
    "scoreboard players operation @s astraldef += #v astral.tmp",
    "execute if score @s astral.defp = #d astral.tmp run return 0",
    "scoreboard players operation @s astral.defp = #d astral.tmp",
    "tag @s remove astral.db0", "tag @s remove astral.db1", "tag @s remove astral.db2", "tag @s remove astral.db3",
    "tag @s remove astral.db4", "tag @s remove astral.db5", "tag @s remove astral.db6", "tag @s remove astral.db7",
    "tag @s remove astral.db8", "tag @s remove astral.db9", "tag @s remove astral.db10", "tag @s remove astral.db11",
] + ['execute if score #d astral.tmp matches 2048.. run tag @s add astral.db11', 'execute if score #d astral.tmp matches 2048.. run scoreboard players remove #d astral.tmp 2048', 'execute if score #d astral.tmp matches 1024.. run tag @s add astral.db10', 'execute if score #d astral.tmp matches 1024.. run scoreboard players remove #d astral.tmp 1024', 'execute if score #d astral.tmp matches 512.. run tag @s add astral.db9', 'execute if score #d astral.tmp matches 512.. run scoreboard players remove #d astral.tmp 512', 'execute if score #d astral.tmp matches 256.. run tag @s add astral.db8', 'execute if score #d astral.tmp matches 256.. run scoreboard players remove #d astral.tmp 256', 'execute if score #d astral.tmp matches 128.. run tag @s add astral.db7', 'execute if score #d astral.tmp matches 128.. run scoreboard players remove #d astral.tmp 128', 'execute if score #d astral.tmp matches 64.. run tag @s add astral.db6', 'execute if score #d astral.tmp matches 64.. run scoreboard players remove #d astral.tmp 64', 'execute if score #d astral.tmp matches 32.. run tag @s add astral.db5', 'execute if score #d astral.tmp matches 32.. run scoreboard players remove #d astral.tmp 32', 'execute if score #d astral.tmp matches 16.. run tag @s add astral.db4', 'execute if score #d astral.tmp matches 16.. run scoreboard players remove #d astral.tmp 16', 'execute if score #d astral.tmp matches 8.. run tag @s add astral.db3', 'execute if score #d astral.tmp matches 8.. run scoreboard players remove #d astral.tmp 8', 'execute if score #d astral.tmp matches 4.. run tag @s add astral.db2', 'execute if score #d astral.tmp matches 4.. run scoreboard players remove #d astral.tmp 4', 'execute if score #d astral.tmp matches 2.. run tag @s add astral.db1', 'execute if score #d astral.tmp matches 2.. run scoreboard players remove #d astral.tmp 2', 'execute if score #d astral.tmp matches 1.. run tag @s add astral.db0', 'execute if score #d astral.tmp matches 1.. run scoreboard players remove #d astral.tmp 1'])
from escala import PROT_DEF_PCT as _PROT
for _slot in ("head", "chest", "legs", "feet"):
    _lines = ["scoreboard players set #e astral.tmp 0"]
    for _ench, _pct in _PROT.items():
        _lines += [f'execute store result score #n astral.tmp run data get storage {NS}:tmp '
                   f'eq.{_slot}.components."minecraft:enchantments"."minecraft:{_ench}" {_pct}',
                   "scoreboard players operation #e astral.tmp += #n astral.tmp"]
    _lines += ["scoreboard players operation #e astral.tmp *= #p astral.tmp",
               "scoreboard players operation #e astral.tmp /= #cien astral.tmp",
               "scoreboard players operation #d astral.tmp += #e astral.tmp"]
    fn(f"player/def_prot_{_slot}", _lines)
from escala import VANILLA_PIEZAS as _VAN
_ARMOR_SLOT = {"head": "armor.head", "chest": "armor.chest", "legs": "armor.legs", "feet": "armor.feet"}
for _slot, _items in _VAN.items():
    _lines = ["scoreboard players set #p astral.tmp 0", "scoreboard players set #r astral.tmp 0"]
    for _item, _pts, _def in _items:
        _lines.append(f"execute if items entity @s {_ARMOR_SLOT[_slot]} {_item} run scoreboard players set #r astral.tmp {_pts}")
        _lines.append(f"execute if items entity @s {_ARMOR_SLOT[_slot]} {_item} run scoreboard players set #p astral.tmp {_def}")
    _lines += ["scoreboard players operation #d astral.tmp += #p astral.tmp",
               "scoreboard players operation #vp astral.tmp += #r astral.tmp",
               f"execute if entity @s[tag=astral.protdef] if score #p astral.tmp matches 1.. run function {NS}:player/def_prot_{_slot}"]
    fn(f"player/def_van_{_slot}", _lines)
fn("player/def_van_mod", [
    f"attribute @s minecraft:armor modifier remove {NS}:vanilla_def",
    "scoreboard players operation @s astral.vanp = #vp astral.tmp",
    f"execute if score #vp astral.tmp matches 1.. store result storage {NS}:tmp van.n int -1 run scoreboard players get #vp astral.tmp",
    f"execute if score #vp astral.tmp matches 1.. run function {NS}:player/def_van_mod2 with storage {NS}:tmp van",
])
fn("player/def_van_mod2", [f"$attribute @s minecraft:armor modifier add {NS}:vanilla_def $(n) add_value"])
fn("vandef/publico", ["scoreboard players set #pub astral.vandef 1",
                      'tellraw @s {"text":"Armadura vanilla como Defensa: ABIERTA a todos","color":"green"}'])
fn("vandef/privado", ["scoreboard players set #pub astral.vandef 0", "tag @a remove astral.vandef",
                      'tellraw @s {"text":"Armadura vanilla como Defensa: solo ByTrainx","color":"yellow"}'])
fn("vandef/apagar", ["scoreboard players set #pub astral.vandef -1", "tag @a remove astral.vandef",
                     'tellraw @s {"text":"Armadura vanilla como Defensa: APAGADA (reduccion de Minecraft)","color":"red"}'])
# Protecciones de Minecraft: mismo efecto que el original salvo para quien tiene astral.protdef (ahi da Defensa).
_SIN_PROTDEF = {"condition": "minecraft:inverted", "term": {"condition": "minecraft:entity_properties",
                "entity": "this", "predicate": {"nbt": '{Tags:["astral.protdef"]}'}}}
def _prot_vanilla(ench, base, tag, anvil, weight, min_c, max_c, attrs=None):
    tags = ([{"expected": True, "id": f"minecraft:{tag}"}] if tag else []) + \
           [{"expected": False, "id": "minecraft:bypasses_invulnerability"}]
    eff = {"minecraft:damage_protection": [{
        "effect": {"type": "minecraft:add", "value": {"type": "minecraft:linear", "base": base, "per_level_above_first": base}},
        "requirements": {"condition": "minecraft:all_of", "terms": [
            {"condition": "minecraft:damage_source_properties", "predicate": {"tags": tags}}, _SIN_PROTDEF]}}]}
    if attrs:
        eff["minecraft:attributes"] = [attrs]
    put(f"data/minecraft/enchantment/{ench}.json", {
        "anvil_cost": anvil, "description": {"translate": f"enchantment.minecraft.{ench}"}, "effects": eff,
        "exclusive_set": "#minecraft:exclusive_set/armor", "max_cost": {"base": max_c[0], "per_level_above_first": max_c[1]},
        "max_level": 4, "min_cost": {"base": min_c[0], "per_level_above_first": min_c[1]}, "slots": ["armor"],
        "supported_items": "#minecraft:enchantable/armor", "weight": weight})
_prot_vanilla("protection", 1.0, None, 1, 10, (1, 11), (12, 11))
_prot_vanilla("fire_protection", 2.0, "is_fire", 2, 5, (10, 8), (18, 8), {
    "amount": {"type": "minecraft:linear", "base": -0.15, "per_level_above_first": -0.15},
    "attribute": "minecraft:burning_time", "id": "minecraft:enchantment.fire_protection", "operation": "add_multiplied_base"})
_prot_vanilla("blast_protection", 2.0, "is_explosion", 4, 2, (5, 8), (13, 8), {
    "amount": {"type": "minecraft:linear", "base": 0.15, "per_level_above_first": 0.15},
    "attribute": "minecraft:explosion_knockback_resistance", "id": "minecraft:enchantment.blast_protection", "operation": "add_value"})
_prot_vanilla("projectile_protection", 2.0, "is_projectile", 2, 5, (3, 6), (9, 6))
# Filo de Minecraft (26/11): +FILO_PCT% por nivel para quien tiene astral.filo; el resto, el +1..+3 fijo original.
from escala import FILO_PCT
_CON_FILO = {"condition": "minecraft:entity_properties", "entity": "attacker", "predicate": {"nbt": '{Tags:["astral.filo"]}'}}
put("data/minecraft/enchantment/sharpness.json", {
    "anvil_cost": 1, "description": {"translate": "enchantment.minecraft.sharpness"},
    "effects": {"minecraft:damage": [
        {"effect": {"type": "minecraft:add", "value": {"type": "minecraft:linear", "base": 1.0, "per_level_above_first": 0.5}},
         "requirements": {"condition": "minecraft:inverted", "term": _CON_FILO}},
        {"effect": {"type": "minecraft:multiply", "factor": {"type": "minecraft:linear",
                    "base": 1 + FILO_PCT / 100, "per_level_above_first": FILO_PCT / 100}},
         "requirements": _CON_FILO}]},
    "exclusive_set": "#minecraft:exclusive_set/damage", "max_cost": {"base": 21, "per_level_above_first": 11},
    "max_level": 5, "min_cost": {"base": 1, "per_level_above_first": 11},
    "primary_items": "#minecraft:enchantable/melee_weapon", "slots": ["mainhand"],
    "supported_items": "#minecraft:enchantable/sharp_weapon", "weight": 10})
fn("filo/publico", ["scoreboard players set #pub astral.filo 1",
                    'tellraw @s {"text":"Filo en porcentaje: ABIERTO a todos (falta /astralmesa filo publico para la ficha)","color":"green"}'])
fn("filo/privado", ["scoreboard players set #pub astral.filo 0", "tag @a remove astral.filo",
                    'tellraw @s {"text":"Filo en porcentaje: solo ByTrainx","color":"yellow"}'])
fn("filo/apagar", ["scoreboard players set #pub astral.filo -1", "tag @a remove astral.filo",
                   'tellraw @s {"text":"Filo en porcentaje: APAGADO (Filo de Minecraft)","color":"red"}'])
# /function astral:protdef/publico abre la Proteccion-Defensa a todos; privado la deja solo en ByTrainx.
fn("protdef/publico", ["scoreboard players set #pub astral.protdef 1",
                       'tellraw @s {"text":"Proteccion como Defensa: ABIERTA a todos","color":"green"}'])
fn("protdef/privado", ["scoreboard players set #pub astral.protdef 0", "tag @a remove astral.protdef",
                       'tellraw @s {"text":"Proteccion como Defensa: solo ByTrainx","color":"yellow"}'])
fn("protdef/apagar", ["scoreboard players set #pub astral.protdef -1", "tag @a remove astral.protdef",
                      'tellraw @s {"text":"Proteccion como Defensa: APAGADA (Proteccion de Minecraft para todos)","color":"red"}'])
# Vida base estilo Hypixel (escala.VIDA_JUGADOR_BASE). La armadura suma VIDA_PIEZA por pieza.
fn("player/vida_base", [
    f"attribute @s minecraft:max_health base set {VIDA_JUGADOR_BASE}",
    f"tag @s add astral.vida{VIDA_JUGADOR_BASE}",
    "effect give @s minecraft:instant_health 1 6 true",
])

# ---------------------------------------------------------------------------
# Tier de cada mob nuevo (escala.py). Mundo: se adapta a la mejor arma del jugador
# mas cercano (4% uno mas en T1-T5, 10% desde T6; 10% uno menos). Mazmorras: tier fijo.
# Despues puede salir elite (en mazmorras con la mitad de chance).
# ---------------------------------------------------------------------------
from escala import (VIDA_MOB, DANO_MOB, TIER_MAZMORRA, EXTRA_VIDA_MAZMORRA, PROB_TIER_MAS,
                    PROB_TIER_MENOS, PROB_TIER_MAS_ALTO, TIER_PROB_ALTA,
                    COLOR_TIER, PROB_MAZ_MAS, PROB_MAZ_MENOS, VIDA_REF)
# Ademas de los hostiles vanilla: criaturas de MythicMobs con tipos neutrales.
put(f"data/{NS}/tags/entity_type/escalable.json",
    {"values": [f"#{NS}:hostile", "minecraft:iron_golem", "minecraft:vex"]})
from minijuegos import parkour_worlds as _minijuegos
mob_roll = [
    # Incendium (Nether) arma sus mobs en su propio tick (Headless Warrior, etc.): esperar a que termine
    # para que no pise el nombre con tier y vida.
    "execute if dimension minecraft:the_nether unless entity @s[tag=in.checked] run return 0",
    "tag @s add astral.seen",
    # Espiritus de Incendium: vex invisibles de 1 vida que son solo particulas; sin nombre ni tier.
    "execute if entity @s[type=minecraft:vex,tag=in.spirit] run return 0",
    "# mini juegos: sus criaturas son del mapa (oleadas, niveles): sin tier ni elite",
    *[f"execute if dimension minecraft:{w} run return 0" for w in _minijuegos()],
    "# mascotas, vendedores y cofres son invulnerables: no se tocan",
    "execute if data entity @s {Invulnerable:1b} run return 0",
    "# golems de aldea (sin nombre de MythicMobs): no se tocan",
    "execute if entity @s[type=minecraft:iron_golem] unless data entity @s CustomName run return 0",
    "scoreboard players set #mt astral.tmp 0",
    "scoreboard players set #dg astral.tmp 0",
]
for w, t in TIER_MAZMORRA.items():
    mob_roll.append(f"execute if dimension minecraft:{w} run scoreboard players set #mt astral.tmp {t}")
    mob_roll.append(f"execute if dimension minecraft:{w} run scoreboard players set #dg astral.tmp 1")
from escala import TIER_FIJO
for w, t in TIER_FIJO.items():  # Oceano Astral: tier fijo, sin depender del inventario (dg 2 = no es mazmorra)
    mob_roll.append(f"execute if dimension minecraft:{w} run scoreboard players set #mt astral.tmp {t}")
    mob_roll.append(f"execute if dimension minecraft:{w} run scoreboard players set #dg astral.tmp 2")
mob_roll.append(CAVERNAS.mob_roll_corazon())   # Corazon de las Cavernas: tier 5
mob_roll.extend(VACIO.mob_roll())                # Vacio Estelar: tier 7/8 lejos del centro
mob_roll += [
    f"execute if entity @s[tag=ad.vanilla] run function {NS}:mob/tier_mazmorra",
    f"execute if score #dg astral.tmp matches 0 if entity @a[distance=..128,gamemode=!spectator] run function {NS}:mob/tier_mundo",
    # 23/11 (dueno): minimo tier 1 en todas las dimensiones (estructuras de datapacks, spawners, jugadores sin arma Astral).
    "execute if score #mt astral.tmp matches ..0 run scoreboard players set #mt astral.tmp 1",
] + [f"execute if score #mt astral.tmp matches {t} run function {NS}:mob/t{t}" for t in range(1, TIER_MAX + 1)] + [
    f"execute if score #dg astral.tmp matches 1 run function {NS}:mob/extra_mazmorra",
    *__import__("manzanas").mob_roll_tag(None),  # astral.maz: caen Manzanas de Mazmorra
    "scoreboard players operation @s astral.mt = #mt astral.tmp",
    f"function {NS}:mob/elite_chance",
    "data modify entity @s Health set value 1.0E30f",
    f"function {NS}:mob/nombre",
]
fn("mob/roll", mob_roll)
fn("mob/tier_mundo", [
    "scoreboard players operation #mt astral.tmp = @p[distance=..128,gamemode=!spectator] astral.wt",
    "execute if score #mt astral.tmp matches 0 run return 0",
    "execute store result score #r astral.tmp run random value 1..100",
    # Elegir rama ANTES de modificar #mt; return impide cruzar de T6 a la rama baja.
    f"execute if score #mt astral.tmp matches {TIER_PROB_ALTA}.. run return run function {NS}:mob/tier_mundo_alto",
    f"execute if score #r astral.tmp matches ..{PROB_TIER_MAS} if score #mt astral.tmp matches ..{TIER_MAX - 1} run return run scoreboard players add #mt astral.tmp 1",
    f"execute if score #r astral.tmp matches {PROB_TIER_MAS + 1}..{PROB_TIER_MAS + PROB_TIER_MENOS} run scoreboard players remove #mt astral.tmp 1",
])
fn("mob/tier_mundo_alto", [
    f"execute if score #r astral.tmp matches ..{PROB_TIER_MAS_ALTO} if score #mt astral.tmp matches ..{TIER_MAX - 1} run return run scoreboard players add #mt astral.tmp 1",
    f"execute if score #r astral.tmp matches {PROB_TIER_MAS_ALTO + 1}..{PROB_TIER_MAS_ALTO + PROB_TIER_MENOS} run scoreboard players remove #mt astral.tmp 1",
])
fn('mob/tier_mazmorra', [
    'execute store result score #r astral.tmp run random value 1..100',
    f'execute if score #r astral.tmp matches ..{PROB_MAZ_MAS} if score #mt astral.tmp matches ..{TIER_MAX - 1} run return run scoreboard players add #mt astral.tmp 1',
    f'execute if score #r astral.tmp matches {PROB_MAZ_MAS+1}..{PROB_MAZ_MAS+PROB_MAZ_MENOS} if score #mt astral.tmp matches 2.. run scoreboard players remove #mt astral.tmp 1',
])
fn('mob/jefe_mundo', [
    'execute if entity @s[tag=ad.boss.scaled] run return 0',
    # Santuario conserva su balance: no adaptar Ancestrales de esa prueba.
    'execute if dimension minecraft:santuario run return 0',
    'execute if dimension minecraft:santuario_interstellar run return 0',
    *[f'execute if dimension minecraft:{w} run return 0' for w in __import__('instancias').copias('santuario_azeroth')],
    'scoreboard players set #mt astral.tmp 1',
    f'execute if entity @a[distance=..128,gamemode=!spectator] run function {NS}:mob/tier_mundo',
    'execute if score #mt astral.tmp matches ..0 run scoreboard players set #mt astral.tmp 1',
    *[f'execute if score #mt astral.tmp matches {t} run attribute @s minecraft:max_health base set {25*VIDA_REF[t]}' for t in range(1, TIER_MAX + 1)],
    'data modify entity @s Health set value 1.0E30f',
    'scoreboard players operation @s astral.mt = #mt astral.tmp',
    'tag @s add ad.boss.scaled',
])
for t in range(1, TIER_MAX + 1):
    fn(f"mob/t{t}", [
        f"attribute @s minecraft:max_health modifier add {NS}:tier {round(VIDA_MOB[t] - 1, 4)} add_multiplied_base",
        f"tag @s add astral.mt{t}",
    ])
extra_mz = []
for w, mult in EXTRA_VIDA_MAZMORRA.items():
    extra_mz.append(f"execute if dimension minecraft:{w} run attribute @s minecraft:max_health modifier add "
                    f"{NS}:mazmorra {round(mult - 1, 4)} add_multiplied_total")
fn("mob/extra_mazmorra", extra_mz or ["return 0"])

fn("mob/elite_chance", [
    "execute unless entity @a[distance=..64,gamemode=!spectator] run return 0",
    "scoreboard players operation #a astral.tmp = @p[distance=..64,gamemode=!spectator] astral.lvl",
    "execute store result score #day astral.tmp run time query day",
    "scoreboard players operation #day astral.tmp /= #7 astral.const",
    "execute if score #day astral.tmp matches 4.. run scoreboard players set #day astral.tmp 3",
    "scoreboard players operation #a astral.tmp += #day astral.tmp",
    "# T6-T10 no suben mas la probabilidad: tope de amenaza 8 (como un T5 con 3 semanas de mundo)",
    "execute if score #a astral.tmp matches 9.. run scoreboard players set #a astral.tmp 8",
    "# probabilidad = 6% + 5% por nivel de amenaza (la mitad dentro de mazmorras)",
    "scoreboard players operation #c astral.tmp = #a astral.tmp",
    "scoreboard players operation #c astral.tmp *= #5 astral.const",
    "scoreboard players add #c astral.tmp 6",
    "execute if score #dg astral.tmp matches 1 run scoreboard players operation #c astral.tmp /= #2 astral.const",
    "execute store result score #r astral.tmp run random value 1..100",
    "execute if score #r astral.tmp > #c astral.tmp run return 0",
    "# tier del elite = 1 + azar(0..amenaza)/2, maximo 5",
    f"execute store result storage {NS}:tmp elite.max int 1 run scoreboard players get #a astral.tmp",
    f"function {NS}:elite/rand with storage {NS}:tmp elite",
    "scoreboard players operation #t astral.tmp /= #2 astral.const",
    "scoreboard players add #t astral.tmp 1",
    "execute if score #t astral.tmp matches 6.. run scoreboard players set #t astral.tmp 5",
] + [f"execute if score #t astral.tmp matches {i + 1} run return run function {NS}:elite/t{i + 1}" for i in range(5)])

# Nombre: [T#] + (elite) + nombre del mob (el de MythicMobs o el vanilla).
nombre = [f"data modify storage {NS}:tmp mob.n set value []"]
for t in range(1, TIER_MAX + 1):
    nombre.append(f"execute if score #mt astral.tmp matches {t} run data modify storage {NS}:tmp mob.n append value "
                  f"{{text:\"[T{t}] \",color:\"{COLOR_TIER[t]}\"}}")
for i, (name, color, *_rest) in enumerate(ELITE_TIERS):
    nombre.append(f"execute if entity @s[tag=astral.elite{i + 1}] run data modify storage {NS}:tmp mob.n append value "
                  f"{{text:\"{name} \",color:\"{color}\",bold:{'true' if i + 1 >= 4 else 'false'}}}")
nombre.append(f"execute if data entity @s CustomName run data modify storage {NS}:tmp mob.n append from entity @s CustomName")
fn("mob/nombre", nombre + [
    f"execute unless data entity @s CustomName run function {NS}:mob/nombre_vanilla",
    "# un mob comun de tier 0 queda sin cartel",
    f"execute unless data storage {NS}:tmp mob.n[1] run return 0",
    "# ultimo pedazo del nombre: la vida (se actualiza cada segundo con mob/vida)",
    f"data modify storage {NS}:tmp mob.n append value {{text:\" ❤\",color:\"red\"}}",
    f"data modify entity @s CustomName set from storage {NS}:tmp mob.n",
    "data modify entity @s CustomNameVisible set value 1b",
    # Incendium mete a sus mobs (Headless Warrior, Withered Scientist...) en un equipo que oculta el nombre.
    "team leave @s[team=in.noname]",
    "tag @s add astral.hpname",
    f"function {NS}:mob/vida",
])

# Jefe final Trainx (mobs/trainx.py): "✦ Tier V+ ✦ Trainx ❤ vida". Lo llama su skill de MythicMobs
# (los jefes con modelo no pasan por mob/roll porque ya llevan astral.seen).
fn("mob/nombre_vplus", [
    f"data modify storage {NS}:tmp mob.n set value [{{text:\"✦ Tier V+ ✦ \",color:\"#d07bff\",bold:true}}]",
    f"execute if data entity @s CustomName run data modify storage {NS}:tmp mob.n append from entity @s CustomName",
    f"data modify storage {NS}:tmp mob.n append value {{text:\" ❤\",color:\"red\"}}",
    f"data modify entity @s CustomName set from storage {NS}:tmp mob.n",
    "data modify entity @s CustomNameVisible set value 1b",
    "tag @s add astral.hpname",
    f"function {NS}:mob/vida",
])

# Vida en el nombre: " ❤ 11.500" (con puntos de miles). Se llama cerca de jugadores.
H = f"{NS}:tmp hp"
vida = [
    # T6-T10: un elite o jefe puede pasar los 2.147 millones (tope de un puntaje): se muestra en miles.
    "execute store result score #hk astral.tmp run data get entity @s Health 0.001",
    f"execute if score #hk astral.tmp matches 2000000.. run return run function {NS}:mob/vida_g",
    "execute store result score #hp astral.tmp run data get entity @s Health 1",
    "execute if score #hp astral.tmp matches ..0 run scoreboard players set #hp astral.tmp 1",
    "scoreboard players operation #u astral.tmp = #hp astral.tmp",
    "scoreboard players operation #u astral.tmp %= #1000 astral.const",
    "scoreboard players operation #k astral.tmp = #hp astral.tmp",
    "scoreboard players operation #k astral.tmp /= #1000 astral.const",
    "scoreboard players operation #m astral.tmp = #k astral.tmp",
    "scoreboard players operation #m astral.tmp /= #1000 astral.const",
    "scoreboard players operation #k astral.tmp %= #1000 astral.const",
]
for x in ("u", "k", "m"):
    vida.append(f"execute store result storage {H}.{x} int 1 run scoreboard players get #{x} astral.tmp")
for x in ("u", "k"):
    vida += [f"execute if score #{x} astral.tmp matches ..9 run function {NS}:mob/pad_{x}_2 with storage {H}",
             f"execute if score #{x} astral.tmp matches 10..99 run function {NS}:mob/pad_{x}_1 with storage {H}",
             f"execute if score #{x} astral.tmp matches 100.. run function {NS}:mob/pad_{x}_0 with storage {H}"]
vida += [
    f"execute if score #hp astral.tmp matches ..999 run return run function {NS}:mob/vida_1 with storage {H}",
    f"execute if score #hp astral.tmp matches ..999999 run return run function {NS}:mob/vida_2 with storage {H}",
    f"function {NS}:mob/vida_3 with storage {H}",
]
fn("mob/vida", vida)
# Mas de 2.000 millones: " ❤ 3.125.000.000" (las unidades se redondean a miles).
vida_g = [
    "scoreboard players operation #k astral.tmp = #hk astral.tmp",
    "scoreboard players operation #k astral.tmp %= #1000 astral.const",
    "scoreboard players operation #m astral.tmp = #hk astral.tmp",
    "scoreboard players operation #m astral.tmp /= #1000 astral.const",
    "scoreboard players operation #g astral.tmp = #m astral.tmp",
    "scoreboard players operation #g astral.tmp /= #1000 astral.const",
    "scoreboard players operation #m astral.tmp %= #1000 astral.const",
]
for x in ("k", "m", "g"):
    vida_g.append(f"execute store result storage {H}.{x} int 1 run scoreboard players get #{x} astral.tmp")
for x in ("k", "m"):
    vida_g += [f"execute if score #{x} astral.tmp matches ..9 run function {NS}:mob/pad_{x}_2 with storage {H}",
               f"execute if score #{x} astral.tmp matches 10..99 run function {NS}:mob/pad_{x}_1 with storage {H}",
               f"execute if score #{x} astral.tmp matches 100.. run function {NS}:mob/pad_{x}_0 with storage {H}"]
vida_g.append(f"function {NS}:mob/vida_4 with storage {H}")
fn("mob/vida_g", vida_g)
fn("mob/vida_4", ['$data modify entity @s CustomName.extra[-1].text set value " ❤ $(g).$(ms).$(ks).000"'])
for x in ("u", "k", "m"):
    for n, ceros in ((2, "00"), (1, "0"), (0, "")):
        fn(f"mob/pad_{x}_{n}", [f"$data modify storage {H}.{x}s set value \"{ceros}$({x})\""])
fn("mob/vida_1", ['$data modify entity @s CustomName.extra[-1].text set value " ❤ $(u)"'])
fn("mob/vida_2", ['$data modify entity @s CustomName.extra[-1].text set value " ❤ $(k).$(us)"'])
fn("mob/vida_3", ['$data modify entity @s CustomName.extra[-1].text set value " ❤ $(m).$(ks).$(us)"'])
fn("mob/nombre_vanilla", [
    f"execute if entity @s[type={e}] run data modify storage {NS}:tmp mob.n append value "
    f"{{translate:\"entity.minecraft.{e.split(':')[1]}\"}}" for e in HOSTILE + ["minecraft:vex"]])
fn("elite/rand", ["$execute store result score #t astral.tmp run random value 0..$(max)"])

for i, (name, color, hp, dmg, spd, armor, kb) in enumerate(ELITE_TIERS):
    t = i + 1
    stars = "[" + ROMAN[i] + "]"
    lines = [
        f"tag @s add astral.elite",
        f"tag @s add astral.elite{t}",
        f"attribute @s minecraft:max_health modifier add {NS}:elite {hp / 100} add_multiplied_total",
        f"attribute @s minecraft:attack_damage modifier add {NS}:elite {dmg / 100} add_multiplied_total",
        f"attribute @s minecraft:movement_speed modifier add {NS}:elite {spd / 100} add_multiplied_base",
        f"attribute @s minecraft:armor modifier add {NS}:elite {armor} add_value",
        f"attribute @s minecraft:knockback_resistance modifier add {NS}:elite {kb} add_value",
        f"attribute @s minecraft:follow_range modifier add {NS}:elite 0.5 add_multiplied_base",
        "# sin PersistenceRequired: los elites desaparecen como cualquier mob (si no, se acumulan)",
    ]
    if t >= 3:
        lines.append("effect give @s minecraft:fire_resistance infinite 0 true")
    if t >= 4:
        lines.append("effect give @s minecraft:resistance infinite 0 true")
    if t >= 5:
        lines.append("effect give @s minecraft:regeneration infinite 0 true")
    lines.append(f"particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.6 0.4 0.2 {10 * t}")
    fn(f"elite/t{t}", lines)

    # Drops y experiencia al matarlo
    put(f"data/{NS}/advancement/kill/elite{t}.json", {
        "criteria": {"kill": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": [
            {"condition": "minecraft:entity_properties", "entity": "this",
             "predicate": {"nbt": f"{{Tags:[\"astral.elite{t}\"]}}"}}]}}},
        "rewards": {"function": f"{NS}:drop/elite{t}", "experience": 10 * t * t}})
    dl = [f"advancement revoke @s only {NS}:kill/elite{t}"]
    for (mat, p, n) in ELITE_DROPS[i]:
        call = f"function {NS}:drop/give {{id:\"{mat}\",name:\"{MATERIALS[mat][0]}\"}}"
        for _ in range(n):
            dl.append(call if p >= 1 else f"execute if predicate {chance(p)} run {call}")
    # los elites tambien pueden soltar materiales base de su zona
    dl.append(f"execute if predicate {chance(0.15 * t)} if dimension minecraft:the_nether run function {NS}:drop/give {{id:\"fragmento_umbrio\",name:\"Fragmento Umbrio\"}}")
    dl.append(f"execute if predicate {chance(0.15 * t)} if dimension minecraft:the_end run function {NS}:drop/give {{id:\"fragmento_astral\",name:\"Fragmento Astral\"}}")
    dl.append(f"execute if predicate {chance(0.08 * t)} if dimension minecraft:overworld run function {NS}:drop/give {{id:\"gema_luminica\",name:\"Gema Luminica\"}}")
    fn(f"drop/elite{t}", dl)

# Tiers 6-10: material propio de cada tier (items_t6_10). Un mob de tier t puede soltar el de cada tier 6..t.
from items_t6_10 import MATERIAL_TIER, DROP_MATERIAL, DROP_OCASO_T5
_NOT = lambda tag: {"condition": "minecraft:inverted", "term": {"condition": "minecraft:entity_properties",
                    "entity": "this", "predicate": {"nbt": f"{{Tags:[\"{tag}\"]}}"}}}
for _t in range(5, TIER_MAX + 1):
    for _kind in ("comun", "elite", "jefe"):
        _cond = [{"condition": "minecraft:entity_properties", "entity": "this",
                  "predicate": {"nbt": f"{{Tags:[\"astral.mt{_t}\"]}}"}}]
        if _kind == "comun":
            _cond += [_NOT("astral.elite"), _NOT("ad.boss.scaled")]
        elif _kind == "elite":
            _cond += [{"condition": "minecraft:entity_properties", "entity": "this",
                       "predicate": {"nbt": "{Tags:[\"astral.elite\"]}"}}]
        else:
            _cond += [{"condition": "minecraft:entity_properties", "entity": "this",
                       "predicate": {"nbt": "{Tags:[\"ad.boss.scaled\"]}"}}]
        _probs = ({6: DROP_OCASO_T5.get(_kind, 0)} if _t == 5 else
                  {n: DROP_MATERIAL[_kind] for n in range(6, _t + 1)})
        _probs = {n: p for n, p in _probs.items() if p > 0}
        if not _probs:
            continue
        put(f"data/{NS}/advancement/kill/tier{_t}_{_kind}.json", {
            "criteria": {"kill": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": _cond}}},
            "rewards": {"function": f"{NS}:drop/tier{_t}_{_kind}"}})
        _dl = [f"advancement revoke @s only {NS}:kill/tier{_t}_{_kind}"]
        for _n, _p in _probs.items():
            _mid = MATERIAL_TIER[_n]
            _call = f"function {NS}:drop/give {{id:\"{_mid}\",name:\"{MATERIALS[_mid][0]}\"}}"
            _dl.append(_call if _p >= 1 else f"execute if predicate {chance(_p)} run {_call}")
        fn(f"drop/tier{_t}_{_kind}", _dl)

# Manzanas de Mazmorra: caen de mobs de su tier en mazmorras y la Infinita (manzanas.py).
from manzanas import generate as generate_manzanas
generate_manzanas(put, fn, chance)

fn("elite/fx", [
    "# elites viejos que quedaron persistentes: liberarlos una vez para que puedan desaparecer",
    "execute as @e[tag=astral.elite,tag=!astral.libre] run data modify entity @s PersistenceRequired set value 0b",
    "tag @e[tag=astral.elite,tag=!astral.libre] add astral.libre",
    "execute as @e[tag=astral.elite4] at @s run particle minecraft:flame ~ ~1 ~ 0.3 0.5 0.3 0.01 3",
    "execute as @e[tag=astral.elite5] at @s run particle minecraft:end_rod ~ ~1 ~ 0.3 0.5 0.3 0.02 4",
])

# ---------------------------------------------------------------------------
# Guia
# ---------------------------------------------------------------------------
def page(*parts):
    return list(parts)


def ing_text(kind, ident, count):
    if kind == "c":
        return f"{count}x {ITEMS[ident]['name']}"
    names = {"water_bottle": "Botella de agua"}
    return f"{count}x " + names.get(ident, ident.split(":")[-1].replace("_", " "))


pages = [
    page(txt("Guia AstralRPG\n\n", "dark_purple", bold=True),
         txt("FORJA ASTRAL\n", "black", bold=True),
         txt("1. Pone una Mesa de Herreria.\n2. Tira encima los materiales (tecla Q).\n"
             "3. Agachate al lado.\n\nSi estan todos, se forja solo.\n\n", "black"),
         txt("Tira solo lo de una receta por vez.", "dark_gray")),
    page(txt("MATERIALES\n\n", "black", bold=True),
         txt("Nether: Wither Skeletons y Piglin Brutes sueltan Esencia, Fragmentos Umbrios y Nucleos de Furia.\n\n"
             "End: Endermans (Cristal y Fragmento Astral), Shulkers (Corazon). Picando end stone y talando arboles "
             "del End salen Fragmentos y Madera Estelar.", "black")),
    page(txt("MAS MATERIALES\n\n", "black", bold=True),
         txt("Gema Luminica: cofres de estructuras del Overworld.\n\nNucleo Eolico: Vindicators.\n\n"
             "Netherita Fundida: un lingote de netherita en el horno.\n\n/trigger astral.guia te da otra guia.", "black")),
]
by_group = {}
for (out, n, ings, group) in RECIPES:
    by_group.setdefault(group, []).append((out, n, ings))
for group, recs in by_group.items():
    chunk = []
    for (out, n, ings) in recs:
        entry = [txt(ITEMS[out]["name"] + (f" x{n}" if n > 1 else "") + "\n", "dark_blue", bold=True)]
        entry += [txt(" " + ing_text(*i) + "\n", "black") for i in ings]
        chunk.append(entry)
        if len(chunk) == 2:
            pages.append([txt(group + "\n", "dark_purple", bold=True)] + [p for e in chunk for p in e])
            chunk = []
    if chunk:
        pages.append([txt(group + "\n", "dark_purple", bold=True)] + [p for e in chunk for p in e])

book = {"minecraft:written_book_content": {"title": "Guia AstralRPG", "author": "AstralRPG", "pages": pages},
        "minecraft:custom_data": snbt({NS: {"id": "guia"}})}
put(f"data/{NS}/loot_table/guia.json", {"type": "minecraft:command", "pools": [{"rolls": 1, "entries": [
    {"type": "minecraft:item", "name": "minecraft:written_book",
     "functions": [{"function": "minecraft:set_components", "components": book}]}]}]})
# ---------------------------------------------------------------------------
# GUIA CON MENUS (dialogos) + FORJA DESDE EL MENU
# Se abre con Esc -> "Guia AstralRPG", con la tecla de acciones rapidas o /trigger astral.guia.
# Para forjar hay que estar a 3 bloques o menos de una Mesa de Herreria.
# ---------------------------------------------------------------------------
VANILLA_NAMES = {"water_bottle": "Botella de agua", "minecraft:blaze_powder": "Polvo de blaze",
                 "minecraft:iron_ingot": "Lingote de hierro", "minecraft:leather": "Cuero",
                 "minecraft:stick": "Palo", "minecraft:coal": "Carbon", "minecraft:lava_bucket": "Cubo de lava",
                 "minecraft:feather": "Pluma", "minecraft:string": "Hilo", "minecraft:fishing_rod": "Cana de pescar",
                 "minecraft:redstone_block": "Bloque de redstone", "minecraft:blaze_rod": "Vara de blaze",
                 "minecraft:golden_apple": "Manzana dorada", "minecraft:iron_block": "Bloque de hierro",
                 "minecraft:iron_spear": "Lanza de hierro",
                 "minecraft:diamond_block": "Bloque de diamante", "minecraft:diamond": "Diamante",
                 "minecraft:prismarine_crystals": "Cristales de prismarina", "minecraft:amethyst_block": "Bloque de amatista",
                 "minecraft:gold_block": "Bloque de oro", "minecraft:netherite_ingot": "Lingote de netherita",
                 "minecraft:netherite_block": "Bloque de netherita", "minecraft:emerald_block": "Bloque de esmeralda",
                 "minecraft:leather_helmet": "Casco de cuero", "minecraft:leather_chestplate": "Pechera de cuero",
                 "minecraft:leather_leggings": "Pantalones de cuero", "minecraft:leather_boots": "Botas de cuero"}


def ing_name(kind, ident):
    return ITEMS[ident]["name"] if kind == "c" else VANILLA_NAMES.get(ident, ident.split(":")[-1].replace("_", " "))


def ing_pred(kind, ident):
    if kind == "c":
        return f'*[minecraft:custom_data~{{{NS}:{{id:"{ident}"}}}}]'
    if ident == "water_bottle":
        return 'minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}]'
    return f"{ident}[!minecraft:custom_data]"


def item_stack(iid, count=1):
    return {"id": ITEMS[iid]["base"], "count": count, "components": ITEMS[iid]["components"]}


RID = {}
for idx, (out, n, ings, group) in enumerate(RECIPES, start=1):
    RID[idx] = (out, n, ings)
    lines = [f"data modify storage {NS}:tmp forge.missing set value []"]
    for (kind, ident, count) in ings:
        lines.append(f"execute store result score #h astral.tmp run clear @s {ing_pred(kind, ident)} 0")
        lines.append(f"execute if score #h astral.tmp matches ..{count - 1} run data modify storage {NS}:tmp forge.missing "
                     f"append value \"{count}x {ing_name(kind, ident)}\"")
    lines.append(f"execute if data storage {NS}:tmp forge.missing[0] run return run function {NS}:forge/missing")
    prev = chain_prev(out, n, ings)
    if prev:
        # La pieza anterior se transforma (conserva encantamientos); si no se encuentra en un slot, se fabrica nueva.
        lines.append(f"execute store result score #ip astral.tmp run function {NS}:forge/ip/{out}/{prev}")
    for i, (kind, ident, count) in enumerate(ings):
        if prev and i == 0:
            lines.append(f"execute unless score #ip astral.tmp matches 1.. run clear @s {ing_pred(kind, ident)} {count}")
            continue
        lines.append(f"clear @s {ing_pred(kind, ident)} {count}")
        if ident == "minecraft:lava_bucket":
            lines.append("give @s minecraft:bucket 1")
    for _ in range(n):
        lines.append((f"execute unless score #ip astral.tmp matches 1.. run " if prev else "")
                     + f"loot give @s loot {NS}:item/{out}")
    it = ITEMS[out]
    # La guia fabrica desde el inventario; debe notificar igual que el altar.
    for _tier in (1, 5):
        if f'tier:{_tier},' in it['components']['minecraft:custom_data'] or f'tier:{_tier}}}' in it['components']['minecraft:custom_data'] or out == f'baston_{_tier}':
            lines.append(f"function {NS}:quest/event/forge{_tier}")
    lines += [
        "playsound minecraft:block.smithing_table.use player @s ~ ~ ~ 1 1",
        "playsound minecraft:block.enchantment_table.use player @s ~ ~ ~ 0.8 1.4",
        "particle minecraft:enchant ~ ~1 ~ 0.5 0.5 0.5 1 40",
        "tellraw @s " + json.dumps([txt("Forjaste: ", "gray"), txt(it["name"] + (f" x{n}" if n > 1 else ""), it["color"])]),
        "return 1",
    ]
    fn(f"forge/r/{idx}", lines)

fn("forge/missing", [
    "tellraw @s " + json.dumps([txt("Te falta: ", "red"),
                                {"nbt": "forge.missing[]", "storage": f"{NS}:tmp", "separator": txt(", ", "red"),
                                 "color": "gold", "italic": False}]),
    "playsound minecraft:entity.villager.no player @s ~ ~ ~ 0.7 1",
    "return 0",
])
near = []
for dy in (0, -1, 1, -2, 2, -3, 3):
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            near.append(f"execute if block ~{dx} ~{dy} ~{dz} minecraft:smithing_table run return 1")
fn("forge/near", near + ["return 0"])
fn("forge/craft", [
    f"execute store result storage {NS}:tmp forge.id int 1 run scoreboard players get @s astral.forja",
    "scoreboard players reset @s astral.forja",
    f"execute unless function {NS}:forge/near run return run tellraw @s " + json.dumps(
        [txt("Tenes que estar al lado de una ", "red"), txt("Mesa de Herreria", "gold"), txt(" para forjar.", "red")]),
    f"function {NS}:forge/dispatch with storage {NS}:tmp forge",
])
fn("forge/dispatch", [f"$function {NS}:forge/r/$(id)"])


def guide_ink(label):
    """Conservar colores por categoria con tinta oscura sobre el pergamino."""
    palette = {'white': '#30241b', 'gray': '#3b3029', 'dark_gray': '#3b3029',
               'gold': '#8a4500', 'yellow': '#8a4500', 'aqua': '#00727a',
               'dark_aqua': '#00727a', 'light_purple': '#8e1f8e', 'dark_purple': '#8e1f8e',
               'red': '#b01c1c', 'dark_red': '#b01c1c', 'green': '#1d7a2e',
               'dark_green': '#1d7a2e', 'blue': '#2a4fb5', 'dark_blue': '#2a4fb5', 'black': '#161210'}
    if isinstance(label, list):
        return [guide_ink(part) for part in label]
    if not isinstance(label, dict):
        return label
    result = dict(label)
    color = result.get('color', 'white')
    if color.startswith('#') and len(color) == 7:
        rgb = [int(color[i:i+2], 16) for i in (1, 3, 5)]
        # Los colores que ya son oscuros se dejan tal cual; los claros se oscurecen.
        if max(rgb) > 0xd0 or sum(rgb) > 0x180:
            result['color'] = '#' + ''.join(f'{round(c * .43):02x}' for c in rgb)
    else:
        result['color'] = palette.get(color, '#30241b')
    # Sin sombra: sobre el pergamino claro la sombra oscura hace borroso el texto.
    result['shadow_color'] = 0
    if 'extra' in result:
        result['extra'] = guide_ink(result['extra'])
    return result


def dlg(path, title, body, actions, back=None, columns=1, width=310):
    if not actions:
        # pantalla solo de lectura: un unico boton para volver
        d = {"type": "minecraft:notice", "title": title, "body": body, "after_action": "none",
             "can_close_with_escape": True, "pause": False,
             "action": {"label": txt("Volver", "#3b3029"), "width": 200,
                        "action": {"type": "show_dialog", "dialog": f"{NS}:{back or 'guia'}"}}}
        put(f"data/{NS}/dialog/{path}.json", d)
        return
    d = {"type": "minecraft:multi_action", "title": title, "body": body, "actions": actions,
         "columns": columns, "after_action": "none", "can_close_with_escape": True, "pause": False}
    if back:
        d["exit_action"] = {"label": txt("Volver", "#3b3029"), "width": 200,
                            "action": {"type": "show_dialog", "dialog": f"{NS}:{back}"}}
    else:
        d["exit_action"] = {"label": txt("Cerrar", "#3b3029"), "width": 200}
    put(f"data/{NS}/dialog/{path}.json", d)


def btn(label, dialog=None, command=None, tooltip=None, width=150):
    b = {"label": guide_ink(label if isinstance(label, dict) else txt(label, "white")), "width": width}
    if tooltip:
        b["tooltip"] = tooltip
    if dialog:
        b["action"] = {"type": "show_dialog", "dialog": f"{NS}:{dialog}"}
    if command:
        b["action"] = {"type": "run_command", "command": command}
    return b


def msg(text, color="gray", width=300):
    return {"type": "minecraft:plain_message", "contents": txt(text, color) if isinstance(text, str) else text,
            "width": width}


def recipe_leaf(path, title, rids, back):
    """Lista de items; cada uno abre su propia pantalla con el boton Forjar."""
    actions = []
    for rid in rids:
        out, n, ings = RID[rid]
        it = ITEMS[out]
        recipe_detail(rid, path)
        actions.append(btn(txt(it["name"] + (f" x{n}" if n > 1 else ""), it["color"]), dialog=f"receta/{rid}",
                           tooltip=txt(", ".join(f"{c}x {ing_name(k, i)}" for (k, i, c) in ings), "gray"), width=300))
    dlg(path, txt(title, "light_purple", bold=True),
        [msg("Elegi que queres forjar.", "gray")], actions, back=back)


def recipe_detail(rid, back):
    out, n, ings = RID[rid]
    it = ITEMS[out]
    desc = [txt(it["name"] + (f" x{n}" if n > 1 else "") + "\n", it["color"], bold=True),
            txt("Necesitas:\n", "gray")]
    desc += [txt(f"  {c}x {ing_name(k, i)}\n", "white") for (k, i, c) in ings]
    desc.append(txt("Tambien en la mesa de crafteo\n" if MESA[out]
                    else "Solo Forja: las cantidades superan la mesa 3x3\n", "dark_green"))
    body = [{"type": "minecraft:item", "item": item_stack(out, n),
             "description": {"contents": desc, "width": 220},
             "show_decorations": True, "show_tooltip": True, "width": 16, "height": 16},
            msg("Pasa el mouse sobre el item para ver sus stats. Tenes que estar al lado de una Mesa de Herreria.",
                "dark_gray")]
    d = {"type": "minecraft:multi_action", "title": txt(it["name"], it["color"], bold=True), "body": body,
         "actions": [btn(txt("Forjar", "green", bold=True), command=f"/trigger astral.forja set {rid}", width=200)],
         "columns": 1, "after_action": "close", "can_close_with_escape": True, "pause": False,
         "exit_action": {"label": txt("Volver", "gray"), "width": 200,
                         "action": {"type": "show_dialog", "dialog": f"{NS}:{back}"}}}
    put(f"data/{NS}/dialog/receta/{rid}.json", d)


def rids_where(pred):
    return [rid for rid, (out, n, ings) in RID.items() if pred(out)]


# Hojas de recetas
leaves = {}
mats = rids_where(lambda o: ITEMS[o]["kind"] == "material")
recipe_leaf("guia/materiales_1", "Forja: Materiales (1/2)", mats[:7], "guia/materiales")
recipe_leaf("guia/materiales_2", "Forja: Materiales (2/2)", mats[7:], "guia/materiales")
CLASSES = [("berserker", "Berserker", "#ff4d4d", [("espada_", "Espadas"), ("hacha_", "Hachas")]),
           ("mago", "Mago", "#b26bff", [("baston_", "Bastones")]),
           ("arquero", "Arquero", "#5ee08a", [("arco_", "Arcos"), ("ballesta_", "Ballestas")])]
for cid, cname, ccol, weps in CLASSES:
    sub = []
    for t in range(1, TIER_MAX + 1):
        r = rids_where(lambda o, t=t: o.startswith(f"{cid}_{t}_"))
        recipe_leaf(f"guia/{cid}_{t}", f"{cname}: armadura {ROMAN[t - 1]}", r, f"guia/{cid}")
        sub.append(btn(txt(f"Armadura {ROMAN[t - 1]} - {ARMOR_SETS[cid]['tiers'][t - 1]['name']}", ccol),
                       dialog=f"guia/{cid}_{t}", width=300))
    for pre, wname in weps:
        r = rids_where(lambda o, pre=pre: o.startswith(pre) and (o[-1].isdigit() or o=='espada_heroe_errante'))
        recipe_leaf(f"guia/{cid}_{pre[:-1]}", f"{cname}: {wname}", r, f"guia/{cid}")
        sub.append(btn(txt(wname, "gold"), dialog=f"guia/{cid}_{pre[:-1]}", width=300))
    dlg(f"guia/{cid}", txt(cname, ccol, bold=True),
        [msg(f"Equipo de {cname}. Cada tier se forja con la pieza del tier anterior.")], sub, back="guia")
# Clases nuevas (22/11, clases.py): armaduras solo en sus tiers y su arma.
from clases import SETS as _CL_SETS
for cid, cdef in _CL_SETS.items():
    sub = []
    for t, (_vid, tname) in sorted(cdef["tiers"].items()):
        r = rids_where(lambda o, t=t, cid=cid: o.startswith(f"{cid}_{t}_"))
        recipe_leaf(f"guia/{cid}_{t}", f"{cdef['clase']}: armadura {ROMAN[t - 1]}", r, f"guia/{cid}")
        sub.append(btn(txt(f"Armadura {ROMAN[t - 1]} - {tname}", cdef["color"]), dialog=f"guia/{cid}_{t}", width=300))
    pre, wname = {"segador": ("guadana_", "Guadanas"), "invocador": ("libro_invocador_", "Libros"),
                  "asesino": ("cuchillo_", "Cuchillos")}[cid]
    r = rids_where(lambda o, pre=pre: o.startswith(pre) and o[-1].isdigit())
    recipe_leaf(f"guia/{cid}_arma", f"{cdef['clase']}: {wname}", r, f"guia/{cid}")
    sub.append(btn(txt(wname, "gold"), dialog=f"guia/{cid}_arma", width=300))
    dlg(f"guia/{cid}", txt(cdef["clase"], cdef["color"], bold=True),
        [msg(f"Equipo de {cdef['clase']}. Cada tier se forja con la pieza del tier anterior.")], sub, back="guia")
recipe_leaf("guia/lanzas", "Lanzas (Combate)", rids_where(lambda o: o.startswith("lanza_")), "guia")
recipe_leaf("guia/carnivora", "Equipo Carnivora III", rids_where(lambda o: o.startswith("carnivora_")), "guia")
recipe_leaf("guia/asura", "Equipo Asura IV", rids_where(lambda o: o in ("asura_espada", "asura_alas")), "guia")
recipe_leaf("guia/agua", "Equipo de Agua III", rids_where(lambda o: o.startswith("agua_")), "guia")
recipe_leaf("guia/oficios", "Ropa de Minero y Talador I", rids_where(lambda o: o.startswith(("minero_", "talador_"))), "guia")
tal_btns = []
for tid, t in TALISMANS.items():
    recipe_leaf(f"guia/talisman_{tid}", t["name"], rids_where(lambda o, tid=tid: o.startswith(f"talisman_{tid}_")), "guia/talismanes")
    tal_btns.append(btn(txt(t["name"], t["color"]), dialog=f"guia/talisman_{tid}"))
dlg("guia/talismanes", txt("Talismanes", "aqua", bold=True),
    [msg("Se llevan en la mano secundaria. Se hacen con lo que sueltan los mobs elite.")], tal_btns, back="guia", columns=2)
recipe_leaf("guia/especiales", "Especiales", rids_where(
    lambda o: o in SPECIAL_WEAPONS or o in ("gancho", "gancho_realista", "guadana_umbria", "guantes_meteoro")), "guia")
recipe_leaf("guia/taladros", "Taladros (Mineria)", rids_where(lambda o: o.startswith("taladro_")), "guia")
recipe_leaf("guia/motosierras", "Motosierras (Tala)", rids_where(lambda o: o.startswith("motosierra_")), "guia")
dlg("guia/materiales", txt("Materiales", "light_purple", bold=True),
    [msg("Materiales que se forjan a partir de otros.")],
    [btn("Pagina 1", dialog="guia/materiales_1"), btn("Pagina 2", dialog="guia/materiales_2"),
     btn(txt("Donde se consiguen", "gold"), dialog="guia/drops")], back="guia", columns=2)

# Donde se consigue cada material
WHERE = {}
for group, (mobs, drops) in MOB_DROPS.items():
    for (m, p, cond) in drops:
        who = ", ".join(x.split(":")[1].replace("_", " ").title() for x in mobs) if len(mobs) <= 2 else "mobs del Nether"
        WHERE.setdefault(m, []).append(f"{who} ({int(p * 100)}%" + (", en el End)" if cond == "end" else ")"))
WHERE.setdefault("gema_luminica", []).append("cofres de estructuras del Overworld (25%)")
WHERE.setdefault("fragmento_cristal", []).append("picando end stone en el End (4%)")
WHERE.setdefault("madera_estelar", []).append("talando arboles o chorus en el End")
WHERE.setdefault("netherita_fundida", []).append("lingote de netherita en el horno")
WHERE.setdefault("esencia_elite", []).append("mobs elite (todos los tiers)")
WHERE.setdefault("alma_corrupta", []).append("mobs elite Campeon, Pesadilla y Astral")
WHERE.setdefault("chispa_astral", []).append("mobs elite Astral (60%)")
drop_body = [msg("Materiales que se consiguen en el mundo:", "gray")]
for m, ways in WHERE.items():
    drop_body.append({"type": "minecraft:item", "item": item_stack(m),
                      "description": {"contents": [txt(ITEMS[m]["name"] + "\n", ITEMS[m]["color"], bold=True),
                                                   txt("  " + "; ".join(ways), "gray")], "width": 250},
                      "show_decorations": True, "show_tooltip": True, "width": 16, "height": 16})
dlg("guia/drops", txt("Donde se consiguen", "gold", bold=True), drop_body, [], back="guia/materiales")

dlg("guia/como", txt("Como se juega", "light_purple", bold=True), [
    msg("MESA Y LIBRO DE RECETAS", "gold"),
    msg("Las recetas que entran en 3x3 tambien se hacen en una mesa normal. El libro verde las desbloquea "
        "al conseguir uno de sus materiales; hace clic para autollenar. Usa materiales Astral exactos. "
        "La mesa exige el nivel de AuraSkills del resultado. Las recetas grandes siguen en la Forja.", "gray"),
    msg("ACCESO RAPIDO A LA GUIA", "gold"),
    msg("Opciones -> Controles -> Acciones rapidas: asigna una tecla para abrir la Guia Astral.", "gray"),
    msg("FORJA ASTRAL", "gold"),
    msg("Pone una Mesa de Herreria, abri esta guia al lado y apreta Forjar en lo que quieras hacer. "
        "Los materiales se sacan solos de tu inventario.", "gray"),
    msg("CLASES", "gold"),
    msg("Berserker (Forja), Mago (Hechiceria) y Arquero (Arqueria) tienen 5 tiers de armadura y armas. "
        "Cada objeto pide un nivel de AuraSkills para usarlo: /skills para ver tus niveles.", "gray"),
    msg("ARMAS ESPECIALES", "gold"),
    msg(f"Bastones: click derecho lanza un proyectil arcano. Atraviesa hasta {len(HECHIZO_PERFORA)} enemigos "
        f"(dano {'/'.join(f'{v:.0%}' for v in HECHIZO_PERFORA)}). Arcos: mantene click derecho y disparan solos. "
        "Saltador: click derecho para impulsarte. Gancho: lanzalo a un bloque y volve a pulsar para tirarte.", "gray"),
    msg("MOBS ELITE", "gold"),
    msg("Cuanto mejor es tu equipo y mas dias pasan, aparecen mas mobs elite (Veterano, Elite, Campeon, "
        "Pesadilla y Astral). Son mas fuertes y sueltan materiales para Talismanes y Lanzas.", "gray"),
], [], back="guia")

from mobs.mascotas import MASCOTAS as GUIDE_PETS
for pet_page in range(3):
    pets=list(GUIDE_PETS.items())[pet_page*6:(pet_page+1)*6]
    dlg(f'guia/mascotas_{pet_page+1}', txt(f'Mascotas ({pet_page+1}/3)', 'gold', bold=True),
        [msg(f"{d['nombre']}: {d['fuente']}\nNv. 1: {d['texto'][0]}; +10: {d['texto'][1]}; +20: {d['texto'][2]}") for pid,d in pets],
        [btn('Ver pagina '+str(i),dialog=f'guia/mascotas_{i}') for i in range(1,4) if i!=pet_page+1]
        +[btn('Abrir /mascotas',command='/mascotas')],back='guia')

dlg("guia/proteccion", txt("Terrenos y mochilas", "gold", bold=True), [
    msg("Solo en survival: pala de oro, clic derecho en dos esquinas. Protege todo de fondo a techo. Minimo 6x6 (36 bloques).", "gray"),
    msg("Empezas con 36 bloques de area, sin ganar por tiempo. /shop -> Proteccion suma area: 36 + 25 = 61, no 11x11. Podes repartirla entre zonas de minimo 36 cada una.", "gray"),
    msg("/trust jugador comparte; /untrust jugador retira acceso; /abandonclaim libera la zona. WorldGuard y los candados de Bolt siguen vigentes.", "gray"),
    msg("Mochilas: se compran en /shop -> Mochilas: Cuero 9 espacios ($5.000), Cobre 18 ($20.000), Hierro 27 ($50.000), Oro 36 ($100.000) y Diamante 45 ($175.000). Necesitas un lugar libre en el inventario.", "gray"),
    msg("La mochila es un objeto: tenela en la mano y hace clic derecho para abrirla. Tambien se fabrican (cuero + hilo + cofre) y se mejoran rodeandolas con 8 lingotes del nivel siguiente; Netherite (54) en la mesa de herreria. /bp muestra las recetas.", "gray"),
    msg("Cuidado: si moris, la mochila cae con tus cosas a la tumba y su contenido va con ella. No se puede meter una mochila dentro de otra.", "gray"),
], [], back="guia")
dlg("guia/mercader", txt("Goblin Mercader", "green", bold=True), [
    msg("Cada 40-60 minutos visita a alguien en Survival durante 5 minutos. Clic derecho abre su tienda Astral con stock por jugador y visita. Si le pegas, se defiende solo de vos y se va.", "gray"),
    msg("Golemcitos en Bosque, Minas y Cumbre: grupos de 2-4, con XP embotellada segun su tier. En Infinita se juntan los tres cada diez tandas de aparicion.", "gray"),
], [], back="guia")
dlg("guia/consumibles", txt("Experiencia y suerte", "green", bold=True), [
    msg("Frasco Pequeno: 60 puntos; Grande: 200; Gigante: 550 puntos de XP vanilla. Barril: 5.500 puntos. Clic derecho usa uno; Shift + clic usa todos los de esa mano. Se apilan de a 16.", "gray"),
    msg("Manzana de la Suerte: comela para mejorar las chances raras, epicas y legendarias de las gachas durante cinco minutos. Otra renueva el tiempo. No garantiza premios.", "gray"),
    msg("Se consiguen en /shop -> Consumibles, gachas, cofres de jefe y rankings. Los eventos ancestrales y la Infinita de tier VI o mas tambien dan XP embotellada.", "gray"),
], [], back="guia")
dlg("guia/cocina", txt("Cocina (Crop & Kettle)", "gold", bold=True), [
    msg("Crop & Kettle por maybejake.", "gray"),
    msg("En survival: nuevos cultivos, comidas y mas de cien recetas. La olla se fabrica con un caldero y una fogata. Consulta los avances y el recetario de Crop & Kettle para progresar.", "gray"),
    msg("Los cultivos y las interacciones de cocina se usan en survival. Conserva los ingredientes nuevos para descubrir mas recetas.", "gray"),
], [], back="guia")
dlg("guia/datapacks", txt("Mundo y datapacks", "gold", bold=True), [
    msg("El Survival usa datapacks que cambian el mundo. Todo lo que encontres ahi tambien sube de tier: los mobs aparecen como minimo en Tier I.", "gray"),
    msg("Stellarity (End): islas nuevas, biomas, criaturas y botin del End. El End no tiene dragon: el portal de salida y los portales a las islas exteriores ya estan abiertos. En la piedra del End aparece la Mena de Asura (monedas para el Equipo Asura IV).", "gray"),
    msg("Incendium (Nether): biomas, fortalezas y jefes nuevos del Nether, con armas y botin propios.", "gray"),
    msg("Dungeons and Taverns, Structory y Explorify: tabernas, torres, ruinas, criptas y fortalezas nuevas por todo el mundo, con cofres y mobs propios. DnT Stronghold Overhaul renueva las fortalezas del End.", "gray"),
    msg("Crop & Kettle: cultivos y comidas nuevas (ver Cocina).", "gray"),
    msg("Los encantamientos de estos datapacks tambien salen en la Mesa de Encantamientos y en sus cofres.", "gray"),
], [], back="guia")

dlg("guia", txt("Guia AstralRPG", "light_purple", bold=True), [
    msg("Elegi una seccion. Para forjar, abri la guia al lado de una Mesa de Herreria.", "gray")], [
    # Colores fuertes y distintos entre si, pensados para leerse sobre el pergamino.
    btn(txt("Como se juega", "#7a3a10"), dialog="guia/como"),
    btn(txt("Goblin y golemcitos", "#1c7d2c"), dialog="guia/mercader"),
    btn(txt("Experiencia y suerte", "#1c7d2c"), dialog="guia/consumibles"),
    btn(txt("Terrenos y mochilas", "#7a3a10"), dialog="guia/proteccion"),
    btn(txt("Cocina (Crop & Kettle)", "#7a3a10"), dialog="guia/cocina"),
    btn(txt("Datapacks", "#7a3a10"), dialog="guia/datapacks"),
    btn(txt("Misiones e historia", "#006e78"), command="/trigger aq.journal"),
    btn(txt("Materiales", "#a0177a"), dialog="guia/materiales"),
    btn(txt("Berserker", "#b8141c"), dialog="guia/berserker"),
    btn(txt("Mago", "#5a24c8"), dialog="guia/mago"),
    btn(txt("Arquero", "#1c7d2c"), dialog="guia/arquero"),
    btn(txt("Segador", "#b23a48"), dialog="guia/segador"),
    btn(txt("Invocador", "#7b5cff"), dialog="guia/invocador"),
    btn(txt("Asesino", "#3fbf8f"), dialog="guia/asesino"),
    btn(txt("Lanzas", "#c04800"), dialog="guia/lanzas"),
    btn(txt("Talismanes", "#1a5cc0"), dialog="guia/talismanes"),
    btn(txt("Especiales", "#4a3a30"), dialog="guia/especiales"),
    btn(txt("Taladros", "#8a6a00"), dialog="guia/taladros"),
    btn(txt("Motosierras", "#4a7410"), dialog="guia/motosierras"),
    btn(txt("Carnivora III", "#477a10"), dialog="guia/carnivora"),
    btn(txt("Asura IV", "#8a6a00"), dialog="guia/asura"),
    btn(txt("Agua III", "#4fd8e8"), dialog="guia/agua"),
    btn(txt("Minero y Talador", "#8a5530"), dialog="guia/oficios"),
    btn(txt(f"{len(GUIDE_PETS)} mascotas", "#006e78"), dialog="guia/mascotas_1"),
], columns=2)
# Boton en el menu de pausa y en acciones rapidas
put("data/minecraft/tags/dialog/pause_screen_additions.json", {"values": [f"{NS}:guia"]})
put("data/minecraft/tags/dialog/quick_actions.json", {"values": [f"{NS}:guia"]})

fn("guide/give", [
    "scoreboard players reset @s astral.guia",
    f"dialog show @s {NS}:guia",
])
put(f"data/{NS}/advancement/join.json", {
    "criteria": {"join": {"trigger": "minecraft:tick"}}, "rewards": {"function": f"{NS}:guide/join"}})
fn("guide/join", [
    "tellraw @s " + json.dumps([txt("Bienvenido a AstralRPG. ", "light_purple"),
                                txt("Abri la guia con Esc -> Guia AstralRPG, o con /trigger astral.guia", "gray")]),
    f"dialog show @s {NS}:guia",
])

# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
# Kit para probar el Herrero y el bonus de set: materiales para llegar a +10 (con repuesto por si falla),
# una espada, un arco y el set Berserker II completo
_kit = {}
for _L, (_p, _pr, _mats) in MEJORAS.items():
    for _m, _n in _mats:
        _kit[_m] = _kit.get(_m, 0) + _n
fn("admin/kit_pruebas", [f"loot give @s loot {NS}:item/{m}" for m, n in _kit.items() for _ in range(n + n // 2)]
   + [f"loot give @s loot {NS}:item/{i}" for i in ("espada_2", "arco_2")]
   + [f"loot give @s loot {NS}:item/berserker_2_{pz}" for pz in PIECES]
   + ["tellraw @s " + json.dumps(txt("Kit de pruebas: materiales para mejorar hasta +10, espada, arco y set Berserker II.",
                                     "light_purple"))])
fn("admin/materiales", [f"loot give @s loot {NS}:item/{m}" for m in MATERIALS] + [f"loot give @s loot {NS}:item/{m}" for m in MATERIALS])
# Kits de prueba: cajas de shulker por categoria (el inventario no alcanza para todo)
from items_t6_10 import MATERIALES as _MAT_ALTO


def _tier_de(iid):
    """Tier de un item de clase por su id: berserker_7_helmet -> 7, espada_10 -> 10."""
    for part in reversed(iid.split("_")):
        if part.isdigit():
            return int(part)
    return 0


KITS = [
    ("cuchillos", "Cuchillos I-X", "red", "minecraft:red_shulker_box", [i for i in ITEMS if i.startswith("cuchillo_")]),
    ("consumibles", "Consumibles Astrales", "green", "minecraft:green_shulker_box", list(__import__("tanda_xp").PRECIOS) + [f"manzana_t{t}" for t in range(2, 11)]),
    ("historia", "Recuerdos de historia", "aqua", "minecraft:light_blue_shulker_box",
     [i for i in ITEMS if ITEMS[i]["kind"] == "quest"]),
    ("materiales", "Materiales", "light_purple", "minecraft:purple_shulker_box",
     [i for i in ITEMS if ITEMS[i]["kind"] == "material" and i != 'colmillo_carnivoro' and not i.startswith('asura_')
      and i not in ('perla_abisal', 'coral_astral') and i not in _MAT_ALTO]),
    ('agua', 'Equipo de Agua (Oceano)', 'aqua', 'minecraft:light_blue_shulker_box',
     [i for i in ITEMS if i.startswith('agua_') or i in ('perla_abisal', 'coral_astral')]),
    ('carnivora', 'Equipo Carnivora', 'green', 'minecraft:green_shulker_box',
     [i for i in ITEMS if i.startswith('carnivora_') or i == 'colmillo_carnivoro']),
    ('asura_peluches', 'Asura y peluches', 'gold', 'minecraft:yellow_shulker_box',
     [i for i in ITEMS if i.startswith(('asura_', 'peluche_'))]),
    ("berserker", "Armaduras Berserker", "red", "minecraft:red_shulker_box",
     [i for i in ITEMS if i.startswith("berserker_") and _tier_de(i) <= 5]),
    ("mago", "Armaduras Mago", "dark_purple", "minecraft:magenta_shulker_box",
     [i for i in ITEMS if i.startswith("mago_") and _tier_de(i) <= 5]),
    ("arquero", "Armaduras Arquero", "green", "minecraft:lime_shulker_box",
     [i for i in ITEMS if i.startswith("arquero_") and _tier_de(i) <= 5]),
    ("armas", "Armas de clase", "gold", "minecraft:orange_shulker_box",
     [i for i in ITEMS if i.split("_")[0] in ("espada", "hacha", "baston", "guadana", "arco") and (i[-1].isdigit() and _tier_de(i) <= 5 or i == "espada_heroe_errante")]),
    # Tiers 6-10 (14/11/2026)
    ("berserker_alto", "Armaduras Berserker VI-X", "red", "minecraft:red_shulker_box",
     [i for i in ITEMS if i.startswith("berserker_") and _tier_de(i) >= 6]),
    ("mago_alto", "Armaduras Mago VI-X", "dark_purple", "minecraft:magenta_shulker_box",
     [i for i in ITEMS if i.startswith("mago_") and _tier_de(i) >= 6]),
    ("arquero_alto", "Armaduras Arquero VI-X", "green", "minecraft:lime_shulker_box",
     [i for i in ITEMS if i.startswith("arquero_") and _tier_de(i) >= 6]),
    ("armas_alto", "Armas de clase VI-X", "gold", "minecraft:orange_shulker_box",
     [i for i in ITEMS if i.split("_")[0] in ("espada", "hacha", "baston", "guadana", "arco") and i[-1].isdigit() and _tier_de(i) >= 6]),
    ("materiales_alto", "Lanzas y materiales VI-X", "light_purple", "minecraft:purple_shulker_box",
     [i for i in ITEMS if i.startswith("lanza_") and _tier_de(i) >= 6] + sorted(_MAT_ALTO)),
    ("especiales", "Especiales, Lanzas y Talismanes", "aqua", "minecraft:cyan_shulker_box",
     [i for i in ITEMS if i in SPECIAL_WEAPONS or i.startswith("talisman_") or i.startswith("lanza_") and _tier_de(i) <= 5 or i in
      ("gancho", "gancho_realista", "guadana_umbria", "guantes_meteoro")]),
    ("ballestas", "Ballestas de Arquero", "green", "minecraft:green_shulker_box",
     [i for i in ITEMS if i.startswith("ballesta_")]),
    ("herramientas", "Taladros y Motosierras", "yellow", "minecraft:yellow_shulker_box",
     [i for i in ITEMS if i.startswith(("taladro_", "motosierra_"))]),
    ("oficios", "Ropa de Minero y Talador", "gold", "minecraft:brown_shulker_box",
     [i for i in ITEMS if i.startswith(("minero_", "talador_"))]),
    # Gemas de la Reforja (gemas.py): Cruda a Impecable y Perfecta/Estelar en dos cajas.
    ("gemas", "Gemas Cruda a Impecable", "light_purple", "minecraft:purple_shulker_box",
     [GEMAS.item_id(t, q) for t, q in GEMAS.todas() if q <= 3]),
    ("gemas_altas", "Gemas Perfecta y Estelar", "light_purple", "minecraft:magenta_shulker_box",
     [GEMAS.item_id(t, q) for t, q in GEMAS.todas() if q >= 4]),
    ("cavernas", "Cavernas de Cristal", "light_purple", "minecraft:purple_shulker_box", list(CAVERNAS.ITEMS)),
    ("vacio", "Vacio Estelar", "dark_purple", "minecraft:black_shulker_box", list(VACIO.ITEMS)),
    ("historia", "Items del Modo Historia", "gold", "minecraft:orange_shulker_box", list(__import__("historia_items").ITEMS_HISTORIA)),
    # Clases nuevas (clases.py, 22/11)
    ("segador", "Armaduras del Segador", "red", "minecraft:red_shulker_box", [i for i in ITEMS if i.startswith("segador_")]),
    ("invocador", "Armaduras del Invocador", "dark_purple", "minecraft:purple_shulker_box",
     [i for i in ITEMS if i.startswith("invocador_")]),
    ("libros", "Libros del Invocador", "dark_purple", "minecraft:magenta_shulker_box",
     [i for i in ITEMS if i.startswith("libro_invocador_")]),
    ("asesino_bajo", "Armaduras del Asesino I-V", "dark_green", "minecraft:green_shulker_box",
     [i for i in ITEMS if i.startswith("asesino_") and _tier_de(i) <= 5]),
    ("asesino_alto", "Armaduras del Asesino VI-X", "dark_green", "minecraft:lime_shulker_box",
     [i for i in ITEMS if i.startswith("asesino_") and _tier_de(i) >= 6]),
]
_kitted = set()
for kid, kname, kcolor, box, ids in KITS:
    assert len(ids) <= 27, (kid, len(ids))
    _kitted.update(ids)
    put(f"data/{NS}/loot_table/kit/{kid}.json", {"type": "minecraft:command", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": box, "functions": [
            {"function": "minecraft:set_contents", "component": "minecraft:container",
             "entries": [{"type": "minecraft:loot_table", "value": f"{NS}:item/{i}"} for i in ids]},
            {"function": "minecraft:set_components", "components": {
                "minecraft:item_name": txt(f"Kit: {kname}", kcolor)}}]}]}]})
    fn(f"admin/kit_{kid}", [f"loot give @s loot {NS}:kit/{kid}"])
_missing = [i for i in ITEMS if i not in _kitted]
assert not _missing, _missing
fn("admin/todo", [f"loot give @s loot {NS}:kit/{k[0]}" for k in KITS] + [
    "tellraw @s " + json.dumps(txt(f"Te dimos {len(KITS)} cajas de shulker con todos los items de AstralRPG.", "gray"))])

# ---------------------------------------------------------------------------
# Taladros y motosierras: area y tala de arboles
# Cada tick se guarda el bloque al que apuntas. Cuando la estadistica "usado" del pico/hacha
# sube y ese bloque ya es aire, lo rompiste vos: se pica el area o se sigue el tronco.
# ---------------------------------------------------------------------------
from tools import TREE_LOGS, DRILLABLE, FACING, area_ranges
put(f"data/{NS}/tags/block/drillable.json", {"values": DRILLABLE})
put(f"data/{NS}/tags/block/tree_logs.json", {"values": [f"minecraft:{b}" for b in TREE_LOGS]})
put(f"data/{NS}/tags/block/ray_pass.json", {"values": ["minecraft:air", "minecraft:cave_air", "minecraft:void_air",
                                                       "minecraft:water", "minecraft:lava", "minecraft:light"]})
DRILL_SEL = f"minecraft:netherite_pickaxe[minecraft:custom_data~{{{NS}:{{tool:\"drill\"}}}}]"
SAW_SEL = f"minecraft:netherite_axe[minecraft:custom_data~{{{NS}:{{tool:\"saw\"}}}}]"
fn("tool/aim", [
    "scoreboard players set @s astral.tok 0",
    "scoreboard players set #r astral.tmp 52",
    f"execute anchored eyes positioned ^ ^ ^ run function {NS}:tool/ray",
])
fn("tool/ray", [
    f"execute unless block ~ ~ ~ #{NS}:ray_pass run return run function {NS}:tool/hit",
    "scoreboard players remove #r astral.tmp 1",
    f"execute if score #r astral.tmp matches 1.. positioned ^ ^ ^0.1 run function {NS}:tool/ray",
])
fn("tool/hit", [
    "scoreboard players set @s astral.tok 1",
    f"execute if block ~ ~ ~ #{NS}:tree_logs run scoreboard players set @s astral.tok 2",
    "tag @s add astral.me",
    f"execute align xyz summon minecraft:marker run function {NS}:tool/store",
    "tag @s remove astral.me",
])
fn("tool/store", [
    "execute store result score @a[tag=astral.me,limit=1] astral.tx run data get entity @s Pos[0]",
    "execute store result score @a[tag=astral.me,limit=1] astral.ty run data get entity @s Pos[1]",
    "execute store result score @a[tag=astral.me,limit=1] astral.tz run data get entity @s Pos[2]",
    "kill @s",
])
fn("tool/broke", [
    "scoreboard players reset @s astral.dr",
    "scoreboard players reset @s astral.cs",
    f"execute if predicate {NS}:sneaking run return 0",
    # Zonas protegidas: la misma lista que gameplay.py (mazmorras con sus mundos actuales).
    *[f'execute if dimension minecraft:{w} run return 0' for w in __import__('gameplay').PROTECTED],
    # Cavernas de Cristal: el area la pica AstralCavernas (rompe todo, como el jugador).
    f"execute if dimension minecraft:{CAVERNAS.WORLD} run return 0",
    f"execute if dimension minecraft:{VACIO.WORLD} run return 0",   # Vacio Estelar: area de AstralVacio
    "execute if score @s astral.tok matches ..0 run return 0",
    f"execute store result storage {NS}:tmp tool.x int 1 run scoreboard players get @s astral.tx",
    f"execute store result storage {NS}:tmp tool.y int 1 run scoreboard players get @s astral.ty",
    f"execute store result storage {NS}:tmp tool.z int 1 run scoreboard players get @s astral.tz",
    f"function {NS}:tool/at with storage {NS}:tmp tool",
])
fn("tool/at", [
    f"$execute positioned $(x) $(y) $(z) if block ~ ~ ~ #{NS}:ray_pass run function {NS}:tool/do",
])
fn("tool/do", [
    "execute if entity @s[tag=astral.mines] run return 0",
    f"execute if items entity @s weapon.mainhand {DRILL_SEL} run return run function {NS}:tool/drill",
    f"execute if score @s astral.tok matches 2 if items entity @s weapon.mainhand {SAW_SEL} run function {NS}:tool/saw",
])
# --- taladro: el plano depende de hacia donde miras
fn("tool/drill", [
    f"execute store result score #a astral.tmp run data get entity @s SelectedItem.components.\"minecraft:custom_data\".{NS}.area",
    "execute if score #a astral.tmp matches ..1 run return 0",
    f"execute if entity @s[x_rotation=50..90] run return run function {NS}:tool/d/down",
    f"execute if entity @s[x_rotation=-90..-50] run return run function {NS}:tool/d/up",
    "# si el bloque esta a la altura de tus pies, el area crece hacia arriba",
    "execute store result score #py astral.tmp run data get entity @s Pos[1]",
    "scoreboard players set #up astral.tmp 0",
    "execute if score @s astral.ty <= #py astral.tmp run scoreboard players set #up astral.tmp 1",
    "scoreboard players set #v astral.tmp 0",
    "execute if entity @s[x_rotation=50..90] run scoreboard players set #v astral.tmp 1",
    "execute if entity @s[x_rotation=-90..-50] run scoreboard players set #v astral.tmp 1",
    f"execute if entity @s[y_rotation=-45..45] run return run function {NS}:tool/d/s",
    f"execute if entity @s[y_rotation=45..135] run return run function {NS}:tool/d/w",
    f"execute if entity @s[y_rotation=-135..-45] run return run function {NS}:tool/d/e",
    f"execute unless entity @s[y_rotation=-135..135] run function {NS}:tool/d/n",
    "playsound minecraft:block.stone.break block @a ~ ~ ~ 0.8 0.8",
])
# Mark only entities created by this synchronous loot command, never player drops.
fn("tool/bosque_loot", [
    'tag @e[type=minecraft:item,distance=..2] add ab.older',
    'loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand',
    'tag @e[type=minecraft:item,distance=..2,tag=!ab.older] add ab.saw',
    'execute as @e[type=minecraft:item,distance=..2,tag=ab.saw,tag=!ab.older] run data merge entity @s {PickupDelay:32767s,Item:{components:{"minecraft:custom_data":{ab_saw:1b}}}}',
    'tag @e[type=minecraft:item,distance=..2,tag=ab.older] remove ab.older',
])
fn("tool/mine", [
    f"execute unless block ~ ~ ~ #{NS}:drillable unless block ~ ~ ~ #{NS}:tree_logs run return 0",
    # Menas del Oceano Astral: solo taladro de amatista (tier 3) o mejor (oceano_items.py).
    *__import__('oceano_items').drill_guard(),
    # Vetas de las Cavernas de Cristal (cavernas.py): taladro tier 4+ y conteo para comisiones.
    *CAVERNAS.tool_mine_lines(),
    *VACIO.tool_mine_lines(),
    'execute if dimension minecraft:astral_bosque run function astral:tool/bosque_loot',
    'execute unless dimension minecraft:astral_bosque run loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand',
    "particle minecraft:poof ~0.5 ~0.5 ~0.5 0.2 0.2 0.2 0.01 2",
    # En el Oceano Astral no puede quedar aire: el hueco se llena de agua.
    "execute if dimension minecraft:oceano run return run setblock ~ ~ ~ minecraft:water",
    "setblock ~ ~ ~ minecraft:air",
])
for vertical_name, direction in [('down',-1),('up',1)]:
    # El bloque inicial ya lo rompio el jugador. Mirando vertical: columna bajo los pies/encima.
    fn('tool/d/'+vertical_name,[
        f'execute if score #a astral.tmp matches {minimum}.. positioned ~ ~{direction*depth} ~ '
        f'if block ~ ~ ~ #{NS}:drillable run function {NS}:tool/mine'
        for depth,minimum in [(1,2),(2,4),(3,5)]])
for f, (F, R) in FACING.items():
    disp = []
    for a in range(2, 6):
        for vert in (0, 1):
            for up in ((0, 1) if not vert else (0,)):
                us, vs = area_ranges(a, up, vert)
                lines = []
                for u in us:
                    for v in vs:
                        if (u, v) == (0, 0):
                            continue
                        if vert:
                            d = [u * R[k] + v * F[k] for k in range(3)]
                        else:
                            d = [u * R[k] + (v if k == 1 else 0) for k in range(3)]
                        lines.append(f"execute positioned ~{d[0]} ~{d[1]} ~{d[2]} if block ~ ~ ~ #{NS}:drillable "
                                     f"run function {NS}:tool/mine")
                if a == 2 and not vert:
                    # 24/11 (dueno): 2x1 con el compañero ya vacio (picando un escalon, zanja): rompe el del otro lado.
                    other = -1 if up else 1
                    lines = [lines[0].replace(" run function", " run return run function"),
                             f"execute positioned ~ ~{other} ~ if block ~ ~ ~ #{NS}:drillable run function {NS}:tool/mine"]
                name = f"tool/d/{f}{a}{'v' if vert else 'h'}{up}"
                fn(name, lines)
                cond = f"if score #a astral.tmp matches {a} if score #v astral.tmp matches {vert}"
                if not vert:
                    cond += f" if score #up astral.tmp matches {up}"
                disp.append(f"execute {cond} run function {NS}:{name}")
    fn(f"tool/d/{f}", disp)

# --- motosierra: sigue el tronco hacia arriba y a los costados
LEAF_CHECK = {"condition": "minecraft:any_of", "terms": [
    {"condition": "minecraft:location_check", "offsetX": dx, "offsetY": dy, "offsetZ": dz,
     "predicate": {"block": {"blocks": "#minecraft:leaves", "state": {"persistent": "false"}}}}
    for dy in range(0, 31) for dx in range(-2, 3) for dz in range(-2, 3) if not (dy == 0 and abs(dx) < 2 and abs(dz) < 2)]}
put(f"data/{NS}/predicate/natural_tree.json", LEAF_CHECK)
fn("tool/saw", [
    f"execute store result score #b astral.tmp run data get entity @s SelectedItem.components.\"minecraft:custom_data\".{NS}.chain",
    "execute if score #b astral.tmp matches ..0 run return 0",
    "# solo arboles naturales: tiene que haber hojas que no puso un jugador",
    f"execute unless predicate {NS}:natural_tree run return 0",
    "execute if score #b astral.tmp matches 300.. run scoreboard players set #b astral.tmp 300",
    f"function {NS}:tool/chain",
    "playsound minecraft:block.wood.break block @a ~ ~ ~ 1 0.7",
])
NEIGH = [(0, 1, 0)] + [(dx, 1, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)] + \
        [(dx, 0, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dz) != (0, 0)] + \
        [(dx, -1, dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)]
fn("tool/chain", [
    f"execute if score #b astral.tmp matches 1.. positioned ~{dx} ~{dy} ~{dz} if block ~ ~ ~ #{NS}:tree_logs "
    f"run function {NS}:tool/cut" for (dx, dy, dz) in NEIGH])
fn("tool/cut", [
    "scoreboard players remove #b astral.tmp 1",
    f"function {NS}:tool/mine",
    f"function {NS}:tool/chain",
])

# ---------------------------------------------------------------------------
# load / loops
# ---------------------------------------------------------------------------
load = [
    "scoreboard objectives add astral.tmp dummy",
    "scoreboard objectives add astral.const dummy",
    "scoreboard objectives add astral.hp dummy",
    "scoreboard objectives add astral.cd dummy",
    "scoreboard objectives add astral.grap dummy",
    "scoreboard objectives add astral.bleed dummy",
    "scoreboard objectives add astral.bleedd dummy",
    "scoreboard objectives add astral.remd dummy",
    "scoreboard objectives add astral.ht dummy",
    "scoreboard objectives add astral.wt dummy",
    "scoreboard objectives add astral.at dummy",
    "scoreboard objectives add astral.mt dummy",
    "scoreboard objectives add astral.rem dummy",
    "scoreboard objectives add astral.lvl dummy",
    "scoreboard objectives add astral.draw dummy",
    "scoreboard objectives add astral.use minecraft.used:minecraft.carrot_on_a_stick",
    "scoreboard objectives add astral.m_es minecraft.mined:minecraft.end_stone",
    "scoreboard objectives add astral.m_ch minecraft.mined:minecraft.chorus_plant",
    "scoreboard objectives add astral.guia trigger",
    "scoreboard objectives add astral.forja trigger",
    "scoreboard objectives add astral.dr minecraft.used:minecraft.netherite_pickaxe",
    "scoreboard objectives add astral.cs minecraft.used:minecraft.netherite_axe",
    "scoreboard objectives add astral.tok dummy",
    "scoreboard objectives add astral.tx dummy",
    "scoreboard objectives add astral.ty dummy",
    "scoreboard objectives add astral.tz dummy",
] + [f"scoreboard objectives add {o} {c}" for (o, c) in log_objs] + [
    f"scoreboard objectives add {o} {c}" for (o, c, _d) in place_objs] + [
    "scoreboard objectives add astral.dlog dummy", "scoreboard objectives add astral.des dummy"] + [
    "scoreboard players set #2 astral.const 2",
    "scoreboard players set #3 astral.const 3",
    "scoreboard players set #5 astral.const 5",
    "scoreboard players set #7 astral.const 7",
    "scoreboard players set #10 astral.const 10",
    "scoreboard players set #100 astral.const 100",
    "scoreboard players set #10000 astral.const 10000",
    "scoreboard players set #1000 astral.const 1000",
    f"schedule function {NS}:loop/t5 5t replace",
    f"schedule function {NS}:loop/t10 10t replace",
    f"schedule function {NS}:loop/t20 20t replace",
    f"schedule function {NS}:tanda4b/asura/tick 200t replace",   # 23/11: mena de Asura en el End
]

# ---------------------------------------------------------------------------
# Bonus de set por piezas (SET_BONUS en items.py): se revisa cada segundo
# ---------------------------------------------------------------------------
SLOTS4 = ["armor.head", "armor.chest", "armor.legs", "armor.feet"]
set_check, set_kill = [], []
for set_id, bonus in SET_BONUS.items():
    obj = f"astral.set_{set_id[:3]}"
    load.append(f"scoreboard objectives add {obj} dummy")
    set_check.append(f"scoreboard players set @s {obj} 0")
    for sl in SLOTS4:
        set_check.append(f'execute if items entity @s {sl} *[minecraft:custom_data~{{{NS}:{{set:"{set_id}"}}}}] '
                         f"run scoreboard players add @s {obj} 1")
    for npz, (desc, fx) in bonus.items():
        if "attr" in fx:
            at, amount, op = fx["attr"]
            mid = f"{NS}:set_{set_id}_{npz}"
            set_check += [f"attribute @s {at} modifier remove {mid}",
                          f"execute if score @s {obj} matches {npz}.. run attribute @s {at} modifier add {mid} {amount} {op}"]
        for (eff, secs, lvl) in fx.get("kill", []):
            set_kill.append(f"execute if score @s {obj} matches {npz}.. run effect give @s minecraft:{eff} {secs} {lvl}")
fn("set/check", set_check)
from oficios import check_lines as oficios_check, load_lines as oficios_load
fn("oficios/check", oficios_check())
load += oficios_load()
fn("set/kill", set_kill + ["scoreboard players set @s astral.kills 0"])
load.append("scoreboard objectives add astral.kills minecraft.custom:minecraft.mob_kills")

# ---------------------------------------------------------------------------
# Mejora +1..+10 (MEJORAS en items.py). La llama el Herrero del lobby (MythicMobs) como el jugador:
#   mejora/ver   -> dice cuanto cuesta y deja astralmejn = nivel siguiente (0 si no se puede)
#   mejora/hacer -> gasta los materiales, tira la probabilidad y si sale bien deja astralmejok = nivel
# La plata la cobra MythicMobs solo si astralmejok quedo en ese nivel.
# ---------------------------------------------------------------------------
load += ["scoreboard objectives add astralmejn dummy", "scoreboard objectives add astralmejok dummy"]
HAND = "weapon.mainhand"
KIND = ["scoreboard players set #k astral.tmp 0",
        f'execute if items entity @s {HAND} *[minecraft:custom_data~{{{NS}:{{type:"weapon"}}}}] '
        f"unless items entity @s {HAND} minecraft:carrot_on_a_stick run scoreboard players set #k astral.tmp 1",
        f'execute if items entity @s {HAND} *[minecraft:custom_data~{{{NS}:{{type:"staff"}}}}] run scoreboard players set #k astral.tmp 1',
        f'execute if items entity @s {HAND} *[minecraft:custom_data~{{{NS}:{{type:"armor"}}}}] run scoreboard players set #k astral.tmp 2']
ver = ["scoreboard players set @s astralmejn 0", "scoreboard players set @s astralmejok 0"] + KIND + [
       "execute if score #k astral.tmp matches 0 run return run tellraw @s " + json.dumps(
           [txt("Herrero: ", "gold"), txt("agarra en la mano un arma o una pieza de armadura de AstralRPG. "
                                          "(Los bastones de Mago no se mejoran aca.)", "gray")]),
       "scoreboard players set #l astral.tmp 0"]
for L in range(1, 11):
    for mej in ("mejora_arma", "mejora_armadura"):
        ver.append(f'execute if items entity @s {HAND} *[minecraft:enchantments~[{{enchantments:"{NS}:{mej}",levels:{L}}}]] '
                   f"run scoreboard players set #l astral.tmp {L}")
ver += ["execute if score #l astral.tmp matches 10.. run return run tellraw @s " + json.dumps(
            [txt("Herrero: ", "gold"), txt("este item ya esta en +10, no se puede mejorar mas.", "gray")]),
        "scoreboard players operation #n astral.tmp = #l astral.tmp",
        "scoreboard players add #n astral.tmp 1"]
for L in range(1, 11):
    ver.append(f"execute if score #n astral.tmp matches {L} run function {NS}:mejora/ver/{L}")
fn("mejora/ver", ver)
hacer = []
for L, (plata, prob, mats) in MEJORAS.items():
    pct = int(round(prob * 100))
    costo = ", ".join(f"{n}x {ITEMS[m]['name']}" for m, n in mats)
    bonus = (f"+{round((MEJORA_DANO[L - 1] - 1) * 100)}% de dano (arma) o +{MEJORA_VIDA[L - 1]:g}% de vida por pieza (armadura)")
    lines = ["scoreboard players set #falta astral.tmp 0",
             "tellraw @s " + json.dumps([txt("Herrero: ", "gold"), txt(f"mejora a +{L}", "yellow", bold=True),
                                         txt(f" cuesta {plata}$ y {costo}. Exito: {pct}%. ", "gray"),
                                         txt(f"Da {bonus}.", "dark_gray")])]
    for m, n in mats:
        lines += [f'execute store result score #c astral.tmp run clear @s *[minecraft:custom_data~{{{NS}:{{id:"{m}"}}}}] 0',
                  f"execute if score #c astral.tmp matches ..{n - 1} run scoreboard players set #falta astral.tmp 1"]
    lines += ["execute if score #falta astral.tmp matches 1 run return run tellraw @s " + json.dumps(
                  txt("Te faltan materiales para esta mejora.", "red")),
              f"scoreboard players set @s astralmejn {L}"]
    fn(f"mejora/ver/{L}", lines)
    h = [f'clear @s *[minecraft:custom_data~{{{NS}:{{id:"{m}"}}}}] {n}' for m, n in mats]
    if L >= 5:
        h.append(f"function {NS}:quest/event/upgrade")
    if prob >= 1:
        h.append(f"function {NS}:mejora/ok/{L}")
    else:
        h += [f"execute store success score #ok astral.tmp if predicate {chance(prob)}",
              f"execute if score #ok astral.tmp matches 1 run return run function {NS}:mejora/ok/{L}",
              "playsound minecraft:block.anvil.destroy player @s ~ ~ ~ 1 1",
              "tellraw @s " + json.dumps([txt("Herrero: ", "gold"), txt(f"la mejora a +{L} fallo. ", "red"),
                                          txt("Perdiste los materiales, pero tu item quedo igual y no se cobro la plata.", "gray")])]
    fn(f"mejora/n/{L}", h)
    ok = [f"execute if score #k astral.tmp matches 1 run item modify entity @s {HAND} "
          f'{{function:"minecraft:set_enchantments",enchantments:{{"{NS}:mejora_arma":{L}}},add:false}}',
          f"execute if score #k astral.tmp matches 2 run item modify entity @s {HAND} "
          f'{{function:"minecraft:set_enchantments",enchantments:{{"{NS}:mejora_armadura":{L}}},add:false}}',
          f"scoreboard players set @s astralmejok {L}",
          "playsound minecraft:block.anvil.use player @s ~ ~ ~ 1 1.2",
          "particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.6 0.4 0.3 40",
          "tellraw @s " + json.dumps([txt("Herrero: ", "gold"), txt(f"listo, tu item ahora es +{L}!", "green", bold=True)])]
    if L >= 7:
        ok.append('tellraw @a ["",{"text":"(!) ","color":"gold","bold":true},{"selector":"@s","color":"yellow"},'
                  + json.dumps({"text": f" mejoro un item a +{L} con el Herrero!", "color": "gray"}) + "]")
    # Armas y armaduras: nombre con estrellas y (+N) en la ficha.
    ok += [f'data modify storage {NS}:tmp ficha.id set from entity @s SelectedItem.components."minecraft:custom_data".astral.id',
           f'function {NS}:ficha/apply/{L} with storage {NS}:tmp ficha']
    fn(f"ficha/apply/{L}", [f'$item modify entity @s weapon.mainhand astral:ficha/$(id)/{L}'])
    fn(f"mejora/ok/{L}", ok)
    hacer.append(f"execute if score @s astralmejn matches {L} run function {NS}:mejora/n/{L}")
# hacer vuelve a mirar que item tenes en la mano (#k) antes de tocarlo
fn("mejora/hacer", KIND + ["execute if score #k astral.tmp matches 0 run return 0"] + hacer)
load.append("scoreboard objectives add astraldef dummy")
load.append("scoreboard objectives add astral.protdef dummy")
load.append("execute unless score #pub astral.protdef matches -1..1 run scoreboard players set #pub astral.protdef 0")
load.append("scoreboard objectives add astral.filo dummy")
load.append("execute unless score #pub astral.filo matches -1..1 run scoreboard players set #pub astral.filo 0")
load.append("scoreboard objectives add astral.vandef dummy")
load.append("scoreboard objectives add astral.vanp dummy")
load.append("execute unless score #pub astral.vandef matches -1..1 run scoreboard players set #pub astral.vandef 0")
# Nivel de efectos visuales por jugador (plugin AstralEfectos): 0 Bajo, 1 Medio, 2 Alto.
load.append("scoreboard objectives add astral.fx dummy")
load.append("scoreboard objectives add astral.defp dummy")
load.append(f"function {NS}:cavernas/load")   # cavernas.py: conteo de vetas para comisiones
fn("load", load)
fn("tick", [
    "# taladros y motosierras: primero ver si rompiste el bloque apuntado, despues apuntar de nuevo",
    f"execute as @a[scores={{astral.dr=1..}}] at @s run function {NS}:tool/broke",
    f"execute as @a[scores={{astral.cs=1..}}] at @s run function {NS}:tool/broke",
    f"execute as @a[gamemode=!spectator] if items entity @s weapon.mainhand {DRILL_SEL} at @s run function {NS}:tool/aim",
    f"execute as @a[gamemode=!spectator] if items entity @s weapon.mainhand {SAW_SEL} at @s run function {NS}:tool/aim",
    f"execute as @a[scores={{astral.use=1..}}] at @s run function {NS}:use/main",
    f"execute as @a[scores={{astral.forja=1..}}] at @s run function {NS}:forge/craft",
    "scoreboard players remove @a[scores={astral.cd=1..}] astral.cd 1",
    f"execute as @a[scores={{astral.grap=1..}}] run function {NS}:grapple/tick",
    # Solo busca flechas si alguna se disparo desde la ultima vez (bow/tag marca #flechas).
    "execute store success score #flechas_ver astral.tmp if score #flechas astral.tmp matches 1..",
    "scoreboard players set #flechas astral.tmp 0",
    f"execute if score #flechas_ver astral.tmp matches 1 as @e[type=#minecraft:arrows,tag=astral.bowshot] at @s run function {NS}:bow/norm",
    "# si soltaste el arco, se reinicia la carga",
    "scoreboard players set @a[tag=!astral.drew,scores={astral.draw=1..}] astral.draw 0",
    "tag @a remove astral.drew",
])
# Mochilas (ExpendableBackpacks, cabeza con dato propio): no se usan de casco (pedido 12/11/2026).
MOCHILA_CABEZA = 'equipment.head.components."minecraft:custom_data".PublicBukkitValues."expendablebackpacks:backpack_uuid"'
fn("mochila/cabeza", [
    # El objeto entero (contenido, UUID y nivel) vuelve al inventario; si esta lleno queda a los pies, solo para el dueno.
    'execute at @s run summon minecraft:item ~ ~1 ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0s,Tags:["astral.mochila"]}',
    f"execute at @s as @e[type=minecraft:item,tag=astral.mochila,distance=..3,limit=1,sort=nearest] run data modify entity @s Item set from entity @p[tag=astral.mochcab] equipment.head",
    f"execute at @s as @e[type=minecraft:item,tag=astral.mochila,distance=..3,limit=1,sort=nearest] run data modify entity @s Owner set from entity @p[tag=astral.mochcab] UUID",
    "execute at @s run tag @e[type=minecraft:item,tag=astral.mochila,distance=..3] remove astral.mochila",
    "item replace entity @s armor.head with minecraft:air",
    "tellraw @s " + json.dumps(txt("La mochila no se puede usar en la cabeza: volvio a tu inventario.", "yellow")),
])
fn("mochila/check", ["tag @s add astral.mochcab", f"function {NS}:mochila/cabeza", "tag @s remove astral.mochcab"])
fn("loop/t5", [
    f"execute as @a if data entity @s {MOCHILA_CABEZA} run function {NS}:mochila/check",
    f"execute as @a run function {NS}:player/hp",
    f"execute as @a[scores={{astral.kills=1..}}] run function {NS}:set/kill",
    f"schedule function {NS}:loop/t5 5t replace",
])
fn("player/hp", [
    "execute store result score @s astral.hp run data get entity @s Health 100",
    "execute store result score #m astral.tmp run attribute @s minecraft:max_health get 1",
    "execute if score #m astral.tmp matches ..0 run scoreboard players set #m astral.tmp 1",
    "scoreboard players operation @s astral.hp /= #m astral.tmp",
])
log_cond = " ".join([])
t10 = [
    f"execute as @a run function {NS}:player/def",
    f"execute as @a[tag=!astral.vida{VIDA_JUGADOR_BASE}] run function {NS}:player/vida_base",
    *[f"execute as @a[scores={{{o}=1..}}] at @s run function {NS}:mine/placed" for (o, _c, _d) in place_objs],
    f"execute as @a[scores={{astral.m_es=1..}}] at @s run function {NS}:mine/endstone",
    f"execute as @a[scores={{astral.m_ch=1..}}] at @s run function {NS}:mine/chorus",
]
for (o, _) in log_objs:
    t10.append(f"execute as @a[scores={{{o}=1..}}] at @s run function {NS}:mine/log")
t10 += [
    "scoreboard players enable @a astral.guia",
    "scoreboard players enable @a astral.forja",
    f"execute as @a[scores={{astral.guia=1..}}] run function {NS}:guide/give",
    f"schedule function {NS}:loop/t10 10t replace",
]
fn("loop/t10", t10)
fn("loop/t20", [
    f"execute as @e[scores={{astral.bleed=1..}}] at @s run function {NS}:fx/bleed_tick",
    f"execute as @a run function {NS}:upgrade/check",
    f"execute as @a run function {NS}:set/check",
    f"execute as @a run function {NS}:oficios/check",
    f"execute as @e[scores={{astral.rem=1..}}] at @s run function {NS}:fx/remate_tick",
    f"execute as @a run function {NS}:player/lvl",
    f"execute as @e[type=#{NS}:escalable,tag=!astral.seen] at @s run function {NS}:mob/roll",
    f"execute as @e[tag=astral.hpname] at @s if entity @a[distance=..32] run function {NS}:mob/vida",
    f"function {NS}:elite/fx",
    f"schedule function {NS}:loop/t20 20t replace",
])
put("data/minecraft/tags/function/load.json", {"values": [f"{NS}:load"]})
put("data/minecraft/tags/function/tick.json", {"values": [f"{NS}:tick"]})

# chance predicates
for key, p in CHANCES:
    put(f"data/{NS}/predicate/chance/{key}.json", {"condition": "minecraft:random_chance", "chance": p})

put("pack.mcmeta", {"pack": {"description": [txt("AstralRPG", "light_purple"), txt(" - items, clases y Forja Astral", "gray")],
                             "min_format": [DATA_FORMAT, 1], "max_format": [DATA_FORMAT, 1]}})

from misiones import generate as generate_quests
generate_quests(files, ITEMS)
from ambiente import generate as generate_ambience
generate_ambience(files)
from services import generate as generate_services
generate_services(files, ITEMS)
from gameplay import apply as apply_gameplay
apply_gameplay(files, ITEMS, ITEM_VERSIONS, OLD_PREDS)
from ficha import modifier as ficha_modifier, render as render_ficha
for iid, source in FICHAS.items():
    for L in (range(11) if ITEMS[iid]["mejorable"] else [0]):
        put(f'data/{NS}/item_modifier/ficha/{iid}/{L}.json', ficha_modifier(source, L))
        # La migración por slot conserva encantamientos, desgaste y todos los demás componentes.
        upgrade = json.loads(files[f'data/{NS}/item_modifier/upgrade/{iid}.json'])
        upgrade[0]['components'].update(render_ficha(source, L))
        put(f'data/{NS}/item_modifier/upgrade/{iid}/{L}.json', upgrade)
# Forja en el lugar: sale reparada, sin componentes que la pieza nueva no tiene, y conserva encantamientos.
for _out, _prev in sorted(CHAIN):
    _gone = {"!minecraft:damage": {}}
    for _k in ITEMS[_prev]["components"]:
        if _k not in ITEMS[_out]["components"] and _k != "minecraft:enchantments":
            _gone["!" + _k] = {}
    for L in (range(11) if ITEMS[_out]["mejorable"] else [0]):
        _src = (f'data/{NS}/item_modifier/upgrade/{_out}/{L}.json' if _out in FICHAS
                else f'data/{NS}/item_modifier/upgrade/{_out}.json')
        put(f'data/{NS}/item_modifier/forja/{_out}/{_prev}/{L}.json',
            [{"function": "minecraft:set_components", "components": _gone}] + json.loads(files[_src]))
from estrella_menu import generate as generate_menu_star
generate_menu_star(files)
from special_weapons import generate as generate_special_weapons
from oceano_items import CLONES as OCEANO_CLONES
generate_special_weapons(files, {**REQUIREMENTS, **{
    iid: REQUIREMENTS[source] for iid, (source, _, _) in OCEANO_CLONES.items()}})
from mobs.tanda2 import generate as generate_dungeon_waves
generate_dungeon_waves(files)
from tanda4b_world import generate as generate_tanda4b_world
generate_tanda4b_world(files)
from oceano_items import generate as generate_oceano_items
generate_oceano_items(files)
CAVERNAS.tabla_note_block(files)
VACIO.tabla_note_block(files)
from santuario_azeroth import generate as generate_sanctuary
generate_sanctuary(files)
from infinita import generate as generate_infinita
generate_infinita(files)  # Mazmorra Infinita: tier de los mobs (inf/apply)

# ---------------------------------------------------------------------------
# Escribir
# ---------------------------------------------------------------------------
from tanda_xp import generate as generate_xp
generate_xp(files)
from correcciones_goblin import datapack
datapack(files)
from spell_perfora import generate as generate_spell_perfora
generate_spell_perfora(files)
from encmagia import generate as generate_encmagia
generate_encmagia(files)

from guia_atlas import generate as generate_guia_atlas
generate_guia_atlas(files, ITEMS, RID, item_stack, ing_pred, ing_name)

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
for path, content in files.items():
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
zpath = OUT + ".zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for path, content in sorted(files.items()):
        z.writestr(path, content)
print(f"{len(ITEMS)} items, {len(RECIPES)} recetas, {len(files)} archivos -> {zpath}")
