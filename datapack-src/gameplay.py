"""Balance, migracion sin reemplazar inventarios y reglas de las mazmorras."""
import json
from santuario_azeroth import BUKKIT_WORLD as SANCTUARY_BUKKIT_WORLD, ARRIVAL as SANCTUARY_ARRIVAL, ARRIVAL_YAW as SANCTUARY_YAW, ARRIVAL_SPREAD as SANCTUARY_SPREAD
from pathlib import Path
from minijuegos import parkour_worlds, arena_worlds

ROOT=Path(__file__).resolve().parent.parent
from instancias import expand, expand_map
# expand suma las 6 copias de cada mazmorra (instancias.py).
DUNGEONS=expand(('bosque','tumba','mina','cumbre','forja','santuario',
          # mundos actuales de Cumbre, Forja y Santuario (08/11/2026)
          'cumbre_hielo','forja_volcano','santuario_interstellar','santuario_azeroth',SANCTUARY_BUKKIT_WORLD))
PROTECTED=('lobby',)+DUNGEONS+('cavernas','reino','exp_desierto','exp_hielo','exp_santuario')
# Altura absoluta de rescate. Mina tiene salas bajo Y=0; no usar el mismo limite.
RESCUE_HEIGHTS=expand_map({'lobby':60, 'bosque':0, 'tumba':0, 'mina':-60,
                'cumbre':0, 'forja':0, 'santuario':0, 'santuario_azeroth':0, SANCTUARY_BUKKIT_WORLD:0})

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
        for iid,item in items.items():
            selector=f'*[minecraft:custom_data~{{astral:{{id:"{iid}"}}}},!minecraft:custom_data~{{astral:{{v:{version}}}}}]'
            if item.get('mejorable'):
                mej='mejora_armadura' if item['kind']=='armor' else 'mejora_arma'
                for level in range(1,11):
                    upgraded=selector[:-1]+f',minecraft:enchantments~[{{enchantments:"astral:{mej}",levels:{level}}}]]'
                    lines.append(f'execute if items entity @s {slot} {upgraded} run return run item modify entity @s {slot} astral:upgrade/{iid}/{level}')
            lines.append(f'execute if items entity @s {slot} {selector} run return run item modify entity @s {slot} astral:upgrade/{iid}')
        fn('upgrade/slot/'+slot.replace('.','_'),lines)
    # Reparacion puntual incluso en v15; no reconstruye items ni toca mejoras.
    helmet_old='*[minecraft:custom_data~{astral:{id:"carnivora_helmet"}},minecraft:equippable~{asset_id:"astral:carnivora"}]'
    files['data/astral/item_modifier/carnivora_head.json']=json.dumps({
        'function':'minecraft:set_components','components':{'minecraft:equippable':{'slot':'head'}}})
    fn('upgrade/carnivora_head',[
        f'execute unless items entity @s container.* {helmet_old} unless items entity @s armor.head {helmet_old} unless items entity @s weapon.offhand {helmet_old} run return 0',
    ]+[f'execute if items entity @s {slot} {helmet_old} run item modify entity @s {slot} astral:carnivora_head' for slot in slots])
    fn('upgrade/check',['function astral:upgrade/carnivora_head']+[
        f'execute if items entity @s {slot} {old} run function astral:upgrade/slot/{slot.replace(".","_")}' for slot in slots])
    # El impulso lo aplica Skript con velocidad real; el datapack solo valida el objeto y solicita el uso.
    fn('grapple/use',['tag @s add astral.grapple.request'])
    fn('grapple/tick',['scoreboard players reset @s astral.grap'])
    fn('grapple/realistic_check',[
        'tag @s remove astral.realistic.held',
        'execute if items entity @s weapon.mainhand minecraft:fishing_rod[minecraft:custom_data~{astral:{id:"gancho_realista"}}] run tag @s add astral.realistic.held'])
    hook=json.loads(files['data/astral/enchantment/gancho.json']);hook['effects']={}
    files['data/astral/enchantment/gancho.json']=json.dumps(hook)
    output=ROOT/'build/gameplay';output.mkdir(parents=True,exist_ok=True)
    generate_action_bar(output)
    (output/'astral_gameplay.sk').write_text(script(),encoding='utf-8')
    commands=[]
    for world in PROTECTED:
        if 'santuario_azeroth' in world:
            continue  # esta dimension pertenece al datapack, no a Multiverse
        commands += [f'mv gamerule set minecraft:keep_inventory true {world}']
    commands += ['execute in minecraft:santuario_azeroth run gamerule minecraft:keep_inventory true']
    for world in DUNGEONS:
        if world.startswith('santuario_azeroth'):
            continue  # WorldGuard identifica el nombre Bukkit
        commands += [f'rg flag -w {world} __global__ block-break deny',
                     f'rg flag -w {world} __global__ block-place deny',
                     f'rg flag -w {world} __global__ build deny']
    commands += ['lp group default permission set axgraves.allowgraves true']
    (output/'comandos.txt').write_text('\n'.join(commands)+'\n',encoding='utf-8')

def generate_action_bar(output):
    # Defensa directa: evita depender de claves de mensaje adicionales en AuraSkills.
    block = {
        'idle': '{{action_bar.hp_display}}      <green>%objective_score_astraldef%❈ Defensa      {{action_bar.mana_display}}',
        'hp_display': '<red>{hp}/{max_hp}❤',
        'mana_display': '<aqua>{mana}/{max_mana}✎ Maná',
        'xp': '{{action_bar.hp_display}}  <gold>{xp_gained} {skill} {{units.xp}} <gray>({current_xp}/{level_xp} {{units.xp}})  {{action_bar.mana_display}}',
        'maxed': '{{action_bar.hp_display}}  <gold>{xp_gained} {skill} {{units.xp}} <gray>({{ui.maxed}})  {{action_bar.mana_display}}',
        'ability': '{message}',
        'boss_bar_xp': '<gold>{xp_gained} {skill} {{units.xp}} <gray>({percent}%)',
        'boss_bar_maxed': '<gold>{xp_gained} {skill} {{units.xp}} <gray>({{ui.maxed}})',
        'boss_bar_income': '<gold>{xp_gained} {skill} {{units.xp}} <gray>({percent}%) <green>(+${income})',
        'boss_bar_income_maxed': '<gold>{xp_gained} {skill} {{units.xp}} <gray>({{ui.maxed}}) <green>(+${income})',
    }
    from escala import MANA_BASE, REGEN_BASE
    # Mana base y regeneracion de AuraSkills (referencia Hypixel): se editan a mano en el server.
    (output/'AuraSkills').mkdir(parents=True,exist_ok=True)
    (output/'AuraSkills/stats-mana.txt').write_text(
        'plugins/AuraSkills/stats.yml (seccion traits:), despues "skills reload":\n'
        f'  auraskills/max_mana:\n    base: {MANA_BASE}\n'
        f'  auraskills/mana_regen:\n    base: {REGEN_BASE}\n'
        'Sale de datapack-src/escala.py (MANA_BASE, REGEN_BASE). mana_regen = mana por segundo.\n',encoding='utf-8')
    path=output/'AuraSkills/global-action_bar.yml'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('action_bar:\n'+''.join(f'  {key}: '+json.dumps(value,ensure_ascii=False)+'\n' for key,value in block.items()),encoding='utf-8')

def pvp():
    """Arena PvP: el dano de las armas Astral es enorme (escala.py); entre jugadores se
    divide por el factor del arma del atacante, asi el PvP queda como antes."""
    from escala import FACTOR_ARMA
    lines = ['# Arena PvP: dano de armas Astral dividido por su factor (escala.py).',
             'on damage of player with priority low:', '    attacker is a player',
             '    name of world of victim is ' + ' or '.join(f'"{w}"' for w in arena_worlds())]
    for t in range(1, 6):
        lines.append(f'    if scoreboard tags of attacker contains "astral.ht{t}":')
        lines.append(f'        set damage to damage / {round(FACTOR_ARMA[t], 3)}')
    return chr(10).join(lines) + chr(10)


def vida():
    """Escala de vida (escala.py): mobs con tier pegan DANO_GOLPE; lo demas, en proporcion a la vida."""
    from escala import DANO_MOB, TIER_MAZMORRA
    tiers = '\n'.join(f'    if scoreboard tags of {{_e}} contains "astral.mt{t}":\n        return {DANO_MOB[t]}'
                      for t in range(5, 0, -1))
    # Las dimensiones del datapack se llaman world_minecraft_<dim> en Bukkit (el Santuario y sus copias).
    mundos = '\n'.join(f'    if {{_n}} is "{w}" or "minecraft:{w}" or "world_minecraft_{w}":\n        return {DANO_MOB[t]}'
                       for w, t in TIER_MAZMORRA.items())
    mundos += f'\n    if {{_n}} is "{SANCTUARY_BUKKIT_WORLD}":\n        return {DANO_MOB[5]}'
    return r'''
# Escala de vida (escala.py, referencia Hypixel): el jugador tiene 100 de vida base y la armadura suma mucho.
# - Mob con tier (astral.mt#): su golpe, flecha o explosion x DANO_MOB del tier.
# - Mob sin tier dentro de una mazmorra (jefes de MythicMobs): x DANO_MOB del tier de la mazmorra.
# - Todo lo demas (caidas, lava, ahogo, mobs sin tier, PvP): x (vida maxima / 20), como en vanilla.
function astral_dano_tier(e: entity) :: number:
__TIERS__
    return 0

function astral_dano_mundo(w: world) :: number:
    set {_n} to name of {_w}
__MUNDOS__
    return 0

# Defensa Astral del jugador (etiquetas astral.db0..db11 del datapack, en binario).
function astral_defensa(p: player) :: number:
    set {_d} to 0
    set {_v} to 1
    loop 12 times:
        if scoreboard tags of {_p} contains "astral.db%loop-number - 1%":
            add {_v} to {_d}
        set {_v} to {_v} * 2
    return {_d}

on damage of player with priority high:
    set {_k} to (max health of victim) / 10
    if attacker is set:
        if attacker is not a player:
            set {_m} to astral_dano_tier(attacker)
            if {_m} is 0:
                set {_m} to astral_dano_mundo(world of victim)
            if {_m} > 0:
                set {_k} to {_m}
        # Defensa (Hypixel): golpes, flechas, explosiones y PvP x 100 / (defensa + 100).
        set {_d} to astral_defensa(victim)
        if {_k} > 1:
            set damage to damage * {_k}
        if {_d} > 0:
            set damage to damage * 100 / ({_d} + 100)
        stop
    if {_k} > 1:
        set damage to damage * {_k}

# Regeneracion natural, pociones y robo de vida: tambien en proporcion a la vida maxima.
on heal of player:
    heal reason is not custom
    set {_k} to (max health of player) / 10
    if {_k} > 1:
        set heal amount to heal amount * {_k}
'''.replace('__TIERS__', tiers).replace('__MUNDOS__', mundos)


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
    # Solo mazmorras: los mini juegos guardan el inventario al entrar y sus mapas necesitan poner
    # bloques, perlas, elitros, agua y monturas (Color Escape, Paradise 3, droppers). 08/11/2026.
    worlds=' or '.join('"'+w+'"' for w in DUNGEONS)
    protected=' or '.join('"'+w+'"' for w in PROTECTED + parkour_worlds() + arena_worlds())
    rescue_options='\n'.join(f'    rescate-y-{w}: {y}' for w,y in RESCUE_HEIGHTS.items())
    rescue_limits='\n'.join(f'    if name of {{_w}} is "{w}":\n        return {{@rescate-y-{w}}}' for w in RESCUE_HEIGHTS)
    return r'''# Generado por gameplay.py. Skript 2.17+, Paper 26.1. Sin addons ni permisos de vuelo.
options:
__RESCUE_OPTIONS__

# Solo lobby y mazmorras. La altura -10000 deja fuera al resto de mundos.
function astral_rescue_height(w: world) :: number:
__RESCUE_LIMITS__
    return -10000

# Santuario vuelve a su entrada; el resto conserva su rescate al lobby.
function astral_rescue(p: player):
    set velocity of {_p} to vector(0, 0, 0)
    set fall distance of {_p} to 0
    if name of world of {_p} contains "santuario_azeroth":
        # En la misma copia del Santuario donde estaba (instancias.py).
        execute console command "execute as %name of {_p}% at @s run minecraft:tp @s __SANCT_TP__ __SANCT_YAW__ 0"
        set fall distance of {_p} to 0
        send action bar "&eCaiste al vacio: volviste a la entrada del Santuario." to {_p}
        stop
    execute console command "spawn %name of {_p}%"
    send action bar "&eCaiste fuera del mapa: volviste al spawn." to {_p}

# Santuario: si ya hay alguien en la entrada, el que llega queda al costado (2, -2, 4, -4...).
on world change:
    if name of player's world contains "santuario_azeroth":
        wait 2 ticks
        set {_entrada} to location(__SANCT_X__, __SANCT_Y__, __SANCT_Z__, world of player, __SANCT_YAW__, 0)
        if distance between player and {_entrada} > 1.5:
            stop
        set {_n} to 0
        loop players in world of player:
            loop-player is not player
            distance between loop-player and {_entrada} < 10
            add 1 to {_n}
        if {_n} > 0:
            set {_dx} to ceil({_n} / 2) * __SANCT_SPREAD__
            if mod({_n}, 2) is 0:
                set {_dx} to -1 * {_dx}
            teleport player to location(__SANCT_X__ + {_dx}, __SANCT_Y__, __SANCT_Z__, world of player, __SANCT_YAW__, 0)

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
    else:
        # Fuera de las zonas protegidas AxGraves deja una tumba: se recuerda donde al reaparecer.
        set {-astral.tumba::%uuid of victim%} to "&f%{_w}% &e(&f%floor(x-coordinate of victim)%, %floor(y-coordinate of victim)%, %floor(z-coordinate of victim)%&e)"
    delete {-astral.jump.used::%uuid of victim%}
    delete {-astral.launch::%uuid of victim%}

on respawn:
    if {-astral.tumba::%uuid of player%} is set:
        wait 1 second
        send "&6&lTus cosas quedaron en una tumba: %{-astral.tumba::%uuid of player%}%" to player
        send "&7Volve a ese lugar y abrila con clic para recuperarlas." to player
        delete {-astral.tumba::%uuid of player%}

on jump:
    set {-astral.jump.armed::%uuid of player%} to true
    delete {-astral.jump.released::%uuid of player%}

on player jump key release:
    if {-astral.jump.armed::%uuid of player%} is true:
        set {-astral.jump.released::%uuid of player%} to true

on player jump key press:
    if astral_dungeon(world of player) is true:
        stop
    if gamemode of player is not survival:
        if gamemode of player is not adventure:
            stop
    if player is on ground:
        if y component of velocity of player <= 0:
            stop
    if player is swimming:
        stop
    if player is flying:
        stop
    if {-astral.jump.armed::%uuid of player%} is not true:
        stop
    if {-astral.jump.used::%uuid of player%} is true:
        stop
    if {-astral.jump.released::%uuid of player%} is not true:
        stop
    set {-astral.jump.used::%uuid of player%} to true
    delete {-astral.jump.armed::%uuid of player%}
    delete {-astral.jump.released::%uuid of player%}
    # El server no conoce bien la velocidad lateral del jugador (la mueve el cliente): se usa
    # cuanto se movio en el ultimo tick, asi el doble salto conserva el impulso y no frena en seco.
    set {_v} to vector(0, 0.65, 0)
    set {_move} to {-astral.lastmove::%uuid of player%}
    if {_move} is set:
        set {_vx} to x component of {_move}
        set {_vz} to z component of {_move}
        set {_h} to sqrt({_vx} * {_vx} + {_vz} * {_vz})
        if {_h} > 0.6:
            set {_vx} to {_vx} * 0.6 / {_h}
            set {_vz} to {_vz} * 0.6 / {_h}
        set {_v} to vector({_vx} * 1.1, 0.65, {_vz} * 1.1)
    set velocity of player to {_v}
    play sound "entity.breeze.jump" with volume 0.4 and pitch 1.4 at player

every tick:
    loop all players:
        set {_id} to uuid of loop-player
        # Movimiento del ultimo tick (posicion actual - la del tick anterior): lo usa el doble
        # salto para saber hacia donde ibas. El cliente manda el salto antes que su posicion.
        set {_now} to location of loop-player
        set {_prev} to {-astral.lastpos::%{_id}%}
        set {-astral.lastpos::%{_id}%} to {_now}
        delete {-astral.lastmove::%{_id}%}
        if {_prev} is set:
            if world of {_prev} is world of {_now}:
                set {-astral.lastmove::%{_id}%} to vector from {_prev} to {_now}
        set {_limit} to astral_rescue_height(world of loop-player)
        if {_limit} is not -10000:
            if gamemode of loop-player is survival or adventure:
                if y-coordinate of loop-player is less than {_limit}:
                    astral_rescue(loop-player)
                    continue
        if astral_dungeon(world of loop-player) is true:
            if astral_builder(loop-player) is false:
                # Se puede nadar (pedido del dueno, 08/11/2026: el agua trababa Minas Olvidadas).
                if chestplate of loop-player is elytra:
                    execute console command "spawn %name of loop-player%"
                    send "&cNo puedes equipar elitras dentro de una mazmorra. Conservas el objeto." to loop-player
                    continue
        if loop-player is on ground:
            if y component of velocity of loop-player <= 0:
                delete {-astral.jump.used::%{_id}%}
                delete {-astral.jump.armed::%{_id}%}
                delete {-astral.jump.released::%{_id}%}
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

__REALISTIC_HOOK__

on quit:
    delete {-astral.lastpos::%uuid of player%}
    delete {-astral.lastmove::%uuid of player%}
    delete {-astral.jump.used::%uuid of player%}
    delete {-astral.jump.armed::%uuid of player%}
    delete {-astral.jump.released::%uuid of player%}
    delete {-astral.grapple.cd::%uuid of player%}
    astral_hook_clear(player)
    delete {-astral.launch::%uuid of player%}
    delete {-astral.launch.air::%uuid of player%}
__INDICADOR__
__PVP__
__VIDA__'''.replace('__VIDA__',vida()).replace('__REALISTIC_HOOK__',realistic_hook()).replace('__INDICADOR__',indicador()).replace('__PVP__',pvp()).replace('__WORLDS__',worlds).replace('__PROTECTED__',protected).replace('__RESCUE_OPTIONS__',rescue_options).replace('__RESCUE_LIMITS__',rescue_limits).replace('__SANCT_TP__',' '.join(map(str,SANCTUARY_ARRIVAL))).replace('__SANCT_YAW__',str(SANCTUARY_YAW)).replace('__SANCT_X__',str(SANCTUARY_ARRIVAL[0])).replace('__SANCT_Y__',str(SANCTUARY_ARRIVAL[1])).replace('__SANCT_Z__',str(SANCTUARY_ARRIVAL[2])).replace('__SANCT_SPREAD__',str(SANCTUARY_SPREAD))


def realistic_hook():
    return r'''
# FishingHook aplica -0.03 incluso con NoGravity: compensar y fijar el anclaje.
function astral_hook_clear(p: player):
    set {_id} to uuid of {_p}
    set {_hook} to {-astral.realistic::%{_id}%::hook}
    delete {-astral.realistic::%{_id}%}
    delete {-astral.realistic::%{_id}%::*}
    if {_hook} is set:
        if {_hook} is valid:
            kill {_hook}

on unload:
    loop all players:
        astral_hook_clear(loop-player)

# La boya vanilla rebota en paredes. Detectamos el contacto por sus caras.
function astral_hook_contact(at: location) :: block:
    set {_offsets::*} to vector(0, 0, 0), vector(0.18, 0, 0), vector(-0.18, 0, 0), vector(0, 0.28, 0), vector(0, -0.18, 0), vector(0, 0, 0.18) and vector(0, 0, -0.18)
    loop {_offsets::*}:
        set {_probe} to {_at} offset by loop-value
        if block at {_probe} is solid:
            return block at {_probe}

every tick:
    loop all players:
        set {_id} to uuid of loop-player
        set {_hook} to {-astral.realistic::%{_id}%::hook}
        if {_hook} is not set:
            continue
        if {_hook} is not valid:
            astral_hook_clear(loop-player)
            continue
        if world of {_hook} is not world of loop-player:
            astral_hook_clear(loop-player)
            continue
        if distance between {_hook} and loop-player > 32:
            astral_hook_clear(loop-player)
            continue
        if {-astral.realistic::%{_id}%::anchor} is set:
            if {-astral.realistic::%{_id}%::block} is not solid:
                astral_hook_clear(loop-player)
                send action bar "&7El bloque del anclaje desaparecio." to loop-player
                continue
            set gravity of {_hook} to false
            teleport {_hook} to {-astral.realistic::%{_id}%::anchor}
            set velocity of {_hook} to vector(0, 0.03, 0)
            continue
        set {_block} to astral_hook_contact(location of {_hook})
        if {_block} is set:
            # No se engancha al piso bajo los pies al lanzar.
            if distance between {_hook} and eye location of loop-player < 1.5:
                continue
            set {-astral.realistic::%{_id}%::anchor} to location of {_hook}
            set {-astral.realistic::%{_id}%::block} to {_block}
            set gravity of {_hook} to false
            set velocity of {_hook} to vector(0, 0.03, 0)
            teleport {_hook} to {-astral.realistic::%{_id}%::anchor}
            play sound "block.chain.hit" with volume 0.6 and pitch 1.4 at {_hook}
            send action bar "&dGancho anclado. Clic derecho para tirar." to loop-player

# La identidad se valida con custom_data en el momento del evento, no por nombre.
# Cada lanzamiento pertenece a un jugador y a un anzuelo concreto.
on fishing state change:
    set {_id} to uuid of player
    execute console command "execute as %name of player% run function astral:grapple/realistic_check"
    set {_real} to false
    if scoreboard tags of player contains "astral.realistic.held":
        set {_real} to true
    remove "astral.realistic.held" from scoreboard tags of player
    if event-fishing state is fishing line cast:
        astral_hook_clear(player)
        if {_real} is false:
            stop
        if astral_dungeon(world of player) is true:
            cancel event
            send action bar "&cEl gancho no se puede usar dentro de las mazmorras." to player
            stop
        if gamemode of player is spectator:
            cancel event
            stop
        set {-astral.realistic::%{_id}%} to uuid of fishing hook
        set {-astral.realistic::%{_id}%::hook} to fishing hook
        stop
    if {-astral.realistic::%{_id}%} is not set:
        stop
    if uuid of fishing hook is not {-astral.realistic::%{_id}%}:
        stop
    # Mordidas y peces nunca sirven como anclaje ni generan premios de pesca.
    if event-fishing state is fish bite or fish caught or fish escaped:
        cancel event
        stop
    if event-fishing state is not bobber in ground or entity caught or reel in:
        stop
    set {_anchor} to {-astral.realistic::%{_id}%::anchor}
    set {_block} to {-astral.realistic::%{_id}%::block}
    if event-fishing state is not reel in:
        if {_anchor} is not set:
            set {_anchor} to location of fishing hook
    if event-fishing state is entity caught:
        set {_anchor} to location of hooked entity
    cancel event
    astral_hook_clear(player)
    if {_real} is false:
        stop
    if astral_dungeon(world of player) is true:
        stop
    if gamemode of player is spectator:
        stop
    if {_block} is set:
        if {_block} is not solid:
            stop
    if event-fishing state is reel in:
        if {_anchor} is not set:
            send action bar "&7El anzuelo no se engancho a nada." to player
            stop
    if world of {_anchor} is not world of player:
        stop
    set {_distance} to distance between eye location of player and {_anchor}
    if {_distance} > 32:
        send action bar "&cEl anclaje esta demasiado lejos (max. 32 bloques)." to player
        stop
    if {_distance} < 2:
        stop
    set {_v} to vector from eye location of player to {_anchor}
    set vector length of {_v} to 1.35
    set velocity of player to {_v}
    set {-astral.launch::%{_id}%} to now
    delete {-astral.launch.air::%{_id}%}
    play sound "entity.fishing_bobber.retrieve" with volume 0.6 and pitch 1.1 at player

on death of player:
    astral_hook_clear(victim)

on world change:
    astral_hook_clear(player)
    delete {-astral.jump.used::%uuid of player%}
    delete {-astral.jump.armed::%uuid of player%}
    delete {-astral.jump.released::%uuid of player%}
'''

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
