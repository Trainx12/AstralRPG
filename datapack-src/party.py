"""AstralParty: generacion del puente Skript y del panel compacto de TAB."""
from pathlib import Path
import argparse
import os
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REVIVE_WAVES = 30
REVIVE_BOSS = 15
WIPE_SECONDS = 3
PARTY_MAX = 6


def bridge(script):
    """Conserva party_miembros y sustituye el propietario de comandos/estado."""
    start = script.index('function party_avisar(')
    end = script.index('function maz_jugadores(')
    script = script[:start] + '''# AstralParty mantiene la API que consumen mazentrar e Infinita.
command /astralpartysync <text> <text> [<player>]:
    executable by: console
    trigger:
        if arg-1 is "clear":
            delete {-party.lider::*}
            delete {-party.miembros::*}
        else if arg-1 is "add":
            if arg-3 is set:
                set {-party.lider::%uuid of arg-3%} to arg-2
                set {-party.miembros::%arg-2%::%uuid of arg-3%} to arg-3

on load:
    wait 1 tick
    execute console command "astralpartyinternal sync"

''' + script[end:]
    script = script.replace('        set {-maz.fin::%arg-1%} to now',
        '        execute console command "astralpartyinternal victory %arg-1%"\n        set {-maz.fin::%arg-1%} to now')
    return script


def tab_sections(text):
    import yaml
    data = yaml.safe_load(text)
    for board in data['scoreboard']['scoreboards'].values():
        rows = board['lines']
        # Tres parejas de miembros: nombre corto + porcentaje; detalle completo en TAB.
        # Quita solo decoracion/tiempo jugado para reservar 4 filas dentro del limite vanilla.
        while len(rows) > 11:
            index = next((i for i, row in enumerate(rows) if '─' in row or 'Tiempo jugado' in row or '/party para' in row), None)
            if index is None:
                raise ValueError('No hay espacio para Party sin quitar informacion de juego')
            rows.pop(index)
        rows.extend(['%astral_party_titulo%', '%astral_party_fila1%', '%astral_party_fila2%', '%astral_party_fila3%'])
        assert len(rows) <= 15
    # Preservar comentarios y formato del generador original.
    import re
    for name, board in data['scoreboard']['scoreboards'].items():
        pattern = rf'(    {re.escape(name)}:\n.*?      lines:\n)((?:        - [^\n]*\n)+)'
        replacement = lambda m: m[1] + ''.join('        - "' + row + '"\n' for row in board['lines'])
        text, count = re.subn(pattern, replacement, text, flags=re.S)
        if count != 1: raise ValueError('No se encontro el tablero: ' + name)
    pattern = r'(      footer:\n)((?:        - .*\n)+)'
    text, count = re.subn(pattern, lambda m: m[0] + ''.join(f'        - "%astral_party_{key}%"\n' for key in ('linea','tab1','tab2','tab3')), text)
    if count != 1: raise ValueError('No se encontro footer de TAB')
    return text


def metadata():
    import mazmorras_copias
    from infinita import WORLDS
    from viajes_mazmorras import destinations
    from instancias import DUNGEON_WORLDS, copias, bukkit
    worlds = mazmorras_copias.all_worlds() + list(WORLDS)
    bosses = []
    for d in destinations():
        if not d.get('enabled'): continue
        for i, room in enumerate(d['rooms']):
            x,y,z = room['centro']
            for dim in copias(DUNGEON_WORLDS[d['key']]):
                bosses.append(f'{bukkit(dim)},{x},{y},{z},{i == len(d["rooms"])-1}')
    import oceano_fosa
    x,y,z,*_ = oceano_fosa.LLEGADA
    for dim in oceano_fosa.WORLDS:
        bosses.append(f'{bukkit(dim)},{x},{y},{z},True')
    return worlds, bosses


def build(java, server, papi):
    target = ROOT / '.local/party-classes'
    target.mkdir(parents=True, exist_ok=True)
    deps = list((server / 'libraries').rglob('*.jar')) + [papi]
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
        '-classpath', os.pathsep.join(map(str, deps)), '-d', str(target),
        str(ROOT/'datapack-src/runtime/AstralParty.java')], check=True)
    worlds, bosses = metadata()
    dest = ROOT/'build/runtime/AstralParty.jar'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((target/'astral').glob('AstralParty*.class')):
            z.writestr(zipfile.ZipInfo('astral/'+p.name, (2026,11,17,0,0,0)), p.read_bytes())
        z.writestr('plugin.yml', "name: AstralParty\nversion: 1.1.0\nmain: astral.AstralParty\napi-version: '26.1.2'\ndepend: [Skript, PlaceholderAPI]\ncommands:\n  party:\n    aliases: [grupo]\n  astralpartyinternal: {}\n")
        z.writestr('party.properties', f'waves={REVIVE_WAVES}\nboss={REVIVE_BOSS}\nwipe={WIPE_SECONDS}\nmax={PARTY_MAX}\nworlds='+','.join(worlds)+'\n')
        z.writestr('boss-rooms.csv', '\n'.join(bosses))
        z.writestr('fight-rooms.csv', '\n'.join(fight_rooms())+'\n')
    return dest


def fight_rooms():
    """Limites de pelea, no confundir spawn_bounds (solo apariciones) con la arena.

    CSV: mundo, centro xyz, radio de entrada, lado, prefijo del controlador,
    nombre del controlador. Infinita/Fosa usan sus tags de enemigos vivos.
    """
    from viajes_mazmorras import destinations
    from instancias import DUNGEON_WORLDS, copias, bukkit
    import infinita, oceano_fosa
    rows = []
    for d in destinations():
        if not d.get('enabled'): continue
        for room in d['rooms']:
            x, y, z = room['centro']
            side = 2 * room['r']
            if 'fight_bounds' in room:
                lo, hi = room['fight_bounds']
                x, z = (lo[0]+hi[0])/2, (lo[2]+hi[2])/2
                side = max(hi[0]-lo[0], hi[2]-lo[2])
            for dim in copias(DUNGEON_WORLDS[d['key']]):
                rows.append(f"{bukkit(dim)},{x},{y},{z},{room['r']},{side},{d['key']},Control {room['name']}")
    # Cupula: puntos de spawn a 30 bloques; borde a 32, dentro del recinto.
    for world in infinita.WORLDS:
        rows.append(f'{world},0.5,63,0.5,32,64,inf,')
    # Recorte de la cueva documentado en oceano_fosa: x -50..54, z 35..153.
    for world in oceano_fosa.WORLDS:
        rows.append(f'{world},2,112,94,60,118,fosa,')
    return rows


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--java', type=Path, required=True)
    a.add_argument('--server', type=Path, required=True)
    a.add_argument('--papi', type=Path, required=True)
    args = a.parse_args()
    print(build(args.java.resolve(), args.server.resolve(), args.papi.resolve()))
