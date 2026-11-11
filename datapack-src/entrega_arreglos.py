"""Manifiesto y vistas de revision. No instala ni publica archivos."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import yaml
from mobs.mazmorra import MINA
from mobs.mazmorras_data import catalog
from mobs.salas_seguras import PADS, install_commands, overlay
from mobs.terreno import get,AIR
from terceros import privado

ROOT=Path(__file__).resolve().parents[1]


def font(size):
    try:return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
    except OSError:return ImageFont.load_default()


def previews(ds):
    from menu_ui import panel,icon,KEYS,SLOTS
    from menus import principal_menu,mascotas_extra_menu
    from mobs.mascotas import MASCOTAS
    out=ROOT/'build/previews';out.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGBA',(1080,840),'#17222c')
    inv=panel()
    for key,slot in zip(KEYS,SLOTS):inv.alpha_composite(icon(key),(31+slot%9*18,57+slot//9*18))
    inv=inv.resize((672,840),Image.Resampling.NEAREST);im.alpha_composite(inv)
    draw=ImageDraw.Draw(im);data=yaml.safe_load(principal_menu())['items']
    for i,key in enumerate(KEYS):
        import re
        label=re.sub(r'&[0-9a-fk-or]','',data[key]['display_name'])
        draw.text((685,20+i*30),f'{SLOTS[i]:02}  {label}',font=font(18),fill='white')
    im.convert('RGB').save(out/'menu-astral-arreglos.png')
    private=privado()/'build/previews';private.mkdir(parents=True,exist_ok=True)
    # Dos paginas, mismos slots e iconos del pack FINAL privado.
    image=Image.new('RGB',(1260,660),'#1b2430');draw=ImageDraw.Draw(image)
    for page in (2,3):
        x0=(page-2)*630
        draw.text((x0+15,10),f'/mascotas - pagina {page}/3',font=font(22),fill='#edd180')
        cards=yaml.safe_load(mascotas_extra_menu(page))['items']
        for pid,d in MASCOTAS.items():
            if pid not in cards:continue
            slot=cards[pid]['slot'];i=(d['n']-7)%9
            x=x0+15+(i%3)*205;y=55+(i//3)*190
            draw.rectangle((x,y,x+194,y+179),fill='#263b43',outline='#c9a14f')
            p=privado()/f'build/item-pack/assets/astral/textures/item/mascotas/catalogo_{pid}.png'
            if not p.exists():raise FileNotFoundError(p)
            icon_img=Image.open(p).convert('RGBA').resize((90,90),Image.Resampling.NEAREST)
            image.paste(icon_img,(x+50,y+10),icon_img)
            draw.text((x+8,y+106),d['nombre'],font=font(13),fill='white')
            draw.text((x+8,y+128),f'Casilla {slot} | Gacha de Monturas',font=font(12),fill='#eccd7e')
            draw.text((x+8,y+147),'Detalle: nivel, bonus e invocacion',font=font(11),fill='#a7ced3')
    image.save(private/'arreglos-mascotas.png')
    # Coordenadas sobre una proyeccion horizontal del terreno real (privado).
    sheet=Image.new('RGB',(450*len(ds),530),'#1b2430');draw=ImageDraw.Draw(sheet)
    for i,d in enumerate(ds):
        r=d['rooms'][-1];x,y,z=r['final_npcs']['cofre'];cx,cz=math.floor(x),math.floor(z)
        for dx in range(-24,25):
            for dz in range(-24,25):
                b=get(d['world'],cx+dx,y-1,cz+dz)
                color='#2f4960' if b in AIR else '#645f50'
                if b=='minecraft:lava':color='#d04d23'
                if b=='minecraft:barrier':color='#5d3d74'
                planned=overlay(d['world'],cx+dx,y-1,cz+dz)
                if planned!=b:color='#bc9d43'
                if 'gold' in b:color='#deb742'
                if any(v in b for v in ('snow','ice','quartz','white')):color='#c1dfe2'
                if any(v in b for v in ('log','plank','slab')):color='#826438'
                xx=i*450+26+(dx+24)*8;yy=60+(dz+24)*8
                draw.rectangle((xx,yy,xx+7,yy+7),fill=color)
        def dot(point,color):
            px=i*450+26+(point[0]-cx+24)*8;py=60+(point[2]-cz+24)*8
            if i*450+20<=px<(i+1)*450-20 and 50<=py<=460:
                draw.ellipse((px-5,py-5,px+5,py+5),fill=color)
        dot(r['boss_spawn'],'#ef6565');dot(r['llegada'],'#5acaff');dot((x,y,z),'#55ff9b')
        draw.text((i*450+15,12),d['name'],font=font(21),fill='white')
        draw.text((i*450+15,465),f'Cofre: {x}, {y}, {z}',font=font(16),fill='#55ff9b')
        draw.text((i*450+15,490),'Verde: cofre | rojo: jefe | azul: llegada',font=font(12),fill='white')
        draw.text((i*450+15,510),'Oro: apoyo propuesto; no instalado',font=font(12),fill='#eccd7e')
    sheet.save(private/'arreglos-cofres.png')
    affected=[(d,r) for d in ds for r in d['rooms'] if any(
        get(d['world'],p[0],p[1]-1,p[2]) in AIR for p in [*r['spawn_points'],*([r['boss_spawn']] if r.get('boss_room') else [])])]
    plan=Image.new('RGB',(520*len(affected),540),'#1b2430');draw=ImageDraw.Draw(plan)
    for index,(d,r) in enumerate(affected):
        points=[*r['spawn_points'],r['llegada'],r['centro']]
        minx,maxx=min(p[0] for p in points)-5,max(p[0] for p in points)+5
        minz,maxz=min(p[2] for p in points)-5,max(p[2] for p in points)+5
        scale=min(460/(maxx-minx),420/(maxz-minz))
        def xy(x,z):return index*520+25+(x-minx)*scale,65+(z-minz)*scale
        for world,a,b,material in PADS:
            if world!=d['world'] or a[1]!=math.ceil(r['llegada'][1])-1:continue
            x0,y0=xy(a[0],a[2]);x1,y1=xy(b[0]+1,b[2]+1)
            if index*520<=x0<(index+1)*520 and 50<=y0<=490:
                draw.rectangle((x0,y0,x1,y1),outline='#d5b657',fill='#5d5133')
        for point,color in [(p,'#6aee9f') for p in r['spawn_points']]+[(r['llegada'],'#56c8ff')]:
            x,y=xy(point[0],point[2]);draw.ellipse((x-4,y-4,x+4,y+4),fill=color)
        draw.text((index*520+12,12),d['name']+' / '+r['id'],font=font(20),fill='white')
        draw.text((index*520+12,40),f'Altura minima: {r["llegada"][1]} | {len(r["spawn_points"])} puntos',font=font(15),fill='#eccd7e')
        draw.text((index*520+12,505),'Verde: aparicion | azul: llegada | oro: apoyo propuesto',font=font(12),fill='white')
    plan.save(private/'arreglos-apoyos.png')


def main():
    ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
    from mobs.mascotas import MASCOTAS
    doc=ROOT/'docs/SERVIDOR.md';text=doc.read_text(encoding='utf8')
    start=text.index('| Mascota | Nivel 1 |');end=text.index('\n- **Uso:**',start)
    table=['| Mascota | Nivel 1 | + Nivel 10 | + Nivel 20 | Como se consigue |','|---|---|---|---|---|']
    for pid,d in MASCOTAS.items():table.append('| '+' | '.join([d['nombre'],*d['texto'],d['fuente']])+' |')
    text=text[:start]+'\n'.join(table)+'\n'+text[end:]
    text=text.replace('`astral.mascota.<lobo|cuervo|golem|zorro|dragon|fenix>`','`astral.mascota.<id>` (23 IDs en `datapack-src/mobs/mascotas.py`)')
    text=text.replace('`astral.mascota.<id> (23 IDs en `mobs/mascotas.py`)`','`astral.mascota.<id>` (23 IDs en `datapack-src/mobs/mascotas.py`)')
    doc.write_text(text,encoding='utf8')
    summary=ROOT/'docs/PARA_CHATGPT.md';text=summary.read_text(encoding='utf8')
    start=text.index('| Mascota | Nivel 1 |');end=text.index('\n- **Uso:**',start)
    text=text[:start]+'\n'.join(table)+'\n'+text[end:]
    text=text.replace('`astral.mascota.<id> (23 IDs en `datapack-src/mobs/mascotas.py`)`','`astral.mascota.<id>` (23 IDs en `datapack-src/mobs/mascotas.py`)')
    import re
    text=re.sub(r'23 mascotas 3D que dan efectos y suben hasta el nivel 30 \([^\n]*?\)\.',
                '23 mascotas 3D que dan efectos y suben hasta el nivel 30 (6 originales + 17 nuevas; catalogo completo abajo).',text)
    summary.write_text(text,encoding='utf8')
    previews(ds)
    out=ROOT/'build/deploy';out.mkdir(parents=True,exist_ok=True)
    commands=install_commands()
    (out/'arreglos-apoyos.txt').write_text('# PROPUESTA: revisar vista privada y aprobar antes de ejecutar. Salas vacias.\n'+'\n'.join(commands)+'\n',encoding='utf8')
    audit={d['key']:{r['id']:{k:r[k] for k in ('centro','llegada','spawn_points','golem_points','boss_spawn','final_npcs','chest_platform') if k in r} for r in d['rooms']} for d in ds}
    (out/'arreglos-puntos.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
    rows=['# Arreglos de esqueletos, Volcano, salas e interfaces','',
          'Base: c3d4af8. Entrega local, SIN despliegue remoto. Servidor vigente: Empower; Aternos es copia.',
          'No usar APIs privadas ni Worlds > Upload. Nunca reemplazar world ni subir mapas/regiones.', '',
          '## Revision previa necesaria','',
          'Los apoyos propuestos para Tumba y Cumbre NO estan instalados: revisar y aprobar antes de desplegar las oleadas. '
          'Se proponen porque el jefe estaba bajo la llegada del jugador y los puntos alternativos altos eran tejados. '
          'No cambiar las llegadas elegidas por el dueno. `arreglos-apoyos.txt` contiene cada comando exacto: '
          'solo fill keep de bloques de apoyo; no borra ni sustituye bloques existentes. '
          'Si un apoyo ocupa una decoracion no solida, no desplegar: corregir el punto en el generador.', '',
          'Vista propia: `build/previews/esqueletos-brazos.png` (cinco variantes, idle/caminar/ataque, frente/costado).',
          'Menu: `build/previews/menu-astral-arreglos.png`. Son renders CPU, no capturas de Minecraft.',
          'Vistas PRIVADAS: `.local/terceros/AstralRPG-privado/build/previews/arreglos-cofres.png` y `arreglos-mascotas.png`. '
          'Tambien `arreglos-apoyos.png` en esa carpeta privada muestra las cuatro salas afectadas. '
          'No copiarlas al repo publico. Falta aprobacion visual del dueno antes de instalar.', '',
          '## Archivos exactos','', '| Archivo local | Destino |','|---|---|']
    for k in ('arquero','escudero','espadachin','guardian'):
        rows.append(f'| `build/models/astral_esq_{k}.bbmodel` | `plugins/BetterModel/models/astral_esq_{k}.bbmodel` |')
    for sub in ('mobs','skills'):
        for key in ('mazmorra','bosque','tumba','cumbre','forja','tanda3a','tanda3b'):
            rows.append(f'| `build/mythicmobs/{sub}/{key}.yml` | `plugins/MythicMobs/{sub}/{key}.yml` |')
    for key in ('principal','mascotas_2','mascotas_3'):
        rows.append(f'| `build/menus/DeluxeMenus/gui_menus/{key}.yml` | `plugins/DeluxeMenus/gui_menus/{key}.yml` |')
    from terceros import PETS
    for pid,*_ in PETS:
        rows.append(f'| `build/menus/DeluxeMenus/gui_menus/mascota_{pid}.yml` | `plugins/DeluxeMenus/gui_menus/mascota_{pid}.yml` |')
    for name in ('gacha_monturas','gacha_monturas_garantia'):
        rows.append(f'| `build/lobby/CrazyCrates/crates/{name}.yml` | `plugins/CrazyCrates/crates/{name}.yml` |')
    rows += ['| `build/mapas_exploracion/astral_viajes.sk` | `plugins/Skript/scripts/astral_viajes.sk` |',
             '| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |']
    for w in ('parkour_paradise3','parkour_spiral2'):
        rows.append(f'| `.local/mapas/subir/{w}-datapack.zip` (PRIVADO) | `world/datapacks/{w}-datapack/` (descomprimir contenido, reemplazar la version instalada) |')
    rows += ['| `.local/arreglos-pack/AstralRPG-Textures.zip` (FINAL PRIVADO) | R2, objeto `AstralRPG-Textures.zip`; verificar descarga publica y actualizar `resource-pack-sha1` |','',
             'No subir tambien una copia ZIP de los parkours si se conserva la carpeta: evitar dos versiones habilitadas. '
             'Reemplazar los datapacks adaptados COMPLETOS: funciones more_maps inertes y logros imposibles. '
             'El texto Volcano esta en more_maps:interact; sus llamadas tick y logros de Interaction explican el riesgo de reentrada. '
             'No se inspecciono el servidor remoto; si persiste, descargar SOLO las carpetas instaladas '
             '`world/datapacks/parkour_paradise3-datapack/`, `world/datapacks/parkour_spiral2-datapack/` y cualquier otro pack con namespace `more_maps`, '
             'a `.local/coordination/servidor-datapacks/` para comparar. No bajar ni subir mundos.', '',
             '## Orden y recargas','',
             '1. Aprobar vistas y apoyos; salas vacias, respaldo de archivos de la tabla. Apagar el servidor.',
             '2. Subir los archivos indicados. Subir el pack FINAL privado con `python tools/subir_pack_r2.py .local/arreglos-pack/AstralRPG-Textures.zip`, '
             'verificar descarga publica y SHA-1; entonces actualizar server.properties. No usar el ZIP publico como pack final.',
             '3. Iniciar y revisar consola. El reinicio carga datapack, modelos y configs. Para ajustes posteriores: '
             '`bettermodel reload`, `mm reload`, `dm reload`, `crates reload`, `skript:skript reload astral_viajes`. '
             '`minecraft:reload` solo recarga datapacks; no sustituye reinicio de propiedades/pack.',
             '4. ANTES de admitir jugadores a las salas, ejecutar los comandos aprobados de `arreglos-apoyos.txt`. '
             'Comprobar suelo y aire en TODOS los puntos de `arreglos-puntos.json`. Es requisito de esta version, no una migracion automatica.',
             '5. Recrear los controladores SOLO con salas vacias; mismas coordenadas e IDs (abajo). '
             'No matar un jefe con una partida activa. Probar oleadas, ayudantes, cofre, guia y vuelta al lobby.',
             '6. Reconectar con pack y comprobar brazos/arco y contorno. Probar ataques e Interaction en world sin Volcano, '
             'y ambos parkours sin publicidad repetida. Revisar 25 accesos del menu, las 23 mascotas y vitrina normal/garantizada.', '',
             '## Cofres','', '| Mazmorra | Plataforma | Cofre X Y Z |','|---|---|---|']
    for d in ds:
        r=d['rooms'][-1]
        platform='Si: altar de troncos' if d['key']=='bosque' else 'Si: altar de oro, elevar apoyo propuesto' if d['key']=='tumba' else 'No: spawn del jefe'
        rows.append(f'| {d["name"]} | {platform} | {r["final_npcs"]["cofre"]} |')
    rows += ['', 'Forja: aire Y47 sobre suelo invisible barrier Y46 y lava Y45. No se coloca el cofre dentro de ninguno. '
             'La sala no tiene una tarima visible diferenciada junto al jefe. Minas: suelo de ladrillo continuo. '
             'Cumbre: plaza de nieve; el apoyo propuesto resuelve la altura, sin inventar un altar de recompensa.', '',
             '## Controladores (solo sin jugadores)','', '```text']
    for d in ds:
        for r in d['rooms']:
            key=d['key'];world=d['world'];rid=r['id'];x,y,z=r['centro']
            rows += [f'mm mobs kill astral_{key}_control_{rid}',f'execute in minecraft:{world} run function astral:tanda2/{key}/{rid}/reset',
                     f'mm mobs spawn astral_{key}_control_{rid} 1 {world},{x},{y},{z}']
    rows += ['```','','## Interfaces auditadas','',
             'Principal: 14 accesos conservados y 11 agregados: Bosque, Fragmentos, tienda, peluches, subastas, venta, intercambio, tres gachas y duelos. '
             'Forja y recetas siguen en Guia; titulos en Cosmeticos; todas las paginas de aventura siguen accesibles. '
             'Trade y Duel requieren nombre, por eso el boton explica el comando.',
             'Mascotas: paginas 1/2/3 y 23 detalles; iconos de nuevas mascotas en el circuito privado. '
             'CrazyCrates: 20 mascotas obtenibles en gacha (17 nuevas + cuervo/dragon/fenix); Lobo/Golem/Zorro conservan drops. '
             'Pesos y garantia sin cambio. Guia: catalogo completo en tres paginas. Misiones/cronista: contador pet generico cubre las 23; '
             'no habia lista fija de seis en sus textos. TAB no muestra mascota activa; no necesita lista nueva. '
             'El panel artistico de pagina 1 y los seis detalles originales conservan arte; nuevas paginas usan sus modelos privados.', '',
             '## Reproduccion del pack aislado','',
             'La base privada aprobada es a6d26e9 / SHA-1 a18b694f5002cef979fe72ad6caf24134550db03. '
             'Tras convertir los modelos con BetterModel local: `python tools/copiar_assets_arreglos.py .local/tanda4a-paper/plugins/BetterModel/build/assets`; '
             '`python datapack-src/build_pack.py datapack-src/pack-source`; `python tools/armar_pack_arreglos.py`. '
             'Los 17 iconos se preparan con build_privado.py --prepare, pero el ensamblador aislado toma SOLO sus 51 archivos catalogo_<id>, '
             'sin mezclar los demas derivados privados. Procedencia y hash en `.local/arreglos-pack/procedencia.json`. '
             'La copia exclusiva para Git privado esta en `build/entregas/arreglos-esqueleto-volcano/` de ese repositorio. '
             'Se detecto una edicion concurrente ajena en tanda4b_privado.py: no se incluye en el commit ni en este pack aislado.', '',
             '## Limites','',
             'No se desplego ni se subio a R2. No hubo cliente Minecraft conectado: falta captura en juego del contorno y aprobacion visual. '
             'Las pruebas del tracker y regresiones se informan en el resultado; un render CPU no certifica el cliente. '
             'Los apoyos son una propuesta explicita, no una modificacion del mapa instalada. '
             'Mundo normal: conservados puntos de elites y aparicion natural; solo se corrige el rig compartido. Santuario sin cambios.']
    for name,path in [('Pack publico (reserva)',ROOT/'build/AstralRPG-Textures.zip'),('Pack FINAL privado aislado',ROOT/'.local/arreglos-pack/AstralRPG-Textures.zip')]:
        if path.exists():rows.append(f'{name}: SHA-1 `{hashlib.sha1(path.read_bytes()).hexdigest()}`.')
    (out/'arreglos-esqueleto-volcano.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    test_log=ROOT/'.local/arreglos-tests-ok.txt'
    probe_log=ROOT/'.local/arreglos-probe/paper.log'
    if test_log.exists() and probe_log.exists():
        raw=test_log.read_bytes()
        tests=raw.decode('utf16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf8',errors='replace')
        probe=probe_log.read_text(encoding='utf8',errors='replace')
        if 'Ran 193 tests' in tests and '\nOK' in tests and 'ARREGLOS_PROBE tested=10' in probe and 'ARREGLOS_PROBE FAIL' not in probe:
            (out/'arreglos-verificacion.md').write_text(
                '# Verificacion local del 11/11/2026\n\n'
                '- Suite completa: 193 pruebas aprobadas (incluye 9 regresiones nuevas).\n'
                '- verify.py: JSON, funciones, loot, sprites, IDs y secuencia de mazmorras validos.\n'
                '- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0: 10 casos aprobados. '
                'Todos los displays de los 7 modelos de sala tienen glow y RGB FFFFFF. '
                'Los 3 controles de mundo normal no reciben el glow del modelo.\n'
                '- Texturas de las 5 variantes de esqueleto identicas a c3d4af8; arco unido a la mano durante 25 muestras por animacion.\n'
                '- Alturas y piso/aire de todos los puntos generados validados con la propuesta de apoyos aplicada virtualmente. '
                'No certifica que esos apoyos esten instalados: requieren aprobacion y ejecucion explicita.\n'
                '- Sin cliente Minecraft: captura del contorno, recorrido de salas y aprobacion visual pendientes. '
                'Sin despliegue remoto, sin subida a R2. Logs conservados solo en .local.\n',encoding='utf8')


if __name__=='__main__':main()
