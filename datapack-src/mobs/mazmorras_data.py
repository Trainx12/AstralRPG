"""Catalogo de mazmorras. Entradas habilitadas para las pruebas de Aternos.

Coordenadas propuestas con plataformas de combate; revisar el recorrido en Minecraft.
Las Minas siguen en mazmorra.MINA y conservan todos sus identificadores.
"""
from copy import deepcopy
import re

try:
    from . import mythic
except ImportError:
    import mythic

# Lectura del terreno de los ZIP, no una recorrida dentro de Minecraft.
DEFINITIONS = [
    dict(key="bosque", name="Bosque Sombrio", map="bosque.zip", boss="chaman", event="chaman", tier=2,
         points=[(1440.5, 104, 1568.5), (1504.5, 107, 1504.5), (1600.5, 97, 1440.5)],
         arrivals={"sala1": (1440.5, 103, 1569.5)},
         labels=["Sendero de las raices", "Claro corrompido", "Altar del Chaman"],
         enemies=["espantapajaros", "abejorro", "cara"], money=1500),
    dict(key="tumba", name="Tumba del Rey de Arena", map="desierto.zip", boss="momia", event="momia", tier=3,
         points=[(-148.5, 60, -98.5), (-175.5, 88, 203.5), (0.568, 72, 0.512)],
         # Sala2: seleccion WorldEdit (-191,88,195)..(-160,93,211).
         arrivals={"sala1": (-148.426, 62, -97.473), "sala2": (-203.163, 88, 203.533)},
         # Sala final revisada por el dueno: jefe en la primera captura,
         # jugadores en la segunda. El radio incluye ambos extremos de la sala.
         final_arrival=(0.368, 73, -44.104), final_radius=56, final_spawn_radius=0,
         labels=["Patio de los olvidados", "Pasaje de los sellos", "Trono del Rey de Arena"],
         enemies=["espantapajaros", "arana", "cara"], money=2000),
    dict(key="cumbre", name="Cumbre Helada", map="ice-lobby.zip", world="cumbre_hielo",
         boss="yeti", event="yeti", tier=4,
         points=[(16.5, 64, 18.5), (24.5, 66, -1.5), (6.5, 63, 32.5)],
         arrivals={"sala1": (8.5, 65, 8.5)}, room_radius=14, final_radius=12,
         labels=["Paso de la escarcha", "Ascenso blanco", "Trono del Yeti"],
         enemies=["arana", "cara", "espantapajaros"], money=2500),
    dict(key="forja", name="Corazon de la Forja", map="volcano.zip", world="forja_volcano",
         boss="golem_forja", event="golem_forja", tier=5,
         # Llegada para revision del mapa. Colocar el controlador solo despues
         # de que el dueno seleccione una zona de combate para el golem.
         points=[(82.5, 52, -55.5)],
         labels=["Nucleo de la Forja"],
         enemies=["espantapajaros", "arana", "cara"], money=3000),
    dict(key="santuario", name="Santuario Celestial", map="mapa_Santuari_Mazmorra.zip",
         world="santuario_interstellar", boss=None, event="santuario", tier=6,
         points=[(46.5, 180, 48.5)], arrival=(34.5, 180, 40.5), radius=18,
         labels=["Prueba de los cinco ecos"],
         enemies=[], money=5000),
]
ARENA = dict(world="arena", map="batalla_de_Jugadores.zip", enabled=True,
             arrival=(-206.5, 73, -2371.5), npc="astral_npc_arena",
             spawn_bounds=((-218, 73, -2383), (-194, 73, -2357)),
             # Reparto aleatorio entre puntos interiores con piso y altura libre.
             spawn_points=[(x + 0.5, 73, z + 0.5)
                           for x in range(-217, -195, 5)
                           for z in range(-2382, -2360, 5)])


def variant(key, source, ancestral=False, boss=False):
    base = "astral_" + source
    mid = f"astral_{key}_{source}" + ("_eco" if ancestral else "")
    data = deepcopy(mythic.ancestral_def(base) if ancestral else mythic.MOBS[base])
    if boss and key in ('bosque','tumba','cumbre','forja'):
        from escala import VIDA_JEFE
        data['hp'] = VIDA_JEFE[key]
        data['dungeon'] = key
        if key == 'bosque':
            # clear borra los goals vanilla de hechizos (incluido invocar vex).
            data['hostile_ai'] = True
        if key == 'cumbre':
            data['speed'] = 0.005
            data['stationary'] = True
            data['skills'] = [s for s in data.get('skills', []) if 'leap{' not in s]
            data['skills'] += ['- skill{s=AST_YETI_PISOTON} @self ~onTimer:160',
                               '- projectile{onHit=AST_YETI_HIELO;v=14;i=1;hR=2;vR=2;mr=120;bulletType=ITEM;material=SNOWBALL} @PlayersInRadius{r=120} ~onTimer:100']
        if key == 'forja':
            data['model_skill'] = 'AST_MODEL_astral_golem_forja_mazmorra'
            data['skills'] = list(data.get('skills', [])) + ['- potion{type=FIRE_RESISTANCE;duration=2147483647;level=0;hasParticles=false} @self ~onSpawn']
    if key == 'cumbre' and source == 'yeti' and boss:
        data['model_skill'] = 'AST_MODEL_astral_yeti_cumbre'
    if boss: data["suppress_quest"] = True  # credito compartido al terminar la sala
    if ancestral:
        # Conserva modelo, tintado, fases, afijo y drops del Ancestral. La prueba
        # no anuncia un evento mundial ni desaparece a mitad del combate.
        data["skills"] = [s for s in data.get("skills", []) if "@PlayersOnServer" not in s and "AST_ANCESTRAL_SEVA_" not in s]
        original = base + "_ancestral"
        block = mythic.mob_block(original, data, model=base, elite=mythic.ANCESTRALES[base])
        block = block.replace(original + ":\n", mid + ":\n", 1)
    else:
        block = mythic.mob_block(mid, data, model=base)
    # Contorno permanente como la flecha espectral, solo en esta variante de mazmorra.
    block = block.replace("  Options:\n", "  Options:\n    Glowing: true\n", 1)
    # No desaparecer como los mobs del mundo: si no, Minecraft las borra al rato y el control
    # de la sala pasa de oleada (08/11/2026). RESET/LIMPIA las quitan.
    block = block.replace("    Despawn: true\n", "    Despawn: false\n")
    if key == "tumba" and boss:
        # Only this summoned boss can acknowledge victory to its own controller.
        # Se avisa al control de la sala del jefe con un comando vanilla: los targeters de
        # MythicMobs (@Parent, @MobsInRadius) no encuentran al armor stand marker del control.
        block += ("  - command{c=\"execute at <caster.uuid> run tag @e[type=armor_stand,distance=..96,"
                  "name='Control Trono del Rey de Arena'] add tumba.jefe.derrotado\"} @self ~onDeath\n")
    # Tambien esperar/limpiar los ayudantes que invocan sus fases y afijos.
    helpers = set(re.findall(r"summon\{type=([^;}]+)", " ".join(data.get("skills", []))))
    if ancestral:
        helpers.add(base)  # el afijo Invocador puede llamar a la version normal
    for _, _, once, timers in mythic.FASES.get(base, []):
        text = " ".join(once + [s for sk, _ in timers.values() for s in sk])
        helpers.update(re.findall(r"summon\{type=([^;}]+)", text))
    return mid, block, helpers


def catalog():
    out = []
    for definition in DEFINITIONS:
        key = definition["key"]
        blocks, enemies, helpers = [], [], set()
        for source in definition["enemies"]:
            mid, block, _ = variant(key, source)
            enemies.append(mid); blocks.append(block)
        rooms = []
        if key == "santuario":
            waves = []
            for source in ("cangrejo", "chaman", "momia", "yeti", "golem_forja"):
                mid, block, add = variant(key, source, ancestral=True, boss=True)
                blocks.append(block); helpers.update(add)
                waves.append([(mid, 1, 0)])
            rooms.append(dict(id="sala1", name=definition["labels"][0], centro=definition["points"][0],
                              llegada=definition.get("arrival", definition["points"][0]),
                              r=definition.get("radius", 30), oleadas=waves, extra=sorted(helpers)))
        else:
            boss, block, helpers = variant(key, definition["boss"], boss=True)
            blocks.append(block)
            for i, (point, label) in enumerate(zip(definition["points"], definition["labels"])):
                last = i == len(definition["points"]) - 1
                waves = [[(boss,1,0)]] if last else [[(enemies[i],4+i,2)], [(enemies[i],2,1),(enemies[(i+1)%len(enemies)],3,1)]]
                rooms.append(dict(id=f"sala{i+1}", name=label, centro=point,
                                  llegada=definition.get("arrivals", {}).get(
                                      f"sala{i+1}", definition.get("final_arrival", point) if last else point),
                                  r=definition.get("final_radius", 28) if last else definition.get("room_radius", 18),
                                  spawn_radius=definition.get("final_spawn_radius", 4) if last else 4,
                                  oleadas=waves, extra=sorted(helpers) if last else []))
        dungeon = dict(key=key, name=definition["name"], world=definition.get("world", key), mobs={}, rooms=rooms,
                        npc=f"astral_npc_{key}", reward=[("esencia_elite",4),("alma_corrupta",1)],
                        money=definition["money"], cooldown="30m", event=definition["event"],
                        enabled=definition.get("enabled", True), mob_blocks="\n".join(blocks), tier=definition["tier"], map=definition["map"])
        if key == "tumba":
            dungeon["rooms"][-1]["require_boss_death"] = True
            # Al ganar: cofre en el centro de la base de oro (donde aparece la Momia) y el
            # guia de Expediciones al lado. Bloque de oro comprobado debajo de 0 71 0.
            dungeon["rooms"][-1]["final_npcs"] = {"cofre": (0.5, 72, 0.5), "guia": (0.5, 72, 3.5)}
            configure_tumba_sala2(dungeon)
            configure_tumba_sala1(dungeon)
        else:
            # Cofre del jefe donde llegan a la sala final (piso comprobado: es la llegada).
            dungeon["rooms"][-1]["final_npcs"] = {"cofre": dungeon["rooms"][-1]["llegada"]}
        from mobs.tanda2 import configure
        out.append(configure(dungeon))
    return out


def configure_tumba_sala2(dungeon):
    """Dificil para dos tier III. Variantes propias, sin alterar al jefe Momia."""
    prefix = "astral_tumba_s2_"
    specs = {
        "arana": dict(type="CAVE_SPIDER", name="&2Arana Venenosa", hp=32, dmg=6, speed=0.30, money=15),
        "momia": dict(type="HUSK", name="&eMomia del Pasaje", hp=60, dmg=9, speed=0.24, money=20),
        "esqueleto": dict(type="SKELETON", name="&fEsqueleto del Pasaje", hp=40, dmg=7, speed=0.25,
                          equip=["bow HAND"], money=20),
        "cara": dict(type="PHANTOM", name="&cCara Voladora del Pasaje", hp=36, dmg=7, speed=0.30,
                     model=("astral_cara", 1, "FFFFFF"), money=20),
        "espantapajaros": dict(type="VEX", name="&6Espantapajaros del Pasaje", hp=70, dmg=10, speed=0.25,
                              model=("astral_espantapajaros", 1, "FFFFFF"), money=30),
        "golem": dict(type="IRON_GOLEM", name="&6&lGolem Agresivo de Arena", hp=380, dmg=16, speed=0.24,
                      hostile=True, money=100),
    }
    dungeon["mobs"].update({prefix + key: value for key, value in specs.items()})
    room = dungeon["rooms"][1]
    room.update(r=36, extra=[],
                spawn_bounds=((-191, 88, 195), (-160, 93, 211)),
                # Piso solido y tres bloques de aire comprobados en el recorte local.
                spawn_points=[(x, 88, z) for x, z in (
                    (-189.5, 196.5), (-189.5, 199.5), (-183.5, 196.5), (-180.5, 196.5),
                    (-174.5, 196.5), (-171.5, 196.5), (-165.5, 196.5), (-162.5, 196.5),
                    (-162.5, 199.5), (-162.5, 202.5), (-162.5, 205.5), (-162.5, 208.5))],
                golem_points=[(-188.5, 88, 198.5), (-161.5, 88, 208.5)],
                # Base para 1-2 jugadores; refuerzos por encima de dos, por oleada.
                group_scaling={1: (prefix + "momia", 3, 1),
                               2: (prefix + "esqueleto", 4, 1),
                               3: (prefix + "golem", 1, 2)},
                oleadas=[[(prefix + m, n, 0) for m, n in wave] for wave in (
                    [("arana", 5), ("momia", 5), ("esqueleto", 4), ("cara", 2), ("espantapajaros", 1)],
                    [("arana", 7), ("momia", 6), ("esqueleto", 5)],
                    [("golem", 2)])])


def configure_tumba_sala1(dungeon):
    """Mismo balance tier III de sala2, con cantidades y zona propias."""
    prefix = "astral_tumba_s1_"
    for mob in ("arana", "momia", "esqueleto", "cara"):
        data = deepcopy(dungeon["mobs"]["astral_tumba_s2_" + mob])
        data["name"] = data["name"].replace("del Pasaje", "del Patio")
        dungeon["mobs"][prefix + mob] = data
    dungeon["rooms"][0].update(
        r=28, extra=[], spawn_bounds=((-168, 58, -112), (-128, 63, -86)),
        # Puntos sobre piso y libres de obstaculos en el recorte local.
        spawn_points=[(-164.5, 58, -108.5), (-160.5, 58, -104.5),
                      (-160.5, 58, -100.5), (-160.5, 58, -92.5),
                      (-156.5, 58, -108.5), (-156.5, 60, -100.5),
                      (-152.5, 58, -100.5), (-148.5, 60, -100.5),
                      (-148.5, 60, -88.5), (-140.5, 58, -100.5)],
        group_scaling={1: (prefix + "momia", 3, 1), 2: (prefix + "esqueleto", 4, 1)},
        oleadas=[[(prefix + m, n, 0) for m, n in wave] for wave in (
            [("arana", 3), ("momia", 3), ("esqueleto", 2), ("cara", 1)],
            [("arana", 4), ("momia", 3), ("esqueleto", 3)])])
