"""Mazmorra Infinita (pedido del dueno 12/11/2026): practicar y farmear contra el tier elegido.

- /infinita: ventana para elegir tier (1..5 y 5+) y otra para la velocidad de aparicion
  (Facil, Normal, Dificil, Pesadilla). La party entra junta; 6 copias para varios grupos.
- 20 minutos en el tier elegido; despues +1 tier cada 10 minutos (5 minutos antes avisa:
  "Te veo muy tranquilo, creo que podes dar mas pelea"). En 5+ sigue subiendo: +25% vida y dano.
- Mobs vanilla con el tier del datapack (mob/tN): dano, XP y nombre como el resto del juego.
  Creepers (algunos nucleares) sin romper bloques ni lastimar a otros mobs. Todos atacan al jugador.
- Mapa: doubledungeonspawn.schem (privado), pegado igual en las 6 salas (ver bloque MAPA).

python infinita.py -> build/infinita/astral_infinita.sk y build/infinita/comandos.txt
El datapack (inf/apply/*) lo agrega build.py con generate(files).
"""
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/infinita'
COPIES = 6
WORLDS = ['infinita'] + [f'infinita_{n}' for n in range(2, COPIES + 1)]

# ===================== MAPA (UNICO LUGAR) =====================================================
# doubledungeonspawn.schem (del dueno, de terceros: solo en .local/infinita-mapa, nunca al repo).
# Cupula redonda: piso a y=62 (pies en 63), pedestal en el centro y antorchas de alma flotando
# (se conservan: WorldEdit pega sin fisica). Se pega con su origen en PASTE_ORIGIN
# (tools/pegar_infinita.py) y se suben las mismas regiones a las 6 salas.
SCHEM = '.local/infinita-mapa/doubledungeonspawn.schem'
PASTE_ORIGIN = (0, 64, 0)
REGIONS = ('r.-1.-1.mca', 'r.-1.0.mca', 'r.0.-1.mca', 'r.0.0.mca')
ARRIVAL = (0.5, 63, 8.5, 180)   # al sur del pedestal, mirando al centro
# Piso comprobado (2 de aire arriba y piso alrededor), en circulo a 24-30 bloques del centro.
SPAWN_POINTS = [(24.5, 63, 0.5), (26.5, 63, 15.5), (15.5, 63, 26.5), (0.5, 63, 30.5), (-14.5, 63, 26.5),
                (-25.5, 63, 15.5), (-27.5, 63, 0.5), (-25.5, 63, -14.5), (-14.5, 63, -25.5), (0.5, 63, -29.5),
                (15.5, 63, -25.5), (26.5, 63, -14.5)]
# ===============================================================================================

TIERS = [(1, 'Tier I', 'LIME_DYE'), (2, 'Tier II', 'GREEN_DYE'), (3, 'Tier III', 'YELLOW_DYE'),
         (4, 'Tier IV', 'ORANGE_DYE'), (5, 'Tier V', 'RED_DYE'), (6, 'Tier V+', 'NETHER_STAR')]
# (id, nombre, material, segundos entre apariciones)
SPEEDS = [(1, 'Facil', 'LIME_WOOL', 4), (2, 'Normal', 'YELLOW_WOOL', 3), (3, 'Dificil', 'ORANGE_WOOL', 2),
          (4, 'Pesadilla', 'RED_WOOL', 1)]
PRIMERA_SUBIDA = 20 * 60
CADA_SUBIDA = 10 * 60
AVISO = 5 * 60
MENSAJE_AVISO = 'Te veo muy tranquilo, creo que podes dar mas pelea'
EXTRA_5MAS = 0.25           # +25% vida y dano por cada subida dentro de 5+
TOPE_VIVOS = (10, 8)        # mobs vivos maximos: 10 + 8 por jugador
# (summon, peso, NBT extra)
# summon no equipa armas: se las damos. SNBT con comillas simples (en Skript la comilla doble se duplica).
def _arma(item):
    return ",equipment:{mainhand:{id:'minecraft:" + item + "',count:1}}"


MOBS = [('zombie', 3, ''), ('husk', 1, ''), ('drowned', 1, _arma('trident')), ('zombie_villager', 1, ''),
        ('skeleton', 2, _arma('bow')), ('stray', 1, _arma('bow')), ('bogged', 1, _arma('bow')),
        ('wither_skeleton', 1, _arma('stone_sword')), ('spider', 2, ''), ('cave_spider', 1, ''), ('creeper', 2, ''),
        ('creeper', 1, ",powered:1b,ExplosionRadius:6b,CustomName:'Creeper Nuclear',CustomNameVisible:1b"),
        ('witch', 1, ''), ('pillager', 1, _arma('crossbow')), ('vindicator', 1, _arma('iron_axe')), ('enderman', 1, '')]


def generate(files):
    """Funciones del datapack: aplicar el tier elegido (y el extra de 5+) a cada mob nuevo."""
    def fn(path, lines):
        files[f'data/astral/function/{path}.mcfunction'] = '\n'.join(lines) + '\n'
    for t in range(1, 6):
        # mob/nombre arma el cartel [Tn] con #mt: sin esto mostraba el tier del ultimo mob de otro mundo.
        fn(f'inf/apply/t{t}', ['tag @s add astral.seen', f'scoreboard players set #mt astral.tmp {t}', f'function astral:mob/t{t}',
                               f'scoreboard players set @s astral.mt {t}', 'function astral:inf/plus',
                               'data modify entity @s Health set value 1.0E9f', 'function astral:mob/nombre',
                               'tag @s remove inf.nuevo'])
    plus = []
    for k in range(1, 41):
        f = round(EXTRA_5MAS * k, 3)
        plus += [f'execute if score #inf_plus astral.tmp matches {k} run attribute @s minecraft:max_health modifier add astral:infinita {f} add_multiplied_total',
                 f'execute if score #inf_plus astral.tmp matches {k} run attribute @s minecraft:attack_damage modifier add astral:infinita {f} add_multiplied_total']
    fn('inf/plus', plus)


def menu_button():
    """Boton en /mazmorras (casilla 47, fila de abajo)."""
    return dict(material='SPAWNER', slot=47, display_name='&5&lMazmorra Infinita',
                lore=['&7Elegi tu tier y la velocidad de los mobs.', '&7Cada 10 minutos sube la dificultad.',
                      '&7Entra con tu party. 6 salas para varios grupos.'],
                click_commands=['[close]', '[player] infinita<delay=3>'])


def script(primera=None, cada=None, aviso=None):
    # La prueba local acorta los tiempos (segundos); el server usa 20/10/5 minutos.
    PRIMERA_SUBIDA = primera or globals()['PRIMERA_SUBIDA']
    CADA_SUBIDA = cada or globals()['CADA_SUBIDA']
    AVISO = aviso or globals()['AVISO']
    W = ' or '.join(f'"{w}"' for w in WORLDS)
    weights = [m for m in MOBS for _ in range(m[1])]
    L = ['# Generado por infinita.py: Mazmorra Infinita (6 copias, tier, velocidad, subida cada 10 min).',
         '# Variables {-...}: solo memoria. Usa party_miembros() de astral_mazmorras_copias.sk.',
         '',
         'on load:',
         *[f'    execute console command "scoreboard objectives add {o} dummy"' for o in ('inf.tier', 'inf.plus', 'inf.min', 'inf.seg', 'inf.kills')],
         '',
         'function inf_mundo(w: world) :: boolean:',
         f'    if name of {{_w}} is {W}:',
         '        return true',
         '    return false',
         '',
         'function inf_jugadores(w: world) :: number:',
         '    set {_c} to 0',
         '    loop all players:',
         '        world of loop-player is {_w}',
         '        gamemode of loop-player is survival or adventure',
         '        add 1 to {_c}',
         '    return {_c}',
         '',
         'function inf_nombre_tier(t: number) :: text:',
         *[f'    if {{_t}} is {t}:\n        return "{n}"' for t, n, _ in TIERS],
         '    return "Tier V+"',
         '',
         'function inf_ventana_tier(p: player):',
         '    set {_inv} to a new chest inventory with 3 rows named colored "&5Mazmorra Infinita - Tier"',
         *[f'    set slot {9 + 1 + i} of {{_inv}} to {mat.lower().replace('_', ' ')} named "&f&l{n}"' for i, (t, n, mat) in enumerate(TIERS)],
         *[f'    set lore of slot {10 + i} of {{_inv}} to "&7Pelea contra mobs de {n}." and "&720 min en este tier; despues sube cada 10 min."'
           for i, (t, n, mat) in enumerate(TIERS)],
         '    set slot 22 of {_inv} to barrier named "&cCerrar"',
         '    set {-inf.gui::%uuid of {_p}%} to "tier"',
         '    open {_inv} to {_p}',
         '',
         'function inf_ventana_vel(p: player):',
         '    set {_inv} to a new chest inventory with 3 rows named colored "&5Mazmorra Infinita - Velocidad"',
         *[f'    set slot {11 + i} of {{_inv}} to {mat.lower().replace('_', ' ')} named "&f&l{n}"' for i, (v, n, mat, s) in enumerate(SPEEDS)],
         *[f'    set lore of slot {11 + i} of {{_inv}} to "&7Aparece un grupo de mobs cada {s} s." and "&7Mas jugadores, mas mobs."'
           for i, (v, n, mat, s) in enumerate(SPEEDS)],
         '    set slot 22 of {_inv} to barrier named "&cCerrar"',
         '    set {-inf.gui::%uuid of {_p}%} to "vel"',
         '    open {_inv} to {_p}',
         '',
         'command /infinita:',
         '    executable by: players',
         '    description: Mazmorra Infinita: elegi tier y velocidad.',
         '    trigger:',
         '        inf_ventana_tier(player)',
         '',
         'on inventory click:',
         '    set {_g} to {-inf.gui::%uuid of player%}',
         '    if {_g} is not set:',
         '        stop',
         '    cancel event',
         '    set {_s} to index of event-slot',
         '    if clicked inventory is player\'s inventory:',
         '        stop',
         '    if {_s} is 22:',
         '        delete {-inf.gui::%uuid of player%}',
         '        close player\'s inventory',
         '        stop',
         '    if {_g} is "tier":',
         f'        if {{_s}} is between 10 and {9 + len(TIERS)}:',
         '            set {-inf.elige.tier::%uuid of player%} to {_s} - 9',
         '            close player\'s inventory',
         '            wait 2 ticks',
         '            inf_ventana_vel(player)',
         '        stop',
         '    if {_g} is "vel":',
         f'        if {{_s}} is between 11 and {10 + len(SPEEDS)}:',
         '            delete {-inf.gui::%uuid of player%}',
         '            close player\'s inventory',
         '            inf_entrar(player, {-inf.elige.tier::%uuid of player%}, {_s} - 10)',
         '',
         'on inventory close:',
         '    if {-inf.gui::%uuid of player%} is "vel":',
         '        stop',
         '    delete {-inf.gui::%uuid of player%}',
         '',
         'function inf_entrar(p: player, tier: number, vel: number):',
         '    if {_tier} is not set:',
         '        set {_tier} to 1',
         *[f'    set {{_w::{i}}} to "{w}"' for i, w in enumerate(WORLDS, 1)],
         '    set {_m::*} to party_miembros({_p})',
         '    set {_elegida} to 0',
         f'    loop {COPIES} times:',
         '        set {_mundo} to world({_w::%loop-number%})',
         '        if {_mundo} is set:',
         '            loop {_m::*}:',
         '                loop-value-2 is not {_p}',
         '                world of loop-value-2 is {_mundo}',
         '                set {_elegida} to loop-number',
         '        if {_elegida} > 0:',
         '            exit loop',
         '    if {_elegida} > 0:',
         '        set {_grupo::*} to {_p}',
         '    else:',
         f'        loop {COPIES} times:',
         '            set {_mundo} to world({_w::%loop-number%})',
         '            if {_mundo} is set:',
         '                if inf_jugadores({_mundo}) is 0:',
         '                    if {-inf.on::%{_w::%loop-number%}%} is not set:',
         '                        set {_elegida} to loop-number',
         '                        exit loop',
         '        if {_elegida} is 0:',
         f'            send "&cMazmorra ocupada: &flas {COPIES} salas de la Mazmorra Infinita estan en uso. &7Proba en un rato." to {{_p}}',
         '            stop',
         '        loop {_m::*}:',
         '            if loop-value is {_p}:',
         '                add loop-value to {_grupo::*}',
         '            else if name of world of loop-value is "lobby":',
         '                add loop-value to {_grupo::*}',
         '        set {_n} to {_w::%{_elegida}%}',
         '        set {-inf.on::%{_n}%} to true',
         '        set {-inf.tier::%{_n}%} to {_tier}',
         '        set {-inf.plus::%{_n}%} to 0',
         '        set {-inf.vel::%{_n}%} to {_vel}',
         '        set {-inf.seg::%{_n}%} to 0',
         f'        set {{-inf.next::%{{_n}}%}} to {PRIMERA_SUBIDA}',
         '        set {-inf.kills::%{_n}%} to 0',
         '        set {-inf.cd::%{_n}%} to 0',
         '        delete {-inf.avisado::%{_n}%}',
         '    set {_n} to {_w::%{_elegida}%}',
         '    set {_i} to 0',
         '    loop {_grupo::*}:',
         '        set {_dx} to ceil({_i} / 2) * 2',
         '        if mod({_i}, 2) is 1:',
         '            set {_dx} to -1 * {_dx}',
         '        add 1 to {_i}',
         f'        execute console command "execute in minecraft:%{{_n}}% run minecraft:tp %uuid of loop-value% %{ARRIVAL[0]} + {{_dx}}% {ARRIVAL[1]} {ARRIVAL[2]} {ARRIVAL[3]} 0"',
         '        send "&5[Mazmorra Infinita] &fSala %{_elegida}% - %inf_nombre_tier({-inf.tier::%{_n}%})%. &7Para salir: /spawn" to loop-value',
         '',
         'every 1 second:',
         '    loop {-inf.on::*}:',
         '        set {_n} to loop-index',
         '        set {_mundo} to world({_n})',
         '        if {_mundo} is not set:',
         '            delete {-inf.on::%{_n}%}',
         '        else:',
         '            set {_pj} to inf_jugadores({_mundo})',
         '            if {_pj} is 0:',
         '                inf_limpiar({_n})',
         '            else:',
         '                inf_tick({_n}, {_mundo}, {_pj})',
         '',
         'function inf_limpiar(n: text):',
         '    execute console command "execute in minecraft:%{_n}% run minecraft:kill @e[tag=inf.mob,distance=0..]"',
         '    delete {-inf.on::%{_n}%}',
         '    delete {-inf.tier::%{_n}%}',
         '    delete {-inf.plus::%{_n}%}',
         '    delete {-inf.vel::%{_n}%}',
         '    delete {-inf.seg::%{_n}%}',
         '    delete {-inf.next::%{_n}%}',
         '    delete {-inf.kills::%{_n}%}',
         '    delete {-inf.cd::%{_n}%}',
         '    delete {-inf.avisado::%{_n}%}',
         '',
         'function inf_tick(n: text, w: world, pj: number):',
         '    add 1 to {-inf.seg::%{_n}%}',
         '    set {_r} to {-inf.next::%{_n}%} - {-inf.seg::%{_n}%}',
         '    # Aviso 5 minutos antes de cada subida.',
         f'    if {{_r}} <= {AVISO}:',
         '        if {-inf.avisado::%{_n}%} is not set:',
         '            set {-inf.avisado::%{_n}%} to true',
         '            loop all players:',
         '                world of loop-player is {_w}',
         f'                send title "&c&lAtencion" with subtitle "&e{MENSAJE_AVISO}" to loop-player for 4 seconds',
         f'                send "&5[Mazmorra Infinita] &e{MENSAJE_AVISO}. &7En 5 minutos sube la dificultad." to loop-player',
         '    if {_r} <= 0:',
         '        if {-inf.tier::%{_n}%} < 6:',
         '            add 1 to {-inf.tier::%{_n}%}',
         '        else:',
         '            add 1 to {-inf.plus::%{_n}%}',
         f'        add {CADA_SUBIDA} to {{-inf.next::%{{_n}}%}}',
         '        delete {-inf.avisado::%{_n}%}',
         '        set {_r} to {-inf.next::%{_n}%} - {-inf.seg::%{_n}%}',
         '        loop all players:',
         '            world of loop-player is {_w}',
         '            send title "&4&lSUBE LA DIFICULTAD" with subtitle "&f%inf_nombre_tier({-inf.tier::%{_n}%})%" to loop-player for 3 seconds',
         '            play sound "entity.wither.spawn" with volume 0.6 to loop-player',
         '    # Barra de accion: tier, tiempo a la proxima subida y bajas.',
         '    set {_t} to inf_nombre_tier({-inf.tier::%{_n}%})',
         '    if {-inf.plus::%{_n}%} > 0:',
         f'        set {{_t}} to "%{{_t}}% +%{{-inf.plus::%{{_n}}%}} * {int(EXTRA_5MAS * 100)}%%%"',
         '    set {_mm} to floor({_r} / 60)',
         '    set {_ss} to mod({_r}, 60)',
         '    set {_sz} to "%{_ss}%"',
         '    if {_ss} < 10:',
         '        set {_sz} to "0%{_ss}%"',
         '    loop all players:',
         '        world of loop-player is {_w}',
         '        send action bar "&5%{_t}% &8| &fSube en &e%{_mm}%:%{_sz}% &8| &fBajas: &a%{-inf.kills::%{_n}%}%" to loop-player',
         '        # Valores para el panel lateral (panel_mundos.py).',
         '        execute console command "scoreboard players set %name of loop-player% inf.tier %{-inf.tier::%{_n}%}%"',
         '        execute console command "scoreboard players set %name of loop-player% inf.plus %{-inf.plus::%{_n}%}%"',
         '        execute console command "scoreboard players set %name of loop-player% inf.min %{_mm}%"',
         '        execute console command "scoreboard players set %name of loop-player% inf.seg %{_ss}%"',
         '        execute console command "scoreboard players set %name of loop-player% inf.kills %{-inf.kills::%{_n}%}%"',
         '    # Que todos ataquen al jugador (arañas y endermans incluidos).',
         '    # Solo jugadores en supervivencia/aventura (en creativo nadie recibe dano).',
         '    loop all players in {_w}:',
         '        gamemode of loop-player is survival or adventure',
         '        add loop-player to {_ps::*}',
         '    set {_vivos} to 0',
         '    loop all entities in {_w}:',
         '        if scoreboard tags of loop-entity contains "inf.mob":',
         '            add 1 to {_vivos}',
         '            if target of loop-entity is not set:',
         '                if {_ps::*} is set:',
         '                    set target of loop-entity to random element out of {_ps::*}',
         '    # Aparicion: un grupo cada X segundos segun la velocidad; un mob por jugador.',
         '    add 1 to {-inf.cd::%{_n}%}',
         *[f'    if {{-inf.vel::%{{_n}}%}} is {v}:\n        set {{_cada}} to {s}' for v, n, mat, s in SPEEDS],
         '    if {-inf.cd::%{_n}%} < {_cada}:',
         '        stop',
         '    set {-inf.cd::%{_n}%} to 0',
         f'    set {{_tope}} to {TOPE_VIVOS[0]} + {TOPE_VIVOS[1]} * {{_pj}}',
         '    loop {_pj} times:',
         '        if {_vivos} < {_tope}:',
         '            inf_spawn({_n})',
         '            add 1 to {_vivos}',
         '',
         'function inf_spawn(n: text):',
         *[f'    set {{_p::{i}}} to "{x} {y} {z}"' for i, (x, y, z) in enumerate(SPAWN_POINTS, 1)],
         f'    set {{_pos}} to {{_p::%random integer between 1 and {len(SPAWN_POINTS)}%}}',
         f'    set {{_k}} to random integer between 1 and {len(weights)}',
         *[f'    if {{_k}} is {i}:\n        set {{_s}} to "{t} %{{_pos}}% {{Tags:[\'inf.mob\',\'inf.nuevo\']{nbt}}}"'
           for i, (t, w, nbt) in enumerate(weights, 1)],
         '    execute console command "execute in minecraft:%{_n}% run summon %{_s}%"',
         '    set {_t} to {-inf.tier::%{_n}%}',
         '    set {_extra} to {-inf.plus::%{_n}%}',
         '    if {_t} is 6:',
         '        set {_t} to 5',
         '        add 1 to {_extra}',
         '    execute console command "scoreboard players set #inf_plus astral.tmp %{_extra}%"',
         '    execute console command "execute in minecraft:%{_n}% as @e[tag=inf.nuevo,distance=0..] run function astral:inf/apply/t%{_t}%"',
         '',
         '# Bajas de la partida.',
         'on death:',
         '    if scoreboard tags of victim contains "inf.mob":',
         '        add 1 to {-inf.kills::%name of world of victim%}',
         '',
         '# Creepers (y cualquier mob de la sala) no lastiman a otros mobs; las explosiones no rompen bloques (mob_griefing false).',
         'on damage:',
         '    if scoreboard tags of victim contains "inf.mob":',
         '        if damage cause is entity explosion or block explosion:',
         '            cancel event',
         '            stop',
         '        if attacker is set:',
         '            if scoreboard tags of attacker contains "inf.mob":',
         '                cancel event',
         '',
         '# Quien muere sale de la partida y vuelve al lobby (inventario conservado por keep_inventory).',
         'on death of player:',
         '    if inf_mundo(world of victim) is true:',
         '        set {-inf.salio::%uuid of victim%} to true',
         '',
         'on respawn:',
         '    if {-inf.salio::%uuid of player%} is set:',
         '        delete {-inf.salio::%uuid of player%}',
         '        wait 2 ticks',
         '        execute console command "spawn %name of player%"',
         '']
    return '\n'.join(L)


def commands():
    """Crear las 6 salas (una vez). Las regiones del mapa se suben con el server apagado (ver build/deploy)."""
    x, y, z, yaw = ARRIVAL
    out = ['# Mazmorra Infinita: crear las 6 salas una vez; despues subir las regiones del mapa (server apagado).']
    for w in WORLDS:
        out += [f'mv create {w} normal --world-type FLAT --no-structures --no-adjust-spawn '
                '--generator-settings {"layers":[{"block":"minecraft:air","height":1}],"biome":"minecraft:the_void"}',
                f'mv modify {w} set difficulty hard', f'mv modify {w} set gamemode survival',
                f'mv modify {w} set pvp false', f'mv modify {w} set allow-weather false',
                f'mv gamerule set minecraft:spawn_mobs false {w}', f'mv gamerule set minecraft:keep_inventory true {w}',
                f'mv gamerule set minecraft:mob_griefing false {w}', f'mv gamerule set minecraft:advance_time false {w}',
                f'rg flag -w {w} __global__ build deny', f'rg flag -w {w} __global__ block-break deny',
                f'rg flag -w {w} __global__ block-place deny', f'rg flag -w {w} __global__ chest-access deny',
                f'rg flag -w {w} __global__ pvp deny', f'rg flag -w {w} __global__ mob-spawning allow',
                f'rg flag -w {w} __global__ interact allow', f'rg flag -w {w} __global__ use deny',
                f'execute in minecraft:{w} run setworldspawn {int(x)} {y} {int(z)}']
    return chr(10).join(out) + chr(10)


def generate_files():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'astral_infinita.sk').write_text(script(), encoding='utf8')
    (OUT/'comandos.txt').write_text(commands(), encoding='utf8')


if __name__ == '__main__':
    generate_files()
    print(OUT)
