"""Integracion CNK 1.3.12: originales intactos, derivados solo en ASTRAL_PRIVADO.

No descarga ni publica contenido. --base permite elegir el FINAL instalado.
La entrega no habilita distribuir el FINAL por R2: requiere permiso del autor.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import zipfile

from terceros import ROOT, privado
from final_base import select_base
from guia_atlas import ENTRADA

VERSION = '1.3.12'
SOURCE = ROOT / '.local/terceros/crop-kettle'
OUTPUT = 'build/entregas/crop-kettle'
LICENSE = 'https://www.curseforge.com/minecraft/data-packs/crop-and-kettle/license'


def sha(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def read_zip(path):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('ZIP con nombres duplicados: ' + str(path))
        return {n: z.read(n) for n in z.namelist() if not n.endswith('/')}


def write_zip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 16, 0, 0, 0)), data,
                       compress_type=zipfile.ZIP_DEFLATED)
    tmp.replace(path)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf8')


def effective(files):
    """Resuelve los overlays anunciados para data format 101.1, sin extraer ZIP."""
    meta = json.loads(files['pack.mcmeta'])
    result = {n: b for n, b in files.items() if n.startswith('data/')}
    for entry in meta.get('overlays', {}).get('entries', []):
        if tuple(entry['min_format']) <= (101, 1) <= tuple(entry['max_format']):
            prefix = entry['directory'] + '/'
            result.update({n[len(prefix):]: b for n, b in files.items() if n.startswith(prefix)})
    return result


def patch_datapack(original):
    files = effective(original)
    changed = []
    # Con varios dialogos vanilla reemplaza el boton Guia Astral por una lista.
    # Astral registra su guia; CNK/Smithed no agregan accesos en pausa ni rapidas.
    for tag in ('pause_screen_additions', 'quick_actions'):
        name = f'data/minecraft/tags/dialog/{tag}.json'
        if name in files:
            obj = json.loads(files[name])
            obj['values'] = [v for v in obj.get('values', [])
                             if (v.get('id') if isinstance(v, dict) else v) == ENTRADA]
            obj.pop('replace', None)
            files[name] = encoded(obj)
            changed.append(name)
    # El pan de CNK usa BREAD: distinguirlo del pan comprado/crafteado vanilla
    # evita comprar trigo barato y revender la coccion al precio vanilla.
    # EconomyShopGUI debe conservar match-item-meta=true y no ignorar custom_data.
    bread = 'data/cnk/loot_table/food/bread.json'
    if bread in files:
        obj = json.loads(files[bread])
        obj.setdefault('functions', []).append({
            'function': 'minecraft:set_custom_data',
            'tag': {'astral_cnk': {'cocina': True}}})
        files[bread] = encoded(obj)
        changed.append(bread)
    # Guardar los triggers en survival; evita colocar bloques/cultivos o alterar NPC
    # en dimensiones de lobby, minas, mazmorras o plugins. No copia codigo CNK al repo.
    for name, data in list(files.items()):
        if '/advancement/' in name and name.endswith('.json'):
            obj = json.loads(data)
            for criterion in obj.get('criteria', {}).values():
                conditions = criterion.setdefault('conditions', {})
                player = conditions.get('player', [])
                if isinstance(player, dict):
                    player = [{'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': player}]
                conditions['player'] = player + [{'condition': 'minecraft:reference', 'name': 'astral_cnk:survival'}]
            files[name] = encoded(obj)
            changed.append(name)
        elif name.endswith('.mcfunction'):
            text = data.decode('utf8')
            filtered = re.sub(r'@a\[', '@a[predicate=astral_cnk:survival,', text)
            filtered = re.sub(r'@a(?![\w\[])', '@a[predicate=astral_cnk:survival]', filtered)
            if filtered != text:
                files[name] = filtered.encode('utf8')
                changed.append(name)
    files['data/astral_cnk/predicate/survival.json'] = encoded({
        'condition': 'minecraft:entity_properties', 'entity': 'this',
        'predicate': {'location': {'dimension': 'minecraft:overworld'}}})
    files['pack.mcmeta'] = encoded({'pack': {'description': 'Crop & Kettle por maybejake — uso privado AstralRPG',
                                               'min_format': [101, 1], 'max_format': [101, 1]}})
    return files, changed


def merge_pack(base, extra):
    files = dict(base)
    conflicts = []
    for name, data in extra.items():
        if not name.startswith('assets/'):
            continue  # Conservar metadata, icono y compatibilidad del FINAL base.
        if name in base:
            if base[name] == data:
                continue
            conflicts.append(name)
            if name.startswith('assets/minecraft/atlases/') and name.endswith('.json'):
                ours, theirs = json.loads(base[name]), json.loads(data)
                sources = ours.setdefault('sources', [])
                for source in theirs.get('sources', []):
                    if source not in sources:
                        sources.append(source)
                files[name] = encoded(ours)
            continue  # En cualquier otro conflicto gana Astral.
        files[name] = data
    return files, conflicts


def adapt_resource(files):
    """26.1 usa atlas de items: resolver el alias entity/ del atlas CNK.

    No se altera el PNG ni el modelo geometrico; los originales quedan intactos.
    """
    files = dict(files)
    changes = []
    for name, blob in list(files.items()):
        if '/models/' not in name or not name.endswith('.json'):
            continue
        obj = json.loads(blob)
        for key, ref in list(obj.get('textures', {}).items()):
            if not isinstance(ref, str) or ref.startswith('#'):
                continue
            ns, tex = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
            if ns != 'cnk' or tex.startswith(('item/', 'block/')):
                continue
            source = f'assets/{ns}/textures/{tex}.png'
            if tex.startswith('entity/'):
                source = f'assets/{ns}/textures/cnk_entity/{tex[7:]}.png'
            if source not in files:
                raise ValueError('Textura CNK sin resolver: ' + ref)
            dest = f'assets/{ns}/textures/item/{tex}.png'
            files[dest] = files[source]
            if source + '.mcmeta' in files:
                files[dest + '.mcmeta'] = files[source + '.mcmeta']
            obj['textures'][key] = ns + ':item/' + tex
        if obj != json.loads(blob):
            files[name] = encoded(obj)
            changes.append(name)
    return files, changes


def recipe_key(recipe):
    """Normaliza forma/traslacion y simbolos para detectar patrones coincidentes."""
    kind = recipe.get('type', '').removeprefix('minecraft:')
    if kind == 'crafting_shaped':
        rows = recipe['pattern']
        while rows and not rows[0].strip(): rows = rows[1:]
        while rows and not rows[-1].strip(): rows = rows[:-1]
        left = min((len(row) - len(row.lstrip()) for row in rows), default=0)
        right = max((len(row.rstrip()) for row in rows), default=0)
        grid = [[recipe['key'].get(c) for c in row[left:right]] for row in rows]
        a = json.dumps(grid, sort_keys=True)
        b = json.dumps([list(reversed(row)) for row in grid], sort_keys=True)
        return kind, min(a, b)
    if kind == 'crafting_shapeless':
        return kind, tuple(sorted(json.dumps(i, sort_keys=True) for i in recipe['ingredients']))
    return kind, json.dumps(recipe.get('ingredient'), sort_keys=True)


def audit(datapack, astral, resource, base):
    def recipes(files):
        return {n: json.loads(b) for n, b in files.items() if '/recipe/' in n and n.endswith('.json')}
    a, b = recipes(datapack), recipes(astral)
    matches = []
    for n, r in a.items():
        for m, s in b.items():
            same_pattern = recipe_key(r) == recipe_key(s)
            same_result = r.get('result', {}).get('id') == s.get('result', {}).get('id')
            if same_pattern or same_result:
                matches.append({'cnk': n, 'astral': m, 'pattern': same_pattern, 'result': same_result})
    mesa = json.loads((ROOT / 'build/runtime/mesa.json').read_text('utf8'))
    table_matches = []
    for rec in mesa:
        if not rec.get('table'):
            continue
        ingredients = []
        for kind, item, count in rec['ingredients']:
            if kind == 'c':
                loot = json.loads(astral[f'data/astral/loot_table/item/{item}.json'])
                item = loot['pools'][0]['entries'][0]['name']
            if item == 'water_bottle': item = 'minecraft:potion'
            ingredients.extend([item] * count)
        for name, candidate in a.items():
            kind = candidate.get('type', '').removeprefix('minecraft:')
            if kind == 'crafting_shaped':
                slots = [candidate['key'][c] for row in candidate['pattern'] for c in row if c != ' ']
            elif kind == 'crafting_shapeless':
                slots = candidate['ingredients']
            else:
                continue
            options = [slot if isinstance(slot, list) else [slot] for slot in slots]
            if any(sorted(v) == sorted(ingredients) for v in itertools.product(*options)):
                table_matches.append({'cnk': name, 'astral': rec['output']})
    return {'shared_data': sorted(set(datapack) & set(astral)),
            'shared_assets': sorted(n for n in set(resource) & set(base) if n.startswith('assets/')),
            'recipes_cnk': len(a), 'recipes_astral': len(b), 'recipe_matches': matches,
            'runtime_recipes': len(mesa), 'runtime_recipe_matches_by_material': table_matches,
            'vanilla_recipes_overridden': sorted(n for n in datapack if n.startswith('data/minecraft/recipe/')),
            'worldgen_structures': sorted(n for n in datapack if '/worldgen/structure/' in n)}


def delivery(report, probe=None):
    out = privado() / OUTPUT
    def local(path):
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
    lines = ['# Cocina (Crop & Kettle) — 16/11/2026', '',
             'Preparado localmente. Sin subida a R2 ni despliegue en Empower/Aternos.',
             '**Instalacion condicionada a resolver licencia de distribucion y economia antes de activar.**', '',
             '## Version y conservacion', '',
             'Crop & Kettle 1.3.12 por maybejake, para Paper 26.1.2 / Java 25. El original usa pack_format 107; '
             'se aplican sus overlays para 101.1 y se crea una copia privada fijada a 101.1. No se cambia la version del servidor.',
             f"Base FINAL: `{report['base']}`, SHA-1 `{report['base_sha1']}`. Conserva las entregas anteriores, incluida correcciones-goblin-golems.",
             f"FINAL preparado: `{local(out / 'AstralRPG-Textures.zip')}`, SHA-1 **`{report['final_sha1']}`**.",
             f"Datapack adaptado: SHA-1 `{report['datapack_sha1']}`. Originales intactos:", '']
    lines += [f'- `{SOURCE.relative_to(ROOT).as_posix()}/{name}`: SHA-1 `{digest}`.' for name, digest in report['original_sha1'].items()]
    lines += ['', 'Reproducir desde la raiz:', '', '```text',
              'python datapack-src/build.py',
              'python datapack-src/tanda5a.py',
              f"python datapack-src/crop_kettle.py --base \"{report['base']}\"",
              'python -m unittest discover -s datapack-src -p test_crop_kettle.py', '```',
              'El generador sin --base elige el FINAL privado mas reciente y excluye su propia salida. '
              'Antes de desplegar, cotejar esa base con el pack realmente instalado; si difiere, regenerar sobre el instalado. '
              'No instalar el ZIP publico de texturas.', '', '## Compatibilidad y parches', '',
              f"- {report['recipes_cnk']} recetas de registro CNK; {report['recipes_astral']} nativas Astral y {report['runtime_recipes']} recetas de su runtime revisadas: "
              f"{len(report['recipe_matches'])} coincidencias nativas y {len(report['runtime_recipe_matches_by_material'])} coincidencias de ingredientes por material con la mesa Astral.",
              '- Mas de cien recetas de cocina propias van por funciones/olla, no por el registro de recetas de mesa. '
              'No hay reemplazos de `data/minecraft/recipe/*` ni de loot tables vanilla.',
              '- Tags `minecraft:load` y `tick`: aditivos, sin replace. CNK/Smithed no agregan dialogos a '
              '`pause_screen_additions` ni `quick_actions`: queda solamente Guia Astral, registrada por Astral. '
              '`mineable/axe`, no_impact y painting_variant/placeable tampoco reemplazan tags existentes.',
              '- Los criterios de avances conservan sus condiciones previas y agregan el predicado de survival. '
              'Los selectores @a de las funciones tambien se filtran; los bucles de entidades programados corren en el overworld. '
              'El soporte queda limitado a survival, no cocina en Nether/End ni en mundos de plugins.',
              '- CNK incorpora seis estructuras en chunks nuevos. AstralProgression debe estar activo y su lista '
              '`structure-namespaces` debe incluir `cnk` para cancelar generacion fuera del mundo survival configurado. '
              'Sin ese plugin/config NO activar. No se regeneran chunks ni se sustituyen regiones.',
              '- Los aldeanos carniceros de survival pueden recibir ofertas CNK. Los NPC en otros mundos no entran en el escaneo '
              'programado. El original incluye tags de trades de 26.2; la entrega esta fijada a 26.1.2, no certificada para futuras versiones.',
              '- No se pisan item models vanilla/Astral, fuentes ni sounds.json existentes. El atlas de bloques se combina '
              'conservando las fuentes de Astral; splashes.txt conserva Astral. El panorama del menu principal aportado por CNK se incorpora.',
              f"- {len(report['adapted_models'])} modelos CNK adaptan referencias de texturas de entidades al atlas de items, sin cambiar PNG ni geometria. "
              f"Auditoria del FINAL: {report['texture_references_checked']} referencias verificadas.",
              '- El generador y el parche no contienen arte ni codigo copiado de CNK. Los derivados y el informe detallado '
              '`audit.json` permanecen en ASTRAL_PRIVADO. Ningun ZIP CNK/FINAL va al GitHub publico.', '',
              '## Economia: revisar antes de instalar', '',
              'CNK agrega nuevas rutas de produccion de comida vanilla; por ejemplo, masa -> pan da BREAD vanilla, '
              'confirmado en Paper. Los alimentos nuevos usan sobre todo POISONOUS_POTATO con componentes propios. '
              'Vender por material sin comprobar componentes podria convertir estos objetos en dinero o venderlos accidentalmente.',
              'La copia local de EconomyShopGUI del 31/10 (no acredita precios actuales) contiene: '
              'POISONOUS_POTATO venta $15; BREAD compra $252/venta $63,04; WHEAT $20/$5; '
              'MILK_BUCKET $18,45/$4,62; COOKIE $33,60/$8,48; PUMPKIN_PIE $42,48/$10,64. '
              'No se cambiaron precios ni se publico esa copia privada.',
              'Antes de habilitar, revisar los shops actuales y probar /sellgui y venta rapida con un item CNK, '
              'un item Astral y su equivalente vanilla. Confirmar que los componentes impidan vender custom como vanilla; '
              'si no, agregar filtro de custom_data.cnk o deshabilitar las entradas afectadas con la configuracion actual del servidor. '
              'Revisar tambien arbitraje de compra de ingredientes y venta del pan producido. No se certifica economia remota.', '',
              '## Licencia', '',
              f'[Custom License de maybejake]({LICENSE}), edicion 25/10/2025: permite jugar en cualquier servidor '
              'y editar para uso personal; exige credito y prohibe redistribuir CNK/assets o usarlos en proyectos propios. '
              'La guia acredita al autor. Los ZIP no traen LICENSE; se verifico la pagina del autor.',
              'La combinacion se prepara solo para este uso local privado. **No subir este FINAL a un bucket R2 publico** '
              'sin permiso expreso del autor para distribuir el pack combinado a los jugadores. La licencia permite jugar en server, '
              'pero no concede de forma expresa esa redistribucion publica. Obtener ese permiso o acordar un circuito autorizado '
              'de instalacion de recursos desde la descarga oficial antes del despliegue. No se publico el FINAL ni se altero R2.', '',
              '## Archivos y destinos (solo despues de resolver condiciones)', '',
              'La documentacion vigente identifica Empower como principal desde el 07/11; Aternos es copia. '
              'Confirmar panel y pack instalado con Claude. Apagar desde el panel y respaldar solamente los archivos a reemplazar.', '',
              '| Archivo local | Destino |', '|---|---|',
              f"| `{local(out / 'CropAndKettle-Astral.zip')}` | `world/datapacks/CropAndKettle-Astral.zip` |",
              '| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` (actualiza la guia) |',
              '| `build/tanda5a/AstralProgression/config.yml` | Integrar `cnk` en `plugins/AstralProgression/config.yml` → `structure-namespaces`, conservando el resto de la config remota |',
              f"| `{local(out / 'AstralRPG-Textures.zip')}` | Pack de recursos FINAL privado; distribucion pendiente de permiso del autor |", '',
              'Instalar CNK una sola vez en `world/datapacks/`, junto a Astral: Paper comparte datapacks entre dimensiones. '
              'No copiar en lobby/minas/mazmorras ni crear carpetas datapacks dentro de cada dimension. '
              'Eliminar solo una instalacion CNK duplicada si existe, previa copia; nunca tocar mapas.',
              'El config regenerado tambien refleja golems/items de fuentes ya publicadas; para esta instalacion integrar '
              'solamente `cnk` en la lista remota, sin reemplazar otros ajustes.',
              'Cuando exista permiso para el circuito de recursos, actualizar `resource-pack-sha1` con el SHA-1 de la descarga verificada '
              'y mantener su URL correspondiente. No pegar un hash local sin verificar el archivo distribuido.', '',
              '## Inicio, consola y comprobacion', '',
              'Reinicio completo obligatorio: datapack/worldgen, configuracion y resource pack. No usar recarga general en caliente. '
              'No se necesita mm reload ni skript reload si las configs ya cargaron al iniciar. '
              'Si se ajustan solo precios despues: `sreload`.',
              'Consola: `datapack list enabled`; verificar Astral y CropAndKettle-Astral, ausencia de errores de functions/advancements/recipes '
              'y AstralProgression activo con survival correcto. Comprobar carga de Skript y MythicMobs. '
              'Revisar el boton Guia Astral del menu de pausa y el recetario CNK con cliente.',
              'En survival, fabricar olla (caldero+fogata), cocinar una receta del recetario y plantar un cultivo nuevo; '
              'comprobar crecimiento, cosecha y protecciones de claims/WorldGuard con un jugador sin permisos de admin. '
              'Repetir intento en lobby/minas/mazmorras: no debe activar CNK ni generar estructuras. '
              'Medir `spark` antes/despues con carga representativa; la prueba local no certifica TPS remoto.',
              'Nunca usar Worlds > Upload en la fila world, ni sustituir mundos/regiones. '
              'No se utilizaron navegador, APIs privadas ni credenciales para este trabajo.', '', '## Pruebas locales', '']
    if probe and (probe / 'cnk.log').exists():
        text = (probe / 'cnk.log').read_text('utf8', errors='replace')
        ok = 'CNK RESULT failures=0' in text and 'CNK FAIL' not in text
        cost = re.search(r'weighted-ms/tick=([\d.Ee+-]+)', text)
        lines += [f"Ensayo `{local(probe)}`: {'APROBADO' if ok else 'NO aprobado'}. "
                  'Paper 26.1.2, Java 25, Astral completo, Skript, MythicMobs y BetterModel. '
                  'Jugador NMS sin cliente: olla real consume masa y produce pan; maiz crece con random ticks acelerados; '
                  'predicado de survival positivo y Nether excluido.',
                  f"Costo ponderado de entradas CNK: {float(cost[1]):.6f} ms/tick." if cost else 'Costo pendiente.',
                  'Microbenchmark local: 200 llamadas por entrada, ponderadas por sus periodos; '
                  'un jugador, una olla y un cultivo. Incluye dispatch de comandos; no equivale a perfil de produccion. '
                  'Logs privados incluyen baseline y CNK; no se publican.']
    else:
        lines += ['Ensayo Paper pendiente de registrar con --probe <directorio-ensayo>.']
    lines += ['', 'Reproducir: `python tools/probar_crop_kettle_paper.py --java <java25> '
              '--base .local/correcciones-probe/paper --work .local/crop-kettle-ensayo-nuevo`. '
              'No instalar CropKettleProbe.jar en remoto. Pruebas propias: seis controles unitarios de conservacion, '
              'overlays, atlas, animacion y aislamiento; mas conservacion byte a byte del FINAL anterior cuando esta disponible.',
              'Pendientes: cliente visual, interacciones/protecciones con jugadores reales, estructuras en mundos de plugins, '
              'economia actual, permiso de distribucion, R2 y despliegue remoto.']
    target = ROOT / 'build/deploy/crop-kettle.md'
    target.write_text('\n'.join(lines) + '\n', encoding='utf8')


def build(base_path=None, probe=None):
    dp = SOURCE / f'CropAndKettle-v{VERSION}-Data-Pack.zip'
    rp = SOURCE / f'CropAndKettle-v{VERSION}-Resource-Pack.zip'
    if not SOURCE.exists() or not any(SOURCE.iterdir()):
        print('Carpeta Crop & Kettle ausente o vacia: no se modifico nada.')
        return
    if not dp.is_file() or not rp.is_file():
        raise FileNotFoundError('Se necesitan ambos ZIP originales de CNK ' + VERSION)
    out = privado() / OUTPUT
    base_path = select_base(output=out, explicit=base_path)
    if base_path.resolve() == (out / 'AstralRPG-Textures.zip').resolve():
        raise ValueError('El FINAL de salida no puede ser su propia base')
    originals = {dp.name: sha(dp), rp.name: sha(rp)}
    raw, resource, base = read_zip(dp), read_zip(rp), read_zip(base_path)
    data, changes = patch_datapack(raw)
    adapted, adapted_models = adapt_resource(resource)
    combined, conflicts = merge_pack(base, adapted)
    report = audit(data, read_zip(ROOT / 'build/AstralRPG-Items.zip'), resource, base)
    report.update({'original_sha1': originals, 'base': str(base_path.relative_to(ROOT)) if base_path.is_relative_to(ROOT) else str(base_path),
                   'base_sha1': sha(base_path), 'patched_entries': changes, 'asset_conflicts': conflicts,
                   'adapted_models': adapted_models})
    write_zip(out / 'CropAndKettle-Astral.zip', data)
    write_zip(out / 'AstralRPG-Textures.zip', combined)
    from pack_audit import audit as audit_pack
    report['texture_references_checked'] = audit_pack(out / 'AstralRPG-Textures.zip')
    report['final_sha1'] = sha(out / 'AstralRPG-Textures.zip')
    report['datapack_sha1'] = sha(out / 'CropAndKettle-Astral.zip')
    (out / 'audit.json').write_bytes(encoded(report))
    (out / 'pack.sha1').write_text(report['final_sha1'] + '\n', encoding='utf8')
    assert originals == {dp.name: sha(dp), rp.name: sha(rp)}, 'Se alteraron originales'
    print(json.dumps({k: report[k] for k in ('base_sha1', 'final_sha1', 'recipes_cnk', 'recipe_matches', 'asset_conflicts')}, ensure_ascii=False))
    delivery(report, probe)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path)
    parser.add_argument('--probe', type=Path)
    parser.add_argument('--datapack-only', action='store_true',
                        help='Regenera solo el datapack privado; no modifica el FINAL de recursos ni su base')
    args = parser.parse_args()
    if args.datapack_only:
        data, changes = patch_datapack(read_zip(SOURCE / f'CropAndKettle-v{VERSION}-Data-Pack.zip'))
        target = privado() / OUTPUT / 'CropAndKettle-Astral.zip'
        write_zip(target, data)
        audit_path = target.parent / 'audit.json'
        if audit_path.exists():
            report = json.loads(audit_path.read_text('utf8'))
            report.update(datapack_sha1=sha(target), patched_entries=changes)
            audit_path.write_bytes(encoded(report))
        print(f'{target}: SHA-1 {sha(target)}; {len(changes)} entradas adaptadas')
    else:
        build(args.base, args.probe)
