"""Altura minima de las salas y propuesta de apoyos. Nunca modifica regiones.

Los apoyos nuevos se instalan SOLO mediante el comando explicito del manifiesto,
despues de revisar las vistas privadas. No se ejecutan en load/tick.
"""
import math
from mobs.terreno import AIR, get, clear, solid

PADS=[]
MATERIAL={'tumba':'minecraft:chiseled_sandstone','cumbre':'minecraft:snow_block'}


def remember_pad(world,point,material,width=3):
    x,y,z=map(math.floor,point); radius=width//2
    pad=(world,(x-radius,y-1,z-radius),(x+radius,y-1,z+radius),material)
    if pad not in PADS:PADS.append(pad)


def supported(world,point):
    x,y,z=map(math.floor,point)
    return any(w==world and a[0]<=x<=b[0] and a[1]==y-1 and a[2]<=z<=b[2]
               for w,a,b,material in PADS)


def overlay(world,x,y,z):
    x,y,z=map(math.floor,(x,y,z))
    original=get(world,x,y,z)
    for w,a,b,material in PADS:
        if w==world and a[0]<=x<=b[0] and a[1]==y and a[2]<=z<=b[2] and original in AIR:
            return material
    return original


def safe(world,point,height=3):
    x,y,z=point
    return (solid(overlay(world,x,y-1,z))
            and all(overlay(world,x,y+dy,z) in AIR for dy in range(height)))


def configure(dungeon):
    if dungeon['key']=='santuario':return
    key=dungeon['key'];world=dungeon['world']
    for room in dungeon['rooms']:
        minimum=math.ceil(room['llegada'][1])
        for field in ('spawn_points','golem_points'):
            if field not in room:continue
            # En la plaza de Cumbre, los otros pisos blancos son tejados.
            upper=minimum+1 if key=='cumbre' and not room.get('boss_room') else math.inf
            valid=[p for p in room[field] if minimum<=p[1]<=upper and clear(world,*p)]
            # Primero mantener puntos naturales de la misma sala. Si no existe
            # ninguno, preparar una propuesta de apoyos en los puntos elegidos.
            if not valid:
                for x,y,z in room[field]:
                    p=(x,max(minimum,y),z)
                    if p[1]>upper:continue
                    if all(get(world,x,p[1]+dy,z) in AIR for dy in range(3)):
                        if not solid(get(world,x,p[1]-1,z)):
                            if key not in MATERIAL:continue
                            remember_pad(world,p,MATERIAL[key])
                        valid.append(p)
            if not valid:raise ValueError(f'Sala sin apariciones seguras: {key}/{room["id"]}')
            room[field]=valid
        if room.get('boss_room'):
            # El controlador conserva su lugar; el spawn del jefe es explicito.
            x,y,z=room['centro']; p=(x,max(y,minimum),z)
            if not safe(world,p):
                if key not in MATERIAL:raise ValueError(f'Jefe sin piso: {key}')
                if not all(get(world,p[0],p[1]+dy,p[2]) in AIR for dy in range(3)):
                    raise ValueError(f'Jefe sin aire: {key}')
                remember_pad(world,p,'minecraft:gold_block' if key=='tumba' else MATERIAL[key],width=9 if key=='cumbre' else 5)
            room['boss_spawn']=p
            if key=='tumba':room['final_npcs']['guia']=(1.5,73,1.5)
            # Altar de troncos del Bosque y altar de oro de Tumba; las otras
            # salas usan el punto exacto del jefe. Forja tiene suelo de barrier
            # a Y46: el cofre esta en aire Y47, nunca dentro de la barrera/lava.
            chest={'bosque':(1604.5,101,1382.5),'tumba':(0.5,73,0.5)}.get(key,p)
            if not safe(world,chest):raise ValueError(f'Cofre sin piso/aire: {key} {chest}')
            room.setdefault('final_npcs',{})['cofre']=chest
            room['chest_platform']=key in ('bosque','tumba')


def install_commands():
    # keep preserva cualquier bloque existente. El manifiesto exige inspeccion
    # previa; una discrepancia bloquea el despliegue, no se sobrescribe el mapa.
    return [f'execute in minecraft:{w} run fill {a[0]} {a[1]} {a[2]} {b[0]} {b[1]} {b[2]} {material} keep'
            for w,a,b,material in PADS]
