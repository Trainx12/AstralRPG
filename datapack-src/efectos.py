"""Efectos visuales con nivel por jugador (pedido del dueno 14-15/11/2026). Arte propio (pixel art por codigo).

- Plugin AstralEfectos (runtime/AstralEfectos.java): /efectos bajo|medio|alto (score astral.fx; arranca en Medio),
  limite de particulas de golpe (Bajo 3, Medio 6, Alto 12; usa PacketEvents), /astralfx golpe|estallido para jefes
  y Skript, marcadores del datapack (bastones) y rastros/auras en Alto (armas, armaduras con set completo, mascotas
  evolucionadas).
- Bajo = el juego como estaba (las particulas actuales de los bastones se siguen viendo).
- Dibujos de explosion: 8 cuadros 32x32 (cuerpo en grises que se tine con dyed_color + brillos blancos sin tenir),
  en pack-source/assets/astral (pack publico, arte propio).

python efectos.py --jdk <bin de JDK 25> --server <Paper local con packetevents.jar>
python efectos.py --solo-pack     (solo texturas, para build_pack.py)
"""
import argparse
import json
import math
import os
import subprocess
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent
PACK = SRC / 'pack-source/assets/astral'
FRAMES = 8
SIZE = 32

# Aura de armadura con set completo (solo Alto): tipo de particula y color propio del set.
AURA_SET = {'agua': 'agua', 'mago': 'magia', 'berserker': 'furia', 'arquero': 'bosque', 'talador': 'bosque',
            'minero': 'mina', 'carnivora': 'esporas'}
COLOR_SET = {'agua': '#4fd8ff', 'minero': '#e0a83a', 'talador': '#d2483a', 'carnivora': '#bff05a'}
# Elemento de cada jefe segun su ataque (particulas propias en AstralEfectos.elemento).
ELEM_JEFE = {'astral_momia': 'arena', 'astral_yeti': 'hielo', 'astral_golem_forja': 'fuego', 'astral_cangrejo': 'agua',
             'astral_chaman': 'veneno', 'astral_coloso_musgoso': 'naturaleza', 'astral_mina_capataz': 'agua',
             'astral_mina_golem': 'piedra'}
# Bastones por tier: elemento y particula del rayo (Medio/Alto). El color sale de COLOR_TIER.
ELEM_BASTON = {1: ('naturaleza', 'happy_villager'), 2: ('agua', 'bubble_pop'), 3: ('arcano', 'witch'),
               4: ('fuego', 'flame'), 5: ('rayo', 'electric_spark'), 6: ('rosa', 'cherry_leaves'),
               7: ('hielo', 'snowflake'), 8: ('fuego', 'soul_fire_flame'), 9: ('luz', 'end_rod'),
               10: ('vacio', 'reverse_portal')}
# Golpe al piso de cada jefe (mobs/jefes_combate.py): color del dibujo.
COLOR_JEFE = {'astral_momia': '#f2d27a', 'astral_yeti': '#bfefff', 'astral_golem_forja': '#ff6a1a',
              'astral_cangrejo': '#3fd0ff', 'astral_chaman': '#7cff5a', 'astral_coloso_musgoso': '#5fe05a',
              'astral_mina_capataz': '#4fe0c8', 'astral_mina_golem': '#c8c8c8'}


def mm_fx(tipo, color, radio, elem, quien='caster'):
    """Linea de MythicMobs que pide el efecto al plugin (sin '#': en YAML empezaria un comentario)."""
    c = color.lstrip('#')
    return (f'command{{c="astralfx {tipo} <{quien}.l.w> <{quien}.l.x> <{quien}.l.y> <{quien}.l.z> {c} {radio} {elem}"}}')


def _frame(f):
    """Un cuadro del hongo de explosion: (cuerpo en grises para tenir, brillos blancos)."""
    t = f / (FRAMES - 1)
    body = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    hi = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    bp, hp = body.load(), hi.load()
    grow = min(1.0, t * 1.7)
    stem_h = 3 + 11 * grow
    stem_w = 2.5 + 1.5 * grow
    cap_r = 3.5 + 9 * grow
    cap_cy = SIZE - 2 - stem_h - cap_r * 0.45
    base_rx, base_ry = 5 + 9 * grow, 2 + 2 * grow
    fade = max(0.0, (t - 0.55) / 0.45)

    def inside(x, y):
        """0 fuera, si no la 'profundidad' (1 = centro) de la forma unida."""
        cx = x - 15.5
        d = 0.0
        # sombrero: elipse achatada con borde ondulado
        wob = 1 + 0.08 * math.sin(x * 1.3 + f)
        e = (cx / (cap_r * wob)) ** 2 + ((y - cap_cy) / (cap_r * 0.72)) ** 2
        if e < 1:
            d = max(d, 1 - e)
        # tronco
        if cap_cy < y < SIZE - 2 and abs(cx) < stem_w * (1 + 0.25 * (y - cap_cy) / max(1, stem_h)):
            d = max(d, 0.5 * (1 - abs(cx) / (stem_w * 1.3)))
        # nube de la base
        e = (cx / base_rx) ** 2 + ((y - (SIZE - 2.5)) / base_ry) ** 2
        if e < 1:
            d = max(d, 0.8 * (1 - e))
        return d

    for y in range(SIZE):
        for x in range(SIZE):
            d = inside(x, y)
            if d <= 0:
                continue
            # se deshace en pixeles al final (patron fijo, sin azar)
            if fade and ((x * 7 + y * 13 + f * 5) % 17) / 17 < fade:
                continue
            edge = any(inside(x + dx, y + dy) <= 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            g = 120 if edge else (200 if d < 0.35 else 255)
            bp[x, y] = (g, g, g, 255)
            # brillos: bandas onduladas blancas en el sombrero (como la referencia)
            in_cap = ((x - 15.5) / cap_r) ** 2 + ((y - cap_cy) / (cap_r * 0.72)) ** 2 < 0.75
            band = math.sin((y - cap_cy) * 0.9 + math.sin(x * 0.7) * 1.2)
            if in_cap and not edge and band > 0.82 and t < 0.9:
                hp[x, y] = (255, 255, 255, 255)
            elif not edge and d > 0.85 and t < 0.4:
                hp[x, y] = (255, 255, 255, 255)
    return body, hi


def pack_files():
    out = {}
    for f in range(FRAMES):
        body, hi = _frame(f)
        out[f'textures/item/fx/hongo_{f}.png'] = body
        out[f'textures/item/fx/hongo_{f}_brillo.png'] = hi
        out[f'models/item/fx/hongo_{f}.json'] = {
            'parent': 'minecraft:item/generated',
            'textures': {'layer0': f'astral:item/fx/hongo_{f}', 'layer1': f'astral:item/fx/hongo_{f}_brillo'}}
        out[f'items/fx/hongo_{f}.json'] = {'model': {
            'type': 'minecraft:model', 'model': f'astral:item/fx/hongo_{f}',
            # capa 0 se tine con el color del efecto (dyed_color); capa 1 queda blanca
            'tints': [{'type': 'minecraft:dye', 'default': -1}, {'type': 'minecraft:constant', 'value': -1}]}}
    return out


def write_pack():
    for rel, obj in pack_files().items():
        dest = PACK / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(obj, Image.Image):
            obj.save(dest)
        else:
            dest.write_text(json.dumps(obj), encoding='utf-8')
    return PACK


def preview(path=ROOT / 'build/previews/efectos_hongo.png'):
    sheet = Image.new('RGBA', (FRAMES * 132, 140), (40, 44, 52, 255))
    for f in range(FRAMES):
        body, hi = _frame(f)
        tinted = Image.new('RGBA', body.size)
        bp, tp = body.load(), tinted.load()
        for y in range(SIZE):
            for x in range(SIZE):
                r, g, b, a = bp[x, y]
                if a:
                    tp[x, y] = (round(0x5f * r / 255), round(0xe0 * g / 255), round(0x5a * b / 255), 255)
        tinted.alpha_composite(hi)
        sheet.alpha_composite(tinted.resize((128, 128), Image.NEAREST), (f * 132, 6))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def config():
    from escala import COLOR_TIER
    from mobs.mascotas import MASCOTAS
    return {'frames': FRAMES,
            'color-tier': {str(t): c for t, c in COLOR_TIER.items() if c.startswith('#')},
            'color-mascota': {pid: d['color'] for pid, d in MASCOTAS.items()},
            'aura-set': AURA_SET, 'color-set': COLOR_SET}


PLUGIN_YML = """name: AstralEfectos
version: 1.0.0
main: astral.AstralEfectos
api-version: '26.1.2'
softdepend: [packetevents]
commands:
  efectos:
    description: Elegir el nivel de efectos visuales (bajo, medio o alto)
    usage: /efectos [bajo|medio|alto]
  astralfx:
    description: Efecto visual (jefes y scripts)
    usage: /astralfx golpe|estallido <mundo> <x> <y> <z> [#color] [radio]
    permission: astral.admin.efectos
permissions:
  astral.admin.efectos:
    default: op
"""


def build(jdk, server):
    import yaml
    target = ROOT / '.local/efectos-classes'
    target.mkdir(parents=True, exist_ok=True)
    jars = list((server / 'libraries').rglob('*.jar')) + [server / 'plugins/packetevents.jar']
    javac = [str(jdk / ('java.exe' if os.name == 'nt' else 'java')), '-m', 'jdk.compiler/com.sun.tools.javac.Main']
    subprocess.run([*javac, '-encoding', 'UTF-8', '-source', '25', '-target', '25', '-classpath',
                    os.pathsep.join(str(p) for p in jars), '-d', str(target), str(SRC / 'runtime/AstralEfectos.java')], check=True)
    dest = ROOT / 'build/runtime/AstralEfectos.jar'
    dest.parent.mkdir(parents=True, exist_ok=True)
    stamp = (2026, 11, 15, 0, 0, 0)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target / 'astral').glob('AstralEfectos*.class')):
            z.writestr(zipfile.ZipInfo(p.relative_to(target).as_posix(), stamp), p.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', stamp), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', stamp), yaml.safe_dump(config(), sort_keys=False, allow_unicode=True))
    return dest


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--jdk', type=Path)
    ap.add_argument('--server', type=Path, default=ROOT / '.local/testsrv')
    ap.add_argument('--solo-pack', action='store_true')
    a = ap.parse_args()
    print(write_pack())
    print(preview())
    if not a.solo_pack:
        if not a.jdk:
            raise SystemExit('Falta --jdk (bin de JDK 25)')
        print(build(a.jdk.resolve(), a.server.resolve()))
