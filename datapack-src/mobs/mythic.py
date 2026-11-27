# -*- coding: utf-8 -*-
"""
Genera la configuracion de MythicMobs para las criaturas de AstralRPG:
mobs (vida, dano, modelo), monturas, elites, jefes, drops y probabilidad de aparicion.
Salida: ../../build/mythicmobs/{mobs,skills,randomspawns}/astral.yml
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from items import MEJORAS  # noqa: E402  (costos de la mejora +1..+10, los comparte con el datapack)
OUT = os.path.join(HERE, "..", "..", "build", "mythicmobs")


def astral_drop(item, chance, amount=1):
    """Suelta un item de AstralRPG donde muere el mob (usa las loot tables del datapack)."""
    lines = []
    for _ in range(amount):
        lines.append(f"- command{{c=\"execute at <caster.uuid> run loot spawn ~ ~0.5 ~ loot astral:item/{item}\"}} @self ~onDeath {chance}")
    return lines


# --------------------------------------------------------------------------- definicion
# kind: pasivo | hostil | montura | jefe
# Jefes: persiguen un poco mas rapido que una arana; golpe al piso, disparo y salto (mobs/jefes_combate.py).
from mobs.jefes_combate import VELOCIDAD as VELOCIDAD_JEFE, triggers as jefe_triggers, metaskills as jefe_metaskills  # noqa: E402

MOBS = {
    # ---------------- fauna
    "astral_mapache": dict(kind="hostil", type="ZOMBIE", name="&6Mapache Rabioso", hp=14, damage=3, speed=0.3, hostile_ai=True,
                           drops=["leather 1-2 0.8", "sweet_berries 1-3 0.5", "exp 3"],
                           astral=[("cuero_tratado", 0.15)],
                           spawn=dict(chance=0.06, biomes=["minecraft:forest", "minecraft:birch_forest", "minecraft:dark_forest",
                                                           "minecraft:old_growth_pine_taiga", "minecraft:taiga"])),
    "astral_pinguino": dict(kind="hostil", type="ZOMBIE", name="&bPinguino de Hielo", hp=12, damage=3, speed=0.22, hostile_ai=True,
                            skills=['- command{c="astralchill <trigger.uuid>"} @trigger ~onAttack ?~isplayer'],
                            drops=["cod 1-2 0.7", "feather 1-2 0.6", "exp 3"],
                            astral=[("fragmento_cristal", 0.12)],
                            spawn=dict(chance=0.08, biomes=["minecraft:snowy_plains", "minecraft:ice_spikes", "minecraft:frozen_ocean",
                                                            "minecraft:snowy_beach", "minecraft:frozen_peaks"])),
    # ---------------- hostiles
    "astral_espantapajaros": dict(kind="hostil", type="VEX", name="&6Espantapajaros Maldito", hp=34, damage=6, speed=0.25,
                                  drops=["pumpkin 1 0.5", "wheat 1-4 0.8", "string 1-2 0.5", "exp 8"],
                                  astral=[("esencia_elite", 0.08), ("fragmento_umbrio", 0.10)],
                                  skills=[],
                                  spawn=dict(chance=0.05, night=True, biomes=["minecraft:plains", "minecraft:sunflower_plains",
                                                                               "minecraft:savanna", "minecraft:meadow"])),
    "astral_goblin": dict(kind="hostil", type="ZOMBIE", name="&2Goblin", hp=16, damage=3, speed=0.34,
                           hostile_ai=True, attack_animation=None, drops=["exp 5"], skills=[
                               '- command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self ~onSpawn']),
    "astral_abejorro": dict(kind="hostil", type="VEX", name="&8Armored Grub", hp=20, damage=5, speed=0.3,
                            drops=["honeycomb 1-2 0.4", "string 1 0.4", "exp 8"],
                            astral=[("gema_umbria_fragmentada", 0.08), ("esencia_elite", 0.06)],
                            skills=[],
                            spawn=dict(chance=0.04, biomes=["minecraft:flower_forest", "minecraft:dark_forest", "minecraft:swamp",
                                                            "minecraft:mangrove_swamp"])),
    "astral_arana": dict(kind="hostil", type="ZOGLIN", hostile_ai=True, name="&5Arana Amatista", hp=26, damage=5, speed=0.3,
                         drops=["string 1-3 0.9", "spider_eye 1 0.5", "amethyst_shard 1-2 0.5", "exp 8"],
                         astral=[("fragmento_cristal", 0.15), ("cristal_arcano", 0.03)],
                         spawn=dict(chance=0.05, cave=True, biomes=["minecraft:dripstone_caves", "minecraft:lush_caves",
                                                                    "minecraft:deep_dark", "minecraft:dark_forest"])),
    "astral_cara": dict(kind="hostil", type="PHANTOM", name="&cCara Voladora", hp=22, damage=6, speed=0.3,
                        drops=["phantom_membrane 1 0.6", "rotten_flesh 1-2 0.6", "exp 10"],
                        astral=[("gema_umbria", 0.03), ("alma_corrupta", 0.05)],
                        skills=[],
                        spawn=dict(chance=0.03, night=True, biomes=["minecraft:swamp", "minecraft:mangrove_swamp",
                                                                     "minecraft:dark_forest", "minecraft:badlands"])),
    # ---------------- monturas (sin montura puesta: el jugador le pone la suya)
    "astral_grillo": dict(kind="montura", type="HORSE", name="&aGrillo Saltarin", hp=26, speed=0.24, jump=1.25,
                          drops=["leather 1 0.5", "slime_ball 1 0.3", "exp 5"],
                          spawn=dict(chance=0.025, biomes=["minecraft:plains", "minecraft:meadow", "minecraft:sunflower_plains"])),
    "astral_chocobo": dict(kind="montura", type="HORSE", name="&eAve Corredora", hp=30, speed=0.38, jump=0.7,
                           drops=["feather 2-4 0.9", "exp 5"],
                           spawn=dict(chance=0.02, biomes=["minecraft:savanna", "minecraft:savanna_plateau", "minecraft:plains"])),
    "astral_escarabajo": dict(kind="montura", type="HORSE", name="&9Escarabajo Acorazado", hp=60, speed=0.14, jump=0.45,
                              drops=["turtle_scute 1 0.3", "exp 5"], armor=10,
                              spawn=dict(chance=0.02, biomes=["minecraft:jungle", "minecraft:sparse_jungle", "minecraft:bamboo_jungle"])),
    "astral_lagarto": dict(kind="montura", type="SKELETON_HORSE", name="&aLagarto de Pantano", hp=34, speed=0.22, jump=0.6,
                           drops=["leather 1-2 0.8", "exp 5"],
                           spawn=dict(chance=0.025, biomes=["minecraft:swamp", "minecraft:mangrove_swamp", "minecraft:river"])),
    "astral_ave": dict(kind="montura", type="PARROT", name="&6Gran Ave", hp=40, speed=0.32, fly=True,
                       drops=["feather 3-6 1", "exp 6"],
                       spawn=dict(chance=0.01, biomes=["minecraft:windswept_hills", "minecraft:stony_peaks", "minecraft:jagged_peaks",
                                                       "minecraft:meadow"])),
    "astral_pterodactilo": dict(kind="montura", type="PHANTOM", name="&9Pterodactilo", hp=50, speed=0.36, fly=True,
                                drops=["bone 2-4 0.9", "exp 6"],
                                spawn=dict(chance=0.008, biomes=["minecraft:badlands", "minecraft:eroded_badlands",
                                                                 "minecraft:wooded_badlands", "minecraft:jungle"])),
    # ---------------- jefes
    "astral_momia": dict(kind="jefe", type="HUSK", name="&e&lMomia Ancestral", hp=320, damage=10, speed=VELOCIDAD_JEFE,
                         # Barra roja, no amarilla: BetterHud usa la amarilla para el panel y la vuelve invisible
                         bar="RED", drops=["gold_ingot 3-8 1", "bone 4-8 1", "exp 120"],
                         astral=[("alma_corrupta", 1.0), ("chispa_astral", 0.35), ("gema_luminica", 0.8), ("esencia_elite", 1.0, 3)],
                         skills=["- summon{type=HUSK;amount=2;radius=3} @self ~onTimer:300",
                                 "- potion{type=SLOW;duration=80;level=1} @target ~onAttack 0.4",
                                 "- message{m=\"&eLa Momia Ancestral despierta...\"} @PlayersInRadius{r=30} ~onSpawn"],
                         spawn=dict(chance=0.0015, biomes=["minecraft:desert"])),
    "astral_yeti": dict(kind="jefe", type="RAVAGER", name="&f&lYeti de las Cumbres", hp=450, damage=14, speed=VELOCIDAD_JEFE,
                        bar="WHITE", drops=["snow_block 4-10 1", "leather 4-8 1", "exp 150"],
                        astral=[("alma_corrupta", 1.0, 2), ("chispa_astral", 0.45), ("cristal_refinado", 0.8), ("esencia_elite", 1.0, 3)],
                        skills=["- potion{type=SLOW;duration=100;level=2} @PlayersInRadius{r=6} ~onTimer:200",
                                "- leap{velocity=150;noise=0} @target ~onTimer:160 0.5",
                                "- message{m=\"&fUn rugido helado retumba en la montana...\"} @PlayersInRadius{r=40} ~onSpawn",
                                ],      # mascota (mobs/mascotas.py)
                        spawn=dict(chance=0.0012, biomes=["minecraft:frozen_peaks", "minecraft:snowy_slopes", "minecraft:ice_spikes"])),
    "astral_golem_forja": dict(kind="jefe", type="IRON_GOLEM", name="&c&lGolem de la Forja", hp=500, damage=16, speed=VELOCIDAD_JEFE,
                               bar="RED", drops=["netherite_scrap 1-2 0.5", "iron_ingot 6-12 1", "blaze_rod 2-4 1", "exp 180"],
                               astral=[("nucleo_furia", 1.0, 2), ("netherita_fundida", 0.6), ("chispa_astral", 0.5),
                                       ("esencia_elite", 1.0, 3)],
                               hostile_ai=True,
                               skills=["- ignite{ticks=80} @PlayersInRadius{r=4} ~onTimer:100",
                                       "- particles{p=flame;amount=40;hS=1;vS=1.5;speed=0.05} @self ~onTimer:40",
                                       "- message{m=\"&cEl suelo arde, el Golem de la Forja se levanta.\"} @PlayersInRadius{r=40} ~onSpawn"],
                               spawn=dict(chance=0.002, world="world_nether", biomes=["minecraft:basalt_deltas", "minecraft:nether_wastes",
                                                                                       "minecraft:crimson_forest"])),
    "astral_cangrejo": dict(kind="jefe", type="ZOGLIN", name="&6&lCangrejo Ermitano Gigante", hp=260, damage=9, speed=VELOCIDAD_JEFE,
                            bar="PINK", drops=["nautilus_shell 1 0.6", "prismarine_shard 2-5 1", "exp 100"],
                            astral=[("alma_corrupta", 0.8), ("corazon_shulker", 0.3), ("esencia_elite", 1.0, 2)],
                            skills=["- throw{velocity=8;velocityY=4} @target ~onAttack 0.35",
                                    "- message{m=\"&6Algo enorme se arrastra por la arena...\"} @PlayersInRadius{r=30} ~onSpawn"],
                            spawn=dict(chance=0.002, biomes=["minecraft:beach", "minecraft:stony_shore", "minecraft:warm_ocean"])),
    "astral_chaman": dict(kind="jefe", type="EVOKER", name="&2&lChaman del Pantano", hp=340, damage=8, speed=VELOCIDAD_JEFE,
                          bar="GREEN", drops=["totem_of_undying 1 0.3", "emerald 3-8 1", "slime_ball 2-6 1", "exp 160"],
                          astral=[("alma_corrupta", 1.0, 2), ("chispa_astral", 0.4), ("gema_umbria", 0.8), ("esencia_elite", 1.0, 3)],
                          skills=["- potion{type=POISON;duration=80;level=1} @PlayersInRadius{r=8} ~onTimer:220",
                                  "- summon{type=WITCH;amount=1;radius=3} @self ~onTimer:400",
                                  "- message{m=\"&2Un canto extrano sale del pantano...\"} @PlayersInRadius{r=40} ~onSpawn"],
                          spawn=dict(chance=0.0015, night=True, biomes=["minecraft:swamp", "minecraft:mangrove_swamp"])),
}

# Elites: versiones modificadas (mas grandes, con otro color) que dan mas cosas
ELITES = {
    "astral_espantapajaros": ("FF3A3A", "&4Espantapajaros Infernal"),
    "astral_abejorro": ("FFC020", "&6Armored Grub Reina"),
    "astral_arana": ("40FFD0", "&3Arana de Cristal Vivo"),
    "astral_cara": ("A040FF", "&5Cara del Abismo"),
    "astral_cangrejo": ("60A0FF", "&9Cangrejo Abisal"),
}


# Eventos mundiales: version "ancestral" de cada jefe. Muy rara, se anuncia a todo el servidor con coordenadas,
# tiene 5 veces la vida del jefe, fases y un afijo, y si nadie la mata en 10 minutos se va.
ANCESTRALES = {
    "astral_momia": ("FFD24A", "&6&lFarao Ancestral"),
    "astral_yeti": ("9FE8FF", "&b&lYeti Ancestral"),
    "astral_golem_forja": ("FF6A2A", "&4&lColoso de la Forja Ancestral"),
    "astral_cangrejo": ("FF9AD0", "&d&lCangrejo Ancestral"),
    "astral_chaman": ("7CFF6A", "&2&lGran Chaman Ancestral"),
}
ANCESTRAL_MINUTOS = 10
# 26/11 (dueno): los jefes del Survival se trababan. Miden como mucho ALTO_JEFE_MUNDO bloques (los de
# mazmorra y Santuario tienen sus propias skills de modelo y no cambian) y persiguen saltando si quedan lejos.
ALTO_JEFE_MUNDO = 6.0
ANCESTRAL_VIDA = 5      # veces la vida de un jefe normal del mismo tier


def escala_mundo(mid, s=2.0):
    """Escala del modelo para el jefe del Survival: la de siempre, pero sin pasar de ALTO_JEFE_MUNDO de alto."""
    from mobs.tamanos import dimensions
    alto = dimensions(mid, s)[1]
    return s if alto <= ALTO_JEFE_MUNDO else round(s * ALTO_JEFE_MUNDO / alto, 3)


# Persecucion de los jefes del Survival: si el objetivo queda a mas de 6 bloques salta hacia el; si se
# trabo detras de arboles o paredes y queda a mas de 18, aparece al lado (solo si el objetivo esta a < 48).
PERSECUCION_MUNDO = [
    "- leap{velocity=110;noise=0} @target ~onTimer:60 ?!playerwithin{d=6} ?targetwithin{d=24}",
    "- teleport{spreadh=3;spreadv=0} @target ~onTimer:200 ?!playerwithin{d=18} ?targetwithin{d=48}",
]


def ancestral_def(mid):
    d = dict(MOBS[mid])
    color, name = ANCESTRALES[mid]
    d["name"] = name
    # el elite ya multiplica x2.5. Minecraft corta la vida maxima en 1024, asi que se queda en 1000
    # y se compensa con Resistencia I permanente (20% menos dano)
    d["hp"] = min(d["hp"] * 2, 400)
    d["damage"] = d["damage"]     # el elite ya lo sube x1.6
    d["ancestral"] = True
    d["astral"] = list(d.get("astral", [])) + [("frasco_xp_pequeno",0.65),("frasco_xp_grande",0.35),("frasco_xp_gigante",0.20),("barril_xp",0.025)] + [("chispa_astral", 1.0, 2), ("alma_corrupta", 1.0, 2)]
    d["skills"] = list(d.get("skills", [])) + [
        f"- 'message{{m=\"&6&l(!) &e{name} &7desperto en &f<caster.l.x> <caster.l.y> <caster.l.z> &7(&f<caster.l.w>&7). Tienen {ANCESTRAL_MINUTOS} minutos!\"}} @PlayersOnServer ~onSpawn'",
        "- sound{s=entity.ender_dragon.growl;v=0.5} @PlayersOnServer ~onSpawn",
        "- potion{type=RESISTANCE;duration=240;level=0;hasParticles=false} @self ~onSpawn",
        "- potion{type=RESISTANCE;duration=240;level=0;hasParticles=false} @self ~onTimer:200",
        f"- skill{{s=AST_ANCESTRAL_SEVA_{mid}}} @self ~onTimer:{ANCESTRAL_MINUTOS * 1200}",
        # Evento cada X horas (ancestral_evento.py): si el jugador elegido se aleja o cambia de mundo,
        # el Skript le pone esta etiqueta y el jefe se va (sin premios).
        f"- skill{{s=AST_ANCESTRAL_FUERA_{mid}}} @self ~onTimer:20 ?hastag{{tag=astral.ancestral.fuera}}",
        f"- skill{{s=AST_ANCESTRAL_FUERA_{mid}}} @self ~onLoad ?hastag{{tag=astral.ancestral.fuera}}",
        f"- 'message{{m=\"&6&l(!) &e<trigger.name> &7derroto a {name}&7!\"}} @PlayersOnServer ~onDeath ?isplayer'",
    ]
    d["spawn"] = dict(d["spawn"], chance=round(d["spawn"]["chance"] * 0.25, 6))
    return d


# Fases de los jefes: al bajar de cierta vida cambian de comportamiento (se marca con un tag para que pase una sola vez).
# Cada fase: (porcentaje de vida, mensaje, skills que corren una vez al entrar, skills que se repiten mientras dure)
# Las repetidas llevan su propio trigger (~onTimer:N); el generador les agrega la condicion de la fase.
def _onda(dano, radio, part, sonido):
    """Ataque en area con aviso: particulas en el piso, 1 segundo para alejarse, despues pega."""
    return [f"particles{{p={part};amount=60;hS={radio};vS=0.2;speed=0}} @self",
            f"sound{{s={sonido};v=1.5}} @self", "delay 20",
            f"particles{{p={part};amount=120;hS={radio};vS=0.6;speed=0.1}} @self",
            # 23/11: golpe en area = doble del golpe del jefe (su Damage); el x tier lo pone astral_gameplay.sk.
            f"basedamage{{multiplier=2}} @PlayersInRadius{{r={radio}}}"]


FASES = {
    "astral_momia": [
        (60, "&eLa Momia Ancestral levanta una tormenta de arena!",
         ["summon{type=HUSK;amount=3;radius=4} @self", "potion{type=BLINDNESS;duration=60;level=0} @PlayersInRadius{r=12}"],
         {"onda": (_onda(5, 5, "cloud", "entity.husk.converted_to_zombie"), 120)}),
        (25, "&6&lLa Momia Ancestral entra en furia: matala antes de que se cure!",
         ["potion{type=RESISTANCE;duration=160;level=2} @self"],
         {"cura": (["heal{a=8} @self", "particles{p=happy_villager;amount=20;hS=1;vS=1.5} @self"], 100)}),
    ],
    "astral_yeti": [
        (60, "&fEl Yeti golpea el piso: la montana tiembla!",
         ["summon{type=STRAY;amount=2;radius=4} @self"],
         {"onda": (_onda(6, 6, "snowflake", "entity.ravager.roar"), 100)}),
        (25, "&b&lEl Yeti se cubre de hielo y se vuelve mas rapido!",
         ["potion{type=RESISTANCE;duration=160;level=2} @self", "potion{type=SPEED;duration=999999;level=0} @self"],
         {"frio": (["potion{type=SLOWNESS;duration=60;level=1} @PlayersInRadius{r=10}",
                    "particles{p=snowflake;amount=80;hS=8;vS=1} @self"], 80)}),
    ],
    "astral_golem_forja": [
        (60, "&cEl Golem de la Forja se pone al rojo vivo!",
         ["potion{type=SPEED;duration=999999;level=0} @self"],
         {"onda": (_onda(6, 5, "lava", "entity.blaze.shoot") + ["ignite{ticks=60} @PlayersInRadius{r=5}"], 120)}),
        (25, "&4&lEl Golem de la Forja va a explotar de calor: alejate de el!",
         ["potion{type=STRENGTH;duration=999999;level=0} @self"],
         {"empuje": (["throw{velocity=6;velocityY=3} @PlayersInRadius{r=4}",
                      "particles{p=flame;amount=60;hS=2;vS=1} @self"], 140)}),
    ],
    "astral_cangrejo": [
        (60, "&6El Cangrejo llama a sus crias!",
         ["summon{type=CAVE_SPIDER;amount=3;radius=3} @self"], {}),
        (25, "&e&lEl Cangrejo se mete en su caparazon!",
         ["potion{type=RESISTANCE;duration=120;level=3} @self", "potion{type=SPEED;duration=999999;level=0} @self"],
         {"pinza": (_onda(5, 4, "bubble_pop", "entity.turtle.egg_crack"), 100)}),
    ],
    "astral_chaman": [
        (60, "&2El Chaman invoca espiritus del pantano!",
         ["summon{type=VEX;amount=2;radius=2} @self"],
         {"veneno": (["potion{type=POISON;duration=60;level=1} @PlayersInRadius{r=6}",
                      "particles{p=witch;amount=60;hS=5;vS=0.5} @self"], 120)}),
        (25, "&a&lEl Chaman bebe una pocion y se cura!",
         ["heal{a=60} @self", "summon{type=WITCH;amount=2;radius=3} @self"], {}),
    ],
}

# Afijos de los elites: al aparecer cada elite saca uno al azar (se ve en el nombre).
#  id: (nombre, skills que corren al aparecer, skills que se repiten con su trigger)
AFIJOS = {
    "vamp": ("&4Vampirico", [], ["heal{a=4} @self ~onAttack", "particles{p=heart;amount=4;vS=1} @self ~onAttack"]),
    "expl": ("&cExplosivo", [], ["particles{p=explosion;amount=6;hS=2} @self ~onDeath",
                                 "sound{s=entity.generic.explode} @self ~onDeath",
                                 "damage{a=6} @PlayersInRadius{r=4} ~onDeath"]),
    "blind": ("&7Blindado", ["potion{type=RESISTANCE;duration=240;level=0} @self"],
              ["potion{type=RESISTANCE;duration=240;level=0} @self ~onTimer:200"]),
    "veloz": ("&bVeloz", ["potion{type=SPEED;duration=240;level=1} @self"],
              ["potion{type=SPEED;duration=240;level=1} @self ~onTimer:200"]),
    "invoc": ("&5Invocador", [], ["summon{type=<base>;amount=1;radius=3} @self ~onTimer:300 ?playerwithin{d=12} 0.5"]),
    "mald": ("&8Maldito", [], ["potion{type=WEAKNESS;duration=60;level=0} @PlayersInRadius{r=5} ~onTimer:60",
                               "particles{p=smoke;amount=30;hS=2;vS=1} @self ~onTimer:60"]),
}


def afijos_de(mid):
    """El Invocador llama a la version normal del mob; los jefes no invocan copias de si mismos."""
    return [a for a in AFIJOS if not (a == "invoc" and MOBS[mid]["kind"] == "jefe")]


def con_condicion(skill, cond):
    """Agrega una condicion inline a un skill que ya trae trigger (va antes de la probabilidad final, si hay)."""
    parts = skill.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].replace(".", "", 1).isdigit():
        return f"{parts[0]} {cond} {parts[1]}"
    return f"{skill} {cond}"


# Plata para quien mata: la cifra sale de economia.py (tier del mob x categoria) y la paga
# astral_economia.sk (mazmorras: tabla de oleada/jefe por tier del mundo).
PLATA_CATEGORIAS = ("hostil", "elite", "jefe", "ancestral")

# Vendedores del lobby: aldeanos quietos e invulnerables. Al hacerles clic abren su tienda o gacha.
# (ubicacion de cada uno: datapack-src/lobby.py)
def _gacha(gid, cost):
    """Clic: menu de la gacha (DeluxeMenus, datapack-src/menus.py). Shift + clic: vitrina de premios."""
    G = gid.upper()
    return [f"skill{{s=AST_{G}_INFO}} @trigger ~onInteract ?~crouching",
            f"command{{c=\"dm open {gid} <trigger.name>\"}} @self ~onInteract ?~!crouching",
            "state{s=open} @self ~onInteract ?~!crouching"]


def _herrero():
    """La interfaz conserva el objeto y usa las mismas reglas del datapack."""
    return ['command{c="astralherrero <trigger.name>"} @self ~onInteract']


def _bazar():
    """Clic: menu del bazar (DeluxeMenus): mercado (RoyalBazaar), subastas y ordenes (EzAuction)."""
    return ["command{c=\"dm open bazar <trigger.name>\"} @self ~onInteract"]


NPCS = {
    "astral_npc_expediciones": ("&b&lExpediciones Astrales &7- mazmorras y arena", "CARTOGRAPHER",
                                ['command{c="dm open expediciones <trigger.name>"} @self ~onInteract']),
    "astral_npc_guia_reino": ("&b&lExpediciones Astrales &7- elegir destino", "CARTOGRAPHER",
                              ['command{c="dm open expediciones <trigger.name>"} @self ~onInteract']),
    "astral_npc_guia_cavernas": ("&b&lExpediciones Astrales &7- elegir destino", "CARTOGRAPHER",
                                 ['command{c="dm open expediciones <trigger.name>"} @self ~onInteract']),
    "astral_npc_guia_expediciones": ("&b&lExpediciones Astrales &7- elegir destino", "CARTOGRAPHER",
                                 ['command{c="dm open expediciones <trigger.name>"} @self ~onInteract']),
    "astral_npc_bazar": ("&6&lBazar &7(mercado y subastas)", "CARTOGRAPHER", _bazar()),
    # 18/11: elige Casa de Subastas o Banco Astral (menus.subastas_inicio_menu).
    "astral_npc_subastas": ("&e&lSubastas y Banco", "ARMORER", ["command{c=\"dm open subastas_inicio <trigger.name>\"} @self ~onInteract"]),
    "astral_npc_herrero": ("&6&lHerrero &7- mejorar equipo", "WEAPONSMITH", _herrero()),
    "astral_npc_tienda": ("&6&lTienda", "TOOLSMITH",
                          ["command{c=\"sudo <trigger.name> economyshopgui:shop\"} @self ~onInteract"]),
    "astral_npc_venta": ("&a&lVenta rapida", "FARMER",
                         ["command{c=\"astralventa <trigger.name>\"} @self ~onInteract"]),
    "astral_npc_gacha_rpg": ("&5&lGacha de Armas", "LIBRARIAN", _gacha("gacha_rpg", 1000)),
    "astral_npc_gacha_monturas": ("&a&lGacha de Monturas", "SHEPHERD",
                                  _gacha("gacha_monturas", 2500)),
    "astral_npc_gacha_cosmeticos": ("&d&lGacha de Cosmeticos", "CARTOGRAPHER",
                                    _gacha("gacha_cosmeticos", 500)),
    "astral_npc_viajero": ("&f&lViajero &7- ir al mundo", "NITWIT",
                           ["command{c=\"mvtp <trigger.name> w:world\"} @self ~onInteract"]),
    "astral_npc_minas": ("&b&lMinas Astrales &7- elegir mina", "TOOLSMITH",
                         ['command{c="minasmenu <trigger.name>"} @self ~onInteract']),
    "astral_npc_mina_venta": ("&a&lVenta rapida &7- minerales", "MASON",
                              ['command{c="minasventa <trigger.name>"} @self ~onInteract']),
    "astral_npc_mina_viaje": ("&b&lViajes &7- lobby u otra mina", "CARTOGRAPHER",
                              ['command{c="minasmenu <trigger.name>"} @self ~onInteract']),
    "astral_npc_bosque_venta": ("&a&lVenta rapida &7- maderas", "FLETCHER",
                                ['command{c="bosqueventa <trigger.name>"} @self ~onInteract']),
    "astral_npc_bosque_viaje": ("&b&lViajes &7- minas y lobby", "CARTOGRAPHER",
                                ['command{c="minasmenu <trigger.name>"} @self ~onInteract']),
    "astral_npc_cronista": ("&b&lCronista &7- misiones diarias", "LIBRARIAN",
                            ["skill{s=AQ_CRONISTA} @trigger ~onInteract",
                             "skill{s=AQ_CLOCK} @self ~onTimer:200",
                             "skill{s=AQ_CLOCK} @self ~onSpawn",
                             "skill{s=AQ_PAY} @PlayersOnServer ~onTimer:20",
                             "skill{s=AQ_TITLE} @PlayersOnServer ~onTimer:20",
                             "skill{s=AQ_GACHA} @PlayersOnServer ~onTimer:20"]),
}

for _npc in ("herrero", "tienda", "bazar"):
    NPCS[f"astral_npc_{_npc}"][2].insert(0, f"skill{{s=AQ_{_npc.upper()}}} @trigger ~onInteract")


# Las gachas son cofres (modelo de BetterModel sobre una oveja quieta: su caja de golpe es como la de un cofre)
NPC_COFRE = {"astral_npc_gacha_rpg": "astral_cofre_rpg", "astral_npc_gacha_monturas": "astral_cofre_monturas",
             "astral_npc_gacha_cosmeticos": "astral_cofre_cosmeticos"}


# 23/11/2026: estos llevan cartel grande de lobby.NAME_HOLOS en el lugar de su nombre; sin nombre de MythicMobs.
NOMBRE_EN_CARTEL = {"astral_npc_bazar", "astral_npc_subastas", "astral_npc_herrero", "astral_npc_tienda", "astral_npc_venta"}


def npc_block(mid, name, prof, skills):
    cofre = NPC_COFRE.get(mid)
    sin_nombre = mid in NOMBRE_EN_CARTEL
    lines = [f"{mid}:", f"  Type: {'SHEEP' if cofre else 'VILLAGER'}"] + ([] if sin_nombre else [f"  Display: '{name}'"]) + ["  Health: 100", "  Options:",
             "    NoAI: true", "    Invincible: true", "    Silent: true", "    Despawn: false", "    Persistent: true",
             "    Collidable: false", "    PreventItemPickup: true", "    PreventOtherDrops: true",
             f"    AlwaysShowName: {'false' if cofre or sin_nombre else 'true'}"]
    lines += [] if cofre else [f"    Profession: {prof}", "    VillagerType: PLAINS"]
    lines += ["  Skills:", "  - cancelevent @self ~onInteract"]
    if cofre:
        lines += [f"  - model{{m={cofre}}} @self ~onSpawn", f"  - model{{m={cofre}}} @self ~onLoad"]
    from mobs.tanda3c import npc_skills
    lines += ["  - " + s for s in npc_skills(mid)]
    lines += ["  - '" + s.replace("'", "''") + "'" for s in skills]
    return "\n".join(lines) + "\n"


def mob_block(mid, d, model=None, elite=None):
    model = model or mid
    lines = [f"{mid}:", f"  Type: {d['type']}", f"  Display: '{elite[1] if elite else d['name']}'"]
    hp = d["hp"] * (2.5 if elite else 1)
    lines.append(f"  Health: {int(hp)}")
    if d.get("damage"):
        lines.append(f"  Damage: {round(d['damage'] * (1.6 if elite else 1), 1)}")
    if d.get("armor") or elite:
        lines.append(f"  Armor: {d.get('armor', 0) + (6 if elite else 0)}")
    opts = ["    PreventOtherDrops: true", "    Silent: true", "    PreventSunburn: true", "    Despawn: false"
            if d["kind"] in ("montura", "jefe") else "    Despawn: true"]
    if d.get("speed"):
        opts.append(f"    MovementSpeed: {d['speed']}")
    if d["kind"] == "jefe" or elite:
        opts.append("    KnockbackResistance: 0.8")
        opts.append(f"    FollowRange: {64 if d.get('mundo') else 40}")
    opts.append("    PreventRandomEquipment: true")   # el vex no saca su espada encima del modelo
    lines.append("  Options:")
    lines += opts
    if d["kind"] == "montura" and d["type"] == "PHANTOM":
        # pterodactilo: vuela en circulos como un phantom pero no ataca
        lines += ["  AITargetSelectors:", "  - clear"]
    if d.get("hostile_ai") or d["kind"] == "jefe":
        # Todos los jefes persiguen y pegan (13/11/2026); antes solo el golem tenia IA hostil explicita.
        lines += ["  AIGoalSelectors:", "  - clear", "  - meleeattack", "  - randomstroll", "  - lookatplayers",
                  "  AITargetSelectors:", "  - clear", "  - attacker", "  - players"]
    if d["kind"] == "jefe":
        lines += ["  BossBar:", "    Enabled: true", f"    Title: '{d['name']}'", "    Range: 48",
                  f"    Color: {d['bar']}", "    Style: SEGMENTED_10"]
    # drops vanilla
    drops = list(d.get("drops", []))
    if elite:
        drops = [x for x in drops] + ["exp 30", "diamond 1 0.15"]
    lines.append("  Drops:")
    lines += [f"  - {x}" for x in drops]
    # habilidades
    model_skill = d.get('model_skill', f'AST_MODEL_{(elite and mid) or model}')
    sk = [f"- skill{{s={model_skill}}} @self ~onSpawn", f"- skill{{s={model_skill}}} @self ~onLoad"]
    if d['kind'] == 'jefe' and not d.get('suppress_quest'):
        sk += ['- command{c="execute as <caster.uuid> at @s run function astral:mob/jefe_mundo"} @self ~onSpawn']
        # 25/11: la plata leia astral.mtN y los jefes de mundo no la tienen (pagaban siempre tier 1).
        sk += [f'- command{{c="execute as <caster.uuid> if score @s astral.mt matches {t} run tag @s add astral.pt{t}"}} @self ~onSpawn'
               for t in range(1, 11)]
        if d.get("ancestral"):
            # 25/11: jefe_mundo le ponia la misma vida que al jefe normal (murio de 2 golpes). x ANCESTRAL_VIDA.
            sk += [f'- command{{c="minecraft:attribute <caster.uuid> minecraft:max_health modifier add astral:ancestral {ANCESTRAL_VIDA - 1} add_multiplied_total"}} @self ~onSpawn',
                   '- command{c="minecraft:data modify entity <caster.uuid> Health set value 1.0E30f"} @self ~onSpawn']
    if mid in ("astral_mapache", "astral_pinguino"):
        sk += ['- command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self ~onSpawn']
    if mid in ("astral_mapache", "astral_pinguino"):
        # 25/11: el lobby tiene mob-spawning allow (vendedores), asi que los huevos de la gacha
        # funcionaban ahi y la montura no se podia usar (WorldGuard no deja montar). Se borra al
        # aparecer y el huevo vuelve al jugador mas cercano (el que lo uso).
        sk += [f'- command{{c="mm egg give <target.name> {mid} 1"}} @NearestPlayer{{r=10}} ~onSpawn ?world{{w=lobby}}',
               "- message{m=\"&eLos huevos de monturas y criaturas se usan en el mundo, no en el lobby. Te devolvimos el huevo.\"} "
               "@NearestPlayer{r=10} ~onSpawn ?world{w=lobby}",
               '- remove @self ~onSpawn ?world{w=lobby}']
    if d["kind"] == "montura" and not d.get("fly"):
        # Caballo real: evita que un pasajero de BetterModel quede sentado sin conducir.
        sk += [f'- command{{c="execute as <caster.uuid> run tag @s add {mid}"}} @self ~onSpawn',
               f'- command{{c="execute as <caster.uuid> run tag @s add {mid}"}} @self ~onLoad',
               '- command{c="data merge entity <caster.uuid> {Tame:1b}"} @self ~onSpawn',
               '- command{c="data merge entity <caster.uuid> {Tame:1b}"} @self ~onLoad',
               f'- skill{{s=AST_MOUNT_{mid}}} @self ~onSpawn',
               f'- skill{{s=AST_MOUNT_{mid}}} @self ~onLoad',
               '- cancelevent @self ~onInteract',
               '- command{c="astralmount <caster.uuid> <trigger.uuid>"} @self ~onInteract',
               '- skill{s=AST_SILLA_VER} @self ~onLoad',
               # PreventOtherDrops suprime tambien la silla nativa (ver ensayo Paper).
               '- dropitem{items=saddle} @self ~onDeath ?hastag{tag=astral.ensillado}']
    elif d["kind"] == "montura":
        # El runtime comparte propietario y antirrobo con los caballos; conserva asiento volador BetterModel.
        sk += [f'- command{{c="execute as <caster.uuid> run tag @s add {mid}"}} @self ~onSpawn',
               f'- command{{c="execute as <caster.uuid> run tag @s add {mid}"}} @self ~onLoad',
               f"- skill{{s=AST_MOUNT_{mid}}} @self ~onSpawn",
               f"- skill{{s=AST_MOUNT_{mid}}} @self ~onLoad",
               "- skill{s=AST_SILLA_VER} @self ~onLoad",
               "- cancelevent @self ~onInteract",
               '- command{c="astralmount <caster.uuid> <trigger.uuid>"} @self ~onInteract',
               "- setAI{ai=false} @self ~onTimer:10 ?modelhaspassenger",
               "- setAI{ai=true} @self ~onTimer:10 ?!modelhaspassenger ?!hastag{tag=astral.mount_mode}",
               "- dropitem{items=saddle} @self ~onDeath ?hastag{tag=astral.ensillado}"]
    elif d["kind"] in ("hostil", "jefe") or elite:
        if d.get('attack_animation', 'attack'):
            sk.append(f"- state{{s={d.get('attack_animation', 'attack')}}} @self ~onAttack")
    for a in d.get("astral", []):
        item, ch = a[0], a[1]
        amount = a[2] if len(a) > 2 else 1
        if elite and item not in __import__('tanda_xp').XP:
            ch = min(1.0, ch * 2.5)
            amount += 1
        sk += astral_drop(item, ch, amount)
    if elite:
        sk += astral_drop("esencia_elite", 1.0, 2) + astral_drop("alma_corrupta", 0.3)
    sk += d.get("skills", [])
    if d.get("mundo"):
        sk += PERSECUCION_MUNDO
    if d['kind'] in ('hostil','jefe','fauna') and not d.get('native_death_only'):
        sk.append('- skill{s=AST_MUERTE} @self ~onDeath')
    real = f"{mid}" if not elite else mid          # id del mob que se esta generando
    base = model                                   # id de la criatura normal
    if d["kind"] == "jefe":
        sk += ["- " + x for x in jefe_triggers(base)]   # golpe al piso, disparo y salto
    # Un evento personal por baja. Las variantes de mazmorra reutilizan este
    # mismo bloque y por eso conservan tanto las fases como la historia.
    if d["kind"] in ("hostil", "jefe") and not d.get("suppress_quest"):
        _event = base.removeprefix("astral_")
        if _event not in ("espantapajaros", "abejorro", "arana", "cara", "cangrejo", "chaman", "momia", "yeti", "golem_forja"):
            _event = "hostil"
        sk.append(f'- command{{c="execute as <trigger.name> at @s run function astral:quest/event/{_event}"}} @self ~onDeath ?~isplayer')
        if _event == "cangrejo":
            # Sin mazmorra: su fragmento va a /fragmentos la primera vez que lo matas (cofre_mazmorra.py).
            sk.append("- 'message{m=\"&b&lNuevo fragmento: &fFragmento de la Marea&7. Quedo guardado en &f/fragmentos&7.\"} @trigger ~onDeath ?~isplayer ?~!haspermission{p=astral.fragmento.marea}'")
            sk.append('- command{c="lp user <trigger.name> permission set astral.fragmento.marea true"} @self ~onDeath ?~isplayer ?~!haspermission{p=astral.fragmento.marea}')
    if elite and d["kind"] == "hostil":
        sk.append('- command{c="execute as <trigger.name> at @s run function astral:quest/event/elite"} @self ~onDeath ?~isplayer')
    if d["kind"] == "jefe" and (not elite or d.get("ancestral")) and not d.get('stationary'):
        for n, (pct, _, _, timers) in enumerate(FASES.get(base, []), start=2):
            sk.append(f"- skill{{s=AST_FASE_{base}_{n}}} @self ~onDamaged ?healthpercent{{p=<{pct / 100}}} ?!hastag{{tag=astral.fase{n}}}")
            for tname, (_, every) in timers.items():
                sk.append(f"- skill{{s=AST_FASE_{base}_{n}_{tname}}} @self ~onTimer:{every} ?hastag{{tag=astral.fase{n}}} ?playerwithin{{d=24}}")
    if elite:
        sk.append("- randomskill{skills=" + ",".join(f"AST_AFIJO_{real}_{a}" for a in afijos_de(base)) + "} @self ~onSpawn")
        for a in afijos_de(base):
            for x in AFIJOS[a][2]:
                sk.append("- " + con_condicion(x.replace("<base>", base), f"?hastag{{tag=astral.af_{a}}}"))
    cat = plata_categoria(d, elite)
    if cat:
        # Plata del mob segun su tier (economia.py). x(1 + renacimientos) en astral_economia.sk.
        sk.append(f"- skill{{s=AST_PLATA_{cat.upper()}}} @self ~onDeath ?~isplayer")
    lines.append("  Skills:")
    lines += ["  " + s for s in sk]
    return "\n".join(lines) + "\n"


def plata_categoria(d, elite=None):
    if d.get("ancestral"):
        return "ancestral"
    if elite:
        return "elite"
    return d["kind"] if d["kind"] in ("hostil", "jefe") else None


def plata_metaskills():
    """AST_PLATA_<CAT>: una linea por tier (etiqueta astral.mtN que pone mob/roll); sin tier = tier 1."""
    out = []
    for cat in PLATA_CATEGORIAS:
        out += [f"AST_PLATA_{cat.upper()}:", "  Skills:"]
        for t in range(1, 11):
            out.append(f"  - command{{c=\"astralplatamob <trigger.name> {cat} {t}\"}} @self ?hastag{{tag=astral.mt{t}}}")
        # Jefes de mundo: jefe_mundo guarda el tier en el puntaje astral.mt sin la etiqueta astral.mtN
        # (esa etiqueta cambiaria su dano). PLATA_TIER_JEFE les pone astral.ptN solo para la plata.
        for t in range(1, 11):
            out.append(f"  - command{{c=\"astralplatamob <trigger.name> {cat} {t}\"}} @self ?hastag{{tag=astral.pt{t}}}")
        sin = " ".join(f"?!hastag{{tag=astral.mt{t}}} ?!hastag{{tag=astral.pt{t}}}" for t in range(1, 11))
        out += [f"  - command{{c=\"astralplatamob <trigger.name> {cat} 1\"}} @self {sin}", ""]
    return out


def metaskills():
    out = plata_metaskills() + ['AST_MUERTE:', '  Skills:', '  - tint{c=FF5555} @self',
           '  - delay 16', '  - particles{p=poof;amount=14;hS=0.5;vS=0.5} @self', '']
    for mid, d in MOBS.items():
        # Los jefes normales del Survival (Yeti y Golem pasaban los 6 bloques); la Momia de la Tumba usa
        # esta misma skill pero mide 4,1 y no cambia. Cumbre, Forja y Bosque tienen skill propia.
        scale = f';s={escala_mundo(mid)}' if d['kind'] == 'jefe' else ''
        out += [f"AST_MODEL_{mid}:", "  Skills:", "  - addtag{tag=astral.seen} @self", f"  - model{{m={mid}{scale}}} @self"]
        if mid == "astral_goblin":
            out[-1] = "  - delay 1"
        if d["kind"] == "montura":
            # BetterModel mueve la montura con la velocidad de movimiento y salta con jump_strength
            out += [f"AST_MOUNT_{mid}:", "  Skills:", "  - delay 2",
                    f"  - command{{c=\"attribute <caster.uuid> minecraft:movement_speed base set {d['speed']}\"}} @self",
                    f"  - command{{c=\"attribute <caster.uuid> minecraft:max_health base set {d['hp']}\"}} @self",
                    "  - skill{s=AST_SILLA_VER} @self"]
            if d.get("jump"):
                out += [f"  - command{{c=\"attribute <caster.uuid> minecraft:jump_strength base set {d['jump']}\"}} @self"]
    from mobs.tamanos import SPECIAL
    yeti_model,yeti_size=SPECIAL['astral_yeti_cumbre']
    out += ['AST_MODEL_astral_yeti_cumbre:', '  Skills:',
            '  - addtag{tag=astral.seen} @self', f'  - model{{m={yeti_model};s={yeti_size}}} @self']
    # la silla se ve solo si el jugador le puso una montura
    out += ["AST_SILLA_VER:", "  Skills:", "  - delay 3",
            "  - partvisibility{p=silla;v=false} @self ?!hastag{tag=astral.ensillado}",
            "  - partvisibility{p=silla;v=true} @self ?hastag{tag=astral.ensillado}",
            "AST_ENSILLAR:", "  Skills:",
            "  - command{c=\"minecraft:clear <trigger.name> minecraft:saddle 1\"} @self",
            "  - addtag{tag=astral.ensillado} @self",
            "  - partvisibility{p=silla;v=true} @self",
            "  - sound{s=entity.horse.saddle} @self"]
    # fases de los jefes
    for mid, fases in FASES.items():
        for n, (pct, msg, once, timers) in enumerate(fases, start=2):
            out += [f"AST_FASE_{mid}_{n}:", "  Skills:", f"  - addtag{{tag=astral.fase{n}}} @self",
                    f"  - 'message{{m=\"{msg}\"}} @PlayersInRadius{{r=40}}'",
                    "  - sound{s=entity.wither.spawn;v=0.6;p=1.4} @PlayersInRadius{r=40}"]
            out += ["  - " + x for x in once]
            for tname, (lst, _) in timers.items():
                out += [f"AST_FASE_{mid}_{n}_{tname}:", "  Skills:"] + ["  - " + x for x in lst]
    # afijos de los elites (cada uno le cambia el nombre para que se vea cual le toco)
    variantes = [(mid, "elite", ename) for mid, (_, ename) in ELITES.items()]
    variantes += [(mid, "ancestral", ename) for mid, (_, ename) in ANCESTRALES.items()]
    for mid, suf, ename in variantes:
        for a in afijos_de(mid):
            label, once, _ = AFIJOS[a]
            out += [f"AST_AFIJO_{mid}_{suf}_{a}:", "  Skills:", f"  - addtag{{tag=astral.af_{a}}} @self",
                    f"  - 'setname{{name=\"{ename} {label}\"}} @self'"]
            out += ["  - " + x for x in once]
    for mid, (color, name) in ANCESTRALES.items():
        out += [f"AST_MODEL_{mid}_ancestral:", "  Skills:", "  - addtag{tag=astral.seen} @self",
                f"  - model{{m={mid};s=2.0}} @self", "  - delay 2", f"  - tint{{c={color}}} @self",
                # El del Survival (evento cada 3 h): mismo modelo, hasta ALTO_JEFE_MUNDO de alto.
                f"AST_MODEL_{mid}_ancestral_mundo:", "  Skills:", "  - addtag{tag=astral.seen} @self",
                f"  - model{{m={mid};s={escala_mundo(mid)}}} @self", "  - delay 2", f"  - tint{{c={color}}} @self",
                f"AST_ANCESTRAL_SEVA_{mid}:", "  Skills:",
                f"  - 'message{{m=\"&7{name} &7se desvanecio... nadie pudo con el.\"}} @PlayersOnServer'",
                "  - remove @self",
                f"AST_ANCESTRAL_FUERA_{mid}:", "  Skills:",
                f"  - 'message{{m=\"&7{name} &7se desvanecio: el elegido se alejo.\"}} @PlayersOnServer'",
                "  - remove @self"]
    for mid, (color, _) in ELITES.items():
        out += [f"AST_MODEL_{mid}_elite:", "  Skills:", "  - addtag{tag=astral.seen} @self",
                f"  - model{{m={mid};s=1.35}} @self", "  - delay 2",
                f"  - tint{{c={color}}} @self"]
    # Atributos junto al mismo modelo: los eventos spawn/load llaman esta skill.
    from mobs.tamanos import skills as size_skills, SPECIAL
    out += ['AST_MODEL_astral_golem_forja_mazmorra:', '  Skills:',
            '  - addtag{tag=astral.seen} @self', '  - model{m=astral_golem_forja;s=2.0} @self',
            'AST_MODEL_astral_chaman_bosque:', '  Skills:',
            '  - addtag{tag=astral.seen} @self', '  - model{m=astral_chaman;s=1.4} @self']
    sized=[]
    ancestral_mundo = False
    for line in out:
        if line.endswith(':') and not line.startswith(' '):
            ancestral_mundo = line.startswith('AST_MODEL_') and line.endswith('_ancestral_mundo:')
        import re
        match=re.fullmatch(r'  - model\{m=([^;}]+)(?:;s=([^}]+))?\} @self',line)
        attrs = []
        if match and MOBS[match[1]]['kind'] != 'montura':
            attrs = ['  - '+x for x in size_skills(match[1],float(match[2] or 1),MOBS[match[1]]['type'])]
        # 27/11: BetterModel debe crear TODAS las piezas con la escala definitiva.
        # Cambiar scale despues de model{} deja piezas quietas con la transformacion
        # anterior (cabeza flotante). Aplicar tambien en onLoad, antes de recrearlo.
        sized += attrs + [line] if ancestral_mundo else [line] + attrs
    out=sized
    out += ['AST_YETI_PISOTON:', '  Skills:',
            '  - particles{p=snowflake;amount=100;hS=18;vS=0.2} @self', '  - delay 20',
            '  - ' + __import__('efectos').mm_fx('golpe', '#bfefff', 8, 'hielo'),
            '  - basedamage{multiplier=2} @PlayersInRadius{r=20}', '  - throw{velocity=8;velocityY=3} @PlayersInRadius{r=20}',
            'AST_YETI_HIELO:', '  Skills:', '  - basedamage{multiplier=1.25} @PlayersNearOrigin{r=3}',
            '  - potion{type=SLOWNESS;duration=60;level=1} @PlayersNearOrigin{r=3}']
    return "\n".join(out) + "\n" + jefe_metaskills()


# 25/11: el dueno no veia criaturas astrales; +50% a las normales y elites (los ancestrales quedan igual).
MULT_APARICION = 1.5


def spawns():
    out = []
    for mid, d in MOBS.items():
        s = d.get("spawn")
        if not s:
            continue
        base = s["chance"] * MULT_APARICION
        out += spawn_entry(mid, mid, s, round(base, 6))
        if mid in ELITES:
            out += spawn_entry(f"{mid}_elite", f"{mid}_elite", s, round(base * 0.15, 6))
        if mid in ANCESTRALES:
            a = ancestral_def(mid)["spawn"]
            out += spawn_entry(f"{mid}_ancestral", f"{mid}_ancestral", a, a["chance"])
    return "\n".join(out) + "\n"


def spawn_entry(key, mob, s, chance):
    lines = [f"spawn_{key}:", "  Action: ADD", f"  Type: {mob}", f"  Worlds: {s.get('world', 'world')}",
             f"  Chance: {chance}", "  Priority: 1", "  Reason: NATURAL", "  Biomes:"]
    lines += [f"  - {b}" for b in s["biomes"]]
    cond = []
    if s.get("night"):
        cond.append("  - night true")
    if s.get("cave"):
        cond.append("  - outside false")
    if cond:
        lines += ["  Conditions:"] + cond
    return lines


def main():
    for sub in ("mobs", "skills", "randomspawns"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    mobs = [mob_block(mid, dict(d, mundo=True) if d["kind"] == "jefe" else d) for mid, d in MOBS.items()]
    mobs += [mob_block(f"{mid}_elite", MOBS[mid], model=mid, elite=e) for mid, e in ELITES.items()]
    mobs += [mob_block(f"{mid}_ancestral", dict(ancestral_def(mid), mundo=True, model_skill=f"AST_MODEL_{mid}_ancestral_mundo"),
                       model=mid, elite=e) for mid, e in ANCESTRALES.items()]
    mobs += [npc_block(mid, *v) for mid, v in NPCS.items()]
    with open(os.path.join(OUT, "mobs", "astral.yml"), "w", encoding="utf-8") as f:
        f.write("# Criaturas de AstralRPG (generado por datapack-src/mobs/mythic.py)\n\n" + "\n".join(mobs))
    with open(os.path.join(OUT, "skills", "astral.yml"), "w", encoding="utf-8") as f:
        f.write(metaskills())
    with open(os.path.join(OUT, "randomspawns", "astral.yml"), "w", encoding="utf-8") as f:
        f.write(spawns())
    print(len(mobs), "mobs de MythicMobs generados")
    from mobs.tanda3a import generate
    generate()
    from mobs.tanda3b import generate as generate_tanda3b
    generate_tanda3b()
    from mobs.tanda3c import generate as generate_tanda3c
    generate_tanda3c()
    from correcciones_goblin import generate
    generate()


if __name__ == "__main__":
    main()
