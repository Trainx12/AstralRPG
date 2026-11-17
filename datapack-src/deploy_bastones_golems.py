"""FINAL incremental: reparar rutas BetterModel de tres golems, sin redistribuir su arte."""
import argparse
import hashlib
import json
import zipfile
import shutil
from pathlib import Path
from terceros import ROOT, privado
from final_base import select_base

NAME = 'bastones-golems-17-11'
KINDS = ('bosque', 'cristal', 'hielo')


def repair(files):
    result = dict(files)
    delta = []
    for name, blob in files.items():
        if name.startswith('bettermodel/') and any('astral_golem_' + k + '_' in name for k in KINDS):
            target = 'assets/' + name
            if target in result and result[target] != blob:
                raise ValueError('Conflicto con recurso vigente: ' + target)
            result[target] = blob
            del result[name]
            delta.append((name, target))
    for kind in KINDS:
        models = [n for n in result if n.startswith('assets/bettermodel/models/') and
                  'astral_golem_' + kind + '_' in n and n.endswith('.json')]
        if not models:
            raise ValueError('Faltan modelos de ' + kind)
        for name in models:
            data = json.loads(result[name])
            for ref in data.get('textures', {}).values():
                if ref.startswith('#'):
                    continue
                ns, path = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
                if f'assets/{ns}/textures/{path}.png' not in result:
                    raise ValueError('Textura ausente: ' + ref)
    return result, delta


def prepare(base=None, preview=True):
    out = privado() / 'build/entregas' / NAME
    out.mkdir(parents=True, exist_ok=True)
    base = select_base(output=out, explicit=base)
    with zipfile.ZipFile(base) as z:
        original = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    files, delta = repair(original)
    target = out / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, blob in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 17, 0, 0, 0)), blob, compress_type=zipfile.ZIP_DEFLATED)
    changed = {n for row in delta for n in row}
    assert all(files[n] == b for n, b in original.items() if n not in changed)
    digest = hashlib.sha1(target.read_bytes()).hexdigest()
    (out / 'pack.sha1').write_text(digest + '\n', 'utf8')
    (out / 'delta.json').write_text(json.dumps(dict(base=str(base.relative_to(ROOT)),
        base_sha1=hashlib.sha1(base.read_bytes()).hexdigest(), sha1=digest, moved=delta), indent=2), 'utf8')
    if preview:
        from build_privado import preview as render
        modeldir = privado() / 'build/entregas/correcciones-goblin-golems/models'
        render({k: json.loads((modeldir / f'astral_golem_{k}.bbmodel').read_text('utf8')) for k in KINDS},
               name=NAME, include_sword=False)
    print(target)
    print('SHA-1', digest, 'rutas corregidas:', len(delta))
    return target, digest


def delivery(target, digest, public_root=ROOT, paper_log=None):
    """Copia artefactos cerrados; distingue tarea publicada del acumulado local ajeno."""
    out = target.parent
    paths = {
        'build/AstralRPG-Items.zip': 'world/datapacks/AstralRPG-Items.zip',
        'build/runtime/AstralDecor.jar': 'plugins/AstralDecor.jar',
        'build/runtime/AstralEfectos.jar': 'plugins/AstralEfectos.jar',
        'build/gameplay/astral_gameplay.sk': 'plugins/Skript/scripts/astral_gameplay.sk',
    }
    rows = []
    for name, dest in paths.items():
        local = out / 'tarea' / Path(name).relative_to('build')
        local.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(public_root / name, local)
        rows.append((local.relative_to(ROOT).as_posix(), dest, hashlib.sha256(local.read_bytes()).hexdigest()))
        if public_root.resolve() != ROOT.resolve():
            cumulative = out / 'acumulado' / Path(name).relative_to('build')
            cumulative.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, cumulative)
    report = json.loads((out / 'delta.json').read_text('utf8'))
    proof = 'Ensayo Paper pendiente.'
    if paper_log:
        import re
        results = re.findall(r'SPELL RESULT checks=(\d+) failures=(\d+)', paper_log.read_text('utf8', errors='replace'))
        if not results or results[-1][1] != '0':
            raise ValueError('El ensayo Paper no termino sin fallos')
        proof = f'Paper local: {results[-1][0]} comprobaciones aprobadas sobre los artefactos de tarea.'
    text = [
        '# Bastones perforantes y golemcitos - 17/11/2026', '',
        'Preparado; R2, instalacion y revision con cliente remoto pendientes de Claude. '
        'Principal documentado: Empower; Aternos es copia. Confirmar el panel y estado instalado. '
        'Base de esta tarea: 0f0d23a / AstralDecor 1.18.0.', '',
        '## Implementacion', '',
        'Todos los bastones atraviesan hasta tres enemigos distintos: 100% / 70% / 70%, '
        'incluidos fuego IV/VIII. Constante unica HECHIZO_PERFORA en escala.py; Guia Astral y fichas actualizadas (item v26). '
        'AstralSpell selecciona intersecciones vanilla/BetterModel una vez, ordenadas antes de la pared; '
        'spell_perfora.py conserva /damage magic por jugador y los eventos normales de XP/contadores. '
        'Las marcas se limpian en el mismo disparo. PvP solo en arenas; su normalizacion tambien respeta 70%. '
        'Excluye mascotas, monturas con propietario, vendedores, estatuas, NoAI, invulnerables y al mago.',
        'AstralDecor 1.20.0 y AstralEfectos 1.4.0 deben instalarse juntos con el datapack. '
        'El rayo/bola usa la longitud real del trazado, con explosion por impacto y los interruptores existentes.',
        'Causa del morado: 39 entradas de los tres golemcitos estaban en bettermodel/... fuera de assets/. '
        'Se corrige solo ese prefijo; JSON y PNG se conservan byte por byte. '
        'No cambia ningun .bbmodel ni YAML; no requiere subir modelos ni mm reload/bettermodel reload. '
        'El cristal conserva sus cristales rosados originales; no es la textura negra/magenta faltante.', '',
        '## Instalar solo esta tarea con el servidor apagado', '',
        'Estos archivos son copias cerradas de los artefactos publicados de esta tarea, sin los cambios locales previos de Chaman/hitboxes. '
        'Evitan confundir el build compartido, que conserva ese trabajo ajeno. '
        'No instalar el ZIP publico de texturas.', '',
        '| Archivo local desde la raiz | Destino | SHA-256 |', '|---|---|---|',
        *[f'| `{src}` | `{dest}` | `{sha}` |' for src, dest, sha in rows], '',
        'Si Claude instala tambien la entrega previa Chaman/hitboxes, usar las cuatro rutas equivalentes '
        'bajo `acumulado/` en esta misma entrega privada: conservan ambos trabajos locales. '
        'No publicar ese acumulado como parte de esta tarea ni instalar luego un datapack/JAR historico encima. '
        'Sus hashes se registran en manifest-acumulado.json. Los demas modelos/YAML de aquella tarea se toman de su propia entrega.', '',
        'Apagar, respaldar solo los archivos a reemplazar, instalar las cuatro rutas, actualizar el pack como sigue y reiniciar. '
        'No sustituir mundos/regiones ni usar Worlds > Upload en world. '
        'El arranque carga datapack y JAR. Si solo se reinstala el script: `skript:skript reload astral_gameplay`. '
        'No usar /reload para sustituir el reinicio de los JAR/datapack.', '',
        '## FINAL privado y R2', '',
        f'Base mas nueva: `{report["base"]}`, SHA-1 `{report["base_sha1"]}`. '
        'Se verifico preservacion byte por byte de cada entrada fuera de las 39 rutas movidas y resolucion de las texturas de todos los huesos.',
        f'FINAL: `{target.relative_to(ROOT).as_posix()}`. SHA-1 `{digest}`.',
        f'Publicacion pendiente: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`. '
        'Verificar la descarga publica y su SHA-1; despues cambiar solo resource-pack-sha1 en server.properties, conservando URL fija. Reiniciar.',
        'Vistas CPU privadas de los tres: `.local/terceros/AstralRPG-privado/build/previews/bastones-golems-17-11.png`. '
        'No publicar modelos, PNG, FINAL ni vistas en GitHub.', '',
        '## Verificaciones y pendientes', '',
        proof + ' Incluye 100/70/70, cuarto intacto, disparos consecutivos, fuego IV/VIII, pared, '
        'mascotas, montura con dueno, NoAI, invulnerables, extremo visual, estallidos y nivel Bajo/interruptor apagado.',
        '30 pruebas Python relacionadas aprobadas. La suite amplia de 375 pruebas detecto 27 fallos previos '
        'del simulador de oleadas (espera cuatro llegadas donde el generador local previo produce una); '
        'no se modificaron esos generadores ni sus pruebas para esta tarea. '
        'La comprobacion antigua del marcador fx_rayo se actualizo al marcador final fx_perfora y pasa.',
        'Prueba reproducible: `python tools/probar_perforacion_paper.py --java <Java25.exe> --base <Paper-local>`. '
        'Para auditar otra copia cerrada usar `--artifacts <raiz-con-build>`. No instalar SpellProbe.jar.',
        'Pendiente remoto: revisar consola de datapack, AstralDecor, AstralEfectos, Skript y BetterModel; '
        'probar los tres golems en Bosque/Minas/Cumbre con el FINAL nuevo, bastones en horda y pared, '
        'exclusiones, arenas, Hechiceria/XP real con AuraSkills y efectos Bajo/Medio/Alto con cliente. '
        'El ensayo local verifica eventos de dano unicos atribuidos al mago; no sustituye esa revision visual ni la XP de la configuracion remota.', '',
    ]
    (ROOT / 'build/deploy' / (NAME + '.md')).write_text('\n'.join(text), 'utf8')
    cumulative = out / 'acumulado'
    if cumulative.exists():
        hashes = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in cumulative.rglob('*') if p.is_file()}
        (out / 'manifest-acumulado.json').write_text(json.dumps(hashes, indent=2), 'utf8')
    pending = ROOT / 'build/deploy/pendiente-17-11.md'
    heading = '## Bastones perforantes y golemcitos (ultima entrega)'
    old = pending.read_text('utf8')
    if heading in old:
        old = old[:old.index(heading)].rstrip() + '\n'
    pending.write_text(old + f'\n{heading}\n\nLista exacta y hashes: [{NAME}]({NAME}.md). '
        f'AstralDecor 1.20.0, AstralEfectos 1.4.0, datapack v26 y script PvP. '
        f'FINAL privado `{target.relative_to(ROOT).as_posix()}`; SHA-1 `{digest}`, encima de `{report["base_sha1"]}`. '
        'Apagar y reiniciar. R2, servidor y cliente pendientes de Claude; no hay despliegue verificado. '
        'Ver la distincion tarea/acumulado antes de combinar con Chaman/hitboxes. No sustituir mundos.\n', 'utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path)
    parser.add_argument('--no-preview', action='store_true')
    parser.add_argument('--public-root', type=Path, help='Raiz aislada con los artefactos publicados de esta tarea')
    parser.add_argument('--paper-log', type=Path)
    args = parser.parse_args()
    target, digest = prepare(args.base, not args.no_preview)
    if args.public_root:
        delivery(target, digest, args.public_root.resolve(), args.paper_log)
