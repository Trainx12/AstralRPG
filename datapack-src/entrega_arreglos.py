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
    from menus import comandos_menu
    commands=yaml.safe_load(comandos_menu())['items']
    image=Image.new('RGB',(1080,720),'#181323');draw=ImageDraw.Draw(image)
    draw.text((20,10),'Comandos - esquema de casillas y textos generados',font=font(20),fill='white')
    import re
    for key,card in commands.items():
        if key.startswith('fondo'):continue
        slot=card.get('slot')
        if slot is None:continue
        x=slot%9*120;y=50+slot//9*108
        draw.rectangle((x+2,y+2,x+116,y+104),fill='#30283a',outline='#c9a14f')
        label=re.sub(r'&[0-9a-fk-or]','',card.get('display_name',key))
        draw.text((x+6,y+12),label[:17],font=font(12),fill='white')
        for n,line in enumerate(card.get('lore',[])[:3]):
            draw.text((x+6,y+35+n*16),re.sub(r'&[0-9a-fk-or]','',line)[:19],font=font(10),fill='#c8b6dc')
    image.save(out/'menu-comandos.png')
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
        draw.text((i*450+15,510),'Piso natural; sin bloques nuevos',font=font(12),fill='#eccd7e')
    sheet.save(private/'arreglos-cofres.png')
    affected=[(d,r) for d in ds for r in d['rooms'] if d['key'] in ('cumbre','tumba')]
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
        draw.text((index*520+12,40),f'Piso Y: {r["floor_range"]} | {len(r["spawn_points"])} puntos',font=font(15),fill='#eccd7e')
        draw.text((index*520+12,505),'Verde: aparicion | azul: llegada. Sin apoyos.',font=font(12),fill='white')
    plan.save(private/'arreglos-apoyos.png')


def main():
    ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
    previews(ds)
    out=ROOT/'build/deploy';out.mkdir(parents=True,exist_ok=True)
    (out/'arreglos-apoyos.txt').unlink(missing_ok=True)
    audit={d['key']:{r['id']:{k:r[k] for k in ('centro','llegada','floor_range','spawn_points','golem_points','boss_spawn','final_npcs','chest_platform') if k in r} for r in d['rooms']} for d in ds}
    (out/'arreglos-puntos.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
    rows=['# Arreglos: integrados en entrega unica', '',
          'Despliegue pendiente. Seguir urgente-mascotas-texturas.md, que contiene el pack FINAL vigente y todos los destinos.',
          'Esta revision reemplaza la propuesta de apoyos: NO agregar bloques. No usar arreglos-apoyos.txt ni el pack aislado anterior.',
          'Principal: los 14 accesos anteriores mas Fragmentos y Duelos. Trade sigue explicado en Comandos; Peluches dentro de la Tienda.', '',
          '| Mazmorra | Sala | Piso minimo | Piso maximo | Puntos |', '|---|---|---:|---:|---:|']
    for d in ds:
        for r in d['rooms']:
            rows.append(f'| {d["key"]} | {r["id"]} | {r["floor_range"][0]} | {r["floor_range"][1]} | {len(r["spawn_points"])} |')
    rows += ['', 'Vistas CPU propias: build/previews/menu-astral-arreglos.png y menu-comandos.png.',
             'Vistas de mapas solo en el build privado: previews/arreglos-apoyos.png y arreglos-cofres.png. Sin puntos dorados de apoyo.', '',
             '## Controladores: salas vacias, despues de instalar y reiniciar', '', '```text']
    for d in ds:
        for r in d['rooms']:
            key=d['key'];world=d['world'];rid=r['id'];x,y,z=r['centro']
            rows += [f'execute in minecraft:{world} run forceload add {math.floor(x)} {math.floor(z)}',
                     f'mm mobs kill astral_{key}_control_{rid}',f'execute in minecraft:{world} run function astral:tanda2/{key}/{rid}/reset',
                     f'mm mobs spawn astral_{key}_control_{rid} 1 {world},{x},{y},{z}']
    rows += ['```', '', 'Los packs de parkour adaptados del arreglo anterior se conservan: si falta instalarlos, reemplazar solamente sus datapacks, nunca mundos.',
             'Fuentes privadas: .local/mapas/subir/parkour_paradise3-datapack.zip y parkour_spiral2-datapack.zip.',
             'Destinos: world/datapacks/parkour_paradise3-datapack/ y world/datapacks/parkour_spiral2-datapack/ (contenido descomprimido, sin copia ZIP duplicada).', '']
    (out/'arreglos-esqueleto-volcano.md').write_text('\n'.join(rows),encoding='utf8')


if __name__=='__main__':main()
