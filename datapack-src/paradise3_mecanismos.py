"""Diagnostico propio de PP3. Los mundos y el datapack del autor quedan privados.

python datapack-src/paradise3_mecanismos.py
Compara todos los controles del original con la copia preparada; genera el inventario.
"""
import hashlib
import json
from pathlib import Path
import zipfile

from mapas import chunk_records, packed

ROOT = Path(__file__).resolve().parent.parent


def write_deployment(patch):
    """Exporta solo el delta privado y actualiza nuestra seccion, conservando las demas."""
    lines = ['<!-- PP3-SALA5-START -->',
             '## Paradise 3: sala de Y45 (nivel 5) — 17/11/2026', '',
             'Implementacion local preparada; instalacion y prueba jugando pendientes de Claude con navegador.',
             'Original y copia preparada tienen el boton en `-52 45 858`, sobre cuarzo liso en Y44, ',
             '`stone_button[face=floor,facing=south,powered=false]`. La conversion no lo perdio.',
             'El boton activa `-52 42 861` (redstone) desde `pp3_main:levels/level5/tick`; ',
             'los pistones del pasillo dependen de esa salida. Primera placa: `-52 45 840`; ',
             'segunda placa: `-37 45 865`. Ambas mitades habilitan el portal de `-45..-44 51 856..857`.',
             'El autor elimina boton/placas al completar la mitad: su ausencia puede ser normal.',
             'No hay command blocks en la caja x -60..-40, y 40..55, z 840..870; lo controla el datapack.', '',
             'Se agrega recuperacion antes del tick de sala 5: repone solo aire, con el piso original ',
             'sin completar y sin el tag de progreso en el marcador console. No reinicia la sala, ',
             'no apaga botones presionados ni pisa un bloque inesperado. La causa remota sigue sin confirmar.',
             'Inventario de los 83 controles, orientaciones y funciones: [pp3-mecanismos-17-11](pp3-mecanismos-17-11.md).',
             'Geometria completa identica y 23 command blocks correctamente traducidos en la copia local.',
             'Las reglas generadas ya incluyen `use allow` e `interact allow`; comprobar las vigentes.',
             'No se encontro otro control perdido en la conversion. Niveles 66/81 tambien retiran placas ',
             'temporalmente: conservar sus secuencias, no restaurar el inventario en masa.', '',
             '### Archivos exactos y version', '',
             'Regenerar desde raiz: `python datapack-src/minijuegos_datapack.py parkour_paradise3`.',
             'Este delta es independiente de los JAR/Items/pack pendientes de otras tandas. ',
             'No instalar el mundo ZIP ni el datapack completo para esta reparacion.', '',
             f'Archivo privado `{patch.relative_to(ROOT).as_posix()}` (5 funciones). SHA-256: ',
             f'`{hashlib.sha256(patch.read_bytes()).hexdigest()}`.', '',
             'Con servidor apagado, respaldar los cinco destinos existentes desde Files y ',
             'descomprimir el delta DENTRO de `world/datapacks/parkour_paradise3-datapack/`, ',
             'o copiar estos archivos individualmente. No dejar el delta ZIP en `world/datapacks/`: ',
             'no es un pack independiente y duplicaria funciones. Verificar que no exista otra copia activa de PP3.', '',
             '| Archivo local | Destino | SHA-256 |', '|---|---|---|']
    with zipfile.ZipFile(patch) as z:
        for name in z.namelist():
            local = patch.with_suffix('') / name
            local.parent.mkdir(parents=True, exist_ok=True)
            raw = z.read(name)
            local.write_bytes(raw)
            lines.append(f'| `{local.relative_to(ROOT).as_posix()}` | '
                         f'`world/datapacks/parkour_paradise3-datapack/{name}` | '
                         f'`{hashlib.sha256(raw).hexdigest()}` |')
    lines += ['', 'Reiniciar tras copiar el datapack (apagado/inicio completo). No requiere R2 ni recargas de plugins.',
              'Solo corregir flags o reponer un bloque desde consola no requiere apagar ni reiniciar.',
              'No sustituir mundos, regiones ni `level.dat`; nunca Worlds > Upload en la fila world.', '',
              '### Consola y comprobacion remota', '',
              'Con el jugador cerca de la sala para cargar sus chunks, ejecutar primero el diagnostico ',
              'y guardar su salida. Los comandos de funcion siguientes requieren los archivos nuevos:', '',
              '```text',
              'rg info -w parkour_paradise3 __global__',
              'rg flag -w parkour_paradise3 __global__ use allow',
              'rg flag -w parkour_paradise3 __global__ interact allow',
              'function pp3_main:astral/diagnostico_sala5',
              'function pp3_main:astral/reparar_sala5',
              'function pp3_main:astral/diagnostico_sala5',
              '```', '',
              'Conservar `build deny`, `block-place deny` y `block-break deny`: no hace falta colocar objetos.',
              'Si otra region se superpone, revisar `rg info` para esa region: un deny de mayor prioridad ',
              'puede bloquear el uso aunque __global__ permita. No cambiar regiones ajenas sin diagnostico.',
              'Si console falta o las tareas estan detenidas, revisar consola/errores y el ',
              '`forceload query -34 766` del diagnostico; no invocar la reparacion como jugador ',
              '(los tags de progreso pertenecen al marcador). No inventar un marcador duplicado.', '',
              'Rescate minimo sin subir archivos, solo si diagnostico confirma boton ausente, ',
              'cuarzo y primera mitad sin completar, y console sin lvl5_first. Con jugador en la sala:', '',
              '```text',
              'execute in minecraft:parkour_paradise3 as @e[type=marker,name=console,limit=1,distance=0..,tag=!lvl5_first] if block -52 44 858 minecraft:smooth_quartz if block -52 44 842 minecraft:air if block -52 45 858 minecraft:air run setblock -52 45 858 minecraft:stone_button[face=floor,facing=south,powered=false]',
              '```', '',
              'Si hay piedra u otro bloque donde iba el boton, el parche deliberadamente no lo pisa: ',
              'confirmar primero ese estado remoto y compararlo con el inventario original. ',
              'Si ya hay vidrio amarillo, la primera mitad esta completada y no corresponde reponer el boton.',
              'Probar con jugador SIN OP en aventura: presionar boton, comprobar pistones/temporizacion, ',
              'alcanzar la placa norte, completar tramo de lava y cruzar portal. Revisar consola sin errores.',
              'Repetir una entrada posterior para verificar reset original y probar niveles 19/29/40/61/66/78/81 ',
              'para interacciones y retiradas temporales. El ensayo local no certifica estos recorridos remotos.', '',
              '### Verificaciones locales', '',
              '- Auditoria `python datapack-src/paradise3_mecanismos.py`: 83/83 controles, cero diferencias; geometria identica; 23 command blocks iguales a la traduccion esperada.',
              '- Paper 26.1.2 / Java 25: 11/11 comprobaciones, cero errores al cargar funciones adaptadas. ',
              '  Recuperacion de tres controles, boton presionado, redstone encendida/apagada, tags/pisos completados, bloque inesperado y aislamiento entre mundos.',
              '- `python -m unittest discover -s datapack-src -p test_minijuegos.py`: 12 pruebas aprobadas.',
              '- Ensayo reproducible: `python tools/probar_pp3_mecanismos_paper.py --java <java25> --base <Paper-local>`.',
              'Los originales, derivados, delta y logs quedan en `.local/`; no se publican mapas ni credenciales.',
              '<!-- PP3-SALA5-END -->', '']
    path = ROOT / 'build/deploy/pendiente-17-11.md'
    existing = path.read_text(encoding='utf-8')
    start, end = '<!-- PP3-SALA5-START -->', '<!-- PP3-SALA5-END -->'
    if start in existing:
        before, rest = existing.split(start, 1)
        _, after = rest.split(end, 1)
        existing = before.rstrip() + '\n\n' + after.lstrip()
    path.write_text(existing.rstrip() + '\n\n' + '\n'.join(line.rstrip() for line in lines), encoding='utf-8')


def recovery_functions(main, world):
    base = f'data/{main}/function/astral/'
    # Piso y tags son dos comprobaciones independientes de progreso. Nunca tocar
    # un bloque inesperado, un boton presionado o una mitad ya completada.
    first = ('unless entity @s[tag=lvl5_first] '
             'if block -52 44 858 minecraft:smooth_quartz '
             'if block -52 44 842 minecraft:air ')
    second = ('unless entity @s[tag=lvl5_second] '
              'if block -37 44 863 minecraft:lava ')
    repairs = [
        first + 'if block -52 45 858 minecraft:air run setblock -52 45 858 '
        'minecraft:stone_button[face=floor,facing=south,powered=false]',
        first + 'if block -52 45 840 minecraft:air run setblock -52 45 840 '
        'minecraft:acacia_pressure_plate[powered=false]',
        second + 'if block -37 45 865 minecraft:air run setblock -37 45 865 '
        'minecraft:acacia_pressure_plate[powered=false]',
    ]
    return {
        base + 'recuperar_sala5.mcfunction': '\n'.join(
            f'execute in {world} {condition}' for condition in repairs),
        base + 'reparar_sala5.mcfunction': '\n'.join([
            '# Desde consola: solo actua con el marcador original; no reinicia progreso.',
            f'execute in {world} as @e[type=marker,name=console,limit=1,distance=0..] '
            f'run function {main}:astral/recuperar_sala5']),
        base + 'diagnostico_sala5.mcfunction': '\n'.join([
            f'function {main}:astral/diagnostico',
            f'execute in {world} run data get entity '
            '@e[type=marker,name=console,limit=1,distance=0..] Tags',
            *[f'execute in {world} if block {pos} {block} run say [PP3] {label}'
              for pos, block, label in [
                  ('-52 45 858', 'minecraft:stone_button', 'boton presente'),
                  ('-52 45 858', 'minecraft:air', 'boton ausente (puede ser progreso)'),
                  ('-52 44 858', 'minecraft:smooth_quartz', 'primera mitad sin completar'),
                  ('-52 44 858', 'minecraft:yellow_stained_glass', 'primera mitad completada'),
                  ('-52 45 840', 'minecraft:acacia_pressure_plate', 'placa norte presente'),
                  ('-37 45 865', 'minecraft:acacia_pressure_plate', 'placa lava presente'),
                  ('-52 42 861', 'minecraft:redstone_block', 'salida de boton encendida'),
                  ('-52 42 861', 'minecraft:air', 'salida de boton apagada'),
              ]]
        ]),
    }


def controls(path):
    """Inventario exacto, incluida orientacion/potencia; no extrae archivos del ZIP."""
    result = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if '/region/' not in name or not name.endswith('.mca'):
                continue
            for chunk in chunk_records(z.read(name)):
                for section in chunk.get('sections', []):
                    states = section.get('block_states', {})
                    palette = states.get('palette', [])
                    wanted = {i for i, e in enumerate(palette) if any(
                        kind in e['Name'] for kind in ('_button', '_pressure_plate', ':lever'))}
                    if not wanted:
                        continue
                    bits = max(4, (len(palette) - 1).bit_length())
                    for i in range(4096):
                        value = packed(states['data'], i, bits) if len(palette) > 1 else 0
                        if value in wanted:
                            pos = (chunk['xPos'] * 16 + i % 16,
                                   section['Y'] * 16 + i // 256,
                                   chunk['zPos'] * 16 + (i // 16) % 16)
                            result[pos] = palette[value]
    return result


def audit():
    from minijuegos_datapack import Adapter
    folder = ROOT / '.local/mapas'
    original = controls(folder / 'parkour_paradise3.zip')
    prepared = controls(folder / 'subir/parkour_paradise3.zip')
    differences = [p for p in original.keys() | prepared.keys()
                   if original.get(p) != prepared.get(p)]
    adapter = Adapter('parkour_paradise3', folder / 'parkour_paradise3.zip', 'pp3')

    def snapshot(path, rewrite=False):
        geometry, commands = {}, {}
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if '/region/' not in name or not name.endswith('.mca'):
                    continue
                for c in chunk_records(z.read(name)):
                    key = c['xPos'], c['zPos']
                    geometry[key] = [(s['Y'], s.get('block_states')) for s in c.get('sections', [])]
                    for be in c.get('block_entities', []):
                        if 'Command' in be:
                            commands[be['x'], be['y'], be['z']] = (
                                adapter.command(be['Command']) if rewrite else be['Command'])
        return geometry, commands

    original_geometry, expected_commands = snapshot(folder / 'parkour_paradise3.zip', True)
    prepared_geometry, actual_commands = snapshot(folder / 'subir/parkour_paradise3.zip')
    geometry_equal = original_geometry == prepared_geometry
    commands_equal = expected_commands == actual_commands
    report = {
        'original_controls': len(original), 'prepared_controls': len(prepared),
        'differences': differences,
        'geometry_equal': geometry_equal, 'translated_commands_equal': commands_equal,
        'command_blocks': len(expected_commands),
        'controls': [dict(pos=p, state=s) for p, s in sorted(original.items())],
    }
    out = folder / 'subir/pp3-mecanismos-auditoria.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'PP3: {len(original)} controles originales, {len(prepared)} preparados; '
          f'{len(differences)} diferencias. Inventario: {out}')
    print(f'Geometria identica: {geometry_equal}; '
          f'{len(expected_commands)} command blocks traducidos correctamente: {commands_equal}')
    if differences or not geometry_equal or not commands_equal:
        raise ValueError('La copia preparada difiere del original; revisar antes de desplegar')
    lines = ['# Paradise 3: inventario de mecanismos — 17/11/2026', '',
             'Generado por `python datapack-src/paradise3_mecanismos.py`.', '',
             f'{len(original)} controles, cero diferencias de bloque/orientacion/potencia entre original y preparado. ',
             f'Geometria completa identica; {len(expected_commands)} command blocks coinciden con la traduccion esperada.',
             'Esto verifica la copia local, no el estado del servidor.', '',
             '| X Y Z | Bloque y propiedades originales | Funcion que referencia la posicion |',
             '|---|---|---|']
    for pos, state in sorted(original.items()):
        xyz = ' '.join(map(str, pos))
        properties = ','.join(f'{k}={v}' for k, v in sorted(state.get('Properties', {}).items()))
        block = state['Name'].removeprefix('minecraft:') + (f'[{properties}]' if properties else '')
        refs = sorted({name.split('/data/')[1].replace('/function/', ':').removesuffix('.mcfunction')
                       for name, raw in adapter.sources.items()
                       if name.endswith('.mcfunction') and xyz in raw.decode('utf-8', 'replace')
                       and '/more_maps/' not in name})
        lines.append(f'| `{xyz}` | `{block}` | ' +
                     (', '.join(f'`{ref}`' for ref in refs) or 'Redstone/command blocks; sin referencia absoluta en funciones') + ' |')
    lines += ['', 'Los controles de More Maps en `-38 132 764` y `-38 132 768` son publicidad desactivada.',
              'Los niveles 5, 66 y 81 retiran/reponen placas durante el juego: no restaurarlas en masa.',
              'Nivel 81 tambien coloca placas en posiciones relativas durante su animacion; ',
              'el inventario lista el estado guardado, no todos los estados temporales posibles.',
              'Las palancas de 19, 29 y 61 y el boton de 40 se leen por funciones del mapa. ',
              'Placa de 78: invoca el minecart. Conservar las secuencias originales.',
              'Todas estas interacciones requieren `use allow` e `interact allow`, ya generados para PP3.',
              'Solo se recuperan automaticamente los tres controles de sala 5 con guardas de progreso.',
              'Para otros controles ausentes confirmados en vivo: restaurar solo el bloque y estado de esta tabla,',
              'con `execute in minecraft:parkour_paradise3 run setblock X Y Z minecraft:BLOQUE[PROPIEDADES]`.',
              'Nunca ejecutar esa restauracion masiva ni sobre controles temporales de una partida activa.', '']
    (ROOT / 'build/deploy/pp3-mecanismos-17-11.md').write_text(
        '\n'.join(line.rstrip() for line in lines), encoding='utf-8')
    return report


if __name__ == '__main__':
    audit()
