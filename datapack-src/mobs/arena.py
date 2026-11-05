"""Arena PvP aislada: sin drops de muerte ni progreso de misiones."""
from pathlib import Path
from mazmorras_data import ARENA
from mythic import npc_block

ROOT = Path(__file__).resolve().parents[2] / "build"


def generate():
    world = ARENA["world"]
    arrivals = ARENA.get("spawn_points", [ARENA["arrival"]])
    skills = ["# Generado por mobs/arena.py", "ARENA_ENTRAR:", "  Skills:",
              "  - randomskill{skills=" + ",".join(f"ARENA_LLEGADA_{i}" for i in range(len(arrivals))) + "} @trigger", ""]
    for i, (x, y, z) in enumerate(arrivals):
        skills += [f"ARENA_LLEGADA_{i}:", "  Skills:",
                   f'  - \'command{{c="execute in minecraft:{world} run minecraft:tp <trigger.name> {x} {y} {z}"}} @trigger\'', ""]
    # El selector valida cada destino; conservar este ID reutiliza el NPC existente.
    skill = 'command{c="dm open arenas <trigger.name>"} @self ~onInteract'
    mobs = ROOT / "mythicmobs" / "mobs" / "arena.yml"
    mobs.parent.mkdir(parents=True, exist_ok=True)
    mobs.write_text("# Generado por mobs/arena.py\n" + npc_block(ARENA["npc"], "&c&lArena de jugadores &7- PvP", "ARMORER", [skill]), encoding="utf-8")
    skill_file = ROOT / "mythicmobs" / "skills" / "arena.yml"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text("\n".join(skills) + "\n", encoding="utf-8")
    lines = ["# Arena PvP. Instalacion en un mundo NUEVO; coordenadas pendientes de revision.",
             "# No usar Worlds > Upload sobre world. No importar datapacks ni entidades del ZIP original.",
             f'mv create {world} normal --world-type FLAT --no-structures --no-adjust-spawn '
             '--generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
             f'# Con el servidor apagado: regiones limpias a world/dimensions/minecraft/{world}/region.',
             f'mv modify {world} set pvp true', f'mv modify {world} set gamemode survival',
             f'mv modify {world} set allow-weather false',
             f'mv gamerule set minecraft:keep_inventory true {world}',
             f'mv gamerule set minecraft:spawn_mobs false {world}',
             f'mv gamerule set minecraft:mob_drops false {world}',
             f'mv gamerule set minecraft:entity_drops false {world}',
             f'rg flag -w {world} __global__ build deny', f'rg flag -w {world} __global__ chest-access deny',
             f'rg flag -w {world} __global__ pvp allow', f'rg flag -w {world} __global__ mob-spawning allow',
             '# Apagar PvP en el resto. Ejecutar solo sobre mundos que existan:']
    for name in ("world","world_nether","world_the_end","lobby","mina","bosque","tumba","cumbre","forja","santuario"):
        lines += [f'mv modify {name} set pvp false', f'rg flag -w {name} __global__ pvp deny']
    x,y,z=ARENA["arrival"]
    lines += [f'# Entrada de referencia (OP en creativo): execute in minecraft:{world} run minecraft:tp <jugador> {x} {y} {z}',
              f'# El NPC reparte aleatoriamente entre {len(arrivals)} puntos interiores de la zona seleccionada.',
              '# Instalar mobs/arena.yml Y skills/arena.yml en MythicMobs; ejecutar mm reload.',
              '# Al verificarla, ajustar arrival y enabled=True en mobs/mazmorras_data.py y regenerar.',
              f'# NPC del lobby: mm mobs spawn {ARENA["npc"]}',
              '# Salida de jugadores: /spawn. No hay premios ni contadores de bajas PvP.']
    folder=ROOT/"arena";folder.mkdir(parents=True,exist_ok=True)
    (folder/"comandos.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")


if __name__=="__main__": generate()
