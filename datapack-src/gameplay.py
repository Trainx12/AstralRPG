"""Balance, migracion sin reemplazar inventarios y reglas de las mazmorras."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DUNGEONS=('bosque','tumba','mina','cumbre','forja','santuario')
PROTECTED=('lobby',)+DUNGEONS+('cavernas','reino','exp_desierto','exp_hielo','exp_santuario')
# Altura absoluta de rescate. Mina tiene salas bajo Y=0; no usar el mismo limite.
RESCUE_HEIGHTS={'lobby':60, 'bosque':0, 'tumba':0, 'mina':-60,
                'cumbre':0, 'forja':0, 'santuario':0}

def apply(files,items,version):
    def fn(name,lines):files[f'data/astral/function/{name}.mcfunction']='\n'.join(lines)+'\n'
    old=f'*[minecraft:custom_data~{{astral:{{}}}},!minecraft:custom_data~{{astral:{{v:{version}}}}}]'
    slots=[f'container.{n}' for n in range(36)]+['armor.head','armor.chest','armor.legs','armor.feet','weapon.offhand']
    for iid,item in items.items():
        components={k:v for k,v in item['components'].items() if k!='minecraft:enchantments'}
        modifier=[{'function':'minecraft:set_components','components':components}]
        enchant=dict(item['components'].get('minecraft:enchantments',{}))
        if iid.startswith('taladro_'):
            enchant['excellentenchants:tunnel']=0
        if enchant:modifier.append({'function':'minecraft:set_enchantments','enchantments':enchant,'add':False})
        files[f'data/astral/item_modifier/upgrade/{iid}.json']=json.dumps(modifier,ensure_ascii=False)
    for slot in slots:
        lines=[]
        for iid in items:
            selector=f'*[minecraft:custom_data~{{astral:{{id:"{iid}"}}}},!minecraft:custom_data~{{astral:{{v:{version}}}}}]'
            lines.append(f'execute if items entity @s {slot} {selector} run return run item modify entity @s {slot} astral:upgrade/{iid}')
        fn('upgrade/slot/'+slot.replace('.','_'),lines)
    fn('upgrade/check',[
        f'execute if items entity @s {slot} {old} run function astral:upgrade/slot/{slot.replace(".","_")}' for slot in slots])
    # El impulso lo aplica Skript con velocidad real; el datapack solo valida el objeto y solicita el uso.
    fn('grapple/use',['tag @s add astral.grapple.request'])
    fn('grapple/tick',['scoreboard players reset @s astral.grap'])
    hook=json.loads(files['data/astral/enchantment/gancho.json']);hook['effects']={}
    files['data/astral/enchantment/gancho.json']=json.dumps(hook)
    output=ROOT/'build/gameplay';output.mkdir(parents=True,exist_ok=True)
    (output/'astral_gameplay.sk').write_text(script(),encoding='utf-8')
    commands=[]
    for world in PROTECTED:
        commands += [f'mv gamerule set minecraft:keep_inventory true {world}']
    for world in DUNGEONS:
        commands += [f'rg flag -w {world} __global__ block-break deny',
                     f'rg flag -w {world} __global__ block-place deny',
                     f'rg flag -w {world} __global__ build deny']
    commands += ['lp group default permission set axgraves.allowgraves true']
    (output/'comandos.txt').write_text('\n'.join(commands)+'\n',encoding='utf-8')

def indicador():
    """Numeros de dano y vida del mob (reemplaza DamageIndicator).

    El dano y la vida reales son chicos (sin miles de corazones); lo que se ve es lo real
    x FACTOR_MOSTRADO del tier del mob (etiqueta astral.mt# que pone el datapack).
    """
    from escala import FACTOR_MOSTRADO
    factores = '\n'.join(f'    if scoreboard tags of {{_e}} contains "astral.mt{t}":\n        return {round(FACTOR_MOSTRADO[t], 4)}'
                         for t in range(1, 6))
    return r'''
# Indicador de dano: "-2.500" y la vida del mob, en numeros del tier (escala.py).
function astral_factor(e: entity) :: number:
__FACTORES__
    return 1

function astral_fmt(n: number) :: text:
    set {_n} to floor({_n})
    set {_out} to ""
    while {_n} >= 1000:
        set {_r} to mod({_n}, 1000)
        if {_r} < 10:
            set {_out} to ".00%{_r}%%{_out}%"
        else if {_r} < 100:
            set {_out} to ".0%{_r}%%{_out}%"
        else:
            set {_out} to ".%{_r}%%{_out}%"
        set {_n} to floor({_n} / 1000)
    return "%{_n}%%{_out}%"

function astral_dim(w: world) :: text:
    set {_name} to name of {_w}
    if {_name} contains ":":
        return {_name}
    if {_name} is "world":
        return "minecraft:overworld"
    if {_name} is "world_nether":
        return "minecraft:the_nether"
    if {_name} is "world_the_end":
        return "minecraft:the_end"
    return "minecraft:%{_name}%"

on uncancelled damage of living entity with priority monitor:
    victim is not a player
    attacker is a player
    set {_f} to astral_factor(victim)
    set {_real} to final damage * 2
    if {_real} <= 0:
        stop
    set {_vida} to (health of victim * 2) - {_real}
    if {_vida} < 0:
        set {_vida} to 0
    set {_dano} to astral_fmt({_real} * {_f})
    set {_v} to astral_fmt({_vida} * {_f})
    set {_max} to astral_fmt(max health of victim * 2 * {_f})
    set {_color} to "white"
    if damage cause is lightning:
        set {_color} to "aqua"
    else if damage cause is entity explosion or block explosion:
        set {_color} to "gold"
    else if damage cause is projectile:
        set {_color} to "yellow"
    else if damage cause is magic:
        set {_color} to "light_purple"
    set {_id} to random integer between 1 and 999999999
    set {_l} to location of victim
    set {_x} to x-coordinate of {_l} + random number between -0.4 and 0.4
    set {_y} to y-coordinate of {_l} + 2.1 + random number between 0 and 0.3
    set {_z} to z-coordinate of {_l} + random number between -0.4 and 0.4
    set {_d} to astral_dim(world of victim)
    execute console command "execute in %{_d}% run summon minecraft:text_display %{_x}% %{_y}% %{_z}% {billboard:""center"",see_through:1b,shadow:1b,background:0,Tags:[""astral.dmg"",""astral.dmg%{_id}%""],text:[{text:""-%{_dano}%"",color:""%{_color}%"",bold:1b},{text:""\n❤ %{_v}% / %{_max}%"",color:""red"",bold:0b}]}"
    wait 25 ticks
    execute console command "minecraft:kill @e[type=minecraft:text_display,tag=astral.dmg%{_id}%]"

on load:
    execute console command "minecraft:kill @e[type=minecraft:text_display,tag=astral.dmg]"
'''.replace('__FACTORES__', factores)


def script():
    worlds=' or '.join('"'+w+'"' for w in DUNGEONS)
    protected=' or '.join('"'+w+'"' for w in PROTECTED)
    rescue_options='\n'.join(f'    rescate-y-{w}: {y}' for w,y in RESCUE_HEIGHTS.items())
    rescue_limits='\n'.join(f'    if name of {{_w}} is "{w}":\n        return {{@rescate-y-{w}}}' for w in RESCUE_HEIGHTS)
    return r'''# Generado por gameplay.py. Skript 2.17+, Paper 26.1. Sin addons ni permisos de vuelo.
options:
__RESCUE_OPTIONS__

# Solo lobby y mazmorras. La altura -10000 deja fuera al resto de mundos.
function astral_rescue_height(w: world) :: number:
__RESCUE_LIMITS__
    return -10000

# Caer debajo del limite del mundo: directo a /spawn. No se guarda ninguna posicion.
function astral_rescue(p: player):
    set velocity of {_p} to vector(0, 0, 0)
    set fall distance of {_p} to 0
    execute console command "spawn %name of {_p}%"
    send action bar "&eCaiste fuera del mapa: volviste al spawn." to {_p}

function astral_dungeon(w: world) :: boolean:
    if name of {_w} is __WORLDS__:
        return true
    return false

function astral_builder(p: player) :: boolean:
    if gamemode of {_p} is creative:
        if {_p} has permission "astral.mazmorras.editar":
            return true
    return false

function astral_forbidden(p: player) :: boolean:
    loop all items in inventory of {_p}:
        if loop-item is elytra or ender pearl or chorus fruit or wind charge or water bucket:
            return true
        if loop-item is enchanted with riptide:
            return true
        if "%type of loop-item%" contains "trapdoor":
            return true
        if "%type of loop-item%" contains "boat":
            return true
        if "%type of loop-item%" contains "minecart":
            return true
    if chestplate of {_p} is elytra:
        return true
    if offhand item of {_p} is elytra or ender pearl or chorus fruit or wind charge or water bucket:
        return true
    if offhand item of {_p} is enchanted with riptide:
        return true
    return false

on teleport:
    if astral_dungeon(world of event-location) is true:
        if astral_builder(player) is false:
            if world of player is not world of event-location:
                if astral_forbidden(player) is true:
                    cancel event
                    send "&cGuarda los objetos de escape antes de entrar: elitras, perlas, chorus, trampillas, cargas de viento, Propulsion, agua, botes y vagonetas." to player

on break:
    if astral_dungeon(world of player) is true:
        if astral_builder(player) is false:
            cancel event

on place:
    if astral_dungeon(world of player) is true:
        if astral_builder(player) is false:
            cancel event

on right click:
    if astral_dungeon(world of player) is true:
        if astral_builder(player) is false:
            if player's tool is ender pearl or chorus fruit or elytra or wind charge or water bucket:
                cancel event
            if player's offhand item is ender pearl or chorus fruit or elytra or wind charge or water bucket:
                cancel event
            if player's tool is enchanted with riptide:
                cancel event
            if player's offhand item is enchanted with riptide:
                cancel event
            if "%type of player's tool%" contains "boat" or "minecart":
                cancel event
            if "%type of player's offhand item%" contains "boat" or "minecart":
                cancel event
            if "%type of event-block%" contains "trapdoor":
                cancel event

on consume of chorus fruit:
    if astral_dungeon(world of player) is true:
        cancel event

on bucket empty:
    if astral_dungeon(world of player) is true:
        if astral_builder(player) is false:
            cancel event

on mount:
    if event-entity is a player:
        if astral_dungeon(world of event-entity) is true:
            if astral_builder(event-entity) is false:
                cancel event

on death of player:
    set {_w} to name of world of victim
    if {_w} is __PROTECTED__:
        keep the inventory and experiences
        clear drops
        set {_x} to floor(x-coordinate of victim)
        set {_y} to floor(y-coordinate of victim)
        set {_z} to floor(z-coordinate of victim)
        send "&eMoriste en &f%{_w}%&e: &f%{_x}%, %{_y}%, %{_z}%&e. Conservas tus objetos." to victim
    delete {-astral.jump.used::%uuid of victim%}
    delete {-astral.launch::%uuid of victim%}

on jump:
    set {-astral.jump.armed::%uuid of player%} to true
    set {-astral.jump.first::%uuid of player%} to now

on player jump key press:
    if astral_dungeon(world of player) is true:
        stop
    if gamemode of player is not survival:
        if gamemode of player is not adventure:
            stop
    if player is on ground:
        stop
    if player is swimming:
        stop
    if player is flying:
        stop
    if {-astral.jump.armed::%uuid of player%} is not true:
        stop
    if {-astral.jump.used::%uuid of player%} is true:
        stop
    if difference between now and {-astral.jump.first::%uuid of player%} is less than 150 milliseconds:
        stop
    set {-astral.jump.used::%uuid of player%} to true
    set {_v} to velocity of player
    set y component of {_v} to 0.65
    set velocity of player to {_v}
    play sound "entity.breeze.jump" with volume 0.4 and pitch 1.4 at player

every tick:
    loop all players:
        set {_id} to uuid of loop-player
        set {_limit} to astral_rescue_height(world of loop-player)
        if {_limit} is not -10000:
            if gamemode of loop-player is survival or adventure:
                if y-coordinate of loop-player is less than {_limit}:
                    astral_rescue(loop-player)
                    continue
        if astral_dungeon(world of loop-player) is true:
            if astral_builder(loop-player) is false:
                set {_world} to name of world of loop-player
                if loop-player is swimming:
                    if {-astral.dry::%{_id}%::%{_world}%} is set:
                        teleport loop-player to {-astral.dry::%{_id}%::%{_world}%}
                    else:
                        execute console command "spawn %name of loop-player%"
                    continue
                if loop-player is on ground:
                    if block at loop-player is not water:
                        set {-astral.dry::%{_id}%::%{_world}%} to location of loop-player
                if chestplate of loop-player is elytra:
                    execute console command "spawn %name of loop-player%"
                    send "&cNo puedes equipar elitras dentro de una mazmorra. Conservas el objeto." to loop-player
                    continue
        if loop-player is on ground:
            delete {-astral.jump.used::%{_id}%}
            if {-astral.launch.air::%{_id}%} is true:
                delete {-astral.launch::%{_id}%}
                delete {-astral.launch.air::%{_id}%}
        else:
            if {-astral.launch::%{_id}%} is set:
                set {-astral.launch.air::%{_id}%} to true
        if scoreboard tags of loop-player contains "astral.grapple.request":
            remove "astral.grapple.request" from scoreboard tags of loop-player
            if astral_dungeon(world of loop-player) is true:
                send action bar "&cEl gancho no se puede usar dentro de las mazmorras." to loop-player
                continue
            if {-astral.grapple.cd::%{_id}%} is set:
                if difference between now and {-astral.grapple.cd::%{_id}%} is less than 2 seconds:
                    continue
            if gamemode of loop-player is spectator:
                continue
            set {-astral.grapple.cd::%{_id}%} to now
            set {_v} to vector from yaw (yaw of loop-player) and pitch (pitch of loop-player)
            set x component of {_v} to (x component of {_v}) * 1.25
            set y component of {_v} to (y component of {_v}) * 1.25
            set z component of {_v} to (z component of {_v}) * 1.25
            if y component of {_v} is less than 0.9:
                set y component of {_v} to 0.9
            set velocity of loop-player to {_v}
            set {-astral.launch::%{_id}%} to now
            delete {-astral.launch.air::%{_id}%}
            play sound "entity.fishing_bobber.throw" with volume 0.6 and pitch 1.1 at loop-player
        if {-astral.launch::%{_id}%} is set:
            if difference between now and {-astral.launch::%{_id}%} is greater than 30 seconds:
                delete {-astral.launch::%{_id}%}
                delete {-astral.launch.air::%{_id}%}

on damage of player:
    if damage cause is fall:
        if {-astral.launch::%uuid of victim%} is set:
            cancel event
            delete {-astral.launch::%uuid of victim%}
            delete {-astral.launch.air::%uuid of victim%}

on quit:
    delete {-astral.jump.used::%uuid of player%}
    delete {-astral.jump.armed::%uuid of player%}
    delete {-astral.grapple.cd::%uuid of player%}
    delete {-astral.launch::%uuid of player%}
    delete {-astral.launch.air::%uuid of player%}
__INDICADOR__'''.replace('__INDICADOR__',indicador()).replace('__WORLDS__',worlds).replace('__PROTECTED__',protected).replace('__RESCUE_OPTIONS__',rescue_options).replace('__RESCUE_LIMITS__',rescue_limits)

def patch_graves(config):
    """Conservar objetos en la tumba hasta recogerlos; respetar keep_inventory."""
    config=dict(config)
    config['despawn-time-seconds']=-1
    config['store-items']=True
    config['override-keep-inventory']=False
    config['override-keep-level']=False
    config['death-listener-priority']='LOW'
    config['disabled-worlds']=list(dict.fromkeys(config.get('disabled-worlds',[])+list(PROTECTED)))
    return config

def prepare_plugin_configs():
    import yaml
    out=ROOT/'build/gameplay'
    before=ROOT/'.local'
    config=yaml.safe_load((before/'axgraves-antes-balance.yml').read_text(encoding='utf-8'))
    messages=yaml.safe_load((before/'axgraves-messages-antes-balance.yml').read_text(encoding='utf-8'))
    messages['death-message']={'enabled':True,'message':'&eMoriste en &f%world%&e, coordenadas &f%x%, %y%, %z%&e.'}
    for name,data in [('config.yml',patch_graves(config)),('messages.yml',messages)]:
        path=out/'AxGraves'/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding='utf-8')
    for skill in ('mining','foraging'):
        data=yaml.safe_load((before/f'auraskills-{skill}-actual.yml').read_text(encoding='utf-8'))
        # Lista explicita: solo las fuentes naturales actuales, nunca contenedores ni bloques de recursos.
        denied={'diamond_block','emerald_block','gold_block','iron_block','copper_block','netherite_block','beacon','chest','barrel'}
        allowed=[key for key,source in data['sources'].items() if source.get('block','') not in denied and 'shulker' not in source.get('block','')]
        data['tags'][skill+'_luck_applicable']=allowed
        data['default']['check_replace']=True
        path=out/'AuraSkills'/f'{skill}.yml';path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding='utf-8')

if __name__=='__main__':
    prepare_plugin_configs()
    (ROOT/'build/gameplay/astral_gameplay.sk').write_text(script(),encoding='utf-8')
    selector='@e[type=minecraft:armor_stand,tag=astral.balance_test,limit=1]'
    commands=[
        'execute in minecraft:lobby run forceload add 178 225',
        'execute in minecraft:lobby unless entity '+selector+' run summon minecraft:armor_stand 178.636 104 225.735 {Tags:["astral.balance_test"],Invisible:1b,Marker:1b,NoGravity:1b,Invulnerable:1b}',
        f'execute in minecraft:lobby run minecraft:loot replace entity {selector} armor.head loot astral:item/berserker_1_helmet',
        f'execute in minecraft:lobby run minecraft:item modify entity {selector} armor.head '+
        '{function:"minecraft:set_components",components:{"minecraft:damage":117,"minecraft:trim":{material:"minecraft:gold",pattern:"minecraft:coast"}}}',
        f'execute in minecraft:lobby run minecraft:item modify entity {selector} armor.head '+
        '{function:"minecraft:set_enchantments",enchantments:{"astral:mejora_armadura":7,"minecraft:thorns":3},add:false}',
        f'execute in minecraft:lobby run minecraft:item modify entity {selector} armor.head '+
        '{function:"minecraft:set_custom_data",tag:{astral:{v:3}}}',
        f'execute in minecraft:lobby as {selector} run function astral:upgrade/slot/armor_head',
        *[f'execute in minecraft:lobby run minecraft:data get entity {selector} equipment.head.components."minecraft:{key}"' for key in ('custom_data','damage','enchantments','trim','max_damage')],
        f'execute in minecraft:lobby run minecraft:item replace entity {selector} armor.head with minecraft:air',
        f'execute in minecraft:lobby run minecraft:item replace entity {selector} weapon.mainhand with minecraft:air',
        f'execute in minecraft:lobby run minecraft:kill {selector}',
        'execute in minecraft:lobby run forceload remove 178 225',
    ]
    (ROOT/'build/gameplay/prueba-equipo.txt').write_text('\n'.join(commands)+'\n',encoding='utf-8')
