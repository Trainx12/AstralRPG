"""Oceano Astral (tanda A): mundo todo de agua, reglas sin aire, entrada con aviso y regeneracion.

python oceano.py [--java <java25>] [--base .local/testsrv]
  -> build/oceano/AstralOceano.jar (plugin: generador, reglas, /oceano), config.yml,
     build/menus/DeluxeMenus/gui_menus/oceano_aviso.yml, build/oceano/comandos.txt
El jar se compila contra las librerias del Paper local (.local/testsrv); sin Java solo escribe lo demas.
"""
import argparse
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/oceano'
WORLD = 'oceano'
RADIO = 600                  # borde del mundo: 1200 x 1200 bloques
REGENERAR_HORAS = 72         # 3 dias reales
AVISOS_MIN = (10, 5, 1)
TIER_MOBS = 2                # oceano abierto (la mazmorra escondida es tier 3)
VERSION = '1.0.0'
STAMP = (2026, 11, 12, 0, 0, 0)

PLUGIN_YML = f'''name: AstralOceano
version: {VERSION}
main: astral.AstralOceano
api-version: '26.1.2'
load: STARTUP
softdepend: [Multiverse-Core]
commands:
  oceano:
    description: Oceano Astral (entrar, estado; admin regenerar y plantilla)
permissions:
  astral.oceano.admin:
    default: op
  astral.oceano.editar:
    default: op
'''


def config():
    return (f'# Generado por oceano.py\nmundo: {WORLD}\nregenerar-cada-horas: {REGENERAR_HORAS}\n'
            f'avisos-minutos: [{", ".join(map(str, AVISOS_MIN))}]\nproxima-regeneracion: 0\n')


def aviso_menu():
    """Ventana de confirmacion antes de entrar (segundo clic)."""
    lore = ['&7Todo es agua: &cno hay superficie&7 para respirar.',
            '&7Sirven las pociones de respiracion, el casco',
            '&7con &fRespiracion&7 y el casco de tortuga.',
            '', f'&7Monstruos &ftier {TIER_MOBS}&7. Se recomienda ser &ftier 3',
            '&7para minar y explorar.', '',
            f'&8El oceano se regenera cada {REGENERAR_HORAS // 24} dias.', '&8No dejes cosas tuyas ahi.']
    items = {
        'info': dict(material='HEART_OF_THE_SEA', slot=13, display_name='&b&lOceano Astral', lore=lore),
        'entrar': dict(material='LIME_STAINED_GLASS_PANE', slot=11, display_name='&a&lEntrar preparado',
                       lore=['&7Ya tengo con que respirar.', '', '&eClic para entrar.'],
                       click_commands=['[close]', '[player] oceano entrar<delay=3>']),
        'volver': dict(material='RED_STAINED_GLASS_PANE', slot=15, display_name='&c&lTodavia no',
                       lore=['&7Volver a los portales.'], click_commands=['[openguimenu] portales']),
    }
    return dict(menu_title='&1&lOceano Astral - Aviso', size=27, items=items)


def portales_button():
    return {'material': 'HEART_OF_THE_SEA', 'slot': 49, 'display_name': '&b&lOceano Astral',
            'lore': ['&7Un mundo entero bajo el agua.', '&cNo vas a poder respirar.', '', '&eClic para ver el aviso.'],
            'click_commands': ['[openguimenu] oceano_aviso']}


def commands():
    w = WORLD
    return '\n'.join([
        f'# Oceano Astral (oceano.py). Con el plugin AstralOceano instalado y el server encendido:',
        f'mv create {w} normal -g AstralOceano',
        f'mv gamerule set minecraft:do_daylight_cycle false {w}',
        f'execute in minecraft:{w} run time set 6000',
        f'execute in minecraft:{w} run gamerule minecraft:do_weather_cycle false',
        f'execute in minecraft:{w} run worldborder center 0 0',
        f'execute in minecraft:{w} run worldborder set {RADIO * 2}',
        f'rg flag -w {w} __global__ pvp deny',
        '# Despues de pregenerar (o subir las regiones generadas en local): oceano plantilla',
    ]) + '\n'


def build_jar(java, base):
    classes = ROOT / '.local/oceano-build'
    classes.mkdir(parents=True, exist_ok=True)
    deps = [*base.joinpath('libraries').rglob('*.jar'), *base.joinpath('versions').rglob('*.jar')]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8', '-nowarn',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(classes),
                    str(ROOT / 'datapack-src/runtime/AstralOceano.java')], check=False).returncode and sys.exit('No compila AstralOceano.java')
    dest = OUT / 'AstralOceano.jar'
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted((classes / 'astral').glob('AstralOceano*.class')):
            z.writestr(zipfile.ZipInfo('astral/' + path.name, STAMP), path.read_bytes())
        z.writestr(zipfile.ZipInfo('plugin.yml', STAMP), PLUGIN_YML)
        z.writestr(zipfile.ZipInfo('config.yml', STAMP), config())
    return dest


def generate(java=None, base=None):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'config.yml').write_text(config(), encoding='utf-8')
    (OUT / 'comandos.txt').write_text(commands(), encoding='utf-8')
    menus = ROOT / 'build/menus/DeluxeMenus/gui_menus'
    menus.mkdir(parents=True, exist_ok=True)
    (menus / 'oceano_aviso.yml').write_text(json.dumps(aviso_menu(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if java and base:
        print('jar:', build_jar(Path(java), Path(base)))
    return ['oceano_aviso']


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java')
    a.add_argument('--base', default=str(ROOT / '.local/testsrv'))
    args = a.parse_args()
    print(generate(args.java, args.base), '->', OUT)
