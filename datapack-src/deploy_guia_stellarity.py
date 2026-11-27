"""Entrega aislada de la ampliacion de Guia; no modifica ZIP ni menus compartidos.

Lee la captura versionada de HEAD para no publicar cambios previos. --base tiene
que ser el FINAL que corresponda desplegar. --download-base baja el pack publico
actual sin claves; su presencia en R2 no certifica el SHA remoto del servidor.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
from urllib.request import Request, urlopen

import guia_cofre as g
from guia_ampliacion import catalog, extend_source
from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/guia-stellarity'
PRIVATE = privado() / 'build/entregas/guia-stellarity-comida-crafteos'
URL = 'https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip'


def head(path):
    return subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT)


def digest(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def zip_write(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, (2026, 11, 26, 0, 0, 0)), raw, compress_type=zipfile.ZIP_DEFLATED)


def download_base():
    path = ROOT / '.local/coordination/guia-pack-publicado-base.zip'
    path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(URL + '?guia-stellarity=20261126', headers={'User-Agent': 'AstralRPG-pack-verifier/1.0', 'Cache-Control': 'no-cache'})
    temp = path.with_suffix('.download')
    with urlopen(request, timeout=60) as stream, temp.open('wb') as output:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            output.write(chunk)
    if not zipfile.is_zipfile(temp):
        raise ValueError('La descarga no es un pack ZIP valido')
    temp.replace(path)
    print('Base publicada:', digest(path))
    return path


def previews(menus):
    """Planos de revision: no incluye renders de arte de terceros ni simula capturas."""
    from PIL import Image, ImageDraw
    import yaml
    folder = ROOT / 'build/previews/guia-stellarity'
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob('*.png'):
        if old.stem not in menus:
            old.unlink()
    panels = {False: g.general_panel().resize(g.SIZE, Image.Resampling.LANCZOS).convert('RGBA'),
              True: g.receta_panel('METODO').resize(g.SIZE, Image.Resampling.LANCZOS).convert('RGBA')}
    for name, raw in menus.items():
        if not name.startswith(('g_guia_', 'g_atlas_seccion_cocina', 'g_atlas_seccion_crafteos', 'g_atlas_seccion_stellarity')):
            continue
        menu = yaml.safe_load(raw)
        is_recipe = g.BG_CHARS['receta_stellarity'][0] in menu['menu_title']
        panel = panels[is_recipe]
        canvas = Image.new('RGBA', (650, 350), '#0b1024')
        canvas.alpha_composite(panel, (0, 25))
        d = ImageDraw.Draw(canvas)
        d.text((8, 6), 'PLANO DE REVISION - nombres y casillas; sin texturas de items', fill='#f6d27a')
        caption = menu['menu_title'].split(g.TITLE_COLOR)[-1]
        g.fit_text(canvas, caption, (112, 70), 160, '#ffe9a8')
        legend = []
        for it in menu['items'].values():
            slot = it['slot']
            if slot >= 45 or it.get('display_name') == ' ':
                continue
            title = g.plain(it['display_name'])
            n = len(legend) + 1
            x, y = g.slot_xy(slot)
            d.rectangle((x + 2, y + 27, x + 14, y + 39), fill='#25446a', outline='#e8b24a')
            d.text((x + 3, y + 27), str(n), fill='white')
            legend.append(f'{n}. {title} (casilla {slot})')
        for n, label in enumerate(legend):
            col, row = divmod(n, 22)
            d.text((232 + col * 205, 32 + row * 13), label[:39], fill='#c6eafa')
        d.text((232, 328), name[:64], fill='#9db1d0')
        canvas.convert('RGB').save(folder / (name + '.png'))


def generate(base):
    source = extend_source(json.loads(head('build/runtime/guia_fuente.json')))
    full = g.menus(source)
    archive = subprocess.check_output(['git', 'archive', '--format=zip', 'HEAD', 'build/menus/DeluxeMenus'], cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        old = {Path(n).stem: z.read(n).decode('utf8').replace('\r\n', '\n') for n in z.namelist() if n.endswith('.yml') and '/gui_menus/' in n}
    changed = {n: body for n, body in full.items() if old.get(n) != body}
    folder = OUT / 'gui_menus'
    folder.mkdir(parents=True, exist_ok=True)
    for previous in folder.glob('*.yml'):
        if previous.stem not in changed:
            previous.unlink()
    for name, body in changed.items():
        (folder / (name + '.yml')).write_text(body, encoding='utf8')
    registrations = ''.join(f'  {name}:\n    file: {name}.yml\n' for name in changed)
    (OUT / 'config-guia.yml').write_text('# Fusionar dentro de gui_menus; no reemplazar config.yml completo.\n' + registrations, encoding='utf8')
    assets, providers = g.assets(source)
    # Delta exclusivo de la guia: sin retratos, modelos ni ilustraciones existentes.
    assets = {n: b for n, b in assets.items() if n.startswith('assets/astral/textures/font/guia_astral/')}
    (OUT / 'font-providers.json').write_text(json.dumps(providers, ensure_ascii=False, indent=2), encoding='utf8')
    zip_write(OUT / 'GuiaAstral-Assets.zip', assets)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    final = PRIVATE / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(base) as z:
        base_files = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}
    font_path = 'assets/minecraft/font/default.json'
    font = json.loads(base_files[font_path])
    chars = {c for p in providers for c in p.get('advances', {})} | {c for p in providers for line in p.get('chars', []) for c in line}
    def owns(p):
        other = {c for line in p.get('chars', []) for c in line} | set(p.get('advances', {}))
        return p.get('file', '').startswith('astral:font/guia_astral/') or bool(chars & other)
    kept = []
    for p in font['providers']:
        if not owns(p):
            kept.append(p)
        elif p.get('type') == 'space':
            remaining = {c: value for c, value in p['advances'].items() if c not in chars}
            if remaining:
                kept.append(dict(type='space', advances=remaining))
        elif not p.get('file', '').startswith('astral:font/guia_astral/'):
            raise ValueError('Colision con una fuente ajena: ' + str(p.get('file')))
    font['providers'] = providers + kept
    replacement = dict(assets)
    replacement[font_path] = json.dumps(font, ensure_ascii=False).encode('utf8')
    final_files = dict(base_files)
    final_files.update(replacement)
    zip_write(final, final_files)
    # Verificacion de conservacion fuera del delta y modelos Stellarity reales.
    assert all(final_files[n] == b for n, b in base_files.items() if n not in replacement)
    missing = sorted({row['model'] for row in catalog()['items'].values() if row['model'] and
                      'assets/' + row['model'].replace(':', '/items/') + '.json' not in final_files})
    if missing:
        raise ValueError('Modelos Stellarity ausentes del FINAL: ' + ', '.join(missing))
    previews(changed)
    manifest = dict(base=str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else base.name,
                    base_sha1=digest(base), final=str(final.relative_to(ROOT)), final_sha1=digest(final),
                    menus=sorted(changed), new_menus=sorted(set(changed) - set(old)),
                    pack_delta=sorted(n for n, b in replacement.items() if base_files.get(n) != b),
                    unchanged_base_entries=sum(n not in replacement for n in base_files),
                    source='HEAD:build/runtime/guia_fuente.json', version=catalog()['version'])
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (PRIVATE / 'pack.sha1').write_text(manifest['final_sha1'] + '\n', encoding='utf8')
    print('Menus:', len(changed), 'nuevos:', len(manifest['new_menus']), 'FINAL:', manifest['final_sha1'])
    delivery(manifest)
    return manifest


def delivery(m):
    receipt = OUT / 'r2-verificado.json'
    verified = receipt.exists() and json.loads(receipt.read_text(encoding='utf8')).get('sha1') == m['final_sha1']
    r2_status = ('Subido a R2 y descarga publica verificada por tools/subir_pack_r2.py.' if verified
                 else 'R2 pendiente de subir y verificar; no actualizar propiedades hasta completarlo.')
    text = f'''# Guia Astral: Stellarity, Comida y Crafteos

Preparado, sin instalacion remota verificada. Empower, Paper 26.1.2 / Java 25.
Stellarity 5.4.2; no instalar 6.0.1. CNK 1.3.12 se describe como preparado,
sin confirmar su presencia actual. No se instala ni modifica Stellarity o CNK.

## Version y conservacion

Base descargada del R2 publico, SHA-1 `{m['base_sha1']}`. Esto comprueba la version
publicada del pack; no certifica el SHA-1 actual en server.properties remoto.
FINAL privado: `{m['final'].replace(chr(92), '/')}`.
SHA-1 nuevo: `{m['final_sha1']}`.
Estado de R2: **{r2_status}**
Conserva {m['unchanged_base_entries']} entradas de la base fuera del delta de fuentes y fondos de Guia.
No incluye texturas locales de gomera/bazar/renacer ni otras tareas sin publicar.
Los ZIP compartidos build/AstralRPG-Items.zip y build/AstralRPG-Textures.zip,
build/runtime/guia_fuente.json y build.py conservan el trabajo previo.
La captura usada fue HEAD:build/runtime/guia_fuente.json; solo cambia la ampliacion.

## Archivos y destinos

| Local | Destino / accion |
|---|---|
| Cada YAML listado abajo en build/guia-stellarity/gui_menus/ | plugins/DeluxeMenus/gui_menus/ con el mismo nombre |
| build/guia-stellarity/config-guia.yml | Fusionar las entradas dentro de gui_menus en plugins/DeluxeMenus/config.yml; no sustituir el archivo completo |
| FINAL privado indicado arriba | R2, mediante tools/subir_pack_r2.py; no subir el ZIP publico de assets como pack completo |
| SHA-1 indicado arriba | resource-pack-sha1 en server.properties, solo tras verificar descarga publica |

Son {len(m['menus'])} YAML ({len(m['new_menus'])} nuevos) y el fragmento de registro.
build/guia-stellarity/GuiaAstral-Assets.zip y font-providers.json son insumos publicos
del generador, no packs completos ni archivos para plugins.
No se necesita subir datapack a world/datapacks, JAR, Skript, mapas ni mundos:
esta tarea agrega consultas a DeluxeMenus y fondos al resource pack.

## Instalacion y prueba reservada

1. Comprobar que el resource-pack remoto corresponda a la base. Si el pack publicado
   cambio, volver a generar con `python datapack-src/deploy_guia_stellarity.py --download-base`.
   No usar un FINAL local mas nuevo de otra tarea por su fecha.
2. Subir el FINAL con `python tools/subir_pack_r2.py "{m['final'].replace(chr(92), '/')}"`.
   El comando compara el SHA-1 de la descarga publica. Registrar el resultado antes
   de actualizar server.properties desde el panel.
3. Instalar los YAML listados y fusionar config-guia.yml. Conservar el resto de menus.
   Consola: `dm reload`; revisar errores de YAML, requisitos, modelos y menus faltantes.
4. Consola: `lp user ByTrainx permission set astral.guia.ampliacion true`.
   Las ventanas exigen ese permiso Y nombre ByTrainx. No darlo al grupo default.
5. Cargar el nuevo SHA-1 con reinicio completo. Los YAML solos admiten dm reload sin apagar;
   el cambio de pack/propiedades requiere reinicio y reconexion del cliente.
   El pedido de reiniciar sin jugadores lo continua Claude desde el panel: antes usar
   `list` en consola y comprobar cero conectados; no asumirlo por falta de datos.
6. ByTrainx: `/modo admin`, `/sala`, abrir `/guiaastral`, Comida (pagina 1),
   Crafteos y Stellarity (pagina 3). Probar volver/anterior/siguiente/cerrar,
   cantidades, textos al pasar el cursor y colores del fondo. Otro jugador debe
   recibir el aviso de prueba al intentar abrir estas ventanas.
7. Abrir al publico requiere OK del dueno y cambiar el generador que construye
   open_requirement; regenerar la entrega. No quitar requisitos a mano en build.

No reiniciar ni recargar el servidor desde esta tarea. No usar Worlds > Upload,
no reemplazar mundos y no ejecutar /reload de Bukkit para cambiar datapacks.
tools/empower_api.py admite `--yes command "list"` con la clave existente del panel,
pero no devuelve la salida de consola: solo confirma el envio. No sirve para
certificar el numero de conectados; Claude debe leer la consola del panel.
No se usa API privada de Aternos ni se eluden restricciones.

## Verificacion y limites

20 pruebas de test_guia_cofre.py y test_guia_atlas.py: ingredientes, enlaces,
indexado, forma, cantidades, modelos, fuente sin mutacion y recetas sin boton Forja.
Verificar tambien el manifiesto y la auditoria tools/verificar_terceros.py antes del commit.
No se ejecuto el antiguo ensayo Paper de dialogos: el datapack no cambia y ese
ensayo no carga DeluxeMenus. La carga real del plugin y cliente siguen pendientes.

build/previews/guia-stellarity contiene un plano PNG por ventana nueva; son
vistas de casillas y nombres con el fondo real, sin renders de arte de terceros,
sin simular capturas de Minecraft. La revision visual con cliente es obligatoria.
Informe completo privado: .local/coordination/stellarity-informe.md (no publicar).
Datos de la Guia: datapack-src/guia_stellarity.json, 150 objetos y 116 recetas.
El informe incluye efectos, botin condicionado, biomas, estructuras y anexo CNK.

Limitaciones del original: Frost Cloud enumera cinco ingredientes pero exige seis;
el Altar Maldito necesita comprobar activacion porque Astral retira al dragon;
bell_flower y chorus_petal carecen de modelo en el RP disponible (base vanilla).
El RP de traducciones local es 6.0.1, distinto del datapack 5.4.2; los numeros y
recetas se leen del datapack, no se infieren de esas traducciones.

## Texto para Discord — solo despues de abrir al publico

🆕 La Guia Astral suma Comida, Crafteos y Stellarity.
Ahora podes consultar para que sirve cada sistema y ver las recetas del End,
sus materiales y donde se preparan. Tambien vas a encontrar armas, armaduras,
libros, peces y jefes. La cocina Crop & Kettle aparece como preparada hasta
confirmar que este habilitada. Abrilo desde la Guia del Menu Astral.

No publicado en Discord: la ampliacion sigue reservada al dueno.

## Lista exacta de YAML

Cada ruta local siguiente se copia a plugins/DeluxeMenus/gui_menus/ con su mismo nombre:

'''
    text += '\n'.join('- `build/guia-stellarity/gui_menus/' + n + '.yml`' for n in m['menus']) + '\n'
    (ROOT / 'build/deploy/guia-stellarity-comida-crafteos.md').write_text(text, encoding='utf8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path)
    ap.add_argument('--download-base', action='store_true')
    ap.add_argument('--registrar-r2', metavar='SHA1', help='Registrar el resultado exitoso de tools/subir_pack_r2.py, sin regenerar el pack')
    args = ap.parse_args()
    if args.registrar_r2:
        manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf8'))
        if args.registrar_r2 != manifest['final_sha1'] or digest(ROOT / manifest['final']) != args.registrar_r2:
            ap.error('El recibo no corresponde al FINAL generado')
        (OUT / 'r2-verificado.json').write_text(json.dumps(dict(sha1=args.registrar_r2, url=URL,
            verificacion='tools/subir_pack_r2.py: subida y descarga publica coincidentes'), indent=2) + '\n', encoding='utf8')
        delivery(manifest)
        print('Recibo R2 registrado:', args.registrar_r2)
    else:
        base = download_base() if args.download_base else args.base
        if base is None:
            ap.error('Indicar --base FINAL o --download-base; no se adivina que version esta publicada.')
        generate(base.resolve())
