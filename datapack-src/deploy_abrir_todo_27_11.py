"""Entrega aislada; conserva FINAL Bazar y AstralDecor 1.24.8 byte por byte fuera del delta."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

import guia_cofre as g
from guia_ampliacion import extend_source
from deploy_guia_stellarity import head, zip_write
from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/abrir-todo-27-11'
PRIVATE = privado() / 'build/entregas/abrir-todo-27-11'
BASE_PACK = privado() / 'build/entregas/bazar-categorias-27-11/AstralRPG-Textures.zip'
BASE_DECOR = ROOT / 'build/mochilas-ender/AstralDecor.jar'


def sha(path, algorithm='sha1'):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def guide():
    source = extend_source(json.loads(head('build/runtime/guia_fuente.json')))
    menus = g.menus(source)
    folder = OUT / 'gui_menus'
    folder.mkdir(parents=True, exist_ok=True)
    # Ship all guide pages together, including their navigation; no shared build overwritten.
    for name, body in menus.items():
        (folder / (name + '.yml')).write_text(body, encoding='utf8')
    (OUT / 'config-guia.yml').write_text('# Fusionar bajo gui_menus, conservando otros menus.\n' +
        ''.join(f'  {n}:\n    file: {n}.yml\n' for n in menus), encoding='utf8')
    removed = ['g_atlas_seccion_crafteos', 'g_guia_drops', 'guia_astral_3_publica', 'g_atlas_seccion_cocina_publica']
    (OUT / 'retirar-registros.txt').write_text('\n'.join(removed)+'\n', encoding='utf8')
    assert not set(removed) & menus.keys()
    for body in menus.values():
        assert 'open_requirement:' not in body
        for target in re.findall(r'\[openguimenu\] ([a-z0-9_]+)', body):
            assert target in menus, target
    files, providers = g.assets(source)
    files = {n:b for n,b in files.items() if n.startswith('assets/astral/textures/font/guia_astral/')}
    assert sha(BASE_PACK) == '5abd02f93162204a320123d2d0bc233a399d648c', 'FINAL base incorrecto'
    with zipfile.ZipFile(BASE_PACK) as z:
        base = {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    font_path = 'assets/minecraft/font/default.json'
    font = json.loads(base[font_path])
    chars = {c for p in providers for line in p.get('chars', []) for c in line} | {c for p in providers for c in p.get('advances', {})}
    kept = []
    for p in font['providers']:
        if p.get('file','').startswith('astral:font/guia_astral/'):
            continue
        if p['type'] == 'space':
            advances = {c:v for c,v in p['advances'].items() if c not in chars}
            if advances: kept.append(dict(type='space', advances=advances))
        else:
            assert not chars & {c for line in p.get('chars',[]) for c in line}, p
            kept.append(p)
    font['providers'] = providers + kept
    files[font_path] = json.dumps(font,ensure_ascii=False).encode('utf8')
    final = dict(base, **files)
    assert all(final[n] == b for n,b in base.items() if n not in files)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    dest = PRIVATE/'AstralRPG-Textures.zip'
    zip_write(dest, final)
    zip_write(OUT/'GuiaAstral-Assets.zip', files)
    preview = ROOT/'build/previews/abrir-todo-27-11'
    preview.mkdir(parents=True,exist_ok=True)
    from PIL import Image
    g.index_panel(g.pages(g.entries(source))[2], 2, 3).convert('RGB').save(preview/'guia_astral_3.png')
    return dict(base_pack=BASE_PACK.relative_to(ROOT).as_posix(),base_sha1=sha(BASE_PACK),
                final=dest.relative_to(ROOT).as_posix(),final_sha1=sha(dest),menus=sorted(menus),retirar=removed,
                pack_delta=sorted(n for n in files if base.get(n)!=files[n]))


def mounts(java, server, base):
    assert sha(base) == 'd2db96739b1695d3ec5db91a2ae95ea75dcc7859', 'Se requiere la base verificada AstralDecor 1.24.8'
    classes = Path(tempfile.mkdtemp(prefix='abrir-monturas-',dir=ROOT/'.local'))
    deps = [*server.joinpath('libraries').rglob('*.jar'),server/'plugins/mythicmobs.jar',server/'plugins/bettermodel.jar']
    subprocess.run([str(java),'-m','jdk.compiler/com.sun.tools.javac.Main','-encoding','UTF-8',
        '-classpath',os.pathsep.join(map(str,deps)),'-d',str(classes),str(ROOT/'datapack-src/runtime/AstralMounts.java')],check=True)
    with zipfile.ZipFile(base) as z:
        original = {n:z.read(n) for n in z.namelist()}
    assert b'version: 1.24.8' in original['plugin.yml']
    files = {n:b for n,b in original.items() if not n.startswith('astral/AstralMounts')}
    files['plugin.yml'] = files['plugin.yml'].replace(b'version: 1.24.8',b'version: 1.24.9')
    files.update({'astral/'+p.name:p.read_bytes() for p in (classes/'astral').glob('AstralMounts*.class')})
    changed = sorted(n for n in original.keys()|files.keys() if original.get(n)!=files.get(n))
    assert all(n=='plugin.yml' or n.startswith('astral/AstralMounts') for n in changed)
    jar = OUT/'AstralDecor.jar'
    zip_write(jar,files)
    return dict(decor_base=base.relative_to(ROOT).as_posix(),decor_base_sha1=sha(base),decor_sha256=sha(jar,'sha256'),decor_delta=changed)


def product_items():
    # Read current generators only in memory; keep the published economic references,
    # equipment catalog and the categories from the preceding task.
    import bazar
    ns = bazar.fuentes()
    path = ROOT/'build/bazar/productos.yml'
    data = json.loads(path.read_text(encoding='utf8'))
    for iid,p in data['productos'].items():
        it = ns['ITEMS'][iid]
        p['item'] = it['base']+'['+','.join(k+'='+(v if k=='minecraft:custom_data' else ns['snbt'](v)) for k,v in it['components'].items())+']'
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    config = ROOT/'build/bazar/config.yml'
    cfg = json.loads(config.read_text(encoding='utf8'))
    cfg['limites-dinamicos'] = dict(activo=True,hora='05:10',**{'tope-maximo':3})
    config.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def tooltips():
    from PIL import Image, ImageDraw, ImageFont
    from stellarity_tiers import rows
    preview=ROOT/'build/previews/abrir-todo-27-11'
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',17)
    colors={'gray':'#aaaaaa','red':'#ff5555','green':'#55ff55','gold':'#ffaa00','white':'#ffffff','dark_purple':'#aa00aa','yellow':'#ffff55'}
    for key in ('dragonblade','shulker_chestplate'):
        row=rows()[key]; lines=[row['item_name']]+row['ficha']
        im=Image.new('RGB',(760,32+len(lines)*24),'#160d22');d=ImageDraw.Draw(im)
        for n,line in enumerate(lines):
            x=12
            for part in [line]+line.get('extra',[]):
                text=part['text'].replace('$ATTACK_SPEED','1')
                color=colors.get(part.get('color'),part.get('color','#aaaaaa'))
                d.text((x,10+n*24),text,font=font,fill=color);x+=d.textlength(text,font=font)
        im.save(preview/(key+'.png'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java',required=True,type=Path)
    p.add_argument('--server',type=Path,default=ROOT/'.local/testsrv')
    p.add_argument('--base-decor',type=Path,default=BASE_DECOR)
    a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    manifest=guide();manifest.update(mounts(a.java.resolve(),a.server.resolve(),a.base_decor.resolve()))
    product_items();tooltips()
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('FINAL SHA-1:',manifest['final_sha1'])
