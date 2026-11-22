"""GrimAC en modo SOLO AVISA (pedido del dueno, 22/11/2026: "solo avisa hasta que yo te pida castigos").

Uso:  python anticheat.py <carpeta plugins/GrimAC generada por Grim al primer arranque>
Sale: build/anticheat/GrimAC/{config.yml,punishments.yml,messages.yml} + build/anticheat/comandos.txt

Grim 2.3.74 genera sus archivos en espanol. Este script parte de esos archivos (no los copia al repo:
son de Grim, GPLv3, y cambian con cada version) y solo cambia lo necesario:
- castigos: solo [alert] y [log] (sin kick/ban; [webhook]/[proxy] fuera, no hay Discord ni proxy);
- sin "setback" (tirar al jugador para atras) ni cancelar golpes/bloques: los numeros quedan altisimos;
- no echa a nadie por la version de Forge;
- prefijo [AntiTrampas].
Para activar castigos mas adelante: volver a los valores de Grim (correr Grim sin estos archivos) y agregar
comandos tipo "100:0 kick %player% ..." en punishments.yml. Ver docs/SERVIDOR.md, seccion Anti-trampas.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build' / 'anticheat'
NUNCA = '1000000'  # nivel de violacion inalcanzable = nunca tira para atras ni cancela

PREFIJO = '"&8[&cAntiTrampas&8]"'


def cambiar(texto: str, patron: str, nuevo: str, cuantos: int, nombre: str) -> str:
    texto, n = re.subn(patron, nuevo, texto, flags=re.M)
    if n != cuantos:
        sys.exit(f'{nombre}: se esperaban {cuantos} cambios de {patron!r} y hubo {n}. Revisar la version de Grim.')
    return texto


def config(t: str) -> str:
    t = cambiar(t, r'^(\s*immediate-setback-threshold:) .*$', r'\1 -1', 2, 'config')
    t = cambiar(t, r'^(\s*max-advantage:) .*$', r'\1 -1', 2, 'config')
    t = cambiar(t, r'^(\s*setback-violation-threshold:) .*$', rf'\1 {NUNCA}', 1, 'config')
    t = cambiar(t, r'^(\s*setbackvl:) \d+(.*)$', rf'\1 {NUNCA}', 5, 'config')
    t = cambiar(t, r'^(\s*cancelvl:) \d+$', rf'\1 {NUNCA}', 5, 'config')
    t = cambiar(t, r'^(\s*block-impossible-hits:) true$', r'\1 false', 1, 'config')
    t = cambiar(t, r'^(\s*disconnect-blacklisted-forge-versions:) true$', r'\1 false', 1, 'config')
    return '# AstralRPG: SOLO AVISA (sin setbacks ni cancelaciones). Generado por datapack-src/anticheat.py\n' + t


def punishments(t: str) -> str:
    t = cambiar(t, r'^\s*- "\d+:\d+ \[(webhook|proxy)\]"\n', '', 14, 'punishments')
    malos = [l for l in re.findall(r'^\s*- "\d+:\d+ (.*)"$', t, flags=re.M) if l not in ('[alert]', '[log]')]
    if malos:
        sys.exit(f'punishments: hay comandos que no son avisos: {malos}')
    return ('# AstralRPG: SOLO AVISA. Nada de kick/ban hasta que el dueno lo pida.\n'
            '# Generado por datapack-src/anticheat.py\n' + t)


def messages(t: str) -> str:
    return cambiar(t, r'^prefix: .*$', f'prefix: {PREFIJO}', 1, 'messages')


COMANDOS = """# Consola del server, despues de subir GrimAC y reiniciar
# Por las dudas: nadie queda tirado para atras aunque algo se escape de la config.
lp group default permission set grim.nosetback true
# Los OP ya reciben avisos (grim.alerts es de OP por defecto). Prender/apagar para uno: /grim alerts
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    dst = OUT / 'GrimAC'
    dst.mkdir(parents=True, exist_ok=True)
    for nombre, f in (('config.yml', config), ('punishments.yml', punishments), ('messages.yml', messages)):
        texto = (src / nombre).read_text(encoding='utf-8')
        (dst / nombre).write_text(f(texto), encoding='utf-8', newline='\n')
    (OUT / 'comandos.txt').write_text(COMANDOS, encoding='utf-8', newline='\n')
    print(f'Listo: {dst}')


if __name__ == '__main__':
    main()
