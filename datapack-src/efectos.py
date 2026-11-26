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
FRAMES = 12
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
# Color del rayo / bola de cada baston segun su elemento (verde y violeta: las referencias del dueno).
COLOR_BASTON = {1: '#35f04e', 2: '#3fa8ff', 3: '#d24bff', 4: '#ff7a1a', 5: '#ffe14a', 6: '#ff6fd0',
                7: '#8ff0ff', 8: '#39d4ff', 9: '#fff3b0', 10: '#8a4bff'}
# Golpe al piso de cada jefe (mobs/jefes_combate.py): color del dibujo.
COLOR_JEFE = {'astral_momia': '#f2d27a', 'astral_yeti': '#bfefff', 'astral_golem_forja': '#ff6a1a',
              'astral_cangrejo': '#3fd0ff', 'astral_chaman': '#7cff5a', 'astral_coloso_musgoso': '#5fe05a',
              'astral_mina_capataz': '#4fe0c8', 'astral_mina_golem': '#c8c8c8'}


def mm_fx(tipo, color, radio, elem, quien='caster'):
    """Linea de MythicMobs que pide el efecto al plugin (sin '#': en YAML empezaria un comentario)."""
    c = color.lstrip('#')
    return (f'command{{c="astralfx {tipo} <{quien}.l.w> <{quien}.l.x> <{quien}.l.y> <{quien}.l.z> {c} {radio} {elem}"}}')


# ----------------------------------------------------------------------------------- dibujos (pixel art propio)
# Cada dibujo son dos capas: "cuerpo" en grises (se tine con dyed_color) y "brillo" blanco sin tenir.
OSCURO, MEDIO_G, CLARO = 96, 172, 240          # contorno, cuerpo y borde interior (se multiplican por el color)


def _hash(x, y, k=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (k * 83492791)) % 1000 / 1000


def _capas(mask, blanco, size, min_blanco=3):
    """mask(x, y) y blanco(x, y, prof) -> bool. Pinta contorno oscuro, cuerpo y borde claro segun la profundidad."""
    m = [[bool(mask(x, y)) for x in range(size)] for y in range(size)]

    def dentro(x, y):
        return 0 <= x < size and 0 <= y < size and m[y][x]
    body = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    hi = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    bp, hp = body.load(), hi.load()
    for y in range(size):
        for x in range(size):
            if not m[y][x]:
                continue
            d = 1
            while d < 5 and all(dentro(x + dx, y + dy) for dx in range(-d, d + 1) for dy in range(-d, d + 1)
                                if abs(dx) + abs(dy) <= d):
                d += 1
            g = OSCURO if d == 1 else (MEDIO_G if d == 2 else CLARO)
            bp[x, y] = (g, g, g, 255)
            if d >= min_blanco and blanco(x, y, d):
                hp[x, y] = (255, 255, 255, 255)
    return body, hi


def _frame(f):
    """Un cuadro del hongo de explosion (referencia del dueno: hongo verde en pixel art, centro blanco con
    bandas onduladas, tronco con nucleo blanco que se abre en dos patas y contorno oscuro)."""
    crece = min(1.0, f / 6)                       # cuadros 0..6 crece, 7..8 queda, 9..11 se deshace
    g = 1 - (1 - crece) ** 2
    fade = max(0, f - 8) / 3.2
    piso = SIZE - 2
    cap_rx, cap_ry = 3.5 + 9.5 * g, 2.5 + 5.6 * g
    cy = piso - (3 + 17.5 * g) - (f - 8 if f > 8 else 0)
    stem = 2.4 + 2.6 * g

    def mask(x, y):
        cx = x - 15.5
        if fade and _hash(x, y, 3) < fade:
            return False
        if f == 0:                                 # destello en el piso
            return (cx / 6) ** 2 + ((y - piso) / 2.6) ** 2 < 1
        wob = 1 + 0.07 * math.sin(x * 1.1 + f * 1.7)
        if (cx / (cap_rx * wob)) ** 2 + ((y - cy) / cap_ry) ** 2 < 1:
            return True
        if g > 0.5:                                # el borde del sombrero cuelga a los costados
            for s in (-1, 1):
                if (cx - s * cap_rx * 0.8) ** 2 + (y - cy - cap_ry * 0.62) ** 2 < (2.6 * g) ** 2:
                    return True
        if cy < y <= piso:
            ancho = stem + max(0, y - (piso - 4)) * 1.5 * g
            if abs(cx) < ancho:
                if g > 0.75 and y > piso - 3 and abs(cx) < 1 + (y - (piso - 3)) * 0.8:
                    return False                   # el tronco se abre en dos patas
                return True
        return ((cx / (4 + 8 * g)) ** 2 + ((y - piso) / (1.4 + 1.2 * g)) ** 2 < 1) and f < 9

    def blanco(x, y, d):
        cx = x - 15.5
        if f <= 1:
            return True
        en_cap = (cx / cap_rx) ** 2 + ((y - cy) / cap_ry) ** 2 < 0.8
        if en_cap:
            if y < cy - cap_ry * 0.25:
                return True                        # cupula blanca
            return math.sin((y - cy) * 1.5 + math.sin(x * 0.75 + f * 0.6) * 1.5) > 0.2    # bandas onduladas
        return abs(cx) < max(0.6, stem - 2.6) and y > cy     # nucleo blanco del tronco
    return _capas(mask, blanco, SIZE, 4 if f > 2 else 3)


def _estrella(f):
    """Destello de 4 puntas (referencia: destellos blancos en estrella alrededor del rayo)."""
    largo = (2, 4, 6.5)[f]
    body = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    hi = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            dx, dy = abs(x - 7.5), abs(y - 7.5)
            if (dx <= 0.5 and dy <= largo) or (dy <= 0.5 and dx <= largo) or dx + dy <= largo * 0.42 + 0.6:
                body.putpixel((x, y), (CLARO, CLARO, CLARO, 255))
            if (dx <= 0.5 and dy <= largo - 1.5) or (dy <= 0.5 and dx <= largo - 1.5) or dx + dy <= largo * 0.3:
                hi.putpixel((x, y), (255, 255, 255, 255))
    return body, hi


def _llama(f):
    """Llamita / gota de fuego que flota (referencia: llamitas verdes y de fuego)."""
    lado = (-1, 0, 1, 0)[f]

    def mask(x, y):
        cx, cyy = x - 7.5, y - 10.5
        if cx * cx + cyy * cyy < 12.5:
            return True
        if 2 <= y <= 10:                            # punta que se afina y se mueve
            return abs(cx - lado * (10 - y) * 0.28) < (y - 1.2) * 0.42
        return False
    return _capas(mask, lambda x, y, d: (x - 7.5) ** 2 + (y - 11) ** 2 < 3.2, 16)


def _bola(f):
    """Bola de fuego con lenguas que parpadean."""
    def mask(x, y):
        cx, cyy = x - 11.5, y - 11.5
        ang = math.atan2(cyy, cx)
        r = 7.2 + 2.3 * math.sin(ang * 5 + f * 1.6) + 0.8 * math.sin(ang * 9 - f)
        return cx * cx + cyy * cyy < r * r
    return _capas(mask, lambda x, y, d: (x - 11.5) ** 2 + (y - 11.5) ** 2 < (4.4 + 0.5 * math.sin(f * 1.6)) ** 2, 24)


def _salpicadura(f):
    """Mancha plana en el piso (el plugin la acuesta) que se va achicando."""
    r = (13.5, 12, 9.5)[f]

    def mask(x, y):
        cx, cyy = x - 15.5, y - 15.5
        ang = math.atan2(cyy, cx)
        rr = r * (0.72 + 0.2 * math.sin(ang * 3 + 1) + 0.12 * math.sin(ang * 7))
        if _hash(x // 2, y // 2, 5) < 0.03 + 0.2 * f:
            return False
        return cx * cx + cyy * cyy < rr * rr or any(
            (cx - 12 * math.cos(a)) ** 2 + (cyy - 12 * math.sin(a)) ** 2 < 4.5 - f for a in (0.4, 2.3, 3.9, 5.4))
    return _capas(mask, lambda x, y, d: f == 0 and (x - 15.5) ** 2 + (y - 15.5) ** 2 < 16, 32)


def _medialuna(f=0):
    """Rafaga curva (las medialunas oscuras de la referencia)."""
    def mask(x, y):
        return (x - 9.5) ** 2 + (y - 7.5) ** 2 < 49 and (x - 6) ** 2 + (y - 7.5) ** 2 >= 42
    return _capas(mask, lambda x, y, d: False, 16)


def _onda(f):
    """Onda expansiva plana (anillo en el piso) para los golpes de los jefes."""
    radio, ancho = ((12.5, 4.2), (14, 3), (15.2, 1.8))[f]

    def mask(x, y):
        d = math.hypot(x - 15.5, y - 15.5)
        if not radio - ancho < d < radio:
            return False
        return not (f == 2 and _hash(x // 2, y // 2, 9) < 0.35)
    return _capas(mask, lambda x, y, d: f == 0 and math.hypot(x - 15.5, y - 15.5) < radio - ancho + 2.2, 32, 2)


def _rayo():
    """Corte del rayo (filas) repetido a lo largo (columnas): halo que se tine y nucleo blanco."""
    halo = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    nucleo = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for x in range(16):
        ancho = 5 + (1 if x % 5 == 0 else 0) + (1 if x % 8 == 3 else 0)      # el halo late a lo largo
        for y in range(16):
            d = abs(y - 7.5)
            if d < 2:
                nucleo.putpixel((x, y), (255, 255, 255, 255))
            elif d < ancho:
                g = CLARO if d < 3.2 else (MEDIO_G + 40 if d < 4.2 else MEDIO_G)
                if d > ancho - 1 and (x + y) % 2:
                    continue                                                 # borde en damero
                halo.putpixel((x, y), (g, g, g, 255))
    return halo, nucleo


# nombre -> (funcion, cuadros, tamano). El plugin recibe la cantidad de cuadros por config.yml.
DIBUJOS = {'hongo': (_frame, FRAMES, SIZE), 'estrella': (_estrella, 3, 16), 'llama': (_llama, 4, 16),
           'bola': (_bola, 4, 24), 'salpicadura': (_salpicadura, 3, 32), 'medialuna': (_medialuna, 1, 16),
           'onda': (_onda, 3, 32)}
TINTES = [{'type': 'minecraft:dye', 'default': -1}, {'type': 'minecraft:constant', 'value': -1}]


def _modelo_rayo():
    """4 planos cruzados a lo largo de z: desde cualquier lado se ve como un tubo de luz."""
    els = []
    for horizontal, giro in ((False, 0), (False, 45), (True, 0), (True, 45)):
        for tex, tint in (('#halo', 0), ('#nucleo', None)):
            cara = {'uv': [0, 0, 16, 16], 'texture': tex}
            if tint is not None:
                cara['tintindex'] = tint
            if horizontal:
                cara['rotation'] = 90
                el = {'from': [0, 8, 0], 'to': [16, 8, 16], 'faces': {'up': dict(cara), 'down': dict(cara)}}
            else:
                el = {'from': [8, 0, 0], 'to': [8, 16, 16], 'faces': {'east': dict(cara), 'west': dict(cara)}}
            el.update(shade=False, light_emission=15)
            if giro:
                el['rotation'] = {'origin': [8, 8, 8], 'axis': 'z', 'angle': giro}
            els.append(el)
    return {'textures': {'halo': 'astral:item/fx/rayo_halo', 'nucleo': 'astral:item/fx/rayo_nucleo',
                         'particle': 'astral:item/fx/rayo_nucleo'}, 'elements': els}


def pack_files():
    out = {}
    for name, (fn, n, _) in DIBUJOS.items():
        for f in range(n):
            body, hi = fn(f)
            out[f'textures/item/fx/{name}_{f}.png'] = body
            out[f'textures/item/fx/{name}_{f}_brillo.png'] = hi
            out[f'models/item/fx/{name}_{f}.json'] = {
                'parent': 'minecraft:item/generated',
                'textures': {'layer0': f'astral:item/fx/{name}_{f}', 'layer1': f'astral:item/fx/{name}_{f}_brillo'}}
            # capa 0 se tine con el color del efecto (dyed_color); capa 1 queda blanca
            out[f'items/fx/{name}_{f}.json'] = {'model': {
                'type': 'minecraft:model', 'model': f'astral:item/fx/{name}_{f}', 'tints': TINTES}}
    out['textures/item/fx/rayo_halo.png'], out['textures/item/fx/rayo_nucleo.png'] = _rayo()
    out['models/item/fx/rayo.json'] = _modelo_rayo()
    out['items/fx/rayo.json'] = {'model': {'type': 'minecraft:model', 'model': 'astral:item/fx/rayo',
                                           'tints': TINTES[:1]}}
    return out


def write_pack():
    for sub in ('textures/item/fx', 'models/item/fx', 'items/fx'):      # los cuadros viejos no quedan en el pack
        for viejo in (PACK / sub).glob('*') if (PACK / sub).exists() else []:
            viejo.unlink()
    for rel, obj in pack_files().items():
        dest = PACK / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(obj, Image.Image):
            obj.save(dest)
        else:
            dest.write_text(json.dumps(obj), encoding='utf-8')
    return PACK


def tenir(body, hi, color):
    c = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    out = Image.new('RGBA', body.size)
    bp, tp = body.load(), out.load()
    for y in range(body.size[1]):
        for x in range(body.size[0]):
            r, g, b, a = bp[x, y]
            if a:
                tp[x, y] = (c[0] * r // 255, c[1] * g // 255, c[2] * b // 255, 255)
    out.alpha_composite(hi)
    return out


def preview(path=ROOT / 'build/previews/efectos_hongo.png'):
    """Todos los dibujos, cuadro por cuadro, con los colores de las referencias."""
    filas = [('hongo', '#2fe84a'), ('salpicadura', '#2fe84a'), ('onda', '#2fe84a'), ('llama', '#2fe84a'), ('medialuna', '#1f9a3a'),
             ('llama', '#ff7a1a'), ('bola', '#ff8a1a'), ('estrella', '#ff7ae6'), ('estrella', '#ffffff')]
    sheet = Image.new('RGBA', (FRAMES * 100 + 8, len(filas) * 100 + 110), (26, 22, 34, 255))
    for row, (name, color) in enumerate(filas):
        fn, n, _ = DIBUJOS[name]
        for f in range(n):
            im = tenir(*fn(f), color)
            k = 96 // im.size[0]
            sheet.alpha_composite(im.resize((im.size[0] * k, im.size[1] * k), Image.NEAREST), (f * 100 + 6, row * 100 + 4))
    tira = Image.new('RGBA', (16 * 8, 16))
    for i in range(8):
        tira.alpha_composite(tenir(*_rayo(), '#d24bff'), (i * 16, 0))
    sheet.alpha_composite(tira.resize((16 * 8 * 6, 96), Image.NEAREST), (6, len(filas) * 100 + 6))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def config():
    from escala import COLOR_TIER
    from mobs.mascotas import MASCOTAS
    return {'cuadros': {name: n for name, (_, n, _) in DIBUJOS.items()},
            'color-tier': {str(t): c for t, c in COLOR_TIER.items() if c.startswith('#')},
            'color-mascota': {pid: d['color'] for pid, d in MASCOTAS.items()},
            'aura-set': AURA_SET, 'color-set': COLOR_SET}


PLUGIN_YML = """name: AstralEfectos
version: 1.5.0
main: astral.AstralEfectos
api-version: '26.1.2'
softdepend: [packetevents]
commands:
  efectos:
    description: Elegir el nivel de efectos visuales (bajo, medio o alto)
    usage: /efectos [bajo|medio|alto|armaduras|armas|bastones|mascotas|jefes] [on|off]
  astralfx:
    description: Efecto visual (jefes y scripts)
    usage: /astralfx golpe|estallido|rayo <mundo> <x> <y> <z> ...
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
    stamp = (2026, 11, 16, 0, 0, 0)
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
