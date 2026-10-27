# -*- coding: utf-8 -*-
"""
AstralRPG - definicion de materiales, armaduras, armas y recetas.
Todo lo que se quiera balancear se cambia en este archivo y despues se corre build.py.
"""

# Nombres de skills de AuraSkills (id interno, nombre que ve el jugador)
SKILLS = {
    "forging": "Forja",       # Smithing / Herreria en el documento
    "sorcery": "Hechiceria",  # Magic
    "archery": "Arqueria",    # Archery
    "fighting": "Combate",    # Combat
    "mining": "Mineria",      # Engineering
    "foraging": "Tala",       # Woodworking
}

# ---------------------------------------------------------------------------
# MATERIALES
# id: (nombre, color, modelo vanilla que se ve, brillo, descripcion)
# La base de todos los materiales es papel, asi nunca se confunden con items
# vanilla al forjar. El modelo es solo lo que ve el jugador.
# ---------------------------------------------------------------------------
MATERIALS = {
    "netherita_fundida": ("Netherita Fundida", "#c0582f", "minecraft:netherite_ingot", True, "Netherita fundida en un horno."),
    "netherita_reforzada": ("Netherita Reforzada", "#ff7b3a", "minecraft:netherite_ingot", True, "Metal de nivel intermedio-alto."),
    "shadowsteel": ("Acero Sombrio", "#5b4a6b", "minecraft:iron_ingot", True, "Equipamiento de Berserker."),
    "esencia_nether": ("Esencia del Nether", "#b3261e", "minecraft:fermented_spider_eye", False, "Cae de Wither Skeletons."),
    "madera_estelar": ("Madera Estelar", "#9fd8ff", "minecraft:stripped_warped_stem", False, "Madera de los arboles del End."),
    "palo_reforzado": ("Palo Reforzado", "#8a8a9e", "minecraft:breeze_rod", False, "Mango para armas avanzadas."),
    "cuero_tratado": ("Cuero Tratado", "#c58b52", "minecraft:rabbit_hide", False, "Base de todas las armaduras."),
    "cristal_arcano": ("Cristal Arcano", "#b07cff", "minecraft:amethyst_cluster", True, "Se procesa en 4 fragmentos."),
    "fragmento_cristal": ("Fragmento de Cristal Arcano", "#c9a6ff", "minecraft:amethyst_shard", False, "4 forman un Cristal Refinado."),
    "cristal_refinado": ("Cristal Arcano Refinado", "#d9b8ff", "minecraft:echo_shard", True, "Crafteos magicos medio-alto."),
    "fragmento_umbrio": ("Fragmento Umbrio", "#4a3360", "minecraft:flint", False, "Cae de Wither Skeletons y Piglin Brutes."),
    "gema_umbria_fragmentada": ("Gema Umbria Fragmentada", "#6b4a8a", "minecraft:coal", False, "Gema oscura inicial."),
    "gema_umbria": ("Gema Umbria", "#7d3cff", "minecraft:ender_eye", True, "Armas oscuras y mejoras."),
    "gema_umbria_perfecta": ("Gema Umbria Perfecta", "#a24bff", "minecraft:ender_eye", True, "Endgame Berserker y Mago."),
    "gema_luminica": ("Gema Luminica", "#ffe066", "minecraft:glow_berries", True, "Se encuentra en cofres del Overworld."),
    "gema_luminica_perfecta": ("Gema Luminica Perfecta", "#fff3a8", "minecraft:nether_star", True, "Endgame Arquero y Mago."),
    "fragmento_astral": ("Fragmento Astral", "#7ec8ff", "minecraft:prismarine_crystals", False, "Cae de Endermans en el End."),
    "polvo_astral": ("Polvo Astral", "#a8dcff", "minecraft:glowstone_dust", True, "Material de refinado astral."),
    "nucleo_astral": ("Nucleo Astral", "#4fd1ff", "minecraft:heart_of_the_sea", True, "Material endgame universal."),
    "nucleo_furia": ("Nucleo de Furia", "#ff3b3b", "minecraft:magma_cream", False, "Cae de Piglin Brutes y Wither Skeletons."),
    "nucleo_furia_pura": ("Nucleo de Furia Pura", "#ff1a1a", "minecraft:fire_charge", True, "Endgame Berserker."),
    "corazon_shulker": ("Corazon de Shulker", "#c58cff", "minecraft:shulker_shell", True, "Cae de Shulkers."),
    "nucleo_eolico": ("Nucleo Eolico", "#bff5e6", "minecraft:wind_charge", True, "Movilidad y arqueros."),
}

# ---------------------------------------------------------------------------
# DROPS de mobs: (tipo de mob o lista, material, probabilidad, condicion)
# condicion: None, "end" (solo en el End)
# ---------------------------------------------------------------------------
NETHER_MOBS = ["minecraft:blaze", "minecraft:ghast", "minecraft:magma_cube", "minecraft:hoglin",
               "minecraft:piglin", "minecraft:zombified_piglin", "minecraft:wither_skeleton",
               "minecraft:piglin_brute"]
MOB_DROPS = {
    "wither_skeleton": (["minecraft:wither_skeleton"], [
        ("esencia_nether", 0.08, None), ("fragmento_umbrio", 0.15, None), ("nucleo_furia", 0.06, None)]),
    "piglin_brute": (["minecraft:piglin_brute"], [
        ("fragmento_umbrio", 0.15, None), ("nucleo_furia", 0.06, None)]),
    "nether": (NETHER_MOBS, [("gema_umbria", 0.02, None)]),
    "enderman": (["minecraft:enderman"], [
        ("cristal_arcano", 0.05, None), ("fragmento_astral", 0.20, "end")]),
    "shulker": (["minecraft:shulker"], [("corazon_shulker", 0.10, None)]),
    "vindicator": (["minecraft:vindicator"], [("nucleo_eolico", 0.10, None)]),
}

# ---------------------------------------------------------------------------
# RECETAS DEL ALTAR (Forja Astral)
# Ingredientes: ("c", id_material, cantidad) material custom
#               ("v", item_vanilla, cantidad) item vanilla
# salida: (id, cantidad)
# ---------------------------------------------------------------------------
MAT_RECIPES = [
    ("netherita_reforzada", 1, [("c", "netherita_fundida", 1), ("v", "minecraft:blaze_powder", 4)]),
    ("shadowsteel", 1, [("v", "minecraft:iron_ingot", 1), ("c", "esencia_nether", 1)]),
    ("cuero_tratado", 2, [("v", "minecraft:leather", 8), ("v", "water_bottle", 1)]),
    ("palo_reforzado", 1, [("c", "shadowsteel", 2), ("v", "minecraft:stick", 1)]),
    ("fragmento_cristal", 4, [("c", "cristal_arcano", 1)]),
    ("cristal_refinado", 1, [("c", "fragmento_cristal", 4)]),
    ("gema_umbria_fragmentada", 1, [("c", "fragmento_umbrio", 8), ("v", "minecraft:coal", 1)]),
    ("gema_umbria", 1, [("c", "fragmento_umbrio", 8), ("c", "gema_umbria_fragmentada", 1)]),
    ("nucleo_furia_pura", 1, [("c", "nucleo_furia", 4), ("v", "minecraft:blaze_powder", 4), ("v", "minecraft:lava_bucket", 1)]),
    ("polvo_astral", 2, [("c", "fragmento_astral", 8)]),
    ("nucleo_astral", 1, [("c", "polvo_astral", 4), ("c", "cristal_refinado", 4), ("c", "corazon_shulker", 1)]),
    ("nucleo_eolico", 1, [("v", "minecraft:feather", 4), ("c", "madera_estelar", 4), ("c", "gema_luminica", 1)]),
    ("gema_luminica_perfecta", 1, [("c", "gema_luminica", 8), ("c", "nucleo_astral", 1)]),
    ("gema_umbria_perfecta", 1, [("c", "gema_umbria", 8), ("c", "nucleo_furia_pura", 1)]),
]

PIECES = ["helmet", "chestplate", "leggings", "boots"]
PIECE_SLOT = {"helmet": "head", "chestplate": "chest", "leggings": "legs", "boots": "feet"}
PIECE_ES = {"helmet": "Casco", "chestplate": "Pechera", "leggings": "Grebas", "boots": "Botas"}
ARMOR_VALUES = {  # armadura vanilla por pieza
    "leather": {"helmet": 1, "chestplate": 3, "leggings": 2, "boots": 1},
    "chainmail": {"helmet": 2, "chestplate": 5, "leggings": 4, "boots": 1},
    "iron": {"helmet": 2, "chestplate": 6, "leggings": 5, "boots": 2},
    "diamond": {"helmet": 3, "chestplate": 8, "leggings": 6, "boots": 3},
    "netherite": {"helmet": 3, "chestplate": 8, "leggings": 6, "boots": 3},
}
TOUGHNESS = {"leather": 0, "chainmail": 0, "iron": 0, "diamond": 2, "netherite": 3}

# ---------------------------------------------------------------------------
# ARMADURAS. Los stats del documento son del set completo; cada pieza da 1/4.
# keys de stats:
#   hp: % vida maxima  dmg: % dano cuerpo a cuerpo  def: % armadura
#   fire: % menos tiempo quemandose  kb: resistencia al empuje (set)
#   mana: mana maximo (AuraSkills)  mregen: % regeneracion de mana
#   mdmg: % dano magico (hechizos)  cdr: % menos enfriamiento de hechizos
#   rdmg: % dano a distancia  crit: % probabilidad de critico  spd: % velocidad
#   draw: % velocidad de disparo
# efectos (solo en la pechera): lifesteal nivel, furia nivel
# ---------------------------------------------------------------------------
ARMOR_SETS = {
    "berserker": {
        "clase": "Berserker", "color": "#ff4d4d", "skill": "forging",
        "tiers": [
            {"name": "del Saqueador", "mat": "chainmail", "lvl": 12,
             "stats": {"hp": 10, "dmg": 5, "def": -5},
             "cost": [("c", "shadowsteel", 2), ("c", "cuero_tratado", 2), ("c", "gema_umbria_fragmentada", 1)]},
            {"name": "del Carnicero", "mat": "iron", "lvl": 16,
             "stats": {"hp": 18, "dmg": 10, "def": -7, "fire": 30},
             "cost": [("c", "shadowsteel", 3), ("c", "netherita_fundida", 1), ("c", "esencia_nether", 1)]},
            {"name": "del Ensangrentado", "mat": "iron", "lvl": 20, "tough": 1,
             "stats": {"hp": 25, "dmg": 18, "def": -10, "fire": 30}, "lifesteal": 1,
             "cost": [("c", "shadowsteel", 4), ("c", "netherita_reforzada", 1), ("c", "gema_umbria", 1)]},
            {"name": "del Coloso", "mat": "diamond", "lvl": 25,
             "stats": {"hp": 35, "dmg": 25, "def": -12, "fire": 30, "kb": 100}, "lifesteal": 1,
             "cost": [("c", "netherita_reforzada", 2), ("c", "cristal_refinado", 1), ("c", "nucleo_furia", 1)]},
            {"name": "del Dios de la Guerra", "mat": "netherite", "lvl": 30,
             "stats": {"hp": 50, "dmg": 40, "def": -15, "fire": 30, "kb": 100}, "lifesteal": 3, "furia": 2,
             "cost": [("c", "netherita_reforzada", 3), ("c", "nucleo_furia_pura", 1), ("c", "gema_umbria_perfecta", 1)]},
        ],
        "piece_names": {"helmet": "Yelmo", "chestplate": "Coraza", "leggings": "Grebas", "boots": "Botas"},
    },
    "mago": {
        "clase": "Mago", "color": "#b26bff", "skill": "sorcery", "dye": [0x5a2d82, 0x6f35a8, 0x8a3fd1, 0x3d2fa8, 0x1f6fd1],
        "tiers": [
            {"name": "del Aprendiz", "mat": "leather", "lvl": 8,
             "stats": {"mana": 30, "mdmg": 5, "def": -10},
             "cost": [("c", "cuero_tratado", 3), ("c", "fragmento_cristal", 2)]},
            {"name": "del Hechicero", "mat": "leather", "lvl": 14,
             "stats": {"mana": 50, "mdmg": 10, "mregen": 5},
             "cost": [("c", "cristal_refinado", 1), ("c", "gema_luminica", 1)]},
            {"name": "del Invocador", "mat": "leather", "lvl": 20,
             "stats": {"mana": 80, "mdmg": 18, "mregen": 10, "hp": -10},
             "cost": [("c", "cristal_refinado", 2), ("c", "madera_estelar", 1)]},
            {"name": "del Archimago", "mat": "leather", "lvl": 26,
             "stats": {"mana": 120, "mdmg": 25, "mregen": 15, "cdr": 10},
             "cost": [("c", "cristal_refinado", 3), ("c", "corazon_shulker", 1)]},
            {"name": "del Sabio Astral", "mat": "leather", "lvl": 32,
             "stats": {"mana": 180, "mdmg": 40, "mregen": 25, "def": -20},
             "cost": [("c", "nucleo_astral", 1), ("c", "gema_luminica_perfecta", 1)]},
        ],
        "piece_names": {"helmet": "Capucha", "chestplate": "Tunica", "leggings": "Faldones", "boots": "Sandalias"},
    },
    "arquero": {
        "clase": "Arquero", "color": "#5ee08a", "skill": "archery", "dye": [0x4b6b2f, 0x3f8a3a, 0x2f6b4f, 0x6bd1a8, 0x9fe6ff],
        "tiers": [
            {"name": "del Rastreador", "mat": "leather", "lvl": 8,
             "stats": {"rdmg": 5, "spd": 5},
             "cost": [("c", "cuero_tratado", 3), ("c", "madera_estelar", 1)]},
            {"name": "del Explorador", "mat": "leather", "lvl": 14,
             "stats": {"rdmg": 10, "crit": 5, "spd": 8},
             "cost": [("c", "madera_estelar", 2), ("c", "gema_luminica", 1)]},
            {"name": "del Francotirador", "mat": "leather", "lvl": 20, "extra_armor": 1,
             "stats": {"rdmg": 18, "crit": 10, "spd": 10},
             "cost": [("c", "madera_estelar", 3), ("c", "cristal_refinado", 1)]},
            {"name": "del Viento", "mat": "leather", "lvl": 25, "extra_armor": 1,
             "stats": {"rdmg": 25, "crit": 15, "spd": 15, "draw": 10},
             "cost": [("c", "nucleo_eolico", 1), ("c", "gema_luminica", 2)]},
            {"name": "del Halcon Astral", "mat": "leather", "lvl": 30, "extra_armor": 2,
             "stats": {"rdmg": 40, "crit": 25, "spd": 20, "draw": 20},
             "cost": [("c", "nucleo_astral", 1), ("c", "gema_luminica_perfecta", 1)]},
        ],
        "piece_names": {"helmet": "Capucha", "chestplate": "Chaqueta", "leggings": "Pantalones", "boots": "Botas"},
    },
}

ROMAN = ["I", "II", "III", "IV", "V"]

# ---------------------------------------------------------------------------
# ARMAS
# ---------------------------------------------------------------------------
# Espadas Berserker: base, dano total, bonus%, efectos, costo, nivel
SWORDS = [
    {"name": "Espada del Saqueador", "base": "minecraft:iron_sword", "dmg": 6, "bonus": 10, "lvl": 12,
     "fx": {"remate": 1}, "cost": [("c", "gema_umbria_fragmentada", 2), ("c", "palo_reforzado", 1)],
     "desc": ["+5% de dano a enemigos con menos del 50% de vida"]},
    {"name": "Espada del Carnicero", "base": "minecraft:iron_sword", "dmg": 6, "bonus": 18, "lvl": 16, "kb_out": -0.5,
     "fx": {"lifesteal": 2}, "cost": [("c", "shadowsteel", 1), ("c", "netherita_fundida", 1)],
     "desc": ["Robo de vida", "Empuja menos al enemigo"]},
    {"name": "Espada Ensangrentada", "base": "minecraft:diamond_sword", "dmg": 7, "bonus": 25, "lvl": 20,
     "fx": {"lifesteal": 3, "furia": 1}, "cost": [("c", "shadowsteel", 1), ("c", "netherita_reforzada", 1)],
     "desc": ["Robo de vida", "Mas dano cuanto menos vida tenes (hasta +15%)"]},
    {"name": "Espada del Coloso", "base": "minecraft:diamond_sword", "dmg": 7, "bonus": 35, "lvl": 25, "kb_res": 1.0,
     "fx": {"lifesteal": 4}, "cost": [("c", "netherita_reforzada", 1), ("c", "cristal_refinado", 1)],
     "desc": ["Robo de vida", "Inmune al empuje mientras la empunas"]},
    {"name": "Espada del Dios de la Guerra", "base": "minecraft:netherite_sword", "dmg": 8, "bonus": 50, "lvl": 30,
     "fx": {"lifesteal": 5, "furia": 2}, "cost": [("c", "netherita_reforzada", 1), ("c", "nucleo_furia_pura", 1)],
     "desc": ["Robo de vida", "+5% de dano por cada 10% de vida perdida"]},
]
AXES = [
    {"name": "Hacha del Desollador", "base": "minecraft:iron_axe", "dmg": 9, "bonus": 18, "spd": 0.81, "lvl": 12,
     "fx": {}, "cost": [("c", "gema_umbria_fragmentada", 3), ("c", "palo_reforzado", 2)], "desc": []},
    {"name": "Hacha del Verdugo", "base": "minecraft:iron_axe", "dmg": 9, "bonus": 30, "spd": 0.9, "lvl": 16,
     "fx": {"verdugo": 1}, "cost": [("c", "shadowsteel", 2), ("c", "netherita_fundida", 1), ("c", "palo_reforzado", 1)],
     "desc": ["+10% de dano a enemigos con armadura"]},
    {"name": "Hacha Carmesi", "base": "minecraft:diamond_axe", "dmg": 9, "bonus": 40, "spd": 1.0, "lvl": 20,
     "fx": {"sangrado": 1}, "cost": [("c", "shadowsteel", 2), ("c", "netherita_reforzada", 1), ("c", "palo_reforzado", 1)],
     "desc": ["10% de probabilidad de causar sangrado"]},
    {"name": "Hacha del Coloso", "base": "minecraft:diamond_axe", "dmg": 9, "bonus": 55, "spd": 1.0, "lvl": 25,
     "fx": {"sangrado": 1, "hendidura": 1}, "cost": [("c", "netherita_reforzada", 2), ("c", "cristal_refinado", 1), ("c", "palo_reforzado", 1)],
     "desc": ["Golpes en area pequena"]},
    {"name": "Hacha del Apocalipsis", "base": "minecraft:netherite_axe", "dmg": 10, "bonus": 75, "spd": 1.0, "lvl": 30,
     "fx": {"sangrado": 1, "hendidura": 1, "ejecucion": 1}, "cost": [("c", "netherita_reforzada", 2), ("c", "nucleo_furia_pura", 1), ("c", "palo_reforzado", 1)],
     "desc": ["Ejecuta enemigos con menos del 15% de vida"]},
]
# Bastones: mana (AuraSkills), dano magico %, enfriamiento (ticks)
STAFFS = [
    {"name": "Baston del Aprendiz", "model": "minecraft:stick", "mana": 20, "mdmg": 5, "spell": 5.0, "cd": 30, "lvl": 8,
     "cost": [("c", "fragmento_cristal", 1), ("c", "madera_estelar", 2)], "desc": []},
    {"name": "Baston del Hechicero", "model": "minecraft:blaze_rod", "mana": 40, "mdmg": 10, "mregen": 5, "spell": 6.5, "cd": 26, "lvl": 14,
     "cost": [("c", "gema_luminica", 1)], "desc": []},
    {"name": "Baston del Invocador", "model": "minecraft:end_rod", "mana": 70, "mdmg": 18, "spell": 8.0, "cd": 22, "lvl": 20,
     "cost": [("c", "cristal_refinado", 2)], "desc": ["Hechizos cuestan menos"]},
    {"name": "Baston del Archimago", "model": "minecraft:lightning_rod", "mana": 110, "mdmg": 25, "cdr": 10, "spell": 10.0, "cd": 18, "lvl": 26,
     "cost": [("c", "corazon_shulker", 1), ("c", "cristal_refinado", 1)], "desc": ["-10% de enfriamiento"]},
    {"name": "Baston Astral", "model": "minecraft:trident", "mana": 180, "mdmg": 40, "pierce": 20, "spell": 13.0, "cd": 14, "lvl": 32,
     "cost": [("c", "gema_luminica_perfecta", 1), ("c", "nucleo_astral", 1)], "desc": ["Ignora 20% de resistencia magica"]},
]
SCYTHES = [
    {"name": "Guadana Umbria Menor", "base": "minecraft:iron_hoe", "dmg": 6, "lvl": 12, "mdmg": 0,
     "fx": {"lifesteal": 1}, "cost": [("c", "gema_umbria_fragmentada", 2), ("c", "shadowsteel", 1), ("c", "palo_reforzado", 1)],
     "desc": ["Dano magico cuerpo a cuerpo", "Roba vida"]},
    {"name": "Guadana del Ritual", "base": "minecraft:iron_hoe", "dmg": 7, "lvl": 16, "mdmg": 10,
     "fx": {"lifesteal": 1, "maldicion": 1}, "cost": [("c", "gema_umbria", 2), ("c", "shadowsteel", 1)],
     "desc": ["Aplica lentitud o debilidad"]},
    {"name": "Guadana del Vacio", "base": "minecraft:diamond_hoe", "dmg": 8, "lvl": 20, "mdmg": 18,
     "fx": {"lifesteal": 1, "maldicion": 1, "cono": 1}, "cost": [("c", "gema_umbria", 2), ("c", "netherita_reforzada", 1)],
     "desc": ["Ataques en cono frontal"]},
    {"name": "Guadana del Archimago", "base": "minecraft:diamond_hoe", "dmg": 9, "lvl": 26, "mdmg": 30, "reset_cd": True,
     "fx": {"lifesteal": 1, "maldicion": 1, "cono": 1}, "cost": [("c", "cristal_refinado", 1), ("c", "gema_umbria", 1), ("c", "netherita_reforzada", 1)],
     "desc": ["Matar mobs reinicia el enfriamiento de hechizos"]},
    {"name": "Guadana Astral", "base": "minecraft:netherite_hoe", "dmg": 11, "lvl": 32, "mdmg": 45, "reset_cd": True,
     "fx": {"lifesteal": 2, "maldicion": 1, "cono": 1, "ejecucion": 2}, "cost": [("c", "gema_umbria_perfecta", 2), ("c", "nucleo_astral", 1)],
     "desc": ["Ejecuta mobs con menos del 20% de vida"]},
]
# Arcos: bonus de dano, reduccion del tiempo de carga (%)
BOWS = [
    {"name": "Arco del Rastreador", "bonus": 0, "draw": 10, "lvl": 8,
     "cost": [("c", "madera_estelar", 3), ("v", "minecraft:string", 3)], "desc": []},
    {"name": "Arco del Explorador", "bonus": 10, "draw": 25, "lvl": 14,
     "cost": [("c", "gema_luminica", 3)], "desc": []},
    {"name": "Arco del Francotirador", "bonus": 18, "draw": 45, "lvl": 20,
     "cost": [("c", "cristal_refinado", 3)], "desc": ["Mayor precision"]},
    {"name": "Arco del Viento", "bonus": 25, "draw": 65, "lvl": 25, "spd": 10,
     "cost": [("c", "nucleo_eolico", 3)], "desc": ["Mas velocidad mientras lo empunas"]},
    {"name": "Arco Astral", "bonus": 40, "draw": 95, "lvl": 30, "infinite": True,
     "cost": [("c", "gema_luminica_perfecta", 2), ("c", "nucleo_astral", 1)],
     "desc": ["Disparo casi instantaneo", "No gasta flechas normales"]},
]
