"""Entrega, FINAL por delta conservador y vistas CPU de los menus generados."""
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path
from PIL import Image,ImageDraw
import yaml
from terceros import ROOT,privado
from pack_audit import audit
from ventanas_1611 import WINDOWS
from services_ui import png

OUT=ROOT/'build/Servicios-preview/ventanas-16-11'
DELIVERY='build/entregas/mascotas-aurora-botones'

def read_zip(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}

def chars(provider):
    return set(provider.get('advances',{}))|set(''.join(provider.get('chars',[])))

def final():
    from final_base import select_base
    import companero_ui,mascotas_ui
    dest=privado()/DELIVERY;dest.mkdir(parents=True,exist_ok=True)
    base=select_base(output=dest)
    old=read_zip(base);files=dict(old)
    public=read_zip(ROOT/'build/AstralRPG-Textures.zip')
    previous=read_zip(io.BytesIO(subprocess.check_output(['git','show','f81ac2027409d9db46c9708e99ba6d40f82c7287:build/AstralRPG-Textures.zip'],cwd=ROOT)))
    delta={n:b for n,b in public.items() if b!=previous.get(n)}
    files.update(delta)
    # Mantener los glifos exclusivos de terceros y las incorporaciones de tareas anteriores.
    font=json.loads(public['assets/minecraft/font/default.json']);used=set()
    for p in font['providers']:used|=chars(p)
    for p in json.loads(old['assets/minecraft/font/default.json'])['providers']:
        if p['type']=='space':
            extra={c:v for c,v in p['advances'].items() if c not in used}
            if extra:font['providers'].append(dict(type='space',advances=extra))
        elif chars(p) and not chars(p)&used:font['providers'].append(p)
    files['assets/minecraft/font/default.json']=json.dumps(font,ensure_ascii=False).encode()
    for pid in mascotas_ui.ALL_PETS:
        if pid=='fenix':continue
        image=Image.open(privado()/f'arte/gemini/retrato_{pid}.png').convert('RGBA')
        mascotas_ui.CARD_ART[pid]=image;companero_ui.PORTRAITS[pid]=image
    detail,_=companero_ui.assets();pages,_=mascotas_ui.assets()
    private={n:b for n,b in {**detail,**pages}.items() if n.endswith('.png')}
    files.update(private)
    target=dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(zipfile.ZipInfo(n,(2026,11,16,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    allowed=set(delta)|set(private)|{'assets/minecraft/font/default.json'}
    assert all(files[n]==b for n,b in old.items() if n not in allowed)
    refs=audit(target);sha=hashlib.sha1(target.read_bytes()).hexdigest()
    report=dict(base=base.relative_to(ROOT).as_posix(),base_sha1=hashlib.sha1(base.read_bytes()).hexdigest(),final_sha1=sha,
                changed=sorted(n for n in files if files[n]!=old.get(n)),preserved=len(set(old)-allowed),references=refs)
    (dest/'delta.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');(dest/'pack.sha1').write_text(sha+'\n')
    print('FINAL privado',sha,'base',report['base'],'preservados',report['preserved'],flush=True)
    return report


def previews():
    # Solo el pack publico: nunca publicar vistas de los retratos licenciados.
    files=read_zip(ROOT/'build/AstralRPG-Textures.zip')
    font=json.loads(files['assets/minecraft/font/default.json']);glyph={};advances={}
    for provider in font['providers']:
        if provider['type']=='space':advances.update(provider['advances'])
        if provider['type']=='bitmap' and len(provider.get('chars',[]))==1 and len(provider['chars'][0])==1:
            ns,path=provider['file'].split(':',1);name=f'assets/{ns}/textures/{path}'
            if name in files:glyph.setdefault(provider['chars'][0],(name,provider['ascent']))
    def texture(model):
        try:
            ns,path=model.split(':',1);obj=json.loads(files[f'assets/{ns}/items/{path}.json'])['model']
            while obj.get('type')!='minecraft:model':
                obj=obj.get('fallback',obj.get('base',obj.get('model',{})))
                if not obj:return None,None
            ns,path=obj['model'].split(':',1);obj=json.loads(files[f'assets/{ns}/models/{path}.json'])
            tex=obj.get('textures',{});resource=tex.get('layer0',tex.get('all',tex.get('particle','')))
            ns,path=resource.split(':',1);name=f'assets/{ns}/textures/{path}.png'
            return Image.open(io.BytesIO(files[name])).convert('RGBA'),name
        except (KeyError,ValueError,TypeError):return None,None
    OUT.mkdir(parents=True,exist_ok=True);table=[]
    for path in sorted((ROOT/'build/menus/DeluxeMenus/gui_menus').glob('*.yml')):
        data=yaml.safe_load(path.read_text(encoding='utf8'));rows=data['size']//9
        im=Image.new('RGBA',(540,540),'#252832');ox,oy=150,190
        x=ox+32;drawn=False
        title=re.sub(r'&[0-9a-fklmnor]','',data.get('menu_title',''),flags=re.I)
        for char in title:
            if char in advances:x+=advances[char]
            elif char in glyph:
                name,ascent=glyph[char];tile=Image.open(io.BytesIO(files[name])).convert('RGBA')
                im.alpha_composite(tile,(x,oy+54-ascent));x+=tile.getbbox()[2]+1;drawn=True
        d=ImageDraw.Draw(im)
        if not drawn:
            d.rectangle((ox+24,oy+40,ox+200,oy+rows*18+161),fill='#222932',outline='#b9a573')
            d.text((ox+30,oy+43),path.stem,fill='white')
        chosen={}
        for key,item in data.get('items',{}).items():
            if key.endswith('_activo') and key!='efectos_medio_activo':continue
            slots=item.get('slots',[item.get('slot')])
            for slot in slots:
                if not isinstance(slot,int):continue
                if slot not in chosen or int(item.get('priority',999))<int(chosen[slot][1].get('priority',999)):chosen[slot]=(key,item)
            if any(k.endswith('commands') for k in item):
                _,name=texture(item.get('item_model',''))
                source=name or item.get('item_model','SIN MODELO')
                if name and '/provisorias/boton_' in name:source='datapack-src/pack-source/provisorias/'+Path(name).name
                if name and '/item/'+name.split('/item/',1)[-1].split('/')[0] in name and '/nav_' in name:
                    family='mascotas' if '/mascotas/' in name else 'cosmeticos';source=f'datapack-src/pack-source/provisorias/navegacion/{family}_{Path(name).name}'
                provisional=('navegacion/' in source or '/provisorias/' in source and Path(source).name.removeprefix('boton_').removesuffix('.png') not in {k for v in __import__('ventanas_1611').SHEETS.values() for k in v}|{'talador_set','efectos_bajo_activo','efectos_medio_activo','efectos_alto_activo'})
                table.append((path.stem,key,str(item.get('slot',item.get('slots',''))),source,'provisorio' if provisional else 'final/existente'))
        for slot,(key,item) in chosen.items():
            tile,_=texture(item.get('item_model',''));x=ox+31+slot%9*18;y=oy+57+slot//9*18
            if tile is not None:
                tile.thumbnail((18,18),Image.Resampling.LANCZOS);im.alpha_composite(tile,(x+(18-tile.width)//2,y+(18-tile.height)//2))
            elif any(k.endswith('commands') for k in item):
                d.rectangle((x+2,y+2,x+14,y+14),fill='#7a739b');d.text((x+3,y+3),'?',fill='#ffe8a3')
        # Inventario vacio, alineado a las casillas reales.
        end=oy+57+rows*18
        for r in (*range(3),4):
            for c in range(9):
                x=ox+31+c*18;y=end+14+(r*18 if r<3 else 58)
                d.rectangle((x,y,x+15,y+15),outline='#756c6c')
        im=im.crop((45,90,405,min(540,end+120))).convert('RGB')
        target=OUT/f'{path.stem}.png'
        temporary=target.with_suffix('.png.tmp')
        temporary.write_bytes(png(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)))
        temporary.replace(target)
    from travel_ui import previews as travel_previews
    from services_ui import previews as services_previews
    for obsolete in ('skript_minas','skript_minas_venta'):(OUT/f'{obsolete}.png').unlink(missing_ok=True)
    travel_previews(OUT,kinds=('minas','minas-venta'))
    services_previews(OUT)
    for window in ('herrero','venta'):
        im=Image.open(OUT/f'{window}.png').convert('RGBA')
        from menu_ui import icon as menu_icon
        for slot,key in ((45,'back'),(53,'close')):
            tile=menu_icon(key).resize((54,54),Image.Resampling.NEAREST)
            im.alpha_composite(tile,((31+slot%9*18)*3,(57+slot//9*18)*3))
            table.append((window,key,str(slot),'datapack-src/pack-source/ref/gemini/boton_'+key+'.png','final/existente'))
        im.save(OUT/f'{window}.png')
    im=Image.new('RGBA',(224,280),'#252832');d=ImageDraw.Draw(im)
    d.text((30,40),'DESAFIAR A UN JUGADOR',fill='#eee3be')
    for slot in range(54):
        x,y=31+18*(slot%9),57+18*(slot//9);d.rectangle((x,y,x+16,y+16),outline='#5d626b')
    for slot,key in ((45,'back'),(53,'close')):
        im.alpha_composite(menu_icon(key),(31+slot%9*18,57+slot//9*18))
        table.append(('desafiar',key,str(slot),'datapack-src/pack-source/ref/gemini/boton_'+key+'.png','final/existente'))
    d.text((48,100),'Cabezas de jugadores conectados',fill='#d5c58e')
    im.resize((672,840),Image.Resampling.NEAREST).save(OUT/'desafiar.png')
    for family,window,slot in (('cosmeticos','cosmeticos',49),('cosmeticos','cosmeticos_titulos',8),('cosmeticos','cosmeticos_sombreros',53),('mascotas','mascotas',8)):
        table.append((window,'nav_gacha',str(slot),f'datapack-src/pack-source/provisorias/navegacion/{family}_nav_gacha.png','provisorio'))
    for i in range(5):table.append(('mascotas / mascotas_2 / mascotas_3',f'rest_{i}',str(47+i),f'datapack-src/pack-source/provisorias/navegacion/mascotas_rest_{i}.png','provisorio'))
    table += [
      ('minas','viajar','10-15 / 19-25 / 28-34','astral:viajes/mine_<indice>_<estado>','final/existente'),
      ('minas','bosque','47','datapack-src/pack-source/ref/gemini/menu_bosque.png','final/existente'),
      ('minas','spawn','49','astral:menu/icon_spawn','final/existente'),
      ('minas','cerrar','53','astral:viajes/cerrar','final/existente'),
      ('minas-venta','vender','28-34','assets/astral/textures/font/viajes/minas-venta_*.png (boton en fondo)','final/existente'),
      ('minas-venta','cerrar','35','assets/astral/textures/font/viajes/minas-venta_*.png (boton en fondo)','final/existente'),
      ('herrero','mejorar','39-41','astral:servicios/improve_0..2 (variantes blocked/fail)','final/existente'),
      ('herrero','reparar','47','minecraft:anvil (estado y precio dinamicos)','final/existente'),
      ('venta','vender','41-44','astral:servicios/sell_0..3 (variante bloqueada)','final/existente'),
      ('desafiar','jugador','0-44','minecraft:player_head (perfil del jugador)','final/existente'),
    ]
    text='| Ventana | Boton | Slot | Ruta PNG/modelo | Estado |\n|---|---|---|---|---|\n'
    text+=''.join('| '+' | '.join(row)+' |\n' for row in table)
    (OUT/'botones.md').write_text(text,encoding='utf8')
    print('Vistas',len(list(OUT.glob('*.png'))),'botones',len(table),flush=True)
    return table

def delivery(report,verification):
    base='f81ac2027409d9db46c9708e99ba6d40f82c7287'
    paths=subprocess.check_output(['git','diff',base,'--name-only','--','build/menus/DeluxeMenus','build/lobby/CrazyCrates/crates','build/mythicmobs','build/services','build/duelos'],cwd=ROOT,text=True).splitlines()
    paths += ['build/AstralRPG-Items.zip','build/oceano/AstralOceano.jar','build/mascotas/astral_mascotas_retiro.sk']
    def remote(path):
        if path.startswith('build/menus/DeluxeMenus/gui_menus/'):return path.replace('build/menus/','plugins/',1)
        if path.startswith('build/lobby/CrazyCrates/'):return path.replace('build/lobby/','plugins/',1)
        if path.startswith('build/mythicmobs/'):return path.replace('build/mythicmobs/','plugins/MythicMobs/',1)
        if path.endswith('.sk'):return 'plugins/Skript/scripts/'+Path(path).name
        return {'build/AstralRPG-Items.zip':'world/datapacks/AstralRPG-Items.zip','build/oceano/AstralOceano.jar':'plugins/AstralOceano.jar'}.get(path)
    manifest=[]
    for path in sorted(set(paths)):
        dest=remote(path)
        if dest and (ROOT/path).is_file():manifest.append(dict(local=path,destino=dest,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
    out=ROOT/'build/deploy';out.mkdir(exist_ok=True)
    (out/'mascotas-aurora-botones-archivos.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    text=['# Mascotas, Aurora y botones - 16/11/2026','',
      'Implementado y preparado; sin despliegue remoto. GitHub publica codigo y salidas propias, no instala el servidor.',
      '', '## Resultado','',
      '- Retiradas lobo, zorro espectral, golem de piedra, cuervo y dragon. Se mantienen Fenix y las 17 cubee: tres paginas de seis, sin huecos. IDs 6-23, permisos, XP y niveles conservados. Los .bbmodel originales quedan archivados.',
      '- Se eliminaron sus invocaciones, drops de mobs/cofres, detalles, paginas obsoletas, guia y premios normales/con suerte/con garantia. Rarezas totales y garantia cada 40 tiradas conservadas.',
      '- Al entrar, cada permiso retirado da una llave virtual normal de Monturas y un mensaje. Marcador persistente por UUID y mascota en Skript; no borrar variables ni repetir pagos manualmente. Se limpia la seleccion 1-5 y se eliminan solo entidades con tags de mascotas retiradas en el mundo del jugador. Las llaves se usan con `/crates mass-open gacha_monturas virtual 1` (permiso existente `crazycrates.massopen`); no son una compra y no usan Suerte.',
      '- AstralOceano 1.4.0 elimina la tarea Java que invocaba Aurora y su definicion MythicMobs. Era decorativa: no tenia dialogo ni tienda que migrar; el aviso conserva las advertencias del Oceano.',
      '- Seis marcos Gemini finales: configuraciones (3 filas), renacer (6), deseo (6), deseo_lite (6), oficios (4), oceano_aviso (3). Botones de hojas 36 conservan item_model; nivel activo con borde dorado, deseos espaciados, texto oscuro sobre pergamino, precio real de sets en nombre/lore, ayuda de Oficios sin choque, Entrar preparado y Volver.',
      '- Navegacion de mascotas y cosmeticos: PNG 18x18 con trama y marca P, provisoria. Se revisaron tambien Minas, venta, portales, viajes, Infinita, servicios y Duelos; Herrero/Venta y Duelos reciben modelos para volver/cerrar. Las cabezas de jugadores y objetos depositados son su icono real. Botones anchos dibujados en el fondo mantienen sus zonas de clic.',
      '', '## Arte y vistas','',
      'Vistas CPU por ventana: `build/Servicios-preview/ventanas-16-11/`. La galeria publica muestra reservas propias donde hay arte licenciado; no es una captura de Minecraft ni una prueba de interaccion humana.',
      'Tabla completa ventana -> boton -> slot -> PNG/modelo -> estado: [botones.md](../Servicios-preview/ventanas-16-11/botones.md). Los modelos compuestos y los botones dibujados en un fondo se identifican por su recurso del pack; las reservas reemplazables tienen ruta fuente explicita.',
      'Arte final propio: `datapack-src/pack-source/ref/ventanas-1611/*.png` y los `boton_*.png` de hojas 36 en `pack-source/provisorias/` (nombre historico de carpeta). No se rehizo arte final. Reservas pendientes del dueno: `pack-source/provisorias/navegacion/{cosmeticos,mascotas}_nav_{gacha,back,close,info,next}.png` y `mascotas_rest_0.png` a `mascotas_rest_4.png`. Cada tile mide 18x18; el boton Descansar se compone de cinco tiles.',
      '', '## Archivos y destinos','',
      'La documentacion identifica Empower como principal y Aternos como copia. Claude debe verificar el panel y la base realmente instalada. Instalar despues de las tandas XP, balance/agua y Crop & Kettle; no mezclar sus versiones. Manifest exacto con SHA-256: [archivos.json](mascotas-aurora-botones-archivos.json).',
      '| Archivo local | Destino |','|---|---|']
    text += [f"| `{m['local']}` | `{m['destino']}` |" for m in manifest]
    text += ['', 'En `plugins/DeluxeMenus/config.yml`, actualizar solo la seccion gui_menus con `build/menus/DeluxeMenus/config-gui_menus.yml`, conservando otras opciones/menus del servidor. Retirar los registros y archivos `mascota_lobo.yml`, `mascota_zorro.yml`, `mascota_golem.yml`, `mascota_cuervo.yml`, `mascota_dragon.yml` y `mascotas_4.yml`. No borrar otros archivos de mascotas.',
      '', '## FINAL privado y condiciones de despliegue','',
      f"FINAL: `.local/terceros/AstralRPG-privado/{DELIVERY}/AstralRPG-Textures.zip`. SHA-1 **`{report['final_sha1']}`**.",
      f"Base conservada: `{report['base']}`; SHA-1 `{report['base_sha1']}`; {report['preserved']} entradas de base intactas fuera del delta. No instalar `build/AstralRPG-Textures.zip`, que es publico y carece del arte privado.",
      'Este FINAL conserva Crop & Kettle. Su permiso de distribucion publica sigue pendiente segun [crop-kettle.md](crop-kettle.md): no publicar en R2 hasta resolver esa condicion. Si el pack instalado difiere de esta base, recombinar sobre la base correcta antes de instalar; no perder sus entradas.',
      'Una vez resuelto: apagar desde el panel, respaldar solo archivos a reemplazar, instalar JAR/datapack/configs/menus/Skript. Conservar `plugins/AstralOceano/config.yml` (fecha de regeneracion y ajustes) y las variables de Skript. No reemplazar mundos, regiones ni usar Worlds > Upload en world.',
      'Para el pack, solo despues de resolver distribucion: `python tools/subir_pack_r2.py "'+'.local/terceros/AstralRPG-privado/'+DELIVERY+'/AstralRPG-Textures.zip"`. Verificar descarga publica, actualizar resource-pack-sha1 en server.properties y conservar la URL fija. Reinicio completo con Java 25 obligatorio.',
      '', '## Limpieza limitada y consola','',
      'Con la entrada de la Fosa cargada, borrar la Aurora existente solo en el Oceano (comando de consola, sin /):','```text',
      'execute in minecraft:oceano run minecraft:kill @e[tag=oceano.aurora,distance=0..]',
      '```',
      'El selector distance=0.. limita la seleccion a esa dimension. Si la entidad estaba en un chunk descargado, visitar la entrada y repetir. No usar mm mobs killall. El modelo BetterModel privado puede permanecer archivado; el nuevo runtime nunca lo invoca.',
      'El reinicio carga todo. Para recargas posteriores de solo configuracion: `crates reload`, `mm reload`, `dm reload`, `skript:skript reload astral_mascotas_retiro`, `skript:skript reload astral_servicios`, `skript:skript reload astral_duelos`. No usar /reload de Bukkit. El JAR requiere reinicio.',
      'Revisar consola: AstralOceano 1.4.0 habilitado, sin errores de Skript/MythicMobs/DeluxeMenus, sin PET_GANAR de retiradas, sin nuevas Aurora. Entrar con jugador elegible, comprobar llave/mensaje una vez, Fenix y bonus; abrir las seis ventanas con el pack nuevo.',
      '', '## Verificaciones','', verification,
      'Ensayo Paper 26.1.2 / Java 25: dos arranques, RET RESULT failures=0 en ambos. Skript real: dos llaves iniciales, cinco totales, sin duplicado al reingresar ni tras reinicio, seleccion retirada limpiada, entidad retirada eliminada, XP/permiso Fenix intactos. CrazyCrates se representa con un doble que verifica el comando exacto; falta probar la animacion real con cliente.',
      'Compilacion AstralOceano 1.4.0 OK. Auditoria de referencias de pack y conservacion byte por byte del FINAL anterior. Logs y FINAL quedan privados.',
      '', '## Reproduccion','', 'Desde datapack-src: `python build.py`, `python mobs/mascotas.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`, `python lobby.py`, `python duelos.py`, `python menus.py`, `python oceano_fosa.py`, `python oceano.py --java <java25> --base ../.local/testsrv`, `python build_pack.py pack-source`. Luego `python deploy_mascotas_aurora_botones.py`. La importacion de originales Gemini (`ventanas_1611.py --import-art`) es explicita y solo se necesita para actualizar el arte fuente; compilar usa los PNG versionados.',
      'Pruebas: `python -m unittest discover -s datapack-src -p test*.py`; `python tools/probar_retiro_1611_paper.py --java <java25> --base .local/testsrv --work .local/retiro-1611-ensayo-nuevo`. No instalar RetiroProbe.jar en remoto.',
      '', '## Pendientes','',
      'Despliegue remoto, permiso de distribucion heredado de Crop & Kettle, R2, comprobacion de base instalada y revision con cliente real. Navegacion marcada P pendiente de arte final del dueno. No se afirmo instalacion en Aternos ni Empower.']
    (out/'mascotas-aurora-botones.md').write_text('\n'.join(text)+'\n',encoding='utf8')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--verificacion',default='Suite final pendiente de registrar.');a=p.parse_args()
    previews();delivery(final(),a.verificacion)
