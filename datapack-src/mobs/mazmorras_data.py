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
         points=[(-192.5, 83, 128.5), (-128.5, 72, -64.5), (96.5, 73, -192.5)],
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
             arrival=(-171.5, -44, -2282.5), npc="astral_npc_arena")


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
                rooms.append(dict(id=f"sala{i+1}", name=label, centro=point, llegada=point,
                                  r=28 if last else 18, oleadas=waves, extra=sorted(helpers) if last else []))
        out.append(dict(key=key, name=definition["name"], world=key, mobs={}, rooms=rooms,
                        npc=f"astral_npc_{key}", reward=[("esencia_elite",4),("alma_corrupta",1)],
                        money=definition["money"], cooldown="30m", event=definition["event"],
                        enabled=definition.get("enabled", True), mob_blocks="\n".join(blocks), tier=definition["tier"], map=definition["map"]))
    return out
