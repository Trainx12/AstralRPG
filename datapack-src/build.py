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

from items import (SKILLS, MATERIALS, MOB_DROPS, MAT_RECIPES, PIECES, PIECE_SLOT, ARMOR_VALUES,
                   TOUGHNESS, ARMOR_SETS, ROMAN, SWORDS, AXES, STAFFS, SCYTHES, BOWS)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "build", "AstralRPG-Items")
NS = "astral"
DATA_FORMAT = 101  # Minecraft 26.1.x

# ID del encantamiento de mineria 3x3 de ExcellentEnchants (None = no se usa)
TUNNEL_ENCHANT = os.environ.get("ASTRAL_TUNNEL", "excellentenchants:tunnel")

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
    if skill:
        pdc[f"auraskills:{kind}_requirements"] = {f"auraskills:{skill}": int(level)}
    if traits:
        pdc[f"auraskills:{kind}_trait_modifiers"] = [
            {"auraskills:trait": f"auraskills/{t}", "auraskills:value": Dbl(v), "auraskills:operation": op}
            for (t, v, op) in traits]
    return pdc


def add_item(item_id, base, name, color, lore, astral_data, extra=None, pdc=None, model=None,
             glint=None, kind="item"):
    custom = {NS: dict({"id": item_id}, **astral_data)}
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
    ITEMS[item_id] = {"base": base, "components": comps, "name": name, "color": color, "kind": kind}


def req_line(skill, level):
    return txt(f"Requiere: {SKILLS[skill]} {level}", "red")


# ---------------------------------------------------------------------------
# MATERIALES
# ---------------------------------------------------------------------------
for mid, (name, color, model, glint, desc) in MATERIALS.items():
    add_item(mid, "minecraft:paper", name, color,
             [txt(desc), txt("Material de AstralRPG", "dark_gray")],
             {"type": "material"}, model=model, glint=glint, kind="material")

# Gancho de escalada
add_item("gancho", "minecraft:carrot_on_a_stick", "Gancho de Escalada", "#d0d0d0",
         [txt("Click derecho apuntando a un bloque"), txt("para impulsarte hacia el (hasta 32 bloques)."),
          txt("Agachate para soltarte.", "dark_gray")],
         {"type": "hook"}, model="minecraft:fishing_rod",
         extra={"minecraft:enchantments": {f"{NS}:gancho": 1},
                "minecraft:tooltip_display": {"hidden_components": ["minecraft:enchantments"]},
                "minecraft:max_stack_size": 1})
RECIPES.append(("gancho", 1, [("v", "minecraft:fishing_rod", 1), ("v", "minecraft:iron_ingot", 2),
                              ("v", "minecraft:string", 2)], "Especiales"))

for (out, n, ings) in MAT_RECIPES:
    RECIPES.append((out, n, ings, "Materiales"))


# ---------------------------------------------------------------------------
# ARMADURAS
# ---------------------------------------------------------------------------
def armor_attrs(item_id, piece, mat, stats, extra_armor=0, tough_extra=0):
    slot = PIECE_SLOT[piece]
    mods = []

    def m(attr, amount, op, suffix):
        mods.append({"type": f"minecraft:{attr}", "id": f"{NS}:{item_id}.{suffix}", "amount": round(amount, 4),
                     "operation": op, "slot": slot})

    m("armor", ARMOR_VALUES[mat][piece] + extra_armor, "add_value", "armor")
    t = TOUGHNESS[mat] + tough_extra
    if t:
        m("armor_toughness", t, "add_value", "tough")
    if mat == "netherite":
        m("knockback_resistance", 0.1, "add_value", "kbn")
    q = 4.0
    if "hp" in stats:
        m("max_health", stats["hp"] / 100 / q, "add_multiplied_total", "hp")
    if "dmg" in stats:
        m("attack_damage", stats["dmg"] / 100 / q, "add_multiplied_total", "dmg")
    if "def" in stats:
        m("armor", stats["def"] / 100 / q, "add_multiplied_total", "def")
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
            lore.append(req_line(sdef["skill"], tier["lvl"]))
            extra = {"minecraft:attribute_modifiers":
                     armor_attrs(iid, piece, mat, {k: v for k, v in stats.items() if k not in chest_only},
                                 tier.get("extra_armor", 0), tier.get("tough", 0))}
            if mat == "leather":
                extra["minecraft:dyed_color"] = sdef["dye"][ti]
                extra["minecraft:max_damage"] = {"helmet": 55, "chestplate": 80, "leggings": 75, "boots": 65}[piece] * (3 + ti * 2)
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
            if "mregen" in stats:
                traits.append(("mana_regen", stats["mregen"] / 4, "add_percent"))
            if "crit" in stats:
                traits.append(("crit_chance", stats["crit"] / 4, "add"))
            pdc = aura_pdc("armor", sdef["skill"], tier["lvl"], traits)
            astral = {"type": "armor", "set": set_id, "tier": tnum, "piece": piece}
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
                traits=None, more_lore=None):
    lore = [txt(f"{clase} {ROMAN[tier - 1]}", color)] + [txt(d, "gray") for d in desc]
    if more_lore:
        lore += more_lore
    lore.append(req_line(skill, lvl))
    extra = {}
    if mods is not None:
        extra["minecraft:attribute_modifiers"] = mods
    if ench:
        extra["minecraft:enchantments"] = ench
    add_item(iid, base, name, color, lore, dict({"type": "weapon", "tier": tier}, **astral), extra=extra,
             pdc=aura_pdc("item", skill, lvl, traits), model=model, kind="weapon")


FX_ENCH = {"lifesteal": "robo_vida", "furia": "furia", "remate": "remate", "verdugo": "verdugo",
           "sangrado": "sangrado", "hendidura": "hendidura", "maldicion": "maldicion", "cono": "cono"}


def fx_to_ench(fx, exec_kind=None):
    e = {}
    for k, v in fx.items():
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
    weapon_item(iid, s["base"], s["name"], BERS, "Espada Berserker", t, [f"+{s['bonus']}% de dano"] + s["desc"],
                "forging", s["lvl"], weapon_mods(iid, dmg, 1.6, extra), fx_to_ench(s["fx"]), {"w": "sword"})
    ings = list(s["cost"]) if t == 1 else [("c", f"espada_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas Berserker"))

for i, s in enumerate(AXES):
    t = i + 1
    iid = f"hacha_{t}"
    dmg = s["dmg"] * (1 + s["bonus"] / 100)
    weapon_item(iid, s["base"], s["name"], BERS, "Hacha Berserker", t, [f"+{s['bonus']}% de dano"] + s["desc"],
                "forging", s["lvl"], weapon_mods(iid, dmg, s["spd"]), fx_to_ench(s["fx"]), {"w": "axe"})
    ings = list(s["cost"]) if t == 1 else [("c", f"hacha_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas Berserker"))

MAGO = ARMOR_SETS["mago"]["color"]
for i, s in enumerate(STAFFS):
    t = i + 1
    iid = f"baston_{t}"
    traits = [("max_mana", s["mana"], "add")]
    if s.get("mregen"):
        traits.append(("mana_regen", s["mregen"], "add_percent"))
    desc = [f"+{s['mana']} mana", f"+{s['mdmg']}% dano magico", "Click derecho: proyectil arcano"] + s["desc"]
    astral = {"w": "staff", "type": "staff", "spell": int(s["spell"] * 100), "mdmg": s["mdmg"] * 100,
              "cd": s["cd"], "cdr": s.get("cdr", 0) * 100}
    lore_extra = [txt(f"Dano del hechizo: {s['spell']}", "light_purple")]
    add_item(iid, "minecraft:carrot_on_a_stick", s["name"], MAGO,
             [txt(f"Baston de Mago {ROMAN[i]}", MAGO)] + [txt(d) for d in desc] + lore_extra + [req_line("sorcery", s["lvl"])],
             astral, pdc=aura_pdc("item", "sorcery", s["lvl"], traits), model=s["model"], glint=t >= 2,
             extra={"minecraft:max_stack_size": 1}, kind="weapon")
    ings = list(s["cost"]) if t == 1 else [("c", f"baston_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas de Mago"))

for i, s in enumerate(SCYTHES):
    t = i + 1
    iid = f"guadana_{t}"
    ench = fx_to_ench(s["fx"])
    ench[f"{NS}:filo_arcano"] = t
    astral = {"w": "scythe"}
    if s.get("reset_cd"):
        astral["reset_cd"] = 1
    desc = ([f"+{s['mdmg']}% dano magico"] if s["mdmg"] else []) + s["desc"]
    weapon_item(iid, s["base"], s["name"], MAGO, "Guadana de Mago", t, desc, "sorcery", s["lvl"],
                weapon_mods(iid, s["dmg"], 1.3), ench, astral)
    ings = list(s["cost"]) if t == 1 else [("c", f"guadana_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Armas de Mago"))

ARQ = ARMOR_SETS["arquero"]["color"]
for i, s in enumerate(BOWS):
    t = i + 1
    iid = f"arco_{t}"
    desc = ([f"+{s['bonus']}% de dano"] if s["bonus"] else []) + [f"Mantene click derecho: dispara solo cada {[18, 15, 12, 10, 8][i] / 20:.2f}s".replace(".", ",")] + s["desc"]
    mods = None
    if s.get("spd"):
        mods = [{"type": "minecraft:movement_speed", "id": f"{NS}:{iid}.spd", "amount": s["spd"] / 100,
                 "operation": "add_multiplied_base", "slot": "mainhand"}]
    weapon_item(iid, "minecraft:bow", s["name"], ARQ, "Arco de Arquero", t, desc, "archery", s["lvl"], mods,
                {f"{NS}:punteria": t}, {"w": "bow", "draw": s["draw"]})
    ings = list(s["cost"]) if t == 1 else [("c", f"arco_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Arcos"))

# Especiales
add_item("guadana_umbria", "minecraft:netherite_hoe", "Guadana Umbria", "#7d3cff",
         [txt("Clase Segador", "#7d3cff"), txt("Dano en area en cono"), txt("Roba vida"), req_line("sorcery", 16)],
         {"type": "weapon", "w": "scythe"},
         extra={"minecraft:attribute_modifiers": weapon_mods("guadana_umbria", 9, 1.2),
                "minecraft:enchantments": {f"{NS}:cono": 1, f"{NS}:robo_vida": 3}},
         pdc=aura_pdc("item", "sorcery", 16), kind="weapon")
RECIPES.append(("guadana_umbria", 1, [("c", "gema_umbria", 3), ("c", "shadowsteel", 2), ("c", "palo_reforzado", 1)], "Especiales"))

add_item("guantes_meteoro", "minecraft:paper", "Guantes de Puno Meteoro", "#ff8c1a",
         [txt("Clase Monje", "#ff8c1a"), txt("Tus golpes queman"), txt("Mucho mas dano que a mano limpia"),
          req_line("fighting", 12)],
         {"type": "weapon", "w": "gloves"}, model="minecraft:blaze_powder", glint=True,
         extra={"minecraft:attribute_modifiers": weapon_mods("guantes_meteoro", 7, 2.2),
                "minecraft:enchantments": {f"{NS}:igneo": 1}, "minecraft:max_stack_size": 1},
         pdc=aura_pdc("item", "fighting", 12), kind="weapon")
RECIPES.append(("guantes_meteoro", 1, [("c", "netherita_reforzada", 2), ("v", "minecraft:blaze_powder", 2),
                                        ("c", "gema_luminica", 1)], "Especiales"))

drill_ench = {"minecraft:efficiency": 5, "minecraft:unbreaking": 3}
if TUNNEL_ENCHANT:
    drill_ench[TUNNEL_ENCHANT] = 3
add_item("taladro_infernal", "minecraft:netherite_pickaxe", "Taladro Infernal", "#ff5a1f",
         [txt("Reemplaza al pico", "gray"), txt("Rompe en area 3x3", "gold"), req_line("mining", 18)],
         {"type": "tool"}, extra={"minecraft:enchantments": drill_ench},
         pdc=aura_pdc("item", "mining", 18), kind="weapon")
RECIPES.append(("taladro_infernal", 1, [("c", "shadowsteel", 4), ("c", "netherita_reforzada", 1),
                                         ("v", "minecraft:redstone_block", 2), ("v", "minecraft:blaze_rod", 1)], "Especiales"))


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
    ench[f"{NS}:empalar"] = t
    weapon_item(iid, s["base"], s["name"], "#ffb347", "Lanza de Combate", t,
                [f"+{s['bonus']} de dano por golpe"] + s["desc"], "fighting", s["lvl"], None, ench, {"w": "spear"})
    ings = list(s["cost"]) if t == 1 else [("c", f"lanza_{t - 1}", 1)] + s["cost"]
    RECIPES.append((iid, 1, ings, "Lanzas"))

# ---------------------------------------------------------------------------
# Texturas del resource pack (si el item tiene una, usa su modelo)
# ---------------------------------------------------------------------------
from textures import MATERIAL_TEX, BLOCK_ITEMS, WEAPON_TEX, BOW_TEX, GEN_WEAPON, GEN_ITEM, ARMOR_ITEMS
for _iid in list(MATERIAL_TEX) + list(BLOCK_ITEMS) + list(WEAPON_TEX) + list(BOW_TEX) + GEN_WEAPON + GEN_ITEM + ARMOR_ITEMS:
    ITEMS[_iid]["components"]["minecraft:item_model"] = f"{NS}:{_iid}"
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

# ---------------------------------------------------------------------------
# Loot tables de items (sirven para /loot y para el altar)
# ---------------------------------------------------------------------------
for iid, it in ITEMS.items():
    put(f"data/{NS}/loot_table/item/{iid}.json", {
        "type": "minecraft:command",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": it["base"], "functions": [
            {"function": "minecraft:set_components", "components": it["components"]}]}]}]})

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
    for (k, c, ident) in keys:
        SUBS.add(c)
        lines.append(f"execute as @e[type=minecraft:item,distance=..1.2,predicate={NS}:ing/{k},limit=1,sort=nearest] "
                     f"run item modify entity @s contents {NS}:sub/{c}")
        if ident == "minecraft:lava_bucket":
            lines.append("summon minecraft:item ~ ~0.3 ~ {Item:{id:\"minecraft:bucket\",count:1}}")
    for _ in range(n):
        lines.append(f"loot spawn ~ ~0.3 ~ loot {NS}:item/{out}")
    it = ITEMS[out]
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

put(f"data/{NS}/predicate/sneaking.json", {"condition": "minecraft:entity_properties", "entity": "this",
                                           "predicate": {"flags": {"is_sneaking": True}}})


# ---------------------------------------------------------------------------
# ENCANTAMIENTOS (efectos especiales de las armas y armaduras)
# ---------------------------------------------------------------------------
NOHIT = {"condition": "minecraft:inverted", "term": {"condition": "minecraft:entity_properties", "entity": "this",
                                                     "predicate": {"nbt": "{Tags:[\"astral.nohit\"]}"}}}
DIRECT = {"condition": "minecraft:damage_source_properties", "predicate": {"is_direct": True}}
ENCH_ITEMS = f"#{NS}:enchantable"


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
enchant("filo_arcano", "Filo Arcano", "light_purple", 5, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:add",
               "value": {"type": "minecraft:lookup", "values": [0.5, 1.0, 1.8, 3.0, 4.5], "fallback": 4.5}},
    "requirements": DIRECT}]})
enchant("igneo", "Puno Igneo", "gold", 1, ["mainhand"], {"minecraft:post_attack": [{
    "enchanted": "attacker", "affected": "victim",
    "effect": {"type": "minecraft:ignite", "duration": 4.0}, "requirements": all_of(NOHIT, DIRECT)}]})

ARROW_REQ = {"condition": "minecraft:entity_properties", "entity": "direct_attacker",
             "predicate": {"type": "#minecraft:arrows"}}
enchant("punteria", "Punteria", "green", 5, ["mainhand", "offhand"], {
    "minecraft:damage": [{"effect": {"type": "minecraft:multiply", "factor": {
        "type": "minecraft:lookup", "values": [1.0, 1.08, 1.15, 1.22, 1.30], "fallback": 1.3}},
        "requirements": ARROW_REQ}],
    "minecraft:projectile_spawned": [{"effect": {"type": "minecraft:run_function", "function": f"{NS}:bow/tag"}}],
    "minecraft:ammo_use": [{"effect": {"type": "minecraft:set", "value": {
        "type": "minecraft:lookup", "values": [1, 1, 1, 1, 0], "fallback": 0}},
        "requirements": {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:arrow"}}}],
})
enchant("punteria_set", "Punteria del Set", "green", 5, ["chest"], {
    "minecraft:damage": [{"effect": {"type": "minecraft:multiply", "factor": {
        "type": "minecraft:lookup", "values": [1.04, 1.08, 1.12, 1.18, 1.25], "fallback": 1.25}},
        "requirements": ARROW_REQ}]})
enchant("gancho", "Gancho", "gray", 1, ["mainhand"], {"minecraft:tick": [{
    "effect": {"type": "minecraft:apply_impulse", "direction": [0.0, 0.0, 1.0],
               "coordinate_scale": [1.0, 1.0, 1.0], "magnitude": 0.16},
    "requirements": {"condition": "minecraft:entity_scores", "entity": "this", "scores": {"astral.grap": {"min": 1}}}}]})

enchant("empalar", "Empalar", "gold", 5, ["mainhand"], {"minecraft:damage": [{
    "effect": {"type": "minecraft:add",
               "value": {"type": "minecraft:lookup", "values": [1.0, 2.0, 3.0, 4.0, 6.0], "fallback": 6.0}},
    "requirements": DIRECT}]})

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
          "minecraft:ominous_item_spawner", "#minecraft:boat"]
put(f"data/{NS}/tags/entity_type/ignore.json", {"values": IGNORE})
put(f"data/{NS}/tags/entity_type/bosses.json", {"values": ["minecraft:wither", "minecraft:ender_dragon",
                                                           "minecraft:warden", "minecraft:elder_guardian"]})
put(f"data/{NS}/tags/block/passable.json", {"values": ["#minecraft:air", "#minecraft:replaceable"]})

MOB = f"type=!minecraft:player,type=!#{NS}:ignore"

# porcentaje de vida de la victima en #pct (0-100)
fn("fx/victim_pct", [
    "execute store result score #h astral.tmp run data get entity @s Health 100",
    "execute store result score #m astral.tmp run attribute @s minecraft:max_health get 1",
    "execute if score #m astral.tmp matches ..0 run scoreboard players set #m astral.tmp 1",
    "scoreboard players operation #h astral.tmp /= #m astral.tmp",
    "scoreboard players operation #pct astral.tmp = #h astral.tmp",
])
fn("fx/remate", [
    f"function {NS}:fx/victim_pct",
    "execute if score #pct astral.tmp matches 50.. run return 0",
    "execute if score #pct astral.tmp matches ..0 run return 0",
    "# se aplica un rato despues para que no lo absorba la invulnerabilidad del golpe",
    "scoreboard players set @s astral.rem 2",
])
fn("fx/remate_tick", [
    "scoreboard players remove @s astral.rem 1",
    "execute if score @s astral.rem matches 1.. run return 0",
    "tag @s add astral.nohit",
    "damage @s 1.5 minecraft:generic",
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
        f"function {NS}:fx/extra_hit {{dmg:1000.0}}",
    ])
fn("fx/bleed_start", [
    "scoreboard players set @s astral.bleed 5",
    "particle minecraft:dust{color:[0.7,0.0,0.0],scale:1.2} ~ ~1 ~ 0.3 0.4 0.3 0 15",
])
fn("fx/bleed_tick", [
    "scoreboard players remove @s astral.bleed 1",
    "particle minecraft:dust{color:[0.7,0.0,0.0],scale:1.0} ~ ~1 ~ 0.3 0.4 0.3 0 8",
    "tag @s add astral.nohit",
    "damage @s 1.5 minecraft:generic",
    "tag @s remove astral.nohit",
])
fn("fx/cleave", [
    "tag @s add astral.src",
    "execute on attacker run tag @s add astral.atk",
    f"tag @e[{MOB},distance=..2.5,tag=!astral.src,tag=!astral.atk] add astral.tgt",
    "tag @e[tag=astral.tgt] add astral.nohit",
    "execute as @e[tag=astral.tgt] at @s run damage @s 5 minecraft:player_attack by @e[tag=astral.atk,limit=1]",
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
    "execute as @e[tag=astral.tgt] at @s run damage @s 4 minecraft:player_attack by @e[tag=astral.atk,limit=1]",
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
for i, s in enumerate(STAFFS):
    t = i + 1
    sel = f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"baston_{t}"}}}}]'
    cast.append(f"{sel} run scoreboard players set #base astral.tmp {int(s['spell'] * 100)}")
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
cast += [
    "execute if score #base astral.tmp matches ..0 run return 0",
    "scoreboard players operation #base astral.tmp *= #pct astral.tmp",
    "scoreboard players operation #base astral.tmp /= #10000 astral.const",
    f"execute store result storage {NS}:tmp spell.dmg float 0.01 run scoreboard players get #base astral.tmp",
    "scoreboard players operation #cdr astral.tmp *= #cd astral.tmp",
    "scoreboard players operation #cdr astral.tmp /= #100 astral.const",
    "scoreboard players operation #cd astral.tmp -= #cdr astral.tmp",
    "scoreboard players operation @s astral.cd = #cd astral.tmp",
    "tag @s add astral.caster",
    "scoreboard players set #steps astral.tmp 0",
    "playsound minecraft:entity.evoker.cast_spell player @a[distance=..16] ~ ~ ~ 0.8 1.6",
    f"execute anchored eyes positioned ^ ^ ^0.8 run function {NS}:spell/ray",
    "tag @s remove astral.caster",
]
fn("spell/cast", cast)
fn("spell/ray", [
    "particle minecraft:witch ~ ~ ~ 0.05 0.05 0.05 0 2 force",
    "particle minecraft:end_rod ~ ~ ~ 0 0 0 0 1 force",
    f"execute as @e[{MOB},distance=..1.1,tag=!astral.caster,limit=1,sort=nearest] run return run function {NS}:spell/hit with storage {NS}:tmp spell",
    f"execute unless block ~ ~ ~ #{NS}:passable run return run particle minecraft:large_smoke ~ ~ ~ 0.1 0.1 0.1 0.01 6",
    "scoreboard players add #steps astral.tmp 1",
    "execute if score #steps astral.tmp matches 50.. run return 0",
    f"execute positioned ^ ^ ^0.5 run function {NS}:spell/ray",
])
fn("spell/hit", [
    "$damage @s $(dmg) minecraft:magic by @a[tag=astral.caster,limit=1]",
    "particle minecraft:dragon_breath ~ ~1 ~ 0.3 0.4 0.3 0.02 25",
    "playsound minecraft:entity.illusioner.cast_spell player @a[distance=..16] ~ ~ ~ 0.7 1.8",
    "return 1",
])

# ---------------------------------------------------------------------------
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


fn("bow/tag", ["tag @s add astral.bowshot"])
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
BOW_TICKS = [18, 15, 12, 10, 8]
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
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{id:"arco_5"}}}}] run scoreboard players set #free astral.tmp 1',
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
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{{NS}:{{type:"staff"}}}}] run return run function {NS}:spell/cast',
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
fn("mine/endstone", [
    "scoreboard players reset @s astral.m_es",
    f"execute if dimension minecraft:the_end if entity @s[y=-64,dy=114] if predicate {chance(0.04)} run function {NS}:drop/give {{id:\"fragmento_cristal\",name:\"Fragmento de Cristal Arcano\"}}",
])
fn("mine/chorus", [
    "scoreboard players reset @s astral.m_ch",
    f"execute if dimension minecraft:the_end if predicate {chance(0.08)} run function {NS}:drop/give {{id:\"madera_estelar\",name:\"Madera Estelar\"}}",
])
fn("mine/log", [f"scoreboard players reset @s {o}" for (o, _) in log_objs] + [
    f"execute if dimension minecraft:the_end if predicate {chance(0.35)} run function {NS}:drop/give {{id:\"madera_estelar\",name:\"Madera Estelar\"}}",
])

# ---------------------------------------------------------------------------
# DIFICULTAD PROGRESIVA: mobs elite
# ---------------------------------------------------------------------------
put(f"data/{NS}/tags/entity_type/hostile.json", {"values": HOSTILE})

# Nivel de equipo del jugador (0-5): el mejor tier Astral que lleva puesto o en la mano
lvl = ["scoreboard players set @s astral.lvl 0"]
for t in range(1, 6):
    for slot in ("armor.head", "armor.chest", "armor.legs", "armor.feet", "weapon.mainhand", "weapon.offhand"):
        lvl.append(f"execute if score @s astral.lvl matches ..{t - 1} if items entity @s {slot} "
                   f"*[minecraft:custom_data~{{{NS}:{{tier:{t}}}}}] run scoreboard players set @s astral.lvl {t}")
fn("player/lvl", lvl)

fn("elite/roll", [
    "tag @s add astral.seen",
    "execute unless entity @a[distance=..64,gamemode=!spectator] run return 0",
    "scoreboard players operation #a astral.tmp = @p[distance=..64,gamemode=!spectator] astral.lvl",
    "execute store result score #day astral.tmp run time query day",
    "scoreboard players operation #day astral.tmp /= #7 astral.const",
    "execute if score #day astral.tmp matches 4.. run scoreboard players set #day astral.tmp 3",
    "scoreboard players operation #a astral.tmp += #day astral.tmp",
    "# probabilidad = 6% + 5% por nivel de amenaza",
    "scoreboard players operation #c astral.tmp = #a astral.tmp",
    "scoreboard players operation #c astral.tmp *= #5 astral.const",
    "scoreboard players add #c astral.tmp 6",
    "execute store result score #r astral.tmp run random value 1..100",
    "execute if score #r astral.tmp > #c astral.tmp run return 0",
    "# tier = 1 + azar(0..amenaza)/2, maximo 5",
    f"execute store result storage {NS}:tmp elite.max int 1 run scoreboard players get #a astral.tmp",
    f"function {NS}:elite/rand with storage {NS}:tmp elite",
    "scoreboard players operation #t astral.tmp /= #2 astral.const",
    "scoreboard players add #t astral.tmp 1",
    "execute if score #t astral.tmp matches 6.. run scoreboard players set #t astral.tmp 5",
] + [f"execute if score #t astral.tmp matches {i + 1} run return run function {NS}:elite/t{i + 1}" for i in range(5)])
fn("elite/rand", ["$execute store result score #t astral.tmp run random value 0..$(max)"])

for i, (name, color, hp, dmg, spd, armor, kb) in enumerate(ELITE_TIERS):
    t = i + 1
    stars = "[" + ROMAN[i] + "]"
    lines = [
        f"tag @s add astral.elite",
        f"tag @s add astral.elite{t}",
        f"attribute @s minecraft:max_health modifier add {NS}:elite {hp / 100} add_multiplied_base",
        f"attribute @s minecraft:attack_damage modifier add {NS}:elite {dmg / 100} add_multiplied_base",
        f"attribute @s minecraft:movement_speed modifier add {NS}:elite {spd / 100} add_multiplied_base",
        f"attribute @s minecraft:armor modifier add {NS}:elite {armor} add_value",
        f"attribute @s minecraft:knockback_resistance modifier add {NS}:elite {kb} add_value",
        f"attribute @s minecraft:follow_range modifier add {NS}:elite 0.5 add_multiplied_base",
        "data modify entity @s Health set value 1024.0f",
        "data modify entity @s PersistenceRequired set value 1b",
        f"data modify entity @s CustomName set value {{text:\"{stars} {name}\",color:\"{color}\",bold:{'true' if t >= 4 else 'false'}}}",
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

fn("elite/fx", [
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
fn("guide/give", [
    "scoreboard players reset @s astral.guia",
    f"loot give @s loot {NS}:guia",
])
put(f"data/{NS}/advancement/join.json", {
    "criteria": {"join": {"trigger": "minecraft:tick"}}, "rewards": {"function": f"{NS}:guide/join"}})
fn("guide/join", [
    f"loot give @s loot {NS}:guia",
    "tellraw @s " + json.dumps([txt("Bienvenido a AstralRPG. ", "light_purple"),
                                txt("Te dimos la guia de la Forja Astral. Si la perdes: /trigger astral.guia", "gray")]),
])

# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------
fn("admin/materiales", [f"loot give @s loot {NS}:item/{m}" for m in MATERIALS] + [f"loot give @s loot {NS}:item/{m}" for m in MATERIALS])
# Kits de prueba: cajas de shulker por categoria (el inventario no alcanza para todo)
KITS = [
    ("materiales", "Materiales", "light_purple", "minecraft:purple_shulker_box",
     [i for i in ITEMS if ITEMS[i]["kind"] == "material"]),
    ("berserker", "Armaduras Berserker", "red", "minecraft:red_shulker_box",
     [i for i in ITEMS if i.startswith("berserker_")]),
    ("mago", "Armaduras Mago", "dark_purple", "minecraft:magenta_shulker_box",
     [i for i in ITEMS if i.startswith("mago_")]),
    ("arquero", "Armaduras Arquero", "green", "minecraft:lime_shulker_box",
     [i for i in ITEMS if i.startswith("arquero_")]),
    ("armas", "Armas de clase", "gold", "minecraft:orange_shulker_box",
     [i for i in ITEMS if i.split("_")[0] in ("espada", "hacha", "baston", "guadana", "arco") and i[-1].isdigit()]),
    ("especiales", "Especiales, Lanzas y Talismanes", "aqua", "minecraft:cyan_shulker_box",
     [i for i in ITEMS if i.startswith(("lanza_", "talisman_")) or i in
      ("gancho", "guadana_umbria", "guantes_meteoro", "taladro_infernal")]),
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
    "tellraw @s " + json.dumps(txt("Te dimos 6 cajas de shulker con todos los items de AstralRPG.", "gray"))])

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
    "scoreboard objectives add astral.rem dummy",
    "scoreboard objectives add astral.lvl dummy",
    "scoreboard objectives add astral.draw dummy",
    "scoreboard objectives add astral.use minecraft.used:minecraft.carrot_on_a_stick",
    "scoreboard objectives add astral.m_es minecraft.mined:minecraft.end_stone",
    "scoreboard objectives add astral.m_ch minecraft.mined:minecraft.chorus_plant",
    "scoreboard objectives add astral.guia trigger",
] + [f"scoreboard objectives add {o} {c}" for (o, c) in log_objs] + [
    "scoreboard players set #2 astral.const 2",
    "scoreboard players set #3 astral.const 3",
    "scoreboard players set #5 astral.const 5",
    "scoreboard players set #7 astral.const 7",
    "scoreboard players set #100 astral.const 100",
    "scoreboard players set #10000 astral.const 10000",
    f"schedule function {NS}:loop/t5 5t replace",
    f"schedule function {NS}:loop/t10 10t replace",
    f"schedule function {NS}:loop/t20 20t replace",
]
fn("load", load)
fn("tick", [
    f"execute as @a[scores={{astral.use=1..}}] at @s run function {NS}:use/main",
    "scoreboard players remove @a[scores={astral.cd=1..}] astral.cd 1",
    f"execute as @a[scores={{astral.grap=1..}}] run function {NS}:grapple/tick",
    f"execute as @e[type=#minecraft:arrows,tag=astral.bowshot] at @s run function {NS}:bow/norm",
    "# si soltaste el arco, se reinicia la carga",
    "scoreboard players set @a[tag=!astral.drew,scores={astral.draw=1..}] astral.draw 0",
    "tag @a remove astral.drew",
])
fn("loop/t5", [
    f"execute as @a run function {NS}:player/hp",
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
    f"function {NS}:altar/scan",
    f"execute as @a[scores={{astral.m_es=1..}}] at @s run function {NS}:mine/endstone",
    f"execute as @a[scores={{astral.m_ch=1..}}] at @s run function {NS}:mine/chorus",
]
for (o, _) in log_objs:
    t10.append(f"execute as @a[scores={{{o}=1..}}] at @s run function {NS}:mine/log")
t10 += [
    "scoreboard players enable @a astral.guia",
    f"execute as @a[scores={{astral.guia=1..}}] run function {NS}:guide/give",
    f"schedule function {NS}:loop/t10 10t replace",
]
fn("loop/t10", t10)
fn("loop/t20", [
    f"execute as @e[scores={{astral.bleed=1..}}] at @s run function {NS}:fx/bleed_tick",
    f"execute as @e[scores={{astral.rem=1..}}] at @s run function {NS}:fx/remate_tick",
    f"execute as @a run function {NS}:player/lvl",
    f"execute as @e[type=#{NS}:hostile,tag=!astral.seen] at @s run function {NS}:elite/roll",
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

# ---------------------------------------------------------------------------
# Escribir
# ---------------------------------------------------------------------------
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
