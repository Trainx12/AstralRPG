# -*- coding: utf-8 -*-
"""
Taladros (Mineria) y Motosierras (Tala / Deforestacion).
Cada nivel se forja con el anterior. Del nivel 3 en adelante son indestructibles.
Pico y hacha de netherita tienen velocidad 9: el nivel 1 ya es mas rapido.
"""

ROMAN_EXT = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]

# area: 1 = un bloque, 2 = 2x1, 3 = 2x2, 4 = 3x3, 5 = 4x4
AREA_NAMES = {1: "1x1", 2: "2x1", 3: "2x2", 4: "3x3", 5: "4x4"}

DRILLS = [
    {"id": "taladro_diamante", "name": "Taladro de Diamante", "color": "#7fe6ff", "tex": "drill_repintar.png",
     "area": 1, "speed": 12, "lvl": 5, "dur": 2600,
     "cost": [("v", "minecraft:diamond_block", 2), ("v", "minecraft:iron_block", 2),
              ("v", "minecraft:redstone_block", 4), ("c", "netherita_fundida", 1)]},
    {"id": "taladro_mitril", "name": "Taladro de Mitril", "color": "#3fe0c5", "tex": "mithril_drill_sx_326.png",
     "area": 2, "speed": 13, "lvl": 8, "dur": 3600,
     "cost": [("c", "netherita_reforzada", 2), ("v", "minecraft:prismarine_crystals", 8),
              ("v", "minecraft:diamond_block", 2)]},
    {"id": "taladro_amatista", "name": "Taladro de Amatista", "color": "#e070ff", "tex": "drill_morado.png",
     "area": 2, "speed": 15, "lvl": 12,
     "cost": [("v", "minecraft:amethyst_block", 8), ("c", "fragmento_cristal", 4), ("c", "netherita_reforzada", 3)]},
    {"id": "taladro_rubi", "name": "Taladro de Rubi", "color": "#ff4b4b", "tex": "ruby_drill_tx_15.png",
     "area": 3, "speed": 16, "lvl": 16,
     "cost": [("c", "nucleo_furia", 2), ("c", "shadowsteel", 2), ("v", "minecraft:redstone_block", 8)]},
    {"id": "taladro_topacio", "name": "Taladro de Topacio", "color": "#ffb52e", "tex": "topaz_drill_kgr_12.png",
     "area": 3, "speed": 18, "lvl": 20,
     "cost": [("c", "gema_luminica", 2), ("c", "esencia_elite", 2), ("v", "minecraft:gold_block", 4)]},
    {"id": "taladro_titanio", "name": "Taladro de Titanio", "color": "#a9b8d8", "tex": "titanium_drill_dr_x655.png",
     "area": 4, "speed": 20, "lvl": 25,
     "cost": [("c", "cristal_refinado", 2), ("c", "shadowsteel", 4), ("v", "minecraft:netherite_ingot", 2)]},
    {"id": "taladro_jaspe", "name": "Taladro de Jaspe", "color": "#ff5fa8", "tex": "jasper_drill_x.png",
     "area": 4, "speed": 23, "lvl": 30,
     "cost": [("c", "gema_umbria", 2), ("c", "nucleo_furia_pura", 1), ("c", "alma_corrupta", 2)]},
    {"id": "taladro_gemas", "name": "Taladro de Gemas", "color": "#9d7bff", "tex": "gemstone_drill_lt_522.png",
     "area": 5, "speed": 26, "lvl": 35,
     "cost": [("c", "gema_luminica_perfecta", 1), ("c", "gema_umbria_perfecta", 1), ("c", "polvo_astral", 4)]},
    {"id": "taladro_divan", "name": "Taladro Divan", "color": "#ffcf4a", "tex": "divan_drill.png",
     "area": 5, "speed": 30, "lvl": 40, "ench": {"minecraft:fortune": 3},
     "cost": [("c", "nucleo_astral", 2), ("c", "chispa_astral", 4), ("v", "minecraft:netherite_block", 1)]},
]

# chain: troncos extra que corta ademas del que rompiste (999 = arbol entero)
CHAINSAWS = [
    {"id": "motosierra_basica", "name": "Motosierra Basica", "color": "#c8c8c8", "tex": "basic_chainsaw.png",
     "chain": 0, "speed": 12, "lvl": 5, "dur": 2600,
     "cost": [("v", "minecraft:iron_block", 3), ("v", "minecraft:diamond", 4),
              ("v", "minecraft:redstone_block", 2), ("c", "netherita_fundida", 1)]},
    {"id": "motosierra_avanzada", "name": "Motosierra Avanzada", "color": "#6fe8d8", "tex": "advanced_chainsaw.png",
     "chain": 1, "speed": 14, "lvl": 10, "dur": 3600,
     "cost": [("c", "netherita_reforzada", 2), ("c", "palo_reforzado", 2), ("v", "minecraft:diamond_block", 2)]},
    {"id": "motosierra_industrial", "name": "Motosierra Industrial", "color": "#5adc5a", "tex": "industrial_chainsaw.png",
     "chain": 2, "speed": 17, "lvl": 16,
     "cost": [("c", "shadowsteel", 3), ("c", "esencia_elite", 2), ("v", "minecraft:emerald_block", 2)]},
    {"id": "motosierra_infernal", "name": "Motosierra Infernal", "color": "#ff6a2a", "tex": "gen:infernal",
     "chain": 5, "speed": 21, "lvl": 24,
     "cost": [("c", "nucleo_furia", 3), ("c", "esencia_nether", 4), ("v", "minecraft:netherite_ingot", 2)]},
    {"id": "motosierra_astral", "name": "Motosierra Astral", "color": "#c07bff", "tex": "gen:astral",
     "chain": 999, "speed": 26, "lvl": 32,
     "cost": [("c", "madera_estelar", 8), ("c", "nucleo_astral", 1), ("c", "polvo_astral", 4)]},
]

# Troncos de arboles naturales (los que sigue la motosierra)
TREE_LOGS = ["oak_log", "spruce_log", "birch_log", "jungle_log", "acacia_log", "dark_oak_log", "mangrove_log",
             "cherry_log", "pale_oak_log", "crimson_stem", "warped_stem"]

# Lo que rompen los taladros en area: solo bloques naturales (nunca cofres, hornos ni construcciones)
DRILLABLE = ["#minecraft:base_stone_overworld", "#minecraft:base_stone_nether", "#minecraft:coal_ores",
             "#minecraft:iron_ores", "#minecraft:copper_ores", "#minecraft:gold_ores", "#minecraft:redstone_ores",
             "#minecraft:lapis_ores", "#minecraft:diamond_ores", "#minecraft:emerald_ores", "#minecraft:terracotta",
             "#minecraft:dirt", "#minecraft:sand",
             "minecraft:nether_quartz_ore", "minecraft:nether_gold_ore", "minecraft:ancient_debris",
             "minecraft:cobblestone", "minecraft:cobbled_deepslate", "minecraft:mossy_cobblestone",
             "minecraft:calcite", "minecraft:dripstone_block", "minecraft:smooth_basalt", "minecraft:end_stone",
             "minecraft:sandstone", "minecraft:red_sandstone", "minecraft:magma_block", "minecraft:amethyst_block",
             "minecraft:gravel", "minecraft:clay", "minecraft:soul_sand", "minecraft:soul_soil",
             "minecraft:snow_block", "minecraft:packed_ice"]
