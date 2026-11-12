"""Panel por jugador y bossbar independiente por sala, sin plugins adicionales."""
import json

OBJECTIVES=('ad.room','ad.wave','ad.total','ad.left','ad.max','ad.pending')


def generate(files, dungeons):
    """Una barra por sala y por copia (instancias.py). Todo selector se limita al mundo (distance=0..)."""
    from instancias import copias
    root='data/astral/function/'
    def fn(path, lines): files[root+path+'.mcfunction']='\n'.join(lines)+'\n'
    def suffix(c): return '' if c==1 else f'_c{c}'
    load=[]; tick=['scoreboard players set @a ad.room 0','scoreboard players set @a ad.left 0']
    for objective in OBJECTIVES:
        load.append(f'scoreboard objectives add {objective} dummy')
    rooms=[(d,r) for d in dungeons for r in d['rooms']]
    for index,(d,r) in enumerate(rooms,1):
        key=d['key']; p=f'tanda2/{key}/{r["id"]}'; label=r['name']; t=f'ad.{key}.{r["id"]}'
        worlds=copias(d['world'])
        # La seleccion de sala usa la mas cercana al jugador. Resuelve radios
        # superpuestos (Cumbre) sin sumar participantes de la sala anterior.
        member=f'@a[tag=ad.ui.{index},gamemode=!spectator,distance=0..]'
        for c,world in enumerate(worlds,1):
            bar='astral:'+p+suffix(c)
            tick.append(f'bossbar set {bar} players')
            tick.append(f'execute in minecraft:{world} as @a[gamemode=!spectator,distance=0..] at @s if entity @e[type=armor_stand,name={json.dumps("Control "+label,ensure_ascii=False)},distance=..{r["r"]},sort=nearest,limit=1] run function astral:{p}/ui_join')
            load += [f'bossbar add {bar} {json.dumps(label,ensure_ascii=False)}',
                     f'bossbar set {bar} color purple', f'bossbar set {bar} players']
        # No inferir sala por distancia al mob: solamente controladores conocidos (de este mundo).
        join=[]
        for j,rr in enumerate(d['rooms']):
            join.append(f'tag @e[type=armor_stand,name={json.dumps("Control "+rr["name"],ensure_ascii=False)},distance=0..] add ad.ui.control')
        join += ['tag @e[tag=ad.ui.control,distance=0..,sort=nearest,limit=1] add ad.ui.nearest',
                 f'execute if entity @e[tag=ad.ui.nearest,distance=0..,name={json.dumps("Control "+label,ensure_ascii=False)}] run tag @s add ad.ui.{index}',
                 'tag @e[tag=ad.ui.control,distance=0..] remove ad.ui.nearest','tag @e[tag=ad.ui.control,distance=0..] remove ad.ui.control']
        fn(p+'/ui_join',join)
        live=f'@e[tag={t},distance=0..,nbt=!{{Health:0.0f}}]'
        if not r.get('boss_room'):
            for n in range(1,len(r['oleadas'])+1):
                file=root+p+f'/wave{n}.mcfunction'
                files[file]=f'scoreboard players set @s ad.wave {n}\n'+files[file]+f'function astral:{p}/ui_start\n'
            fn(p+'/ui_start',['scoreboard players operation @s ad.max = @s ad.qm',
                              'scoreboard players operation @s ad.max -= @s ad.q',
                              f'execute store result score #live ad.left run execute if entity {live}',
                              'scoreboard players operation @s ad.max += #live ad.left'])
        else:
            file=root+p+'/companions.mcfunction'
            files[file]='scoreboard players set @s ad.wave 0\n'+files[file]
        for c,world in enumerate(worlds,1):
            bar='astral:'+p+suffix(c); left=f'#left{index}c{c}'; wave=f'#wave{index}c{c}'
            lines=[f'execute store result score @s ad.left run execute if entity {live}',
                   'scoreboard players operation @s ad.pending = @s ad.qm',
                   'scoreboard players operation @s ad.pending -= @s ad.q',
                   'execute if score @s ad.pending matches ..-1 run scoreboard players set @s ad.pending 0',
                   'scoreboard players operation @s ad.left += @s ad.pending',
                   f'execute unless entity @s[tag={key}.on] run return 0',
                   f'execute if entity @s[tag={key}.fin] run return 0',
                   f'scoreboard players set {member} ad.room {index}',
                   f'scoreboard players set {member} ad.total {len(r["oleadas"])}',
                   f'execute as {member} run scoreboard players operation @s ad.wave = @e[tag=ad.ui.source,distance=0..,limit=1] ad.wave',
                   f'execute as {member} run scoreboard players operation @s ad.left = @e[tag=ad.ui.source,distance=0..,limit=1] ad.left']
            if not r.get('boss_room'):
                lines += ['execute if score @s ad.left > @s ad.max run scoreboard players operation @s ad.max = @s ad.left',
                          f'execute store result bossbar {bar} max run scoreboard players get @s ad.max',
                          f'execute store result bossbar {bar} value run scoreboard players get @s ad.left',
                          f'scoreboard players operation {left} ad.left = @s ad.left',
                          f'scoreboard players operation {wave} ad.wave = @s ad.wave']
                title=[{'text':'Oleada '},{'score':{'name':wave,'objective':'ad.wave'}},
                       {'text':f'/{len(r["oleadas"])} - '},{'score':{'name':left,'objective':'ad.left'}},{'text':' restantes'}]
                lines += [f'bossbar set {bar} name '+json.dumps(title,ensure_ascii=False),f'bossbar set {bar} players {member}']
            fn(p+'/ui'+suffix(c),lines)
    # Todos los joins deben preceder a las actualizaciones.
    for index,(d,r) in enumerate(rooms,1):
        p=f'tanda2/{d["key"]}/{r["id"]}'
        selector=f'@e[type=armor_stand,name={json.dumps("Control "+r["name"],ensure_ascii=False)},distance=0..,limit=1]'
        for c,world in enumerate(copias(d['world']),1):
            tick += [f'execute in minecraft:{world} as {selector} at @s run tag @s add ad.ui.source',
                     f'execute in minecraft:{world} as {selector} at @s run function astral:{p}/ui{suffix(c)}',
                     f'execute in minecraft:{world} run tag @e[tag=ad.ui.source,distance=0..] remove ad.ui.source']
        tick.append(f'tag @a remove ad.ui.{index}')
    files[root+'load.mcfunction']+='\n'+'\n'.join(load)+'\n'
    fn('tanda2/ui_tick',tick)
    files.setdefault(root+'loop/t20.mcfunction','')
    files[root+'loop/t20.mcfunction']+='function astral:tanda2/ui_tick\n'


def sidebar_conditions():
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    ds=[MINA]+[d for d in catalog() if d['key']!='santuario']
    from instancias import copias, bukkit
    lines=['  ad_dungeon:','    type: OR','    conditions:',*[f'      - "%world%={bukkit(w)}"' for d in ds for w in copias(d['world'])], '    true: "true"','    false: "false"']; index=0
    for d in ds:
        for r in d['rooms']:
            index+=1
            lines += [f'  ad_room_{index}:', '    conditions:',f'      - "%objective_score_{{ad.room}}%={index}"',
                      f'    true: "{r["name"]}"',f'    false: "%condition:ad_room_{index+1}%"']
    lines[-1]='    false: "Esperando sala"'
    lines += ['  ad_phase:', '    conditions:', '      - "%objective_score_{ad.wave}%=0"',
              '    true: "Jefe"','    false: "Oleada %objective_score_{ad.wave}%/%objective_score_{ad.total}%"',
              '  ad_active:', '    conditions:', '      - "%objective_score_{ad.room}%>0"',
              '    true: "%condition:ad_phase%"','    false: "Esperando sala"']
    return '\n'.join(lines)+'\n'
