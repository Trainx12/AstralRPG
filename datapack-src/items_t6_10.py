# -*- coding: utf-8 -*-
"""Tiers 6 a 10 (pedido del dueno, 14/11/2026).

Las armaduras usan los modelos que eligio el dueno (casco 3D + cuerpo plano, ver armaduras_t6_10.py).
Ese arte es de terceros y vive solo en el pack FINAL privado; aca solo hay ids.
Las armas usan los modelos que eligio el dueno el 15/11 (armas_mod.py, tambien de terceros y solo en el FINAL
privado); en el pack publico se ven como el arma T5 de su familia (reserva de build_pack.py).

Cada pieza o arma de tier N se forja con la del tier N-1 + el material de su tier.
Los materiales nuevos caen de mobs de ese tier o mas (mob/drop_tier en build.py), mas en elites y jefes.
"""

TIERS_NUEVOS = (6, 7, 8, 9, 10)

# Material propio de cada tier: id -> (nombre, color, modelo vanilla, brillo, descripcion)
MATERIAL_TIER = {
    6: "fragmento_ocaso",
    7: "esquirla_eclipse",
    8: "nucleo_supernova",
    9: "esencia_vacio",
    10: "corazon_fin",
}
MATERIALES = {
    "fragmento_ocaso": ("Fragmento de Ocaso", "#ff5fd2", "minecraft:amethyst_shard", True,
                        "Cae de mobs tier 6 o mas (y poco de elites y jefes tier 5)."),
    "esquirla_eclipse": ("Esquirla de Eclipse", "#5ff0ff", "minecraft:echo_shard", True, "Cae de mobs tier 7 o mas."),
    "nucleo_supernova": ("Nucleo de Supernova", "#ff3b3b", "minecraft:fire_charge", True, "Cae de mobs tier 8 o mas."),
    "esencia_vacio": ("Esencia del Vacio", "#e8e8ff", "minecraft:ender_eye", True, "Cae de mobs tier 9 o mas."),
    "corazon_fin": ("Corazon del Fin", "#b388ff", "minecraft:nether_star", True, "Cae de mobs tier 10."),
}

# Probabilidad de que un mob de tier >= N suelte el material de N: (comun, elite, jefe garantizado)
# Pensado para ~1 pieza cada 1-2 horas en ese tier (250 bajas/h, ~10% elites).
DROP_MATERIAL = {"comun": 0.012, "elite": 0.12, "jefe": 1.0}
# Elites y jefes tier 5 sueltan Fragmento de Ocaso (para poder dar el primer paso a T6).
DROP_OCASO_T5 = {"elite": 0.04, "jefe": 0.5}

# Modelo de armadura elegido (id de armaduras_t6_10.SETS). None = sin modelo: se ve como el T5 de la clase.
VISUAL = {
    "mago": {1: "wandering_magician", 2: "netherite_fire_robe", 3: "sanguine_purple", 4: "pyromancer", 5: "dark_cover",
             6: "glacier_robe", 7: "scarlet_robe", 8: "rimeweave_robe", 9: "nebula", 10: "absolution_robe"},
    "berserker": {1: "rogues_berserker", 2: "dead_gladiator", 3: "sunset_wings", 4: "flesh_of_the_feaster",
                  5: "dark_lord", 6: "spark_of_dawn", 7: "lightbringer_armor", 8: "onslaught_armor",
                  9: "justicar_armor", 10: "destroyer_armor"},
    "arquero": {1: "ranger", 2: "netherite_ranger", 3: "anarchy_thief", 4: "fantasy_thief", 5: "shadowwalker",
                6: "strider_armor", 7: "riftstalker_armor", 8: "forgotten_trace", 9: "cultist", 10: "deathmantle_armor"},
}
# Modelos sin casco (el mod no trae cabeza): el casco no se ve puesto y su icono queda el del pack publico.
SIN_CASCO = {"sanguine_purple"}
# Casco pegado a la cabeza (textura plana, sin modelo 3D): el dueno lo pidio para la Nebulosa (Mago T9).
CASCO_PLANO = {"nebula"}


def _cost(t, extra):
    m = MATERIAL_TIER[t]
    out = [("c", m, 4)]
    if t >= 8:
        out.append(("c", MATERIAL_TIER[t - 1], 2))
    return out + extra


def extend_armor(sets):
    b = sets["berserker"]["tiers"]
    b += [
        {"name": "del Titan", "mat": "netherite", "stats": {"hp": 60, "dmg": 48, "def": -15, "fire": 30, "kb": 100},
         "lifesteal": 3, "furia": 1, "cost": _cost(6, [("c", "nucleo_furia_pura", 1)])},
        {"name": "del Portador de Luz", "mat": "netherite", "stats": {"hp": 70, "dmg": 56, "def": -15, "fire": 40, "kb": 100},
         "lifesteal": 4, "furia": 1, "cost": _cost(7, [("c", "nucleo_furia_pura", 1)])},
        {"name": "de la Embestida", "mat": "netherite", "stats": {"hp": 80, "dmg": 64, "def": -15, "fire": 50, "kb": 100},
         "lifesteal": 4, "furia": 2, "cost": _cost(8, [("c", "nucleo_furia_pura", 2)])},
        {"name": "del Justiciero", "mat": "netherite", "stats": {"hp": 90, "dmg": 72, "def": -15, "fire": 60, "kb": 100},
         "lifesteal": 5, "furia": 2, "cost": _cost(9, [("c", "nucleo_furia_pura", 2)])},
        {"name": "del Destructor", "mat": "netherite", "stats": {"hp": 100, "dmg": 80, "def": -15, "fire": 70, "kb": 100},
         "lifesteal": 5, "furia": 2, "cost": _cost(10, [("c", "nucleo_furia_pura", 3)])},
    ]
    from escala import MANA_SET_MAGO
    m = sets["mago"]
    m["tiers"] += [
        {"name": "del Glaciar", "mat": "leather", "stats": {"mana": MANA_SET_MAGO[6], "mdmg": 48, "mregen": 30, "cdr": 10, "def": -20},
         "cost": _cost(6, [("c", "gema_luminica_perfecta", 1)])},
        {"name": "Escarlata", "mat": "leather", "stats": {"mana": MANA_SET_MAGO[7], "mdmg": 56, "mregen": 35, "cdr": 15, "def": -20},
         "cost": _cost(7, [("c", "gema_luminica_perfecta", 1)])},
        {"name": "de la Escarcha", "mat": "leather", "stats": {"mana": MANA_SET_MAGO[8], "mdmg": 64, "mregen": 40, "cdr": 20, "def": -20},
         "cost": _cost(8, [("c", "gema_luminica_perfecta", 2)])},
        {"name": "de la Nebulosa", "mat": "leather", "stats": {"mana": MANA_SET_MAGO[9], "mdmg": 72, "mregen": 45, "cdr": 25, "def": -20},
         "cost": _cost(9, [("c", "gema_luminica_perfecta", 2)])},
        {"name": "de la Absolucion", "mat": "leather", "stats": {"mana": MANA_SET_MAGO[10], "mdmg": 80, "mregen": 50, "cdr": 30, "def": -20},
         "cost": _cost(10, [("c", "gema_luminica_perfecta", 3)])},
    ]
    # El cuero se tine; T6-T10 usan su propia textura, el tinte solo cuenta si falta (reserva).
    m["dye"] = list(m["dye"]) + [0x1f6fd1] * 5
    a = sets["arquero"]
    a["tiers"] += [
        {"name": "del Andariego", "mat": "leather", "extra_armor": 2, "stats": {"rdmg": 48, "crit": 28, "spd": 22, "draw": 24},
         "cost": _cost(6, [("c", "nucleo_eolico", 2)])},
        {"name": "del Acechador", "mat": "leather", "extra_armor": 2, "stats": {"rdmg": 56, "crit": 32, "spd": 25, "draw": 28},
         "cost": _cost(7, [("c", "nucleo_eolico", 2)])},
        {"name": "del Cazador Celeste", "mat": "leather", "extra_armor": 3, "stats": {"rdmg": 64, "crit": 36, "spd": 28, "draw": 32},
         "cost": _cost(8, [("c", "nucleo_eolico", 3)])},
        {"name": "del Ojo de Tormenta", "mat": "leather", "extra_armor": 3, "stats": {"rdmg": 72, "crit": 42, "spd": 31, "draw": 36},
         "cost": _cost(9, [("c", "nucleo_eolico", 3)])},
        {"name": "del Manto Mortal", "mat": "leather", "extra_armor": 3, "stats": {"rdmg": 80, "crit": 50, "spd": 35, "draw": 40},
         "cost": _cost(10, [("c", "nucleo_eolico", 4)])},
    ]
    a["dye"] = list(a["dye"]) + [0x9fe6ff] * 5


# Cada arma T6-T10 tiene su propio item_model. El modelo elegido vive en el pack FINAL privado (armas_mod.py);
# el pack publico trae una reserva igual al arma T5 de la familia (build_pack.py).
FAMILIAS_ARMA = ("espada", "hacha", "baston", "guadana", "arco", "lanza")
ARMA_MODELO = {f"{fam}_{t}": f"astral:{fam}_{t}" for fam in FAMILIAS_ARMA for t in TIERS_NUEVOS}

# Ballestas de Arquero (15/11/2026): tier -> datos. "carga" son los segundos que tarda en cargar
# (vanilla 1,25 s); el dano sale de Punteria del tier, igual que los arcos.
BALLESTAS = {
    3: {"name": "Ballesta Pesada de Zafiro", "carga": 0.9, "lvl": 20, "piercing": 1, "multishot": 0,
        "cost": [("c", "arco_3", 1), ("c", "cristal_refinado", 3), ("v", "minecraft:crossbow", 1)],
        "desc": ["Perforacion: la flecha atraviesa 1 enemigo"]},
    4: {"name": "Ballesta Rapida del Nether", "carga": 0.65, "lvl": 25, "piercing": 1, "multishot": 1,
        "cost": [("c", "ballesta_3", 1), ("c", "nucleo_eolico", 3)],
        "desc": ["Multidisparo: 3 flechas por tiro"]},
    5: {"name": "Ballesta Celeste Veloz", "carga": 0.2, "lvl": 30, "piercing": 2, "multishot": 1,
        "cost": [("c", "ballesta_4", 1), ("c", "gema_luminica_perfecta", 2), ("c", "nucleo_astral", 1)],
        "desc": ["Carga casi instantanea", "Multidisparo: 3 flechas por tiro", "Perforacion II: atraviesa 2 enemigos",
                 "No gasta flechas normales"]},
}
CARGA_VANILLA = 1.25

# Arcos: segundos entre disparos automaticos y multiplicador de Punteria por tier (1..10).
ARCO_AUTO = [18, 15, 12, 10, 8, 7, 6, 5, 5, 4]
PUNTERIA = [1.0, 1.08, 1.15, 1.22, 1.30, 1.38, 1.46, 1.54, 1.62, 1.70]


def extend_weapons(g):
    g["MATERIALS"].update(MATERIALES)
    S, A, ST, SC, B, SP = g["SWORDS"], g["AXES"], g["STAFFS"], g["SCYTHES"], g["BOWS"], g["SPEARS"]
    S += [
        {"name": "Hoja Siniestra", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 60, "lvl": 35,
         "fx": {"lifesteal": 5, "furia": 2}, "cost": _cost(6, [("c", "nucleo_furia_pura", 1)]),
         "desc": ["Robo de vida", "+5% de dano por cada 10% de vida perdida"]},
        {"name": "Daga del Rito Oscuro", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 70, "lvl": 40,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1}, "cost": _cost(7, [("c", "nucleo_furia_pura", 1)]),
         "desc": ["Robo de vida", "Furia", "+5% de dano a enemigos con menos del 50% de vida"]},
        {"name": "Espada Espectral Carmesi", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 80, "lvl": 45,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1}, "cost": _cost(8, [("c", "nucleo_furia_pura", 2)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area pequena"]},
        {"name": "Mandoble de Obsidiana", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 90, "lvl": 50,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1, "ejecucion": 1},
         "cost": _cost(9, [("c", "nucleo_furia_pura", 2)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area", "Ejecuta enemigos con menos del 15% de vida"]},
        {"name": "Espada Esmeralda Nocturna", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 100, "lvl": 55,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1, "ejecucion": 2},
         "cost": _cost(10, [("c", "nucleo_furia_pura", 3)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area", "Ejecuta enemigos con menos del 20% de vida"]},
    ]
    axe_fx = {"sangrado": 1, "hendidura": 1, "ejecucion": 1}
    A += [
        {"name": "Hacha Doble de Jade", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 90, "spd": 1.0, "lvl": 35,
         "fx": dict(axe_fx), "cost": _cost(6, [("c", "nucleo_furia_pura", 1), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida"]},
        {"name": "Hacha del Torbellino", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 105, "spd": 1.0, "lvl": 40,
         "fx": dict(axe_fx, lifesteal=2), "cost": _cost(7, [("c", "nucleo_furia_pura", 1), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida", "Robo de vida"]},
        {"name": "Hacha Doble Aurea", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 120, "spd": 1.05, "lvl": 45,
         "fx": dict(axe_fx, lifesteal=3), "cost": _cost(8, [("c", "nucleo_furia_pura", 2), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida", "Robo de vida"]},
        {"name": "Hacha Marca de Fuego", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 135, "spd": 1.05, "lvl": 50,
         "fx": dict(axe_fx, lifesteal=3, ejecucion=2), "cost": _cost(9, [("c", "nucleo_furia_pura", 2), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 20% de vida", "Robo de vida"]},
        {"name": "Gran Hacha del Verdugo", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 150, "spd": 1.1, "lvl": 55,
         "fx": dict(axe_fx, lifesteal=4, ejecucion=2), "cost": _cost(10, [("c", "nucleo_furia_pura", 3), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 20% de vida", "Robo de vida"]},
    ]
    staff_model = ST[4]["model"]
    for t, (name, mdmg, pierce, cd, lvl, n) in zip(TIERS_NUEVOS, [
            ("Cetro de Amatista Arcana", 48, 25, 19, 37, 1), ("Baston de Brasa Solar", 56, 30, 18, 42, 1),
            ("Baston del Cristal Celeste", 64, 35, 17, 47, 2), ("Baston de la Calavera Errante", 72, 40, 16, 52, 2),
            ("Cetro del Llamahuesos", 80, 45, 15, 57, 3)]):
        ST.append({"name": name, "model": ARMA_MODELO[f"baston_{t}"] or staff_model, "mana": 0, "mdmg": mdmg,
                   "pierce": pierce, "spell": 10.0 + t - 5, "cd": cd, "lvl": lvl,
                   "cost": _cost(t, [("c", "gema_luminica_perfecta", n)]),
                   "desc": [f"Ignora {pierce}% de resistencia magica"]})
    for t, (name, dmg, mdmg, lvl, n, exe, ls) in zip(TIERS_NUEVOS, [
            ("Guadana del Carcelero", 12, 50, 37, 2, 2, 2), ("Guadana Osaria", 13, 55, 42, 2, 2, 3),
            ("Guadana de Piedra Antigua", 14, 60, 47, 3, 2, 3), ("Guadana de Escarcha", 15, 65, 52, 3, 2, 4),
            ("Guadana de la Pesadilla", 16, 70, 57, 4, 2, 5)]):
        SC.append({"name": name, "base": "minecraft:netherite_hoe", "dmg": dmg, "lvl": lvl, "mdmg": mdmg, "reset_cd": True,
                   "fx": {"lifesteal": ls, "maldicion": 1, "cono": 1, "ejecucion": exe},
                   "cost": _cost(t, [("c", "gema_umbria_perfecta", n)]),
                   "desc": ["Ejecuta mobs con menos del 20% de vida", "Matar mobs reinicia el enfriamiento de hechizos"]})
    for t, (name, bonus, lvl, n) in zip(TIERS_NUEVOS, [
            ("Arco de las Almas Perdidas", 48, 35, 1), ("Arco del Vendaval Dorado", 56, 40, 1), ("Arco Enredadera del Eco", 64, 45, 2),
            ("Arco de Burbujas Abisales", 72, 50, 2), ("Arco Embrujado", 80, 55, 3)]):
        B.append({"name": name, "bonus": bonus, "draw": 95, "lvl": lvl, "infinite": True, "cooldown": 0.4,
                  "cost": _cost(t, [("c", "gema_luminica_perfecta", n)]),
                  "desc": ["Disparo casi instantaneo", "No gasta flechas normales"]})
    for t, (name, bonus, lvl, n) in zip(TIERS_NUEVOS, [
            ("Lanza de la Fortuna", 7, 35, 1), ("Tridente del Inframundo", 8, 40, 1), ("Lanza del Principe Errante", 9, 45, 2),
            ("Lanza del Heroe Dorado", 10, 50, 2), ("Guja del Dragon Verde", 12, 55, 3)]):
        SP.append({"name": name, "base": "minecraft:netherite_spear", "lvl": lvl, "bonus": bonus,
                   "fx": {"lifesteal": 3, "sangrado": 1, "hendidura": 1, "ejecucion": 1},
                   "cost": _cost(t, [("c", "chispa_astral", n)]),
                   "desc": ["Ejecuta enemigos con menos del 15% de vida"]})
