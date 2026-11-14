# -*- coding: utf-8 -*-
"""Tiers 6 a 10 (pedido del dueno, 14/11/2026).

Las armaduras usan los modelos que eligio el dueno (casco 3D + cuerpo plano, ver armaduras_t6_10.py).
Ese arte es de terceros y vive solo en el pack FINAL privado; aca solo hay ids.
Las armas todavia no tienen modelo propio: se ven como el arma T5 de su familia (ARMA_MODELO).

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
    "mago": {6: "glacier_robe", 7: "scarlet_robe", 8: "rimeweave_robe", 9: "nebula", 10: "absolution_robe"},
    "berserker": {6: None, 7: "lightbringer_armor", 8: "onslaught_armor", 9: "justicar_armor", 10: "destroyer_armor"},
    "arquero": {6: "strider_armor", 7: "riftstalker_armor", 8: None, 9: None, 10: "deathmantle_armor"},
}


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


# Arma T5 de cada familia: las T6-T10 se ven igual hasta que el dueno elija modelos.
# Para cambiar el modelo de un arma: poner aca su item_model (por ejemplo "astral:espada_6").
ARMA_MODELO = {f"{fam}_{t}": f"astral:{fam}_5" for fam in ("espada", "hacha", "guadana", "arco", "lanza")
               for t in TIERS_NUEVOS}
ARMA_MODELO.update({f"baston_{t}": None for t in TIERS_NUEVOS})  # None = mismo modelo que el baston T5

# Arcos: segundos entre disparos automaticos y multiplicador de Punteria por tier (1..10).
ARCO_AUTO = [18, 15, 12, 10, 8, 7, 6, 5, 5, 4]
PUNTERIA = [1.0, 1.08, 1.15, 1.22, 1.30, 1.38, 1.46, 1.54, 1.62, 1.70]


def extend_weapons(g):
    g["MATERIALS"].update(MATERIALES)
    S, A, ST, SC, B, SP = g["SWORDS"], g["AXES"], g["STAFFS"], g["SCYTHES"], g["BOWS"], g["SPEARS"]
    S += [
        {"name": "Espada del Ocaso", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 60, "lvl": 35,
         "fx": {"lifesteal": 5, "furia": 2}, "cost": _cost(6, [("c", "nucleo_furia_pura", 1)]),
         "desc": ["Robo de vida", "+5% de dano por cada 10% de vida perdida"]},
        {"name": "Espada del Eclipse", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 70, "lvl": 40,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1}, "cost": _cost(7, [("c", "nucleo_furia_pura", 1)]),
         "desc": ["Robo de vida", "Furia", "+5% de dano a enemigos con menos del 50% de vida"]},
        {"name": "Espada Supernova", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 80, "lvl": 45,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1}, "cost": _cost(8, [("c", "nucleo_furia_pura", 2)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area pequena"]},
        {"name": "Espada del Vacio Eterno", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 90, "lvl": 50,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1, "ejecucion": 1},
         "cost": _cost(9, [("c", "nucleo_furia_pura", 2)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area", "Ejecuta enemigos con menos del 15% de vida"]},
        {"name": "Espada del Fin de los Tiempos", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 100, "lvl": 55,
         "fx": {"lifesteal": 5, "furia": 2, "remate": 1, "hendidura": 1, "ejecucion": 2},
         "cost": _cost(10, [("c", "nucleo_furia_pura", 3)]),
         "desc": ["Robo de vida", "Furia", "Golpes en area", "Ejecuta enemigos con menos del 20% de vida"]},
    ]
    axe_fx = {"sangrado": 1, "hendidura": 1, "ejecucion": 1}
    A += [
        {"name": "Hacha del Ocaso", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 90, "spd": 1.0, "lvl": 35,
         "fx": dict(axe_fx), "cost": _cost(6, [("c", "nucleo_furia_pura", 1), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida"]},
        {"name": "Hacha del Eclipse", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 105, "spd": 1.0, "lvl": 40,
         "fx": dict(axe_fx, lifesteal=2), "cost": _cost(7, [("c", "nucleo_furia_pura", 1), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida", "Robo de vida"]},
        {"name": "Hacha Supernova", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 120, "spd": 1.05, "lvl": 45,
         "fx": dict(axe_fx, lifesteal=3), "cost": _cost(8, [("c", "nucleo_furia_pura", 2), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 15% de vida", "Robo de vida"]},
        {"name": "Hacha del Vacio Eterno", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 135, "spd": 1.05, "lvl": 50,
         "fx": dict(axe_fx, lifesteal=3, ejecucion=2), "cost": _cost(9, [("c", "nucleo_furia_pura", 2), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 20% de vida", "Robo de vida"]},
        {"name": "Hacha del Fin de los Tiempos", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 150, "spd": 1.1, "lvl": 55,
         "fx": dict(axe_fx, lifesteal=4, ejecucion=2), "cost": _cost(10, [("c", "nucleo_furia_pura", 3), ("c", "palo_reforzado", 1)]),
         "desc": ["Ejecuta enemigos con menos del 20% de vida", "Robo de vida"]},
    ]
    staff_model = ST[4]["model"]
    for t, (name, mdmg, pierce, cd, lvl, n) in zip(TIERS_NUEVOS, [
            ("Baston del Ocaso", 48, 25, 19, 37, 1), ("Baston del Eclipse", 56, 30, 18, 42, 1),
            ("Baston Supernova", 64, 35, 17, 47, 2), ("Baston del Vacio Eterno", 72, 40, 16, 52, 2),
            ("Baston del Fin de los Tiempos", 80, 45, 15, 57, 3)]):
        ST.append({"name": name, "model": ARMA_MODELO[f"baston_{t}"] or staff_model, "mana": 0, "mdmg": mdmg,
                   "pierce": pierce, "spell": 10.0 + t - 5, "cd": cd, "lvl": lvl,
                   "cost": _cost(t, [("c", "gema_luminica_perfecta", n)]),
                   "desc": [f"Ignora {pierce}% de resistencia magica"]})
    for t, (name, dmg, mdmg, lvl, n, exe, ls) in zip(TIERS_NUEVOS, [
            ("Guadana del Ocaso", 12, 50, 37, 2, 2, 2), ("Guadana del Eclipse", 13, 55, 42, 2, 2, 3),
            ("Guadana Supernova", 14, 60, 47, 3, 2, 3), ("Guadana del Vacio Eterno", 15, 65, 52, 3, 2, 4),
            ("Guadana del Fin de los Tiempos", 16, 70, 57, 4, 2, 5)]):
        SC.append({"name": name, "base": "minecraft:netherite_hoe", "dmg": dmg, "lvl": lvl, "mdmg": mdmg, "reset_cd": True,
                   "fx": {"lifesteal": ls, "maldicion": 1, "cono": 1, "ejecucion": exe},
                   "cost": _cost(t, [("c", "gema_umbria_perfecta", n)]),
                   "desc": ["Ejecuta mobs con menos del 20% de vida", "Matar mobs reinicia el enfriamiento de hechizos"]})
    for t, (name, bonus, lvl, n) in zip(TIERS_NUEVOS, [
            ("Arco del Ocaso", 48, 35, 1), ("Arco del Eclipse", 56, 40, 1), ("Arco Supernova", 64, 45, 2),
            ("Arco del Vacio Eterno", 72, 50, 2), ("Arco del Fin de los Tiempos", 80, 55, 3)]):
        B.append({"name": name, "bonus": bonus, "draw": 95, "lvl": lvl, "infinite": True, "cooldown": 0.4,
                  "cost": _cost(t, [("c", "gema_luminica_perfecta", n)]),
                  "desc": ["Disparo casi instantaneo", "No gasta flechas normales"]})
    for t, (name, bonus, lvl, n) in zip(TIERS_NUEVOS, [
            ("Lanza del Ocaso", 7, 35, 1), ("Lanza del Eclipse", 8, 40, 1), ("Lanza Supernova", 9, 45, 2),
            ("Lanza del Vacio Eterno", 10, 50, 2), ("Lanza del Fin de los Tiempos", 12, 55, 3)]):
        SP.append({"name": name, "base": "minecraft:netherite_spear", "lvl": lvl, "bonus": bonus,
                   "fx": {"lifesteal": 3, "sangrado": 1, "hendidura": 1, "ejecucion": 1},
                   "cost": _cost(t, [("c", "chispa_astral", n)]),
                   "desc": ["Ejecuta enemigos con menos del 15% de vida"]})
