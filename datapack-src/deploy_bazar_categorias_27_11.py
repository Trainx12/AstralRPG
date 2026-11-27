"""Bazar 1.3.1: FINAL por delta del inicio, previews y entrega (sin red)."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw
from terceros import privado
import ventanas_bazar as VB
import ventanas_bazar26 as V

ROOT = Path(__file__).resolve().parents[1]
BASE = privado() / 'build/entregas/guia-stellarity-comida-crafteos/AstralRPG-Textures.zip'
OUT = privado() / 'build/entregas/bazar-categorias-27-11'
BASE_SHA = '6fe11d1968fb35cb64931609e72f7037b8fe7798'
FONT = 'assets/minecraft/font/default.json'
PREFIX = 'assets/astral/textures/font/bazar/productos_'


def change(names, z):
    from services_ui import png
    tiles = VB.tiles('productos')
    files, providers = {}, []
    for i, (g, v, p, alto, ascent, x0, avance) in enumerate(tiles):
        assert max(p.size) <= 256
        path = f'font/bazar/productos_{i}.png'
        files['assets/astral/textures/' + path] = png(p)
        providers += [dict(type='bitmap', file='astral:' + path, height=alto, ascent=ascent, chars=[g]),
                      dict(type='space', advances={v: -(avance + x0)})]
    font = json.loads(z.read(FONT))
    def mine(p):
        return p.get('file', '').startswith('astral:font/bazar/productos_') or (
            p.get('type') == 'space' and p.get('advances') and
            all(0xF600 <= ord(c) < 0xF610 for c in p['advances']))
    old = [p for p in font['providers'] if mine(p)]
    assert old, 'La base no tiene los glifos del inicio del Bazar'
    keep = [p for p in font['providers'] if not mine(p)]
    used = {c for p in keep for row in p.get('chars', []) for c in row} | {c for p in keep for c in p.get('advances', {})}
    assert not used & {c for p in providers for row in p.get('chars', []) for c in row}
    font['providers'] = keep + providers
    files[FONT] = json.dumps(font, ensure_ascii=False).encode()
    for name in names:
        if name.startswith(PREFIX) and name not in files:
            files[name] = None
    return files


def previews():
    data = json.loads((ROOT / 'build/bazar/productos.yml').read_text(encoding='utf8'))['productos']
    im = Image.open(VB.OUT / 'productos.png').convert('RGBA')
    out = ROOT / 'build/previews'
    source = ROOT / 'datapack-src/pack-source'
    pack = zipfile.ZipFile(BASE)
    for cat, slug in [('Combate', 'inicio'), ('Bosque', 'bosque'), ('Oceano', 'oceano')]:
        # Vista CPU con los productos reales del catálogo; no es captura del cliente.
        prev = Image.new('RGBA', im.size, '#282828'); prev.alpha_composite(im)
        names = []
        for slot, (iid, p) in zip([2,3,4,5,6,7,8,11,12,13,14,15,16,17,20,21,22,23,24,25,26,29,30,31,32,33,34,35,38,39,40,41,42,43,44],
                                  ((i,p) for i,p in data.items() if p['categoria'] == cat)):
            paths = [ROOT / f'datapack-src/pack-source/assets/astral/textures/item/{iid}.png',
                     ROOT / f'datapack-src/pack-source/vanilla-base/item/{p["material"].split(":")[-1]}.png']
            paths = [p for p in source.rglob(iid+'.png') if 'terceros' not in p.parts] + paths
            icon = next((Image.open(pth).convert('RGBA') for pth in paths if pth.exists()), None)
            model_path = f'assets/astral/models/item/{iid}.json'
            if model_path in pack.namelist():
                model = json.loads(pack.read(model_path))
                texture = model.get('textures', {}).get('layer0', '')
                if texture.startswith('astral:item/'):
                    path = 'assets/astral/textures/' + texture.split(':',1)[1] + '.png'
                    if path in pack.namelist():icon = Image.open(io.BytesIO(pack.read(path))).convert('RGBA')
            x,y=round(V.col(slot%9)*V.K),round(V.fila(slot//9)*V.K)
            if icon is not None:
                icon.thumbnail((28,28),Image.Resampling.NEAREST);prev.alpha_composite(icon,(x+(36-icon.width)//2,y+(36-icon.height)//2))
            else:
                ImageDraw.Draw(prev).text((x+7,y+10),str(len(names)+1),fill='white')
            names.append(p['nombre'])
        d=ImageDraw.Draw(prev);r=['Combate','Bosque','Oceano'].index(cat)
        d.rectangle((8,round(V.fila(r)*2),126,round(V.fila(r+1)*2)-1),outline='#fff0a0',width=1)
        d.text((12,350),'Vista CPU: '+cat,fill='white')
        for i,n in enumerate(names[:14]):d.text((12,369+i*11),n,fill='white')
        prev.save(out / f'bazar_{slug}_27_11.png')
    pack.close()


def main(resultado):
    assert hashlib.sha1(BASE.read_bytes()).hexdigest() == BASE_SHA, 'FINAL base incorrecto'
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(BASE) as src, zipfile.ZipFile(final, 'w') as dst:
        delta = change(src.namelist(), src)
        for n in src.namelist():
            if n not in delta:dst.writestr(src.getinfo(n), src.read(n))
        for n, payload in sorted(delta.items()):
            if payload is not None:
                info=zipfile.ZipInfo(n, (2026,11,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                dst.writestr(info,payload)
    with zipfile.ZipFile(BASE) as before, zipfile.ZipFile(final) as after:
        old_names, new_names = set(before.namelist()), set(after.namelist())
        changed = old_names ^ new_names
        for n in old_names & new_names:
            # Check metadata first; read matching entries too to certify byte equality.
            if before.getinfo(n).CRC != after.getinfo(n).CRC or before.read(n) != after.read(n):
                changed.add(n)
        assert all(n == FONT or n.startswith(PREFIX) for n in changed), changed
        # Todas las otras ventanas/texturas son idénticas a la base EN VIVO.
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha+'\n', encoding='utf8')
    (OUT / 'delta.json').write_text(json.dumps(sorted(changed), indent=2)+'\n', encoding='utf8')
    previews()
    jarsha = hashlib.sha256((ROOT/'build/bazar/AstralBazar.jar').read_bytes()).hexdigest()
    productsha = hashlib.sha256((ROOT/'build/bazar/productos.yml').read_bytes()).hexdigest()
    doc = f'''# Bazar 1.3.1 — categorías (27/11/2026)

Implementado localmente, sin despliegue ni subida a R2. Sigue `publico: false`.
Incluye la base autorizada 1.3.0 (precios, ventanas e interacciones).

Inicio: 0 Combate, 9 Bosque, 18 Océano, 27 Consumibles, 36 Especiales.
Combate es la selección inicial e incluye ambas Netheritas. Bosque tiene Madera
Estelar y Palo Reforzado; Océano tiene Perla Abisal y Coral Astral. IDs intactos.
SQLite no guarda categorías: no hay que transformar ni reemplazar la base.
El cargador reconoce categorías antiguas; una desconocida cae en Especiales.

| Archivo local | Destino |
|---|---|
| `build/bazar/AstralBazar.jar` | `plugins/update/AstralBazar.jar` |
| `build/bazar/productos.yml` | `plugins/AstralBazar/productos.yml` |
| `.local/terceros/AstralRPG-privado/build/entregas/bazar-categorias-27-11/AstralRPG-Textures.zip` | R2, publicación pendiente de Claude |

SHA-256 JAR: `{jarsha}`.
SHA-256 productos: `{productsha}`.
SHA-1 FINAL: `{sha}`.
Base exacta: `{BASE_SHA}`. Delta verificado: {len(changed)} entradas,
solo texturas y fuente del inicio del Bazar. Glifos de hasta 224 px; no exceden 256.
No instalar `build/AstralRPG-Textures.zip`: conserva trabajo ajeno pendiente.
`ventanas.yml` está embebido en el JAR: no reemplazar el archivo operativo.
Conservar config, permisos, SQLite/WAL/SHM, respaldos y datos de jugadores.

1. Antes de instalar: `/bazar admin pausar`. Respaldar juntos AstralBazar,
   Essentials y datos de jugadores; no copiar la base local de ensayo al servidor.
2. Subir JAR a update y productos al destino indicado. Si no se admite update,
   apagar y reemplazar solo `plugins/AstralBazar.jar`. Aternos puede impedir
   instalar JAR propios: no usar APIs privadas ni eludir esa limitación.
   La documentación identifica Empower como principal y Aternos como copia.
3. Claude publica el FINAL a R2 justo antes del reinicio, verifica la descarga
   y pone `resource-pack-sha1={sha}` en `server.properties`, conservando su URL.
4. Requiere reinicio completo. Esperar el diario; no activar reiniciopendiente,
   no reiniciar por cuenta propia, no PlugMan ni `/reload` para el JAR.
5. Consola: versión AstralBazar 1.3.1, 88 productos, `publico=false`, sin errores.
   `/bazar admin reanudar`; `/bazar admin recargar` solo recarga configuración,
   no sustituye el reinicio de JAR/catálogo. Probar con ByTrainx en `/modo admin`
   y `/sala`, reingresar para descargar el pack. Otro jugador sigue sin acceso.
6. Dueño: comprobar las cinco etiquetas/clics, Netheritas en Combate, dos productos
   en Bosque y dos en Océano, órdenes previas, crear/cancelar/cobrar una orden.
   No abrir al público hasta su aprobación. Sin anuncio Discord mientras oculto.

Nunca sustituir mundos ni usar Worlds > Upload en la fila world.

Verificación: {resultado}

Vistas CPU en `build/previews/bazar_inicio_27_11.png`, `bazar_bosque_27_11.png`
y `bazar_oceano_27_11.png`. No sustituyen la prueba visual del cliente.
Se reusan marco, espadas, caña y letras Gemini; árbol pixel en su misma paleta.
Revisión final del arte por el dueño pendiente.

Reproducción: `python datapack-src/ventanas_bazar26.py productos`,
`python datapack-src/bazar.py --solo-categorias --jdk <bin-Java25>`,
`python datapack-src/deploy_bazar_categorias_27_11.py --resultado "<resultado>"`.
Para solo compilar desde catálogo versionado, añadir `--solo-compilar` a bazar.py.
'''
    (ROOT/'build/deploy/bazar-categorias-27-11.md').write_text(doc,encoding='utf8')
    print('FINAL', final, '\nSHA-1', sha, '\nDelta:', len(changed))


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--resultado', default='Pendiente de ensayo Paper y auditoría de terceros.')
    main(ap.parse_args().resultado)
