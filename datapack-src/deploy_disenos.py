"""Entrega aislada sobre el FINAL ad66e73 instalado; sin red ni despliegue."""
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from terceros import ROOT, privado
from services_ui import png
from pack_audit import audit

BASE_SHA='ad66e732862b13f8042c3b7e0e93844839d55607'
PUBLIC_BASE='a1fe4f2a960396a720728edfcfd9a891c693597d'
DELIVERY='build/entregas/disenos-pendientes'


def read_zip(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}


def preview_pair(before, after, path):
    """Vistas CPU; no se presentan como capturas de Minecraft."""
    width=max(before.width,after.width);height=max(before.height,after.height)
    im=Image.new('RGBA',(width*2,height+20),'#18232b')
    im.alpha_composite(before,(0,20));im.alpha_composite(after,(width,20))
    d=ImageDraw.Draw(im);d.text((4,4),'ANTES - render CPU',fill='white');d.text((width+4,4),'DESPUES - render CPU',fill='white')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(png(im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)))


def render_menu(files,data,model_icons=None):
    """Componer glifos y sprites reales del pack. Reservas vanilla con su inicial;
    las condiciones se muestran en el primer estado (sin ejecutar permisos)."""
    font=json.loads(files['assets/minecraft/font/default.json']);adv={};glyphs={}
    for p in reversed(font['providers']):
        if p['type']=='space':adv.update(p['advances'])
        if (p['type']=='bitmap' and len(p.get('chars',[]))==1 and len(p['chars'][0])==1
                and p['chars'][0] in data['menu_title'] and p.get('height',0)>0):
            ns,rel=p['file'].split(':');name=f'assets/{ns}/textures/{rel}'
            if name in files:
                im=Image.open(io.BytesIO(files[name])).convert('RGBA')
                if im.height!=p['height']:im=im.resize((max(1,round(im.width*p['height']/im.height)),p['height']),Image.Resampling.NEAREST)
                glyphs[p['chars'][0]]=(im,p['ascent'])
    x=0;parts=[]
    for char in data['menu_title']:
        if char in adv:x+=adv[char]
        elif char in glyphs:
            im,ascent=glyphs[char];parts.append((im,x,-ascent));x+=im.getbbox()[2]+1
    if parts:
        left=min(x for _,x,_ in parts);top=min(y for _,_,y in parts)
        width=max(x+im.width for im,x,_ in parts)-left;height=max(y+im.height for im,_,y in parts)-top
        canvas=Image.new('RGBA',(width,height),'#20252b')
        for im,x,y in parts:canvas.alpha_composite(im,(x-left,y-top))
        sx,sy=-1-left,4-top  # slot 0: x=31, y=57 sobre marco de 224px.
    else:
        canvas=Image.new('RGBA',(224,280),'#29272b');sx,sy=31,57
        ImageDraw.Draw(canvas).text((28,25),data['menu_title'].replace('&8',''),fill='white')
    occupied=set();draw=ImageDraw.Draw(canvas)
    for key,item in data['items'].items():
        slots=item.get('slots',[item.get('slot')]);slots=[slots] if isinstance(slots,int) else slots
        for slot in slots:
            if not isinstance(slot,int) or slot in occupied:continue
            occupied.add(slot);xy=(sx+slot%9*18,sy+slot//9*18)
            ref=item.get('item_model','');sprite=None
            if ref in (model_icons or {}):
                art=ImageOps.contain(model_icons[ref],(18,18),Image.Resampling.LANCZOS)
                sprite=Image.new('RGBA',(18,18));sprite.alpha_composite(art,((18-art.width)//2,(18-art.height)//2))
            if ':' in ref:
                ns,rel=ref.split(':',1);definition=f'assets/{ns}/items/{rel}.json'
                if definition in files:
                    tree=json.loads(files[definition]).get('model',{});model=tree.get('model')
                    if isinstance(model,str) and ':' in model:
                        ns,rel=model.split(':',1);mp=f'assets/{ns}/models/{rel}.json'
                        if mp in files:
                            layer=json.loads(files[mp]).get('textures',{}).get('layer0','')
                            if ':' in layer:
                                ns,rel=layer.split(':',1);tp=f'assets/{ns}/textures/{rel}.png'
                                if tp in files and sprite is None:sprite=Image.open(io.BytesIO(files[tp])).convert('RGBA').resize((18,18),Image.Resampling.NEAREST)
            if sprite:canvas.alpha_composite(sprite,xy)
            elif item.get('material') not in ('AIR','PAPER'):
                draw.rectangle((*xy,xy[0]+16,xy[1]+16),outline='#a28b62')
                draw.text((xy[0]+4,xy[1]+3),item['material'][0],fill='#dfcf9f')
    return canvas


def prepare():
    import companero_ui as companion
    import menu_ui
    from build_privado import preview
    from mobs.mascotas import MASCOTAS
    base=privado()/'build/entregas/tren-lobby/AstralRPG-Textures.zip'
    if hashlib.sha1(base.read_bytes()).hexdigest()!=BASE_SHA:raise ValueError('Base instalada diferente: no combinar')
    original=read_zip(base);files=dict(original)
    public=read_zip(ROOT/'build/AstralRPG-Textures.zip')
    previous=read_zip(io.BytesIO(subprocess.check_output(['git','show',PUBLIC_BASE+':build/AstralRPG-Textures.zip'],cwd=ROOT)))
    for name,blob in public.items():
        if blob!=previous.get(name) and name!='assets/minecraft/font/default.json':files[name]=blob
    # Regenerar los retratos con los modelos privados ya adaptados. Nunca reexportar
    # los originales ni mezclar el build global con la entrega instalada.
    models={p.stem:json.loads(p.read_text(encoding='utf8'))
            for p in (privado()/'build/models').glob('astral_pet_*.bbmodel')}
    if len(models)!=17:raise ValueError('Se requieren los 17 modelos privados')
    companion.PORTRAITS.update(preview(models,name='disenos-retratos',include_sword=False,gui=True))
    private_files,providers=companion.assets()
    files.update(private_files)
    # El publico ya incluye los glifos nuevos; conservar proveedores privados ajenos.
    font=json.loads(public['assets/minecraft/font/default.json'])
    oldfont=json.loads(original['assets/minecraft/font/default.json'])
    used=set()
    def chars(p):return set(p.get('advances',{}))|set(''.join(p.get('chars',[])))
    for p in font['providers']:used.update(chars(p))
    for p in oldfont['providers']:
        if chars(p) and not chars(p)&used:font['providers'].append(p)
    files['assets/minecraft/font/default.json']=json.dumps(font,ensure_ascii=False).encode()
    # Mantener los IDs fisicos como recuerdos vanilla; retirar las geometrías
    # exclusivas de alas, sin eliminar texturas compartidas con armas del set.
    for iid in ('asura_alas','carnivora_alas'):
        files[f'assets/astral/items/{iid}.json']=json.dumps({'model':{'type':'minecraft:model','model':'minecraft:item/feather'}}).encode()
    candidates={n for n in files if ('/cosmetics/' in n and '_alas' in n) or
                n in ('assets/asura/models/asura_wings.json','assets/elitecreatures/models/carnivoret_weapon_set/wing.json') or
                n.startswith(('assets/astral/equipment/asura_alas.','assets/astral/equipment/carnivora_alas.'))}
    # Buscar descendientes de modelos/texturas de esas raíces.
    pending=list(candidates)
    while pending:
        name=pending.pop()
        if not name.endswith('.json'):continue
        data=json.loads(files[name])
        refs=list(data.get('textures',{}).values())
        if isinstance(data.get('parent'),str):refs.append(data['parent'])
        for ref in refs:
            if not isinstance(ref,str) or ':' not in ref:continue
            ns,rel=ref.split(':',1)
            for typ,ext in (('textures','png'),('models','json')):
                child=f'assets/{ns}/{typ}/{rel}.{ext}'
                if child in files and child not in candidates:candidates.add(child);pending.append(child)
    for name in sorted(candidates):
        # Conservar un candidato si cualquier JSON externo todavía lo referencia.
        ns,typ,rel=name.split('/',3)[1:]
        ref=ns+':'+rel.rsplit('.',1)[0]
        if any(ref in blob.decode('utf8',errors='ignore') for other,blob in files.items() if other.endswith('.json') and other not in candidates):continue
        files.pop(name,None)
    dest=privado()/DELIVERY;dest.mkdir(parents=True,exist_ok=True)
    target=dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,blob in sorted(files.items()):z.writestr(zipfile.ZipInfo(name,(2026,11,12,0,0,0)),blob,compress_type=zipfile.ZIP_DEFLATED)
    refs=audit(target);sha=hashlib.sha1(target.read_bytes()).hexdigest()
    (dest/'pack.sha1').write_text(sha+'\n')
    changed=sorted(n for n in files if files[n]!=original.get(n));removed=sorted(set(original)-set(files))
    (dest/'procedencia.json').write_text(json.dumps(dict(base_sha1=BASE_SHA,final_sha1=sha,changed=changed,removed=removed,references=refs),indent=2),encoding='utf8')
    previews=dest/'previews';previews.mkdir(exist_ok=True)
    # Iconos de los 20 sombreros desde los modelos del FINAL, siempre privados.
    from preview_tanda4b import java_model
    from cosmeticos_catalogo import HATS
    import tempfile
    hat_models={};hat_images={}
    with tempfile.TemporaryDirectory(dir=dest) as tmp:
        assets=Path(tmp)/'assets'
        for name,blob in files.items():
            if name.startswith(('assets/astral_cosmeticos/','assets/elitecreatures/')):
                path=Path(tmp)/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
        for key,*_ in HATS:
            ref=json.loads(files[f'assets/astral/items/cosmeticos/sombrero_{key}.json'])['model']['model']
            data=java_model(ref,assets)
            ns,rel=ref.split(':');raw=json.loads(files[f'assets/{ns}/models/{rel}.json'])
            data['outliner'][0].update(origin=[8,8,8],rotation=raw.get('display',{}).get('gui',{}).get('rotation',[0,0,0]))
            hat_models['astral:cosmeticos/sombrero_'+key]=data
        preview(hat_models,name='disenos-gorros',include_sword=False,gui=True,collect=hat_images)
    # Todos los detalles nuevos: el antes es la grilla y datos YAML anteriores,
    # el despues usa las mismas funciones que crean el font del FINAL.
    import yaml
    for pid,d in MASCOTAS.items():
        if d['n']<=6:continue
        old=yaml.safe_load(subprocess.check_output(['git','show',f'{PUBLIC_BASE}:build/menus/DeluxeMenus/gui_menus/mascota_{pid}.yml'],cwd=ROOT))
        before=Image.new('RGBA',companion.SIZE,'#25252b');draw=ImageDraw.Draw(before)
        draw.text((20,20),d['nombre'],fill='white')
        for entry in old['items'].values():
            slot=entry['slot'];x,y=companion.slot_xy(slot)
            draw.rectangle((x,y,x+17,y+17),outline='#888888')
        draw.text((25,50),'Titulo de texto / grilla anterior',fill='#aaaaaa')
        companion.preview(previews,pid,12,13)
        after=Image.open(previews/f'mascota-{pid}.png').convert('RGBA')
        after=after.resize((after.width//3,after.height//3),Image.Resampling.NEAREST)
        preview_pair(before,after,previews/f'mascota-{pid}-antes-despues.png')
    own=ROOT/'build/previews/disenos';own.mkdir(parents=True,exist_ok=True)
    # Principal antes/despues con los iconos exactos del pack anterior.
    before=menu_ui.panel();after=menu_ui.panel()
    for key,slot in zip(menu_ui.KEYS,menu_ui.SLOTS):
        xy=(31+slot%9*18,57+slot//9*18)
        before.alpha_composite(Image.open(io.BytesIO(previous[f'assets/astral/textures/item/menu/icon_{key}.png'])).convert('RGBA'),xy)
        after.alpha_composite(menu_ui.icon(key),xy)
    preview_pair(before,after,own/'principal-antes-despues.png')
    from cosmeticos_ui import previews as cosmetics_previews
    cosmetics_previews(own)
    from gorros_ui import panel as hat_panel
    obsolete=own/'gorros-marco-antes-despues.png'
    if obsolete.exists():obsolete.unlink()
    (own/'gorros-marco.png').write_bytes(png(hat_panel().resize((672,840),Image.Resampling.NEAREST)))
    count=len(menu_ui.KEYS)+len(menu_ui.EXTRA_KEYS)
    sheet=Image.new('RGBA',(400,58*((count+3)//4)),'#18232b');draw=ImageDraw.Draw(sheet)
    for i,key in enumerate((*menu_ui.KEYS,*menu_ui.EXTRA_KEYS)):
        x,y=i%4*100,i//4*58
        sheet.alpha_composite(menu_ui.icon(key).resize((36,36),Image.Resampling.NEAREST),(x+32,y))
        draw.text((x+2,y+39),key,fill='#e3c88e')
    (own/'iconos.png').write_bytes(png(sheet.resize((800,sheet.height*2),Image.Resampling.NEAREST)))
    # Inventario completo de botones, incluidos materiales de reserva intencionales.
    rows=[]
    for path in sorted((ROOT/'build/menus/DeluxeMenus/gui_menus').glob('*.yml')):
        data=yaml.safe_load(path.read_text(encoding='utf8'))
        old_blob=subprocess.check_output(['git','show',PUBLIC_BASE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
        old_data=yaml.safe_load(old_blob)
        if old_blob.replace(b'\r\n',b'\n')!=path.read_bytes().replace(b'\r\n',b'\n'):
            private_menu=(path.stem.startswith('mascota_') and MASCOTAS[path.stem.removeprefix('mascota_')]['n']>6
                          or path.stem in ('mascotas_2','mascotas_3','cosmeticos_sombreros'))
            folder=previews if private_menu else own
            preview_pair(render_menu(original if private_menu else previous,old_data,hat_images if private_menu else None),
                         render_menu(files if private_menu else public,data,hat_images if private_menu else None),folder/(path.stem+'-antes-despues.png'))
        for key,item in data['items'].items():
            if any(k.endswith('commands') for k in item):
                old_item=old_data['items'].get(key,{})
                rows.append(dict(menu=path.stem,button=key,material_before=old_item.get('material'),
                    model_before=old_item.get('item_model','vanilla'),
                    material=item.get('material'),model=item.get('item_model','vanilla')))
    (own/'auditoria-iconos.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    print('FINAL',target,'SHA1',sha,'referencias',refs,'cambiadas',len(changed),'retiradas',len(removed))
    manifest(sha,refs,changed,removed)
    return sha


def manifest(sha,refs,changed,removed):
    paths=subprocess.check_output(['git','diff','--name-only',PUBLIC_BASE,'--','build/menus/DeluxeMenus/gui_menus'],cwd=ROOT,text=True).splitlines()
    rows=[('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
          ('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip')]
    rows += [(p,'plugins/DeluxeMenus/gui_menus/'+Path(p).name) for p in paths if (ROOT/p).is_file()]
    rows += [(f'build/lobby/CrazyCrates/crates/{n}.yml',f'plugins/CrazyCrates/crates/{n}.yml') for n in ('gacha_cosmeticos','gacha_cosmeticos_garantia')]
    final='.local/terceros/AstralRPG-privado/'+DELIVERY+'/AstralRPG-Textures.zip'
    lines=['# Disenos pendientes y retiro de alas — preparado, sin desplegar','',
        'Empower / Paper 26.1.2 / Java 25. Aternos es la copia antigua. No se accedio al servidor ni se publico R2.',
        'Generar: `python datapack-src/deploy_disenos.py`, despues de regenerar menus, portales, lobby, datapack y pack publico, y compilar AstralDecor.',
        f'Base FINAL instalada indicada por el plan: `{BASE_SHA}`. Base publica fija: `{PUBLIC_BASE}`.',
        'La base privada incluye el tren ya presente en ad66e73: sus entradas se conservan, pero no se regeneran ni se publican los cambios pendientes del tren.','',
        '## Archivos exactos y destinos','', '| Local | Destino |','|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in rows]
    lines += [f'| `{final}` | R2: objeto `AstralRPG-Textures.zip` |','',
        f'FINAL SHA-1: `{sha}`. {refs} referencias auditadas; {len(changed)} entradas nuevas/cambiadas, {len(removed)} retiradas. Manifiesto privado: `{DELIVERY}/procedencia.json`.',
        'El ZIP publico contiene reservas propias y vanilla. NO instalarlo como FINAL.', '',
        '## Instalacion pendiente','',
        '1. Respaldar los destinos y server.properties. Esperar sala vacia y APAGAR el servidor.',
        '2. Reemplazar los archivos de la tabla. JAR 1.6.0 y datapack requieren reinicio completo. No instalar plugins de prueba ni copiar configuraciones del Paper local.',
        '3. Eliminar `plugins/DeluxeMenus/gui_menus/cosmeticos_alas.yml` y solo la entrada `gui_menus.cosmeticos_alas` de config.yml. Conservar los demas registros. Referencia generada: `build/menus/DeluxeMenus/config-gui_menus.yml`.',
        '4. AstralDecor integra su catalogo de gorros y retira cosmetics.alas sin reemplazar las configuraciones de NPC. Conservar datos de LuckPerms y playerdata: habilitan la compensacion.',
        '5. Publicar el FINAL solo al desplegar y verificar su descarga publica:', '', '```text',
        f'python tools/subir_pack_r2.py {final}', '```', '',
        f'Luego fijar `resource-pack-sha1={sha}` y conservar la URL R2. No ejecutar esta subida como parte de esta entrega.',
        '6. Encender y revisar Done, AstralDecor 1.6.0 y ausencia de errores nuevos de recetas, modelos, menus o cajas. El arranque carga YAML y datapack; no hace falta /reload.',
        '7. Si despues solo se ajustan YAML: `dm reload` y `crates reload`. Nunca PlugMan ni recarga global para cambiar el JAR.',
        '8. No reemplazar mundos ni regiones; nunca Worlds > Upload en world. Solo sustituir el ZIP del datapack en su carpeta.', '',
        'El holograma de la gacha debe decir «Titulos y gorros». No ejecutar todo build/lobby/comandos.txt para cambiar una linea: preservar posicion y vendedores existentes.', '',
        '## Comportamiento y compensacion','',
        '- Asura y Carnivora salen de catalogo, gacha normal y garantia, navegacion y seguimiento de AstralDecor. Tambien se retira el seguimiento de los items de segunda mano: era el mismo sistema.',
        '- Se retiran sus recetas. Los IDs fisicos antiguos siguen resolviendo a una pluma vanilla como recuerdo, sin vuelo, atributos ni geometria de alas. Los nuevos llevan nombre/lore de recuerdo; no se destruyen ni reconstruyen objetos antiguos, por lo que conservan nombres personalizados y componentes.',
        '- Compensacion permanente sin cobro: permiso antiguo de alas Carnivora habilita Sombrero Carnivora; permiso de alas Asura habilita Cuernos de Diablo. No se gastan ni revocan permisos. Abrir /cosmeticos y elegir el gorro. Las posesiones fisicas se conservan como recuerdo; no se convierten en dinero.',
        '- Gorros: el sistema anterior ocultaba el ItemDisplay al portador y usaba un anclaje/escala independientes de la cabeza. Ahora se envia equipo visual HEAD de Minecraft al portador y observadores, sin modificar inventario, armadura ni defensa. Visible en tercera persona; un casco real tiene prioridad. No se afirma un diagnostico remoto: no hubo acceso al servidor real.',
        '- /cosmeticos tiene botones propios GORROS y TITULOS. Los gorros usan el mismo marco ilustrado. Las 23 mascotas tienen el mismo detalle de nivel, experiencia, mejoras, invocar y descansar; las 17 nuevas vuelven a su pagina correcta.', '',
        '## Iconos y vistas','',
        'Principal: Fragmentos reutilizaba Habilidades y Duelos reutilizaba Arenas. Ahora tienen dibujos propios; Cosmeticos muestra un gorro. Se conservan los otros iconos propios.',
        'Submenus: se reemplazan las reservas vanilla de navegacion, comandos, cofres, gacha y minijuegos por iconos de servicio propios. Mochilas, Proteccion y Recetas tienen accesos en Comandos. Tren y Santuario incluyen icono propio preparado: no se inventa un boton /tren ni se modifica el tren pendiente; Santuario conserva su tarjeta ilustrada.',
        'Inventario exacto antes/despues de todos los botones accionables: `build/previews/disenos/auditoria-iconos.json`. Los premios de misiones conservan su objeto vanilla porque representan el premio real. Flechas/cerrar/candados comparten simbolo de navegacion deliberadamente.',
        'Vistas publicas antes/despues de cada menu cambiado: `build/previews/disenos/`. Los detalles nuevos, las paginas 2/3 y gorros con arte licenciado estan exclusivamente en el privado, `'+DELIVERY+'/previews/`. Son renders CPU de glifos y sprites; las reservas vanilla se indican con su inicial, no son capturas de juego. Los retratos salen de los modelos 3D adaptados, sin ImageGen ni copia al pack publico.', '',
        '## Verificacion y limites','',
        'Compilacion Java 25 correcta. verify.py: JSON, funciones/loot, sprites, IDs de misiones y secuencias de mazmorras correctos. Auditoria del FINAL valida todas las referencias.',
        'Paper local con dos jugadores NMS simulados: 14 comprobaciones aprobadas, paquetes HEAD a portador/observador, casco real intacto, reaparicion al quitar casco, quitar gorro, compensacion Asura, persistencia y ausencia de displays/pasajeros. Dependencias de encantamientos incluidas. No valida render de cliente ni integraciones remotas.',
        'Suite completa: 245 pruebas, 242 aprobadas y tres fallos historicos de test_alas_casco (comparacion con 75f49c4), test_oleadas_tanda2 (hashes de Santuario) y test_urgente (rutas anteriores de Santuario). Los tres se reproducen tambien en la copia del commit inicial a1fe4f2; no se modifican esos tests ni sus fuentes por esta tarea. Las 93 regresiones focalizadas de las areas modificadas pasan.',
        'Antes de dar conformidad visual: dos clientes vanilla con este FINAL aceptado, probar sin casco y con casco, tercera persona propia y desde observador, equipar/quitar los 20 gorros, cambio de mundo/reconexion/muerte y AxGraves; recorrer /menu, submenus, /mascotas paginas 1–3 y todos los detalles, gacha normal/garantia. Registrar capturas privadas y consola real. Despliegue y estas pruebas siguen pendientes.', '']
    (ROOT/'build/deploy/disenos-pendientes.md').write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__':prepare()
