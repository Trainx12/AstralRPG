"""Fosa del Crustaceo (Oceano Astral, tanda C): mazmorra acuatica escondida, tier 3, 3 copias.

- Arena: mapa "Underwater Mob Arena" (PvPqnda, TERCEROS: sus regiones viven solo en .local/acuatico/fosa-mundo,
  nunca en el repo). Se copio solo la cueva (x -50..54, z 35..153), sin bloques de comando y llena de agua.
- Entrada escondida en el fondo del Oceano Astral (ENTRADA): al acercarse, `mazentrar <jugador> fosa`
  (party, copia libre y 8 minutos tras el jefe: mazmorras_copias.py).
- Oleadas y jefe: plugin AstralOceano (config `fosa:`). Mobs tier 3 (escala.TIER_FIJO).
- Adentro SOLO respira el set de agua completo: pociones, Respiracion, casco de tortuga y conducto no sirven.
- Recompensa: la define el dueno despues.

python oceano_fosa.py  -> build/mythicmobs/mobs/fosa.yml y build/oceano/fosa-comandos.txt
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ('fosa', 'fosa_2', 'fosa_3')
NOMBRE = 'Fosa del Crustaceo'
TIER = 3
LLEGADA = (4.5, 112, 93.5, 0)           # centro de la cueva (relleno de agua comprobado en local)
JEFE_EN = (4.5, 112, 110.5)
# Puntos de aparicion: agua libre 3x3x2, uno por celda de 12x12, a 14+ bloques de la llegada.
PUNTOS = [(-36, 113, 136), (-30, 113, 79), (-30, 113, 85), (-30, 113, 109), (-30, 113, 121), (-30, 113, 145), (-27, 113, 67),
          (-27, 113, 100), (-24, 113, 67), (-24, 113, 79), (-24, 113, 85), (-24, 113, 97), (-24, 113, 109), (-24, 113, 121),
          (-24, 113, 145), (-15, 113, 133), (-12, 113, 70), (-12, 113, 73), (-12, 113, 85), (-12, 113, 97), (-12, 113, 109),
          (-12, 113, 121), (-12, 113, 133), (-3, 110, 58), (0, 113, 52), (0, 113, 64), (0, 113, 121), (9, 113, 136),
          (12, 113, 55), (12, 113, 64), (12, 113, 73), (12, 113, 109), (12, 113, 136), (15, 113, 121), (24, 113, 70),
          (24, 113, 73), (24, 113, 85), (24, 113, 97), (24, 113, 109), (24, 113, 121), (30, 116, 133), (36, 110, 133),
          (36, 113, 85), (36, 113, 97), (36, 113, 109), (36, 113, 121)]
# Oleadas para 1 jugador (+50% por cada jugador extra). "drowned_tridente" = ahogado con tridente.
OLEADAS = [
    {'drowned': 8, 'pufferfish': 4},
    {'drowned_tridente': 6, 'guardian': 4},
    {'elder_guardian': 2, 'drowned': 6},
    {'jefe': 1},
]
JEFE = 'astral_fosa_cangrejo'
ESCOLTA = 4                               # ahogados que llama el Cangrejo a la mitad de su vida
ENTRADA = (-430, 470)                     # escondida: x, z en el fondo del Oceano Astral (sin cartel ni marca)


def boss_block():
    from mobs.mazmorras_data import variant
    from escala import VIDA_JEFE
    mid, block, _ = variant('fosa', 'cangrejo', boss=True)
    block = block.replace(mid + ':', JEFE + ':', 1)
    block = re.sub(r'(?m)^(  Health: )\S+', lambda m: m[1] + str(round(VIDA_JEFE['tumba'])), block, count=1)
    block = re.sub(r"(?m)^(  Display: ).*$", "  Display: '&b&lCangrejo de la Fosa'", block, count=1)
    block = re.sub(r"(?m)^(    Title: ).*$", "    Title: '&b&lCangrejo de la Fosa'", block, count=1)
    extra = ['  - addtag{tag=fosa.jefe} @self ~onSpawn',
             '  - addtag{tag=fosa.jefe} @self ~onLoad',
             # Es una arana (cangrejo): sin esto se ahogaria en su propia fosa.
             '  - potion{type=WATER_BREATHING;duration=2147483647;level=0;hasParticles=false} @self ~onSpawn',
             f'  - summon{{type=DROWNED;amount={ESCOLTA};radius=4}} @self ~onDamaged ?healthpercent{{p=<0.5}} ?!hastag{{tag=fosa.f2}}',
             '  - message{m="&bEl Cangrejo llama a sus ahogados..."} @PlayersInRadius{r=60} ~onDamaged ?healthpercent{p=<0.5} ?!hastag{tag=fosa.f2}',
             '  - addtag{tag=fosa.f2} @self ~onDamaged ?healthpercent{p=<0.5}']
    block = block.replace('  Skills:\n', '  Skills:\n' + '\n'.join(extra) + '\n', 1)
    return block


def plugin_config():
    """Seccion `fosa:` del config.yml de AstralOceano."""
    pts = ', '.join(f'"{x},{y},{z}"' for x, y, z in PUNTOS)
    olas = '\n'.join('    - "' + ','.join(f'{k}:{v}' for k, v in o.items()) + '"' for o in OLEADAS)
    x, y, z, yaw = LLEGADA
    return (f'fosa:\n  mundos: [{", ".join(WORLDS)}]\n  llegada: "{x},{y},{z}"\n  jefe-en: "{JEFE_EN[0]},{JEFE_EN[1]},{JEFE_EN[2]}"\n'
            f'  jefe: {JEFE}\n  entrada: "{ENTRADA[0]},{ENTRADA[1]}"\n  puntos: [{pts}]\n  oleadas:\n{olas}\n')


def commands():
    L = ['# Fosa del Crustaceo (oceano_fosa.py). Con AstralOceano instalado y las regiones de la arena subidas:']
    for w in WORLDS:
        L += [f'mv import {w} normal -g AstralOceano:vacio',
              f'execute in minecraft:{w} run gamerule minecraft:spawn_mobs false',
              f'execute in minecraft:{w} run gamerule minecraft:mob_griefing false',
              f'execute in minecraft:{w} run gamerule minecraft:advance_time false',
              f'execute in minecraft:{w} run gamerule minecraft:advance_weather false',
              f'execute in minecraft:{w} run gamerule minecraft:keep_inventory true',
              f'rg flag -w {w} __global__ block-break deny',
              f'rg flag -w {w} __global__ block-place deny',
              f'rg flag -w {w} __global__ pvp deny']
    return '\n'.join(L) + '\n'


def generate():
    mobs = ROOT / 'build/mythicmobs/mobs/fosa.yml'
    mobs.parent.mkdir(parents=True, exist_ok=True)
    mobs.write_text('# Generado por oceano_fosa.py: jefe de la Fosa del Crustaceo (tier 3).\n' + boss_block(), encoding='utf-8')
    out = ROOT / 'build/oceano/fosa-comandos.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(commands(), encoding='utf-8')
    return [mobs, out]


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    print(generate())
