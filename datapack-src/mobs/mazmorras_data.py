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
    dict(key="cumbre", name="Cumbre Helada", map="nieve.zip", boss="yeti", event="yeti", tier=4,
         points=[(-128.5, 79, 0.5), (0.5, 115, 0.5), (96.5, 97, 0.5)],
         labels=["Paso de la escarcha", "Ascenso blanco", "Trono del Yeti"],
         enemies=["arana", "cara", "espantapajaros"], money=2500),
    dict(key="forja", name="Corazon de la Forja", map="volcan gigante.zip", boss="golem_forja", event="golem_forja", tier=5,
         # Solo el volcan SUR: el recorte X=1360..1647, Z=1792..2399
         # excluye el volcan norte. Decision del dueno: un solo volcan para orientar el recorrido.
         # La ultima requiere una plataforma sobre el crater. No teletransportar
         # jugadores en supervivencia hasta construirla y verificarla.
         points=[(1536.5, 224, 1900.5), (1456.5, 210, 2032.5), (1536.5, 200, 2304.5)],
         labels=["Ladera de ceniza", "Puente de la escoria", "Nucleo de la Forja"],
         enemies=["espantapajaros", "arana", "cara"], money=3000),
    dict(key="santuario", name="Santuario Celestial", map="vacio.zip", boss=None, event="santuario", tier=6,
         points=[(-329.5, 51, 65.5)], labels=["Prueba de los cinco ecos"],
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
                              llegada=definition["points"][0], r=30, oleadas=waves, extra=sorted(helpers)))
        else:
            boss, block, helpers = variant(key, definition["boss"], boss=True)
            blocks.append(block)
            for i, (point, label) in enumerate(zip(definition["points"], definition["labels"])):
                last = i == len(definition["points"]) - 1
                waves = [[(boss,1,0)]] if last else [[(enemies[i],4+i,2)], [(enemies[i],2,1),(enemies[(i+1)%len(enemies)],3,1)]]
                rooms.append(dict(id=f"sala{i+1}", name=label, centro=point,
                                  llegada=definition.get("arrivals", {}).get(
                                      f"sala{i+1}", definition.get("final_arrival", point) if last else point),
                                  r=definition.get("final_radius", 28) if last else 18,
                                  spawn_radius=definition.get("final_spawn_radius", 4) if last else 4,
                                  oleadas=waves, extra=sorted(helpers) if last else []))
        dungeon = dict(key=key, name=definition["name"], world=key, mobs={}, rooms=rooms,
                        npc=f"astral_npc_{key}", reward=[("esencia_elite",4),("alma_corrupta",1)],
                        money=definition["money"], cooldown="30m", event=definition["event"],
                        enabled=definition.get("enabled", True), mob_blocks="\n".join(blocks), tier=definition["tier"], map=definition["map"])
        if key == "tumba":
            configure_tumba_sala2(dungeon)
            configure_tumba_sala1(dungeon)
        out.append(dungeon)
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
