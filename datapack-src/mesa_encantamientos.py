"""Mesa de encantamientos propia: plugin AstralMesa (reemplaza a LynExp).

Ofrece todos los encantamientos que acepta el objeto (vanilla, ExcellentEnchants y otros plugins),
con paginas, menos las mejoras del Herrero (namespace astral). Mismo cobro que LynExp:
el nivel N de un encantamiento de nivel maximo M cuesta la XP de ceil(N/M*30) niveles (max 1395 puntos).
Tambien conserva lo demas de LynExp: botella de vidrio en la mesa embotella XP y los items de mobs
en un conducto dan XP.

  python mesa_encantamientos.py --jdk <java25>   -> build/mesa/AstralMesa.jar + config.yml + entrega.md
"""
import argparse
import os
from pathlib import Path
import subprocess
import zipfile
from encmagia import MAGIA, DEFINITIVOS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'build' / 'mesa'
STAMP = (2026, 11, 20, 0, 0, 0)

# Mismos valores que tenia LynExp en el server.
CONDUCTO = {'rotten_flesh': 2, 'bone': 3, 'spider_eye': 4, 'string': 1, 'gunpowder': 5,
            'blaze_rod': 10, 'ender_pearl': 8, 'ghast_tear': 12, 'slime_ball': 6}


# Que hace cada encantamiento (se muestra en el libro de la mesa). Sin numeros: los valores de
# ExcellentEnchants pueden cambiar en su config; "mas nivel = mas fuerte" vale para todos los que suben.
VANILLA = {
    'protection': 'Reduce casi todo el daño que recibís.',
    'fire_protection': 'Reduce el daño de fuego y lava y te apaga más rápido.',
    'feather_falling': 'Reduce el daño por caída.',
    'blast_protection': 'Reduce el daño de explosiones y el empuje que te dan.',
    'projectile_protection': 'Reduce el daño de flechas, tridentes y bolas de fuego.',
    'respiration': 'Aguantás más tiempo la respiración bajo el agua.',
    'aqua_affinity': 'Picás bajo el agua a la velocidad normal.',
    'thorns': 'Le devuelve daño a quien te pega (gasta más la armadura).',
    'depth_strider': 'Caminás más rápido bajo el agua.',
    'frost_walker': 'Congela el agua bajo tus pies para caminar arriba.',
    'binding_curse': 'Maldición: no te podés sacar la armadura (salvo al morir).',
    'soul_speed': 'Corrés más rápido sobre arena y tierra de almas.',
    'swift_sneak': 'Te movés más rápido agachado.',
    'sharpness': '+3% de daño por nivel a todos los enemigos (Filo V = +15%).',
    'smite': 'Mucho más daño a muertos vivientes (zombis, esqueletos, wither).',
    'bane_of_arthropods': 'Mucho más daño a arañas, abejas y lepismas, y los frena.',
    'knockback': 'Empuja más lejos a quien golpeás.',
    'fire_aspect': 'Prende fuego a quien golpeás.',
    'looting': 'Los mobs sueltan más botín.',
    'sweeping_edge': 'Más daño al golpe de barrido de la espada.',
    'efficiency': 'Picás, talás y cavás más rápido.',
    'silk_touch': 'Los bloques salen enteros (vidrio, minerales sin romper, etc.).',
    'unbreaking': 'El objeto se gasta más lento.',
    'fortune': 'Los minerales y cultivos sueltan más cosas.',
    'power': 'Las flechas hacen más daño.',
    'punch': 'Las flechas empujan más lejos.',
    'flame': 'Las flechas prenden fuego.',
    'infinity': 'Con una sola flecha en el inventario, disparás sin gastar.',
    'luck_of_the_sea': 'Pescás más tesoros y menos basura.',
    'lure': 'Los peces pican más rápido.',
    'loyalty': 'El tridente vuelve a tu mano después de tirarlo.',
    'impaling': 'Más daño del tridente a criaturas del agua.',
    'riptide': 'Con lluvia o en el agua, el tridente te lanza con él.',
    'channeling': 'Con tormenta, el tridente llama un rayo sobre el enemigo.',
    'multishot': 'La ballesta dispara 3 flechas a la vez.',
    'quick_charge': 'La ballesta carga más rápido.',
    'piercing': 'Las flechas de ballesta atraviesan varios enemigos.',
    'density': 'Más daño de la maza según la altura de la caída.',
    'breach': 'La maza ignora parte de la armadura del enemigo.',
    'wind_burst': 'Al golpear con la maza cayendo, salís impulsado hacia arriba.',
    'lunge': 'La lanza te impulsa hacia adelante al atacar.',
    'mending': 'La XP que juntás repara el objeto.',
    'vanishing_curse': 'Maldición: el objeto desaparece al morir.',
}

ESPECIALES = {
    'auto_reel': 'Recoge la caña sola cuando pica un pez.',
    'bane_of_netherspawn': 'Más daño a mobs del Nether.',
    'blast_mining': 'Chance de picar con una explosión que rompe bloques alrededor.',
    'blindness': 'Chance de dejar ciego al enemigo al golpearlo.',
    'bomber': 'Chance de que el arco dispare una TNT encendida.',
    'cold_steel': 'Chance de darle fatiga de minado a quien te pega.',
    'confusing_arrows': 'Chance de que la flecha maree (náusea) al enemigo.',
    'confusion': 'Chance de marear (náusea) al enemigo al golpearlo.',
    'cure': 'Chance de curar a piglins zombi y aldeanos zombi al golpearlos.',
    'curse_of_breaking': 'Maldición: chance de gastar durabilidad de más.',
    'curse_of_death': 'Maldición: al matar a un jugador podés morir vos también.',
    'curse_of_drowned': 'Maldición: chance de pescar un ahogado.',
    'curse_of_fragility': 'Maldición: no se puede usar en yunque ni piedra de afilar.',
    'curse_of_mediocrity': 'Maldición: chance de que lo que sueltan salga sin encantar.',
    'curse_of_misfortune': 'Maldición: chance de que bloques y mobs no suelten nada.',
    'cutter': 'Chance de sacarle una pieza de armadura al enemigo y dañarla.',
    'darkness_arrows': 'Chance de que la flecha deje en oscuridad al enemigo.',
    'darkness_cloak': 'Chance de dejar en oscuridad a quien te pega.',
    'decapitator': 'Chance de que el jugador o mob suelte su cabeza.',
    'double_catch': 'Chance de pescar el doble.',
    'double_strike': 'Chance de hacer doble daño.',
    'dragon_heart': 'Te da corazones extra (absorción) todo el tiempo.',
    'dragonfire_arrows': 'Chance de que la flecha deje fuego de dragón donde cae.',
    'electrified_arrows': 'Chance de que la flecha llame un rayo con daño extra.',
    'elemental_protection': 'Reduce el daño de pociones y elementos (fuego, hielo, etc.).',
    'ender_bow': 'El arco dispara perlas de ender en vez de flechas.',
    'exhaust': 'Chance de darle hambre al enemigo al golpearlo.',
    'explosive_arrows': 'Chance de disparar una flecha explosiva.',
    'fire_shield': 'Chance de prender fuego a quien te pega.',
    'flame_walker': 'Caminás sobre lava y el magma no te hace daño.',
    'flare': 'Chance de poner una antorcha donde cae la flecha.',
    'ghast': 'El arco dispara bolas de fuego en vez de flechas.',
    'glassbreaker': 'Rompe el vidrio al instante.',
    'hardened': 'Chance de ganar resistencia al recibir daño.',
    'haste': 'Te da prisa minera mientras picás.',
    'hover': 'Chance de que la flecha haga levitar al enemigo.',
    'ice_aspect': 'Congela y frena al enemigo al golpearlo.',
    'ice_shield': 'Chance de congelar y frenar a quien te pega.',
    'infernus': 'El tridente prende fuego al enemigo que toca.',
    'jumping': 'Saltás más alto todo el tiempo.',
    'kamikadze': 'Chance de explotar al morir.',
    'lightweight': 'Podés pisar huevos de tortuga y cultivos sin romperlos.',
    'lingering': 'Chance de que las flechas con poción dejen una nube del efecto.',
    'lucky_miner': 'Chance de ganar más XP de los minerales.',
    'night_vision': 'Visión nocturna todo el tiempo.',
    'nimble': 'Lo que sueltan los mobs va directo a tu inventario.',
    'paralyze': 'Chance de darle fatiga de minado al enemigo al golpearlo.',
    'poisoned_arrows': 'Chance de que la flecha envenene.',
    'rage': 'Chance de ganar fuerza al golpear.',
    'rebound': 'Rebotás al caer, como sobre un bloque de slime.',
    'regrowth': 'Te cura un poco de vida cada algunos segundos.',
    'replanter': 'Vuelve a plantar los cultivos al cosecharlos.',
    'restore': 'Chance de salvar el objeto cuando está por romperse.',
    'river_master': 'Tirás la caña más lejos.',
    'rocket': 'Chance de lanzar al enemigo por el aire.',
    'saturation': 'Te llena la comida cada algunos segundos.',
    'seasoned_angler': 'Ganás más XP pescando.',
    'silk_chest': 'Los cofres salen enteros con todo lo que tienen adentro.',
    'silk_spawner': 'Chance de llevarte el generador de mobs al picarlo.',
    'smelter': 'Chance de que lo que picás salga ya fundido.',
    'sniper': 'Las flechas vuelan más rápido.',
    'soulbound': 'No se te cae al morir.',
    'speed': 'Velocidad todo el tiempo.',
    'stopping_force': 'Chance de recibir menos empuje.',
    'survivalist': 'Los pescados salen ya cocinados.',
    'swiper': 'Chance de robarle XP a los jugadores al golpearlos.',
    'telekinesis': 'Lo que picás va directo a tu inventario.',
    'temper': 'Hasta +10% de daño según la vida que te falta. Solo nivel I.',
    'thrifty': 'Chance de que los mobs suelten su huevo de aparición.',
    'thunder': 'Rayo con daño según tu golpe: 10% de chance y +55% en I, hasta 18% y +115% en V.',
    'treefeller': 'Tala el árbol entero de un golpe.',
    'tunnel': 'Pica varios bloques a la vez (3x3).',
    'vampire': 'Chance de curarte al golpear.',
    'vampiric_arrows': 'Chance de curarte cuando la flecha pega.',
    'veinminer': 'Pica toda la veta de mineral de una.',
    'venom': 'Chance de envenenar al enemigo al golpearlo.',
    'village_defender': 'Más daño a los saqueadores (illagers).',
    'water_breathing': 'Respirás bajo el agua todo el tiempo.',
    'wisdom': 'Los mobs sueltan más XP.',
    'wither': 'Chance de darle efecto wither al enemigo al golpearlo.',
    'withered_arrows': 'Chance de que la flecha dé efecto wither.',
}


BASTONES = [
    'minecraft:looting',                 # botin del mob muerto con el hechizo
    'excellentenchants:wisdom',          # mas XP de los mobs
    'excellentenchants:nimble',          # botin directo al inventario
    'excellentenchants:decapitator',     # cabezas
    'excellentenchants:thrifty',         # huevos de mobs
    'excellentenchants:soulbound',       # no se cae al morir
    'excellentenchants:restore',         # se salva al romperse
    'excellentenchants:curse_of_breaking', 'excellentenchants:curse_of_misfortune', 'excellentenchants:curse_of_mediocrity',
]


# Encantamientos de datapacks del server (Stellarity y Dungeons and Taverns).
DATAPACKS = {
    'stellarity:ambush': 'Mucho más daño a mobs que todavía no te están atacando.',
    'stellarity:critical_strike': 'Cada tanto da un golpe crítico de doble daño.',
    'stellarity:dune_speed': 'Corrés más rápido sobre arena.',
    'stellarity:levitation_shot': 'Las flechas hacen levitar al enemigo.',
    'stellarity:plated': 'Elytra blindada: da armadura pero caés más rápido.',
    'stellarity:soaring': 'Elytra liviana: planeás más lejos.',
    'nova_structures:aerials_bane': 'Más daño a enemigos que están en el aire o vuelan.',
    'nova_structures:antidote': 'Te protege del veneno y del wither (gasta la pechera).',
    'nova_structures:conductivity_curse': 'Maldición: con tormenta te pueden caer rayos.',
    'nova_structures:ghasted': 'La ballesta dispara bolas de fuego de ghast.',
    'nova_structures:gravity': 'Los proyectiles atraen a los enemigos cercanos al punto de impacto.',
    'nova_structures:hydro_veil': 'El arnés del ghast cura y protege con lluvia.',
    'nova_structures:illagers_bane': 'Más daño a los saqueadores (illagers).',
    'nova_structures:multishot': 'El arco dispara varias flechas a la vez.',
    'nova_structures:outreach': 'Llegás a romper y poner bloques más lejos.',
    'nova_structures:photosynthesis': 'El objeto se repara solo con la luz del sol.',
    'nova_structures:piercing': 'Las flechas del arco atraviesan enemigos.',
    'nova_structures:power': 'Más daño de las flechas de ballesta.',
    'nova_structures:spiteful': 'Más daño a enemigos con fuerza; les saca el efecto.',
    'nova_structures:swift_soar': 'El ghast con arnés vuela más rápido.',
    'nova_structures:traveler': 'Al correr subís bloques sin saltar y vas más rápido.',
    'nova_structures:wax_wings': 'La elytra no se gasta... salvo que vueles muy alto de día.',
    'nova_structures:wither_coated': 'Da efecto wither al golpear (el arma se gasta más).',
}

# Claves internas de datapacks (jefes, jinetes, chequeos, objetos unicos): nunca en la mesa.
EXCLUIR_CONTIENE = ['technical', 'jockey/', 'boss', 'level_checker', 'shulker_', 'stellarity:void_s']

# Nombres en espanol para el tooltip (los vanilla los traduce el juego solo).
NOMBRES = {
    'excellentenchants:auto_reel': 'Auto Recoger', 'excellentenchants:bane_of_netherspawn': 'Azote del Nether',
    'excellentenchants:blast_mining': 'Minería Explosiva', 'excellentenchants:blindness': 'Ceguera',
    'excellentenchants:bomber': 'Bombardero', 'excellentenchants:cold_steel': 'Acero Frío',
    'excellentenchants:confusing_arrows': 'Flechas Mareantes', 'excellentenchants:confusion': 'Confusión',
    'excellentenchants:cure': 'Cura', 'excellentenchants:curse_of_breaking': 'Maldición de Rotura',
    'excellentenchants:curse_of_death': 'Maldición de Muerte', 'excellentenchants:curse_of_drowned': 'Maldición del Ahogado',
    'excellentenchants:curse_of_fragility': 'Maldición de Fragilidad', 'excellentenchants:curse_of_mediocrity': 'Maldición de Mediocridad',
    'excellentenchants:curse_of_misfortune': 'Maldición de Desgracia', 'excellentenchants:cutter': 'Cortador',
    'excellentenchants:darkness_arrows': 'Flechas Oscuras', 'excellentenchants:darkness_cloak': 'Manto Oscuro',
    'excellentenchants:decapitator': 'Decapitador', 'excellentenchants:double_catch': 'Doble Pesca',
    'excellentenchants:double_strike': 'Doble Golpe', 'excellentenchants:dragon_heart': 'Corazón de Dragón',
    'excellentenchants:dragonfire_arrows': 'Flechas de Fuego de Dragón', 'excellentenchants:electrified_arrows': 'Flechas Eléctricas',
    'excellentenchants:elemental_protection': 'Protección Elemental', 'excellentenchants:ender_bow': 'Arco de Ender',
    'excellentenchants:exhaust': 'Agotamiento', 'excellentenchants:explosive_arrows': 'Flechas Explosivas',
    'excellentenchants:fire_shield': 'Escudo de Fuego', 'excellentenchants:flame_walker': 'Caminante de Lava',
    'excellentenchants:flare': 'Bengala', 'excellentenchants:ghast': 'Ghast', 'excellentenchants:glassbreaker': 'Rompevidrios',
    'excellentenchants:hardened': 'Endurecido', 'excellentenchants:haste': 'Prisa', 'excellentenchants:hover': 'Levitación',
    'excellentenchants:ice_aspect': 'Aspecto de Hielo', 'excellentenchants:ice_shield': 'Escudo de Hielo',
    'excellentenchants:infernus': 'Infierno', 'excellentenchants:jumping': 'Salto', 'excellentenchants:kamikadze': 'Kamikaze',
    'excellentenchants:lightweight': 'Liviano', 'excellentenchants:lingering': 'Persistente',
    'excellentenchants:lucky_miner': 'Minero Suertudo', 'excellentenchants:night_vision': 'Visión Nocturna',
    'excellentenchants:nimble': 'Ágil', 'excellentenchants:paralyze': 'Parálisis',
    'excellentenchants:poisoned_arrows': 'Flechas Venenosas', 'excellentenchants:rage': 'Furia', 'excellentenchants:rebound': 'Rebote',
    'excellentenchants:regrowth': 'Regeneración', 'excellentenchants:replanter': 'Replantador', 'excellentenchants:restore': 'Restaurar',
    'excellentenchants:river_master': 'Maestro del Río', 'excellentenchants:rocket': 'Cohete', 'excellentenchants:saturation': 'Saciedad',
    'excellentenchants:seasoned_angler': 'Pescador Experto', 'excellentenchants:silk_chest': 'Cofre de Seda',
    'excellentenchants:silk_spawner': 'Generador de Seda', 'excellentenchants:smelter': 'Fundidor', 'excellentenchants:sniper': 'Francotirador',
    'excellentenchants:soulbound': 'Alma Ligada', 'excellentenchants:speed': 'Velocidad', 'excellentenchants:stopping_force': 'Firmeza',
    'excellentenchants:survivalist': 'Superviviente', 'excellentenchants:swiper': 'Ladrón de XP', 'excellentenchants:telekinesis': 'Telequinesis',
    'excellentenchants:temper': 'Temple', 'excellentenchants:thrifty': 'Ahorrador', 'excellentenchants:thunder': 'Trueno',
    'excellentenchants:treefeller': 'Leñador', 'excellentenchants:tunnel': 'Túnel', 'excellentenchants:vampire': 'Vampiro',
    'excellentenchants:vampiric_arrows': 'Flechas Vampíricas', 'excellentenchants:veinminer': 'Minero de Vetas',
    'excellentenchants:venom': 'Veneno', 'excellentenchants:village_defender': 'Defensor de Aldeas',
    'excellentenchants:water_breathing': 'Respiración Acuática', 'excellentenchants:wisdom': 'Sabiduría', 'excellentenchants:wither': 'Wither',
    'excellentenchants:withered_arrows': 'Flechas Wither',
    'stellarity:ambush': 'Emboscada', 'stellarity:critical_strike': 'Golpe Crítico', 'stellarity:dune_speed': 'Velocidad de Duna',
    'stellarity:levitation_shot': 'Tiro Levitante', 'stellarity:plated': 'Blindado', 'stellarity:soaring': 'Planeo',
    'nova_structures:aerials_bane': 'Azote Aéreo', 'nova_structures:antidote': 'Antídoto',
    'nova_structures:conductivity_curse': 'Maldición de Conductividad', 'nova_structures:ghasted': 'Ghasteado',
    'nova_structures:gravity': 'Gravedad', 'nova_structures:hydro_veil': 'Velo de Agua', 'nova_structures:illagers_bane': 'Azote de Illagers',
    'nova_structures:multishot': 'Multidisparo de Arco', 'nova_structures:outreach': 'Alcance', 'nova_structures:photosynthesis': 'Fotosíntesis',
    'nova_structures:piercing': 'Perforación de Arco', 'nova_structures:power': 'Poder de Ballesta', 'nova_structures:spiteful': 'Rencoroso',
    'nova_structures:swift_soar': 'Vuelo Veloz', 'nova_structures:traveler': 'Viajero', 'nova_structures:wax_wings': 'Alas de Cera',
    'nova_structures:wither_coated': 'Bañado en Wither',
}

# Precio segun que tan bueno es: el nivel maximo cuesta la XP de estos niveles (normal = 30 = 1395 puntos).
# 40 niveles = 2920 puntos, 50 = 5345. Las maldiciones son baratas.
BUENO, MUY_BUENO, MALDICION = 40, 50, 10
_MUY_BUENOS = '''minecraft:mending minecraft:infinity minecraft:silk_touch
excellentenchants:soulbound excellentenchants:telekinesis excellentenchants:veinminer excellentenchants:treefeller
excellentenchants:tunnel excellentenchants:blast_mining excellentenchants:nimble excellentenchants:double_strike
excellentenchants:vampire excellentenchants:restore excellentenchants:wisdom excellentenchants:regrowth
excellentenchants:dragon_heart excellentenchants:flame_walker excellentenchants:silk_spawner excellentenchants:smelter
stellarity:critical_strike nova_structures:photosynthesis nova_structures:multishot'''.split()
_BUENOS = '''minecraft:sharpness minecraft:protection minecraft:efficiency minecraft:fortune minecraft:looting
minecraft:unbreaking minecraft:power minecraft:multishot minecraft:riptide minecraft:channeling minecraft:breach
minecraft:density minecraft:wind_burst minecraft:swift_sneak minecraft:soul_speed minecraft:frost_walker
excellentenchants:thunder excellentenchants:temper excellentenchants:rage excellentenchants:saturation
excellentenchants:speed excellentenchants:jumping excellentenchants:night_vision excellentenchants:water_breathing
excellentenchants:lucky_miner excellentenchants:haste excellentenchants:ice_aspect excellentenchants:venom
excellentenchants:wither excellentenchants:electrified_arrows excellentenchants:explosive_arrows excellentenchants:sniper
excellentenchants:vampiric_arrows excellentenchants:hardened excellentenchants:elemental_protection
excellentenchants:decapitator excellentenchants:thrifty excellentenchants:silk_chest excellentenchants:replanter
excellentenchants:cutter excellentenchants:paralyze excellentenchants:rocket excellentenchants:fire_shield
excellentenchants:ice_shield excellentenchants:bomber excellentenchants:ghast excellentenchants:dragonfire_arrows
stellarity:ambush stellarity:dune_speed stellarity:levitation_shot stellarity:plated stellarity:soaring
nova_structures:illagers_bane nova_structures:spiteful nova_structures:wither_coated nova_structures:aerials_bane
nova_structures:power nova_structures:piercing nova_structures:outreach nova_structures:traveler
nova_structures:swift_soar nova_structures:hydro_veil nova_structures:antidote nova_structures:ghasted
nova_structures:gravity nova_structures:wax_wings'''.split()


def costos():
    c = {k: MUY_BUENO for k in _MUY_BUENOS}
    c.update({k: BUENO for k in _BUENOS})
    for k in list(VANILLA) + list(ESPECIALES):
        full = ('minecraft:' if k in VANILLA else 'excellentenchants:') + k
        if 'curse' in k:
            c[full] = MALDICION
    c['nova_structures:conductivity_curse'] = MALDICION
    c.update({"astral:" + k: MUY_BUENO for k in DEFINITIVOS})
    return c


def descripciones():
    d = {f'minecraft:{k}': v for k, v in VANILLA.items()}
    d.update({f'excellentenchants:{k}': v for k, v in ESPECIALES.items()})
    d.update(DATAPACKS)
    d.update({"astral:" + k: v[3] for k, v in MAGIA.items()})
    return d


def precio_subasta():
    import economia
    mob = economia.PLATA_MOB_TIER
    return {
        'activo': True, 'publico': False, 'solo': ['ByTrainx'],
        'archivo': 'CrazyAuctions/data.yml', 'cada-segundos': 60,
        # Sugerido = base del tier (arma ~400 mobs Astral de su tier, pieza de armadura ~240)
        # x (1 + 4% por nivel de encantamiento + 10% por nivel de Mejora del Herrero) + gemas al costo de engarzar.
        # 26/11 (dueno): antes x20/x12 (arco T5 = 500k) era muy barato: Diamante III da ~2,5M en 15 min.
        # Ahora arma T5 ~10M (~1 h de minas altas), pieza de armadura T5 ~6M.
        # 26/11 tarde (dueno): arco T5 a 10M seguia barato -> x2: arma T5 20M, pieza de armadura T5 12M.
        'base-arma': {t: v * 800 for t, v in mob.items()},
        'base-armadura': {t: v * 480 for t, v in mob.items()},
        'por-nivel-encantamiento': 0.04,
        'por-nivel-herrero': 0.10,
        'gema-tier': dict(economia.GEMA_PONER_TIER),
        'gema-calidad': dict(economia.GEMA_CALIDAD_MULT),
    }


def config():
    return {
        'encmagia': {'publico': False},
        'niveles-maximo': 30,
        'particulas': True,
        # astral = mejoras del Herrero (Mejora +N): nunca en la mesa.
        'excluir-namespaces': ['astral'],
        # Baneados por el dueno (24/11): Tunel choca con los taladros. 25/11: Mineria Explosiva, Cortador,
        # Bombardero y Ghast (misma lista que ee_descripciones.BANEADOS).
        'excluir': ['excellentenchants:tunnel', 'excellentenchants:blast_mining', 'excellentenchants:cutter',
                    'excellentenchants:bomber', 'excellentenchants:ghast'],
        'excluir-contiene': EXCLUIR_CONTIENE,
        # Niveles que cuesta el nivel maximo de cada uno (si no esta, niveles-maximo).
        'costos': costos(),
        # Lista de encantamientos en el objeto, estilo Hypixel (la arma AstralMesa por paquetes).
        # Con pocos: cada uno con su descripcion. Con muchos: varios por linea, en azul.
        'tooltip': {'activo': True, 'con-descripcion-hasta': 4, 'por-linea': 3},
        'nombres': {**NOMBRES, **{'astral:' + k: v[0] for k, v in MAGIA.items()}},
        'botella': {'costo-xp': 5},
        'conducto': CONDUCTO,
        # Bastones de mago (carrot_on_a_stick): el juego solo les deja Irrompibilidad y Reparacion.
        # El hechizo es dano magico del jugador, asi que sirven los que actuan al matar o son pasivos.
        'bastones': BASTONES,
        # Texto del libro en la mesa. Si falta uno, el libro sale sin descripcion.
        'descripciones': descripciones(),
        # 25/11 (dueno): precio de subasta abajo de armas/armaduras Astral, estilo Hypixel. Lo mas barato de
        # CrazyAuctions (compra directa) para ese mismo equipo; si no hay, precio sugerido. Solo ByTrainx
        # hasta `astralmesa precios publico`.
        'precio-subasta': precio_subasta(),
        # 26/11 (dueno): la linea "Dano: +N (+M)" suma lo fijo: Mejora del Herrero y Filo en porcentaje
        # (escala.FILO_PCT). Solo a quien tiene la etiqueta astral.filo (la pone el datapack: ByTrainx hasta
        # /function astral:filo/publico). Lo que depende de algo (Furia, Emboscada, Trueno) no se suma.
        'dano-real': dano_real(),
    }


def dano_real():
    from escala import FILO_PCT
    from items import MEJORA_DANO
    return {'activo': True, 'filo-porcentaje': FILO_PCT, 'mejora': list(MEJORA_DANO)}


PLUGIN_YML = """name: AstralMesa
version: 1.5.3
main: astral.AstralMesa
api-version: '26.1.2'
description: Mesa de encantamientos con todos los encantamientos (vanilla y de plugins) salvo las mejoras del Herrero
depend: [AuraSkills]
softdepend: [ExcellentEnchants, packetevents, AstralParty]
commands:
  encmagia:
    description: Abre o cierra los encantamientos mágicos
    permission: astral.mesa.admin
  encmagia_interno:
    description: Puente interno de consola
    permission: astral.mesa.admin
  astralmesa:
    description: Recarga la config de la mesa
    usage: /astralmesa reload
    permission: astral.mesa.admin
permissions:
  astral.mesa.admin:
    default: op
"""


def build_plugin(jdk, server, packetevents):
    import yaml
    jdk, server = Path(jdk), Path(server)
    classes = ROOT / '.local' / 'mesa-classes'
    classes.mkdir(parents=True, exist_ok=True)
    deps = [*server.joinpath('libraries').rglob('*.jar'), *server.joinpath('versions').rglob('*.jar'), Path(packetevents), server / 'plugins/auraskills.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-nowarn', '-classpath',
                    os.pathsep.join(map(str, deps)), '-d', str(classes), str(HERE / 'runtime' / 'AstralMesa.java'), str(HERE / 'runtime' / 'AstralMesaMagia.java')], check=True)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'AstralMesa.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((classes / 'astral').glob('AstralMesa*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + p.name, STAMP), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), yaml.safe_dump(config(), sort_keys=False, allow_unicode=True))
    return dest


ENTREGA = """# Mesa de encantamientos: AstralMesa (reemplaza a LynExp)

Problema: LynExp arma un libro por nivel y la ventana tiene 48 lugares. Con ExcellentEnchants
los libros pasan de 48 y los vanilla quedaban afuera.

AstralMesa muestra todo (vanilla primero, despues ExcellentEnchants, maldiciones al final) con paginas,
sin las mejoras del Herrero (`astral:`). Saca los niveles que el objeto ya tiene y los que chocan con
lo que ya tiene. El objeto queda en la mesa para encantar varias veces; al cerrar vuelve al inventario.

## Subir
1. Files: `plugins/` -> borrar (o renombrar a `.jar.off`) `LynExp-1.0.0-mc26.1-26.1.2.jar`.
2. Subir `build/mesa/AstralMesa.jar` a `plugins/`.
3. Reiniciar el server (crea `plugins/AstralMesa/config.yml`).
4. Probar: clic derecho en una mesa de encantamientos con una espada en el inventario.

Config: `plugins/AstralMesa/config.yml`, recargar con `astralmesa reload`.
"""


def generate():
    import yaml
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'config.yml').write_text(yaml.safe_dump(config(), sort_keys=False, allow_unicode=True), encoding='utf-8')
    (OUT / 'entrega.md').write_text(ENTREGA, encoding='utf-8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--jdk')
    ap.add_argument('--server', default=str(ROOT / '.local' / 'testsrv'))
    ap.add_argument('--packetevents', default=str(ROOT / '.local' / 'spam-paper-cs2dghr2' / 'plugins' / 'packetevents.jar'),
                    help='jar de packetevents (solo para compilar)')
    a = ap.parse_args()
    generate()
    if a.jdk:
        print('plugin ->', build_plugin(a.jdk, a.server, a.packetevents))
    print('mesa ->', OUT)
