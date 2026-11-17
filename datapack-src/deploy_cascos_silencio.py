"""Entrega aislada: cascos v2 sobre panorama, YAML silenciosos y admin del mercader."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

import yaml
from PIL import Image, ImageDraw

import cascos_planos as C
from mobs.silencio import silence, modeled_mobs
from pack_audit import audit
from terceros import ROOT, privado

NAME = 'cascos-silencio-mercader-17-11'
BASE_SHA1 = 'd9ec25c013ccffd028bd384a189e9b3524fdda37'
OUT = privado() / 'build/entregas' / NAME
BASE = privado() / 'build/entregas/mascotas-oceano-panorama-17-11/AstralRPG-Textures.zip'


def pack(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def refs(tree):
    if isinstance(tree, dict):
        if tree.get('type') == 'minecraft:model':
            yield tree['model']
        for val in tree.values():
            yield from refs(val)
    elif isinstance(tree, list):
        for val in tree:
            yield from refs(val)


def icon(files, ref):
    raw = C.resolve(files, ref)
    texture = raw['textures']['layer0']
    ns, path = texture.split(':')
    return Image.open(io.BytesIO(files[f'assets/{ns}/textures/{path}.png'])).convert('RGBA')


def preview(before, after, client):
    rows = []
    for name in sorted(after):
        if not name.startswith('assets/astral/items/') or not name.endswith('.json'):
            continue
        old = json.loads(before.get(name, b'{}')).get('model', {})
        new = json.loads(after[name]).get('model', {})
        for oldref, newref in zip(refs(C.context(old, 'gui')), refs(C.context(new, 'gui'))):
            if '/cascos_planos/' not in newref:
                continue
            original = newref.split('/cascos_planos/',1)[1].replace('/',':',1)
            if original and original not in {r[0] for r in rows}:
                rows.append((original, icon(before, oldref), icon(after, newref), C.render_model(before, original, 128, gui=True)))
    sheet = Image.new('RGBA', (960, 120 + len(rows)*94), '#292929')
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 6), 'CPU - inventario 16 px: ANTES 1x/4x | PLANO V2 1x/4x | ALTERNATIVA 3D (display GUI original)', fill='white')
    def slot(im, x, y, scale):
        cell = Image.new('RGBA', (18,18), '#8b8b8b')
        d = ImageDraw.Draw(cell)
        d.line((0,17,0,0,17,0),fill='#373737');d.line((1,17,17,17,17,1),fill='#ffffff')
        cell.alpha_composite(im.resize((16,16),Image.Resampling.NEAREST), (1,1))
        sheet.alpha_composite(cell.resize((18*scale,18*scale),Image.Resampling.NEAREST),(x,y))
    vanilla = pack(client)
    for i, iid in enumerate(('iron_helmet','diamond_helmet')):
        im=Image.open(io.BytesIO(vanilla[f'assets/minecraft/textures/item/{iid}.png'])).convert('RGBA')
        slot(im, 8+i*100, 33, 4)
        draw.text((8+i*100,107),iid,fill='white')
    for i,(ref, old, new, model) in enumerate(rows):
        y=124+i*94
        slot(old,8,y,1);slot(old,32,y,4)
        slot(new,140,y,1);slot(new,164,y,4)
        slot(model,272,y,1);slot(model,296,y,4)
        draw.text((390,y+12),ref,fill='white')
        # Comparacion de escala inmediata junto a hierro y diamante vanilla.
        for j,iid in enumerate(('iron_helmet','diamond_helmet')):
            slot(Image.open(io.BytesIO(vanilla[f'assets/minecraft/textures/item/{iid}.png'])).convert('RGBA'),400+j*90,y+28,2)
        slot(new,580,y+28,2)
    target=OUT/'previews/cascos_revision_v2.png';target.parent.mkdir(parents=True,exist_ok=True)
    sheet.convert('RGB').save(target)
    return len(rows)


def private_yaml():
    # Conservar bytes salvo Options.Silent en los YAML privados que se instalaran.
    folder=ROOT/'build/mythicmobs'
    public_skills={}
    for p in (folder/'skills').glob('*.yml'):
        public_skills.update(yaml.safe_load(p.read_text('utf8')) or {})
    sources={p.name:p for p in (folder/'mobs').glob('*.yml')}
    sources['astral.yml']=privado()/'build/entregas/monturas-17-11/mythicmobs/mobs/astral.yml'
    skills=dict(public_skills)
    for p in (privado()/'build/entregas/monturas-17-11/mythicmobs/skills').glob('*.yml'):
        skills.update(yaml.safe_load(p.read_text('utf8')) or {})
    p=privado()/'build/entregas/mascotas-oceano-panorama-17-11/mythicmobs/skills/mascotas.yml'
    skills.update(yaml.safe_load(p.read_text('utf8')))
    reports={};paths=[]
    for name,source in sorted(sources.items()):
        data=yaml.safe_load(source.read_text('utf8')) or {}
        original=json.loads(json.dumps(data))
        keys=silence(data,skills)
        # Guardar solo archivos con entidades modeladas, exactos salvo Silent.
        if not keys:continue
        for mid,mob in original.items():
            expected=json.loads(json.dumps(mob))
            if mid in keys:expected.setdefault('Options',{})['Silent']=True
            assert data[mid]==expected
        dest=OUT/'mythicmobs/mobs'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=150),'utf8')
        reports[name]={'modeled':len(keys),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        paths.append((dest,f'plugins/MythicMobs/mobs/{name}'))
    # Verificar tambien todas las salidas publicas, incluyendo metaskills indirectas.
    for p in (folder/'mobs').glob('*.yml'):
        data=yaml.safe_load(p.read_text('utf8')) or {}
        for mid in modeled_mobs(data,public_skills):
            assert data[mid].get('Options',{}).get('Silent') is True,(p,mid)
    return paths,reports


def generate(client):
    assert hashlib.sha1(BASE.read_bytes()).hexdigest()==BASE_SHA1,'FINAL de panorama inesperado'
    OUT.mkdir(parents=True,exist_ok=True)
    before=pack(BASE);after=dict(before)
    rendered=C.normalize(after)
    changed=sorted(n for n,b in after.items() if before.get(n)!=b)
    assert len(rendered)==48, len(rendered)
    assert all('/cascos_planos/' in n or n.startswith('assets/astral/items/') for n in changed)
    target=OUT/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(after.items()):
            z.writestr(zipfile.ZipInfo(n,(2026,11,17,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    report={'base_sha1':BASE_SHA1,'final_sha1':hashlib.sha1(target.read_bytes()).hexdigest(),
            'changed':changed,'icons':len(rendered),'references':audit(target)}
    report['preview_icons']=preview(before,after,client)
    paths,report['silent']=private_yaml()
    (OUT/'delta.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    (OUT/'pack.sha1').write_text(report['final_sha1']+'\n','utf8')
    paths.insert(0,(ROOT/'build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'))
    lines=['# Cascos, silencio y Goblin Mercader — 17/11/2026','',
           'Preparado localmente; sin despliegue ni subida R2. Conservar las entregas 054db88 y 98156c2 pendientes.',
           'Empower es el principal documentado; Aternos es copia. Claude debe confirmar el destino con navegador.',
           '', '| Local desde la raiz | Destino | SHA-256 |','|---|---|---|']
    for local,dest in paths:
        lines.append(f'| `{local.relative_to(ROOT).as_posix()}` | `{dest}` | `{hashlib.sha256(local.read_bytes()).hexdigest()}` |')
    lines += ['',f'Unico FINAL privado: `{target.relative_to(ROOT).as_posix()}`.',
              f'SHA-1 `{report["final_sha1"]}`, encima de panorama/barril `{BASE_SHA1}`. No instalar el ZIP publico.',
              '', '## Instalacion', '',
              '1. Respaldar solo archivos a reemplazar; apagar. Instalar AstralDecor 1.18.0 y los YAML de la tabla. Conservar todas las skills privadas instaladas, incluida la proteccion de mascotas de 98156c2. No instalar probes de pruebas.',
              f'2. Publicar el FINAL: `python tools/subir_pack_r2.py "{target.relative_to(ROOT).as_posix()}"`; verificar descarga publica, conservar URL y actualizar `resource-pack-sha1` al valor anterior.',
              '3. Iniciar: reinicio completo obligatorio por AstralDecor.jar y resource-pack-sha1. Solo YAML, por separado: `mm reload`, sin reinicio; comprobar con entidades nuevas. Las ya existentes pueden conservar Silent anterior hasta reaparecer. No matar todas las entidades ni sustituir mundos.',
              '4. Revisar consola: AstralDecor 1.18.0, MythicMobs y BetterModel sin errores. Probar /astralmercader visita <jugador>, comercio, stock separado, duplicado rechazado, irse y visita natural. Probar jugador sin OP, consola con destino y spawn manual con aviso OP.',
              '5. Con cliente: 48 cascos en inventario/mano/suelo/marco, equipados con 3D intacto; Goblin hostil, mercader, fauna, monturas, jefes y mascotas sin audio vanilla. Confirmar que los sonidos explicitos de skills siguen audibles.',
              'Aternos: usar solamente las vias admitidas del panel. Si no acepta el JAR, queda bloqueada esa instalacion. Nunca Worlds > Upload en world ni reemplazar mundos.',
              '', '## Criterio visual y limites', '',
              '48 PNG de 32x32: arte hasta 28 px, contorno de 1 px y margen transparente de 1 px. Reduccion por area, alfa binario, paleta local de 24 colores, sombras levantadas sin dithering. Vista frontal 3/4 a 25 grados y elevacion 12; luz superior izquierda del renderer.',
              'Se elige plano tambien en GUI: ocupa la casilla de manera uniforme y permite reconocer mejor el casco. Head conserva exactamente el arbol 3D, condiciones y variantes. La alternativa 3D del preview aplica rotation/translation/scale GUI originales en renderer CPU ortografico; no sustituye una captura en cliente.',
              'Vista privada `previews/cascos_revision_v2.png`: antes/despues a 1x y 4x sobre casillas #8b8b8b con borde, alternativa 3D y comparacion junto a hierro/diamante oficiales. Pendiente validacion visual real; no se solicitaron dibujos externos.',
              'Silent modifica solamente Options de entidades con modelo directo o alcanzable por metaskills; sonidos explicitos se conservan. No se agregaron sonidos nuevos.',
              'Spawns manuales del mercader reciben aviso solo para OP al interactuar; la limpieza al cargar chunks anuncia su retiro a OP cercanos (32 bloques). El admin puede forzar visita cerca de un jugador vivo en world, incluso creativo; las visitas naturales siguen limitadas a SURVIVAL.',
              '', '## Verificaciones', '',
              '373 pruebas unitarias aprobadas; contratos de cascos/silencio y mesa repetidos sobre la entrega final: ocho aprobados. 48 iconos y 7359 referencias del FINAL auditadas. Todos los mobs modelados de los YAML publicos y de instalacion pasan Silent, siguiendo metaskills y conservando el resto de sus datos/sonidos.',
              'Paper 26.1.2 / Java 25 con MythicMobs 5.13 y BetterModel reales: 22 comprobaciones, failures=0. OP creativo, consola con jugador, no OP, duplicados, clic/menu, cinco minutos, expiracion, irse, stock por UUID, limite sin quinto cobro, loot entregado, distancia, rechazo de magma, siguiente intervalo y visita natural SURVIVAL. Spawn manual avisa al OP aun con clic cancelado por otro plugin; limpieza anuncia retiro.',
              'El ensayo usa jugadores NMS y proveedor Vault simulado con saldo suficiente. Prueba el handler Bukkit del comando de manera sincrona y la apertura diferida del menu con un receptor de prueba; no certifica la ventana DeluxeMenus real, el proveedor economico remoto ni un cliente conectado. No instalar MerchantProbe.jar.',
              'Reproducir: `python -m unittest discover -s datapack-src -p "test*.py"`; `python tools/probar_mercader_paper.py --java <java25> --base <Paper-local>`; `python tools/verificar_terceros.py` despues de agregar rutas explicitas al indice.',
              'Instalacion, R2, consola remota, feedback auditivo y cliente visual pendientes. Sin bloqueos locales de implementacion; no se accedio al navegador ni se usaron APIs del servidor.', '']
    delivery=ROOT/f'build/deploy/{NAME}.md';delivery.write_text('\n'.join(lines),'utf8')
    pending=ROOT/'build/deploy/pendiente-17-11.md';text=pending.read_text('utf8')
    text=text.replace('## Mascotas, oceano y panorama (tanda actual)', '## Mascotas, oceano y panorama (entrega anterior)')
    text=text.replace('Unico FINAL para instalar: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/',
                      'FINAL anterior, sustituido por la ultima entrega de cascos: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/')
    marker='\n## Cascos, silencio y mercader (ultima entrega)\n'
    text=text.split(marker)[0]+marker+'\n'
    text+=f'Lista exacta y hashes: [{NAME}]({NAME}.md). Sustituye AstralDecor por 1.18.0, YAML de mobs y FINAL de 98156c2; conservar sus demas archivos y 054db88.\n'
    text+=f'Unico FINAL `{target.relative_to(ROOT).as_posix()}`; SHA-1 `{report["final_sha1"]}`. Requiere apagar/reiniciar por JAR y pack. Solo YAML: `mm reload`. R2, servidor y cliente pendientes de Claude; sin despliegue verificado.\n'
    pending.write_text(text,'utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='changed'},indent=2))
    return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--client',type=Path,required=True)
    generate(parser.parse_args().client)
