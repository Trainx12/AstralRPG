"""Datos y cola de oleadas vanilla. La cola usa comandos vanilla, sin Mythic Premium.

Cada sala tiene su propio storage, etiquetas y contador del controlador. Los cuatro
de llegada no ocupan plazas de la oleada, pero bloquean su finalizacion.
"""
import json
import math
import re
from copy import deepcopy
from escala import (VIDA_JEFE, OLEADA_TOPE, OLEADA_TOPE_FORJA, OLEADA_TANDA,
                    OLEADA_INTERVALO, LLEGADA_MOBS, EXTRA_JUGADOR_PCT)

# Punto unico para reemplazar esqueletos por las variantes de la tanda 3.
ESQUELETOS = {'normal': 'SKELETON', 'hielo': 'STRAY', 'forja': 'WITHER_SKELETON'}
WAVES = {
 'bosque': [[ [('ZOMBIE',6),('SPIDER',3)], [('ZOMBIE',6),('SKELETON',4),('SPIDER',3)],
               [('ZOMBIE',5),('SKELETON',4),('SPIDER',3),('WITCH',2)] ]],
 'mina': [[ [('ZOMBIE',5),('SKELETON',3),('SILVERFISH',4)], [('ZOMBIE',5),('SKELETON',3),('CAVE_SPIDER',3)] ],
          [ [('ZOMBIE',5),('SKELETON',4),('CAVE_SPIDER',3)], [('ZOMBIE',6),('SKELETON',3),('CREEPER',2)] ],
          [ [('ZOMBIE',6),('SKELETON',4),('CAVE_SPIDER',3)], [('ZOMBIE',6),('SKELETON',4),('CREEPER',2),('WITCH',2)] ]],
 'tumba': [[ [('HUSK',5),('SKELETON',3),('CAVE_SPIDER',3)], [('HUSK',5),('SKELETON',4),('CAVE_SPIDER',4)] ],
           [ [('HUSK',6),('SKELETON',4),('SPIDER',4)], [('HUSK',6),('SKELETON',5),('CAVE_SPIDER',3),('CREEPER',2)],
             [('RAVAGER',2),('HUSK',4)] ]],
 'cumbre': [[ [('ZOMBIE',6),('STRAY',4),('SPIDER',3)], [('ZOMBIE',6),('STRAY',5),('SPIDER',3),('WITCH',1)],
              [('ZOMBIE',5),('STRAY',4),('VINDICATOR',4)], [('ZOMBIE',2),('STRAY',4),('VINDICATOR',4),('WITCH',2)] ]],
 'forja': [[ [('WITHER_SKELETON',8),('BLAZE',4),('MAGMA_CUBE',2)], [('WITHER_SKELETON',6),('PIGLIN_BRUTE',4),('BLAZE',4)] ],
           [ [('WITHER_SKELETON',6),('PIGLIN_BRUTE',4),('HOGLIN',2)], [('PIGLIN_BRUTE',4),('HOGLIN',3),('BLAZE',4),('MAGMA_CUBE',2)] ]],
}

def expanded(wave, players):
    base=[m for m,n,_ in wave for _ in range(n)]
    total=math.ceil(len(base)*(100+EXTRA_JUGADOR_PCT*max(0,players-2))/100)
    return [base[i % len(base)] for i in range(total)]

def configure(dungeon):
    if dungeon['key']=='santuario' or dungeon.get('tanda2'):
        return dungeon
    from mobs.terreno import points
    d=dungeon; key=d['key']; world=d['world']
    d['tanda2']=True
    d['tier']={'bosque':1,'mina':2,'tumba':3,'cumbre':4,'forja':5}[key]
    old=d['rooms']; boss=deepcopy(old[-1])
    boss['oleadas']=[[(old[-1]['oleadas'][-1][0][0],1,0)]]
    boss['spawn_radius']=0
    if key=='mina':
        d['mobs']['astral_mina_guardian']['hp']=VIDA_JEFE[key]
        d['mobs']={k:v for k,v in d['mobs'].items() if k=='astral_mina_guardian'}
    else:
        d['mobs']={}
        # Las variantes antiguas de criaturas no se usan en las oleadas.
        blocks=d['mob_blocks']; start=blocks.index(f'astral_{key}_'+{'bosque':'chaman','tumba':'momia','cumbre':'yeti','forja':'golem_forja'}[key]+':')
        d['mob_blocks']=blocks[start:]
    if key=='bosque':
        pts=points(world,((1425,97,1550),(1482,102,1583)))
        old=[dict(id='sala1',name='Claro de las raices',centro=pts[len(pts)//2],llegada=pts[len(pts)//2],r=40,
                  spawn_points=pts,spawn_bounds=((1425,97,1550),(1482,102,1583)))]
        boss.update(id='sala2',centro=(1604.5,101,1382.5),llegada=(1603.7,100,1413.4),yaw=-177.9,r=40)
        boss['final_npcs']={'cofre':boss['llegada']}
        # Reserva de configuracion para la planta de la tanda 3 (sin invocarla).
        old[0]['reserved_mobs']=['astral_bosque_planta']
    elif key=='cumbre':
        arrival=(-25.6,33,-23.4)
        pts=points(world,((-51,25,-49),(0,40,2)),white=True,origin=arrival)
        old=[dict(id='sala1',name='Plaza de la fuente',centro=arrival,llegada=arrival,yaw=49.9,r=34,spawn_points=pts)]
        boss.update(id='sala2',centro=(-101.8,30,56.9),llegada=(-54.9,30,6.5),r=80,yaw=-138.9,boss_yaw=-138.9)
        # No inventar otra llegada: el grupo conserva la llegada elegida por el dueno.
        boss.update(llegada=arrival,r=128,yaw=49.9)
        boss['final_npcs']={'cofre':arrival}
    elif key=='forja':
        bounds=[((-21,12,-203),(53,13,-122)),((-158,12,-121),(-92,13,-104))]
        arrivals=[(23.2,13,-159.4),(-125.5,13,-125.7)]
        old=[dict(id=f'sala{i+1}',name=f'Forja - sala {i+1}',centro=arrivals[i],llegada=arrivals[i],
                  yaw=[151.5,-13.4][i],r=[64,48][i],spawn_points=points(world,bounds[i],width=3),spawn_bounds=bounds[i]) for i in range(2)]
        boss.update(id='sala3',centro=(-7.9,47,-21.1),llegada=(0.8,47,26),yaw=-178.2,boss_yaw=-14.8,r=56)
        boss['final_npcs']={'cofre':boss['llegada']}
    else:
        old=old[:-1]
    for room,waves in zip(old,WAVES[key]):
        skeletons={'SKELETON':ESQUELETOS['normal'],'STRAY':ESQUELETOS['hielo'],'WITHER_SKELETON':ESQUELETOS['forja']}
        room['oleadas']=[[(skeletons.get(m,m),n,0) for m,n in wave] for wave in waves]
        room.pop('group_scaling',None); room['extra']=[]
        if 'spawn_points' not in room:
            x,y,z=room['centro']; radius=room['r']-2
            room['spawn_points']=points(world,((math.floor(x-radius),math.floor(y-3),math.floor(z-radius)),
                                                     (math.floor(x+radius),math.floor(y+7),math.floor(z+radius))),width=2)
    # Jefes y sus companeros aparecen juntos. Estos ayudantes tampoco son modelos.
    boss['boss_room']=True
    boss['companions']=('WITHER_SKELETON' if key=='forja' else 'HUSK' if key=='tumba' else 'ZOMBIE',3 if key=='bosque' else 4)
    boss['extra']=[]
    if 'spawn_points' not in boss:
        x,y,z=boss['centro']
        boss['spawn_points']=points(world,((math.floor(x-12),math.floor(y-2),math.floor(z-12)),
                                                 (math.floor(x+12),math.floor(y+2),math.floor(z+12))),width=2)
    d['rooms']=old+[boss]
    return d

def path(d,r): return f'tanda2/{d["key"]}/{r["id"]}'
def tag(d,r): return 'ad.'+d['key']+'.'+r['id']
def cmd(function): return f'command{{c="execute as <caster.uuid> at @s run function astral:{function}"}} @self'

def transform(text,d,kind):
    if not d.get('tanda2'): return text
    import yaml
    data=yaml.safe_load(text); key=d['key']; prefix=key.upper()
    for room in d['rooms']:
        p=path(d,room); S=f'{prefix}_{room["id"].upper()}'; busy=f'{key}.{room["id"]}.busy'
        if kind=='mobs':
            control=data[f'astral_{key}_control_{room["id"]}']
            sk=control['Skills']
            sk.insert(0,cmd(p+'/tick')+' ~onTimer:20')
            for i,line in enumerate(sk):
                line=re.sub(r'\?mobsinradius\{[^}]+\}',f'?!hastag{{tag={busy}}}',line)
                if key=='cumbre' and room.get('boss_room') and '_INICIO}' in line:
                    line+= ' ?hastag{tag=cumbre.unlocked}'
                sk[i]=line
            # Nada de victoria por desaparicion: todos los jefes confirman su muerte.
            if room.get('boss_room'):
                for i,line in enumerate(sk):
                    if '_LIMPIA}' in line:
                        if f'?!hastag{{tag={busy}}}' not in line: line+=f' ?!hastag{{tag={busy}}}'
                        if f'?hastag{{tag={key}.jefe.derrotado}}' not in line: line+=f' ?hastag{{tag={key}.jefe.derrotado}}'
                        sk[i]=line
        else:
            for n in range(1,len(room['oleadas'])+1):
                skill=data[S+('_INICIO' if n==1 else f'_OLA{n}')]['Skills']
                skill[:]=[s for s in skill if not s.startswith(('summon{','randomskill{')) and 'GRUPO' not in s
                          and not s.startswith('removetag{tag='+key+'.espera}')]
                if not room.get('boss_room'):
                    # La cola se arma sin demoras: tick no puede liberar espera entre
                    # la marca de la ola siguiente y la escritura de sus pendientes.
                    skill[:]=[s for s in skill if not s.startswith('delay ')]
                if room.get('boss_room'):
                    mob=room['oleadas'][0][0][0]
                    x,y,z=room['centro']
                    skill += [f'removetag{{tag={key}.jefe.derrotado}} @self',
                              cmd(p+'/arrival'),f'summon{{type={mob};amount=1;radius=0}} @Location{{x={x};y={y};z={z}}}',
                              cmd(p+'/companions'),'delay 10',f'removetag{{tag={key}.espera}} @self']
                else:
                    skill += [cmd(p+f'/wave{n}')]
            reset=data[S+'_RESET']['Skills']
            reset.insert(0,cmd(p+'/reset'))
            if key=='cumbre' and not room.get('boss_room'):
                limpia=data[S+'_LIMPIA']['Skills']
                limpia[:]=[s for s in limpia if not s.startswith('removetag{')]
                limpia.append('command{c="execute at <caster.uuid> run tag @e[type=armor_stand,name=\'Control Trono del Yeti\',distance=..200] add cumbre.unlocked"} @self')
            if room.get('boss_room'):
                data[S+'_LIMPIA']['Conditions']=[f'hastag{{tag={key}.jefe.derrotado}} true',f'hastag{{tag={key}.fin}} false']
                # Ayudantes siguen contando para la limpieza. No retirarlos antes de ganar.
                boss_id=room['oleadas'][0][0][0]
                # Bloques de jefes se agregan en mob_yml, no aqui.
                reset.append(f'removetag{{tag={key}.jefe.derrotado}} @self')
                if key=='cumbre': reset.append('removetag{tag=cumbre.unlocked} @self')
            # Aplicar la orientacion elegida por el dueno en entradas y transiciones.
            targets=[r for r in d['rooms'] if r.get('yaw') is not None]
            for value in data.values():
                for i,line in enumerate(value.get('Skills',[])):
                    if 'minecraft:tp ' not in line: continue
                    for target in targets:
                        xyz=' '.join(map(str,target['llegada']))
                        line=line.replace(xyz+'"}',xyz+f' {target["yaw"]} 0'+'"}')
                    value['Skills'][i]=line
    if kind=='mobs':
        room=d['rooms'][-1]; boss_id=room['oleadas'][0][0][0]
        if boss_id in data:
            sk=data[boss_id]['Skills']
            if not any('jefe.derrotado' in s for s in sk):
                sk.append(f'command{{c="execute at <caster.uuid> run tag @e[type=armor_stand,distance=..160,name=\'Control {room["name"]}\'] add {key}.jefe.derrotado"}} @self ~onDeath')
            sk += [f'addtag{{tag={tag(d,room)}}} @self ~onSpawn']
            sk += [f'addtag{{tag={tag(d,room)}}} @self ~onLoad']
            # Los ayudantes de fase tambien son vanilla y pertenecen a su sala.
            helper=cmd(path(d,room)+'/helpers')
            sk[:]=[re.sub(r'summon\{[^}]+\} @self',helper,s) if 'summon{' in s else s for s in sk]
            # Conservar fases, usando copias de mazmorra con ayudantes vanilla.
            sk[:]=[s.replace('skill{s=AST_FASE_',f'skill{{s=TANDA2_{key}_AST_FASE_') for s in sk]
            if room.get('boss_yaw') is not None:
                sk += [f'command{{c="execute as <caster.uuid> at @s run minecraft:tp @s ~ ~ ~ {room["boss_yaw"]} 0"}} @self ~onSpawn']
    else:
        from mobs import mythic
        source={'bosque':'chaman','tumba':'momia','cumbre':'yeti','forja':'golem_forja'}.get(key)
        helper=cmd(path(d,d['rooms'][-1])+'/helpers')
        if source:
            for name,value in yaml.safe_load(mythic.metaskills()).items():
                if name.startswith('AST_FASE_astral_'+source+'_'):
                    value=deepcopy(value)
                    value['Skills']=[re.sub(r'summon\{[^}]+\} @self',helper,s) for s in value['Skills']]
                    data[f'TANDA2_{key}_'+name]=value
        if key=='mina':
            for name,value in data.items():
                if name.startswith('MINA_GUARDIAN_'):
                    value['Skills']=[re.sub(r'summon\{[^}]+\} @self',helper,s) for s in value['Skills']]
    return '# Generado por mobs/mazmorra.py + mobs/tanda2.py\n'+yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000)

def generate(files):
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    ds=[configure(MINA)]+[d for d in catalog() if d['key']!='santuario']
    def fn(p,lines): files['data/astral/function/'+p+'.mcfunction']='\n'.join(lines)+'\n'
    # Objetivos propios: no dependen de ejecutar comandos de instalacion manuales.
    load='data/astral/function/load.mcfunction'
    files[load]+='\n'+ '\n'.join('scoreboard objectives add '+o+' dummy' for o in ('ad.party','ad.n','ad.i','ad.clock','ad.alive'))+'\n'
    for d in ds:
        key=d['key']
        for r in d['rooms']:
            p=path(d,r); t=tag(d,r); store='astral:'+p; busy=f'{key}.{r["id"]}.busy'
            cap=OLEADA_TOPE_FORJA if key=='forja' else OLEADA_TOPE
            sel=f'@e[tag={t},nbt=!{{Health:0.0f}}]'
            wave_sel=f'@e[tag={t}.wave,nbt=!{{Health:0.0f}}]'
            fn(p+'/reset',[f'kill @e[tag={t}]',f'data remove storage {store} queue',
                           f'tag @s remove {busy}',f'scoreboard players set @s ad.clock 0'])
            fn(p+'/cleanup',[f'kill @e[tag={t}]',f'data remove storage {store} queue'])
            def spawn(m,pt,suffix):
                x,y,z=pt; tags=[t,t+'.'+suffix,'ad.vanilla']
                nbt='Tags:'+json.dumps(tags)+',Glowing:1b,PersistenceRequired:1b'
                if m in ('ZOMBIE','HUSK'): nbt+=',IsBaby:0b'
                if m in ('PIGLIN_BRUTE','HOGLIN'): nbt+=',IsImmuneToZombification:1b'
                if m=='MAGMA_CUBE':
                    # Size 0 never splits; scale restores the large cube hitbox.
                    nbt+=',Size:0,Health:16f,attributes:[{id:"minecraft:max_health",base:16},{id:"minecraft:attack_damage",base:6},{id:"minecraft:scale",base:4}]'
                if m in ('SKELETON','STRAY'): nbt+=',equipment:{mainhand:{id:"minecraft:bow",count:1}}'
                if m=='WITHER_SKELETON': nbt+=',equipment:{mainhand:{id:"minecraft:stone_sword",count:1}}'
                if m=='VINDICATOR': nbt+=',equipment:{mainhand:{id:"minecraft:iron_axe",count:1}}'
                lines=[f'summon minecraft:{m.lower()} {x} {y} {z} {{{nbt}}}',
                       f'execute as @e[tag={t},tag=!astral.seen] at @s run function astral:mob/roll']
                if key=='forja': lines += [f'effect give @e[tag={t}] minecraft:fire_resistance infinite 0 true']
                return lines
            arrival='HUSK' if key=='tumba' else 'ZOMBIE'
            fn(p+'/arrival', [line for i in range(LLEGADA_MOBS) for line in spawn(arrival,r['spawn_points'][i%len(r['spawn_points'])],'arrival')])
            if r.get('boss_room'):
                m,n=r['companions']
                fn(p+'/companions',[line for i in range(n) for line in spawn(m,r['spawn_points'][i%len(r['spawn_points'])],'companion')])
                fn(p+'/helpers',[line for i in range(2) for line in spawn('HUSK' if key=='tumba' else 'SKELETON' if key=='mina' else 'ZOMBIE',r['spawn_points'][i%len(r['spawn_points'])],'companion')])
            for n,wave in enumerate(r['oleadas'],1):
                if r.get('boss_room'): continue
                base=[m for m,count,_ in wave for _ in range(count)]
                queue=[]
                for i,m in enumerate(base):
                    pts=r.get('golem_points',r['spawn_points']) if m=='RAVAGER' else r['spawn_points']
                    f=p+f'/w{n}/spawn{i}'
                    fn(f,spawn(m,pts[i%len(pts)],'wave'))
                    queue.append({'fn':'astral:'+f})
                # ceil(base * 40% * jugadores extra), repartido siguiendo la composicion base.
                lines=[f'tag @s add {key}.espera',f'tag @s add {busy}',
                       f'data modify storage {store} queue set value '+json.dumps(queue),
                       f'execute store result score @s ad.party run execute if entity @a[distance=..{r["r"]},gamemode=!spectator]',
                       'scoreboard players remove @s ad.party 2','scoreboard players set @s ad.n 0',
                       f'execute if score @s ad.party matches 1.. run scoreboard players operation @s ad.n = @s ad.party',
                       f'scoreboard players set #factor ad.n {len(base)*EXTRA_JUGADOR_PCT}',
                       'scoreboard players operation @s ad.n *= #factor ad.n',
                       'scoreboard players add @s ad.n 99','scoreboard players set #hundred ad.n 100',
                       'scoreboard players operation @s ad.n /= #hundred ad.n','scoreboard players set @s ad.i 0',
                       f'function astral:{p}/w{n}/extra', 'scoreboard players set @s ad.clock 0']
                if n==1: lines += [f'function astral:{p}/arrival']
                lines += [f'function astral:{p}/pop']*cap
                fn(p+f'/wave{n}',lines)
                extra=['execute if score @s ad.n matches ..0 run return 0']
                for i,entry in enumerate(queue):
                    extra += [f'execute if score @s ad.i matches {i} run data modify storage {store} queue append value '+json.dumps(entry)]
                extra += ['scoreboard players remove @s ad.n 1','scoreboard players add @s ad.i 1',
                          f'execute if score @s ad.i matches {len(base)}.. run scoreboard players set @s ad.i 0',
                          f'function astral:{p}/w{n}/extra']
                fn(p+f'/w{n}/extra',extra)
            fn(p+'/dispatch',['$function $(fn)'])
            fn(p+'/pop',[f'execute unless data storage {store} queue[0] run return 0',
                         f'execute store result score @s ad.alive run execute if entity {wave_sel}',
                         f'execute if score @s ad.alive matches {cap}.. run return 0',
                         f'function astral:{p}/dispatch with storage {store} queue[0]',
                         f'data remove storage {store} queue[0]'])
            fn(p+'/tick',[f'execute unless entity @s[tag={key}.on] run return 0',
                          'scoreboard players add @s ad.clock 20',
                          *[f'execute if score @s ad.clock matches {OLEADA_INTERVALO}.. run function astral:{p}/pop']*OLEADA_TANDA,
                          f'execute if score @s ad.clock matches {OLEADA_INTERVALO}.. run scoreboard players set @s ad.clock 0',
                          f'execute if data storage {store} queue[0] run tag @s add {key}.espera',
                          f'execute unless data storage {store} queue[0] run tag @s remove {key}.espera',
                          f'tag @s remove {busy}',f'execute if entity {sel} run tag @s add {busy}',
                          f'execute if data storage {store} queue[0] run tag @s add {busy}'])
