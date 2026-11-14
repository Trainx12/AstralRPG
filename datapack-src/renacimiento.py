"""Final del Santuario (Trainx), Renacimiento, Deseos y Deseo lite del Cronista (14/11/2026).

Uso (desde datapack-src):  python renacimiento.py
Salida:
  build/renacimiento/astral_renacimiento.sk   -> plugins/Skript/scripts/
  build/menus/DeluxeMenus/gui_menus/{renacer,deseo,deseo_lite}.yml (los escribe cofre_mazmorra.generate)
  build/renacimiento/comandos.txt              -> consola, una vez

Como funciona (docs/DESEOS_Y_RANKINGS.md):
- Trainx muere -> cada participante (supervivencia/aventura) recibe astral.trainx.vencido y un mensaje poetico.
- /fragmentos -> boton RENACER (con los 7 fragmentos + Trainx vencido) -> confirmar -> se reinicia el progreso
  y se abre la ventana del deseo. Dificultad personal: mobs x(N+2) para quien renacio N veces (se usa el mas alto
  entre los jugadores cercanos).
- Epilogo de la historia del Cronista (misiones.py pone la etiqueta aq.deseo_lite) -> deseo lite.
- /deseos (admin): pendientes con [Aprobar] [Rechazar]. Aprobar NO entrega nada: lo cumple el Admin a mano.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/renacimiento'

FRAGMENTOS = ('marea', 'pantano', 'arena', 'lampara', 'hielo', 'fuego', 'corazon')
MAZMORRAS = ('mina', 'bosque', 'tumba', 'cumbre', 'forja', 'santuario')
# Objetivos de la historia (misiones.py) que se reinician al renacer. Las diarias no se tocan.
HISTORIA = ('state', 'accepted', 'herrero', 'forge1', 'forge5', 'scare', 'bee', 'face', 'helite',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6')
PERM_ADMIN = 'astral.admin.deseos'
VENCIDO = 'astral.trainx.vencido'


def tope():
    """Lo que cuesta abrir la ultima mina astral (pedido del dueno)."""
    from minas import MINES
    return MINES[-1][-1]


def tope_lite():
    return tope() // 4


def plata(n):
    return f'{n:,}'.replace(',', '.') + '$'


# Categorias: (id, icono, nombre, explicacion). 'plata' pide un numero.
CATEGORIAS = {
    'completo': [
        ('plata', 'GOLD_BLOCK', '&e&lPlata', [f'&7Hasta &e{plata(tope())}&7.', '&8(lo que cuesta la ultima mina astral)']),
        ('tier', 'NETHERITE_UPGRADE_SMITHING_TEMPLATE', '&d&lSubir 1 tier todo tu equipo',
         ['&7Armas y armadura que tengas.', '&8Si ya es tier V, queda anotado', '&8para cuando lleguen los tiers nuevos.']),
        ('arma', 'DIAMOND_SWORD', '&b&lUn arma o armadura Astral', ['&7Una que ya exista,', '&7hasta tu tier +1.']),
        ('personalizada', 'NETHER_STAR', '&5&lArma personalizada',
         ['&7Nombre a eleccion y aspecto de un', '&7modelo que ya exista. Dano de su', '&7tier +1 como maximo y UNA',
          '&7habilidad de las que ya existen.']),
        ('otro', 'WRITABLE_BOOK', '&f&lOtro deseo', ['&7Escribilo con tus palabras.', '&7Tiene que respetar las reglas.']),
    ],
    'lite': [
        ('plata', 'GOLD_INGOT', '&e&lPlata', [f'&7Hasta &e{plata(tope_lite())}&7.']),
        ('tier', 'ANVIL', '&d&lSubir 1 tier a 2 piezas', ['&7Dos piezas de tu equipo', '&7(armas o armadura).']),
        ('tiradas', 'CHEST', '&6&l10 tiradas gratis', ['&7De UNA gacha a eleccion:', '&7Armas, Monturas o Cosmeticos.']),
        ('arma', 'IRON_SWORD', '&b&lUn arma o armadura Astral', ['&7Una que ya exista,', '&7de tu tier actual.']),
        ('cosmetico', 'LEATHER_HELMET', '&a&lUn cosmetico', ['&7Uno de la gacha de Cosmeticos', '&7a eleccion.']),
    ],
}
REGLAS = ['&c&lNo se puede pedir:', '&7- Creativo o cambiar de modo de juego.', '&7- OP, permisos o comandos de admin.',
          '&7- Desbloquear todos los tiers o mazmorras.', '&7- Subir skills (AuraSkills).', '&7- Mas deseos.',
          '&7- Plata por encima del tope.', '&7- Cosas que no existen en el server.',
          '&7- Quitarle algo o perjudicar a otro jugador.', '&7- Nada ofensivo.', '',
          '&e&lTodos los deseos los revisa el Admin,', '&eaunque no rompan ninguna regla.',
          '&7Puede rechazarlo o pedirte que lo cambies.']
REGLAS_LITE = REGLAS[:9] + ['&7- Un arma personalizada o el deseo completo.'] + REGLAS[9:]


# ------------------------------------------------------------------ ventanas (DeluxeMenus)
def _inv(slot, entry):
    from cofre_mazmorra import _invisible
    return _invisible(slot, entry)


def renacer_menu():
    from cofre_mazmorra import title, SLOTS_BOTON, SLOTS_RENACER
    items = {
        'pierdes': {'material': 'BARRIER', 'slot': SLOTS_RENACER[0], 'display_name': '&c&lSe reinicia',
                    'lore': ['&7- Las mazmorras (y sus fragmentos:', '&7  se vuelven a conseguir).', '&7- La historia del Cronista.',
                             '&7- Las Minas Astrales.', '&7- Tu plata vuelve a &e0$&7.']},
        'conservas': {'material': 'TOTEM_OF_UNDYING', 'slot': SLOTS_RENACER[1], 'display_name': '&a&lTe quedas con',
                      'lore': ['&7- Tus skills.', '&7- Cosmeticos, monturas y mascotas.', '&7- Tu equipo, tambien el tier V.']},
        'info': {'material': 'NETHER_STAR', 'slot': 22, 'display_name': '&d&lRenacer',
                 'lore': ['&7El mundo se vuelve mas fiero para vos:', '&7los mobs tienen x3 de vida y dano',
                          '&7(y +1 por cada renacimiento mas).', '&7Despues llegan forjas nuevas:',
                          '&7tiers VI a X, que se estan forjando.', '', '&dY la estrella te concede un deseo.']},
        'volver': {'material': 'ARROW', 'slot': 45, 'display_name': '&fVolver a los fragmentos',
                   'click_commands': ['[openguimenu] fragmentos']},
        'cerrar': {'material': 'BARRIER', 'slot': 53, 'display_name': '&cCerrar', 'click_commands': ['[close]']},
    }
    for n, slot in enumerate(SLOTS_BOTON):
        items[f'confirmar_{n}'] = _inv(slot, {'display_name': '&d&lRENACER', 'lore': ['&7Clic para renacer.', '&cNo se puede deshacer.'],
                                             'click_commands': ['[close]', '[player] astralrenacer confirmar']})
    return {'menu_title': title('renacer'), 'size': 54, 'items': items}


def deseo_menu(tipo):
    from cofre_mazmorra import title, SLOTS_DESEO, SLOT_REGLAS
    if tipo == 'lite':
        # Ventana del Cronista (pedido del dueno 14/11): mismo marco azul que las misiones.
        from cronista_ui import title as cronista_title, DESEO_SLOTS, DESEO_REGLAS
        assert DESEO_SLOTS == SLOTS_DESEO and DESEO_REGLAS == SLOT_REGLAS
    items = {}
    for (cat, icon, name, lore), slot in zip(CATEGORIAS[tipo], SLOTS_DESEO):
        items[cat] = {'material': icon, 'slot': slot, 'display_name': name, 'lore': lore + ['', '&eClic para elegir.'],
                      'item_flags': ['HIDE_ATTRIBUTES', 'HIDE_ADDITIONAL_TOOLTIP'],
                      'click_commands': ['[close]', f'[player] astraldeseo {tipo} {cat}']}
    items['reglas'] = {'material': 'BOOK', 'slot': SLOT_REGLAS, 'display_name': '&6&lReglas del deseo',
                       'lore': REGLAS if tipo == 'completo' else REGLAS_LITE}
    items['cerrar'] = {'material': 'BARRIER', 'slot': 53, 'display_name': '&cCerrar',
                       'lore': ['&7Tu deseo te espera: &f/deseo'], 'click_commands': ['[close]']}
    if tipo == 'lite':
        return {'menu_title': cronista_title('deseo'), 'size': 54, 'items': items}
    return {'menu_title': title('deseo'), 'size': 54, 'items': items}


def menus():
    return {'renacer': renacer_menu(), 'deseo': deseo_menu('completo'), 'deseo_lite': deseo_menu('lite')}


# ------------------------------------------------------------------ Skript
def _tell(player_expr, json):
    """tellraw desde la consola (json en SNBT con comillas simples)."""
    return f'execute console command "tellraw {player_expr} {json}"'


def _button(text, color, command, hover=None):
    h = f",hover_event:{{action:'show_text',value:'{hover}'}}" if hover else ''
    return f"{{text:'{text}',color:'{color}',click_event:{{action:'run_command',command:'{command}'}}{h}}}"


TRAINX_TEXTO = [
    '&5&o Trainx cae de rodillas, y por primera vez sonrie.',
    '&d«Bien peleado, viajero. Pero esto no es el final:',
    '&d es apenas la primera vuelta del camino.',
    '&d Los fragmentos de la estrella todavia laten en tu bolsa:',
    '&d la Marea, el Pantano, la Arena, la Lampara, el Hielo, el Fuego...',
    '&d y el Corazon Astral. Juntalos todos y volve a la luz.',
    '&d Con ellos vas a poder &f&lrenacer&d: empezar de nuevo,',
    '&d con un mundo mas fiero que antes y forjas que todavia nadie toco,',
    '&d armas y armaduras de tiers que hoy duermen.',
    '&d Y a quien se anima a renacer, la estrella le concede &f&lun deseo&d.»',
]
LITE_TEXTO = [
    '&b&o El Cronista cierra el libro con cuidado, como si pudiera romperse.',
    '&3«La historia termino, y la escribiste vos.',
    '&3 Antes de que la tinta se seque, te debo algo:',
    '&3 un deseo pequeno, de los que caben en una pagina.»',
]


def skript():
    frag_ok = '\n'.join(f'    if {{_p}} does not have permission "astral.fragmento.{f}":\n        return false' for f in FRAGMENTOS)
    faltan = '\n'.join(f'    if {{_p}} does not have permission "astral.fragmento.{f}":\n        add "{f}" to {{_f::*}}'
                       for f in FRAGMENTOS)
    frag_reset = '\n'.join(f'    execute console command "lp user %{{_n}}% permission unset astral.fragmento.{f}"' for f in FRAGMENTOS)
    maz_reset = '\n'.join(f'    execute console command "lp user %{{_n}}% permission unset astral.{k}.cd"' for k in MAZMORRAS)
    hist_reset = '\n'.join(f'    execute console command "scoreboard players reset %{{_n}}% aq.{o}"' for o in HISTORIA)
    trainx_msg = '\n'.join(f'    send "{line}" to {{_p}}\n    wait 1 second' for line in TRAINX_TEXTO)
    lite_msg = '\n'.join(f'    send "{line}" to {{_p}}\n    wait 1 second' for line in LITE_TEXTO)
    cats = {t: [c[0] for c in CATEGORIAS[t]] for t in CATEGORIAS}
    cat_check = '\n'.join(
        f'        if arg-1 is "{t}":\n' + '\n'.join(f'            if arg-2 is "{c}":\n                set {{_ok}} to true' for c in cats[t])
        for t in cats)
    boton_frag = _button('[Ver mis fragmentos]', 'aqua', '/fragmentos', 'Abrir tus Fragmentos Astrales')
    boton_deseo = _button('[Pedir mi deseo]', 'light_purple', '/deseo', 'Abrir la ventana del deseo')
    return f'''# Generado por datapack-src/renacimiento.py. No editar a mano (docs/DESEOS_Y_RANKINGS.md).
# Trainx (jefe final), Renacimiento, Deseos y Deseo lite del Cronista.

options:
    tope: {tope()}
    topelite: {tope_lite()}

# ------------------------------------------------------------------ Trainx
# MythicMobs (mobs/trainx.py) llama estos comandos desde la consola con el nombre del mundo.
command /trainxinicio <text>:
    executable by: console
    trigger:
        set {{-trainx.ini::%arg-1%}} to unix timestamp of now
        set {{_w}} to world(arg-1)
        set {{_n}} to 0
        loop all players in {{_w}}:
            gamemode of loop-player is survival or adventure
            add 1 to {{_n}}
        if {{_n}} < 4:
            loop all players in {{_w}}:
                send "&5✦ &dTrainx esta pensado para &f4 jugadores tier V&d. Son &f%{{_n}}%&d: va a ser muy duro." to loop-player

command /trainxfin <text>:
    executable by: console
    trigger:
        set {{_w}} to world(arg-1)
        set {{_seg}} to (unix timestamp of now) - ({{-trainx.ini::%arg-1%}} ? unix timestamp of now)
        delete {{-trainx.ini::%arg-1%}}
        loop all players in {{_w}}:
            gamemode of loop-player is survival or adventure
            add loop-player to {{_ps::*}}
            execute console command "lp user %name of loop-player% permission set {VENCIDO} true"
            trainx_mensaje(loop-player)
        if size of {{_ps::*}} > 0:
            rk_trainx({{_seg}}, {{_ps::*}})

function trainx_mensaje(p: player):
    send title "&d&lTrainx cayo" with subtitle "&7la estrella te esta mirando" to {{_p}} for 4 seconds
    play sound "ui.toast.challenge_complete" to {{_p}}
    wait 3 seconds
{trainx_msg}
    {_tell("%name of {_p}%", boton_frag)}

# ------------------------------------------------------------------ Renacimiento
function astral_renac(p: player) :: number:
    return {{astral.renac::%uuid of {{_p}}%}} ? 0

function astral_renacer_listo(p: player) :: boolean:
{frag_ok}
    if {{_p}} does not have permission "{VENCIDO}":
        return false
    return true

function astral_renacer_falta(p: player):
{faltan}
    if size of {{_f::*}} > 0:
        set {{_txt}} to join {{_f::*}} with ", "
        send "&cTe faltan fragmentos: &f%{{_txt}}%&c. Miralos en &f/fragmentos&c." to {{_p}}
    if {{_p}} does not have permission "{VENCIDO}":
        send "&cTodavia no venciste a &d&lTrainx&c, al final del Santuario Celestial." to {{_p}}

command /astralrenacer [<text>]:
    executable by: players
    trigger:
        if astral_renacer_listo(player) is false:
            astral_renacer_falta(player)
            play sound "entity.villager.no" to player
            stop
        if arg-1 is not "confirmar":
            execute console command "dm open renacer %name of player%"
            stop
        astral_renacer(player)

function astral_renacer(p: player):
    set {{_id}} to uuid of {{_p}}
    set {{_n}} to name of {{_p}}
    add 1 to {{astral.renac::%{{_id}}%}}
    set {{_r}} to {{astral.renac::%{{_id}}%}}
    set {{-renac::%{{_id}}%}} to {{_r}}
    # Fragmentos, Trainx y cooldowns de las mazmorras: todo se vuelve a conseguir.
{frag_reset}
    execute console command "lp user %{{_n}}% permission unset {VENCIDO}"
{maz_reset}
    # Historia del Cronista (las diarias no se tocan).
{hist_reset}
    execute console command "tag %{{_n}}% remove aq.title"
    # Minas Astrales: vuelve a la primera.
    delete {{am.rank::%{{_id}}%}}
    delete {{am.blocks::%{{_id}}%}}
    delete {{am.minutes::%{{_id}}%}}
    delete {{-am.b::%{{_id}}%}}
    # Plata a 0, insignia y contador para PlaceholderAPI.
    execute console command "eco set %{{_n}}% 0"
    execute console command "lp user %{{_n}}% meta set astral_renacimiento %{{_r}}%"
    execute console command "lp user %{{_n}}% meta setsuffix 50 "" &d✦%{{_r}}%"""
    set {{astral.deseo.tiene::%{{_id}}%}} to "completo"
    send title "&d&lRenaciste" with subtitle "&7Renacimiento &f%{{_r}}%&7: el mundo ahora es mas fiero" to {{_p}} for 5 seconds
    play sound "entity.wither.death" with volume 0.6 to {{_p}}
    play sound "ui.toast.challenge_complete" to {{_p}}
    execute console command "execute at %{{_n}}% run particle minecraft:end_rod ~ ~1 ~ 1 2 1 0.1 300 force"
    broadcast "&5✦ &d%{{_n}}% &frenacio por &d%{{_r}}%&f° vez. &7La estrella lo mira de nuevo."
    wait 4 seconds
    send "&d«Volviste a empezar, pero no sos el mismo. Pedi tu deseo.»" to {{_p}}
    astral_deseo_abrir({{_p}})

# Dificultad personal: mobs x(N+2) de vida y dano. Se usa el renacimiento mas alto cerca (grupos).
function astral_renac_cerca(l: location) :: number:
    set {{_m}} to 0
    loop all players in radius 32 around {{_l}}:
        set {{_r}} to {{-renac::%uuid of loop-player%}} ? 0
        if {{_r}} > {{_m}}:
            set {{_m}} to {{_r}}
    return {{_m}}

on join:
    set {{-renac::%uuid of player%}} to {{astral.renac::%uuid of player%}} ? 0

on damage of player with priority highest:
    attacker is set
    attacker is not a player
    set {{_r}} to astral_renac_cerca(location of victim)
    {{_r}} > 0
    set damage to damage * ({{_r}} + 2)

on damage with priority highest:
    victim is not a player
    attacker is a player
    set {{_r}} to astral_renac_cerca(location of victim)
    {{_r}} > 0
    set damage to damage / ({{_r}} + 2)

# Plata de los mobs (mobs/mythic.py y mobs/mazmorra.py): +100 % por cada renacimiento del que lo mata.
command /astralplatamob <text> <number>:
    executable by: console
    trigger:
        set {{_m}} to 1
        loop all players:
            name of loop-player is arg-1
            set {{_m}} to 1 + ({{-renac::%uuid of loop-player%}} ? 0)
        set {{_n}} to round(arg-2 * {{_m}})
        execute console command "eco give %arg-1% %{{_n}}%"

# ------------------------------------------------------------------ Deseos
function astral_deseo_abrir(p: player):
    set {{_t}} to {{astral.deseo.tiene::%uuid of {{_p}}%}}
    if {{_t}} is "completo":
        execute console command "dm open deseo %name of {{_p}}%"
    else if {{_t}} is "lite":
        execute console command "dm open deseo_lite %name of {{_p}}%"
    else:
        send "&7No tenes ningun deseo para pedir." to {{_p}}

command /deseo:
    executable by: players
    trigger:
        astral_deseo_abrir(player)

command /astraldeseo <text> <text>:
    executable by: players
    trigger:
        if {{astral.deseo.tiene::%uuid of player%}} is not arg-1:
            send "&cNo tenes ese deseo disponible." to player
            stop
        set {{_ok}} to false
{cat_check}
        if {{_ok}} is false:
            stop
        set {{-deseo.cat::%uuid of player%}} to arg-2
        if arg-2 is "plata":
            if arg-1 is "completo":
                send "&dEscribi en el chat cuanta plata queres &7(solo el numero, maximo &e{plata(tope())}&7)." to player
            else:
                send "&dEscribi en el chat cuanta plata queres &7(solo el numero, maximo &e{plata(tope_lite())}&7)." to player
        else:
            send "&dEscribi tu deseo en el chat, bien explicado &7(un solo mensaje)." to player
        send "&7Para volver a la ventana, escribi &fcancelar&7." to player

on chat:
    set {{_c}} to {{-deseo.cat::%uuid of player%}}
    {{_c}} is set
    cancel event
    set {{_m}} to message
    wait 1 tick
    if {{_m}} is "cancelar":
        delete {{-deseo.cat::%uuid of player%}}
        astral_deseo_abrir(player)
        stop
    set {{_t}} to {{astral.deseo.tiene::%uuid of player%}}
    if {{_t}} is not set:
        delete {{-deseo.cat::%uuid of player%}}
        stop
    if {{_c}} is "plata":
        set {{_s}} to {{_m}}
        replace all "." and "," and "$" and " " with "" in {{_s}}
        set {{_v}} to {{_s}} parsed as integer
        if {{_t}} is "completo":
            set {{_max}} to {{@tope}}
        else:
            set {{_max}} to {{@topelite}}
        if {{_v}} is not set:
            send "&cEso no es un numero. Escribi solo la cantidad (o &fcancelar&c)." to player
            stop
        if {{_v}} < 1:
            send "&cTiene que ser mas que 0." to player
            stop
        if {{_v}} > {{_max}}:
            send "&cTe pasaste del tope (&e%{{_max}}%$&c). Escribi otra cantidad." to player
            stop
        set {{_m}} to "%{{_v}}%$"
    add 1 to {{astral.deseos.n}}
    set {{_k}} to {{astral.deseos.n}}
    set {{astral.deseos::%{{_k}}%::jugador}} to name of player
    set {{astral.deseos::%{{_k}}%::uuid}} to uuid of player
    set {{astral.deseos::%{{_k}}%::tipo}} to {{_t}}
    set {{astral.deseos::%{{_k}}%::cat}} to {{_c}}
    set {{astral.deseos::%{{_k}}%::texto}} to {{_m}}
    set {{astral.deseos::%{{_k}}%::fecha}} to now
    set {{astral.deseos::%{{_k}}%::renac}} to astral_renac(player)
    set {{astral.deseos::%{{_k}}%::estado}} to "pendiente"
    set {{astral.deseos.pend::%{{_k}}%}} to {{_k}}
    delete {{-deseo.cat::%uuid of player%}}
    delete {{astral.deseo.tiene::%uuid of player%}}
    send "&d✦ Tu deseo quedo anotado &7(#%{{_k}}%)&d. El Admin lo va a revisar; te avisamos aca." to player
    play sound "block.amethyst_block.resonate" to player
    loop all players:
        loop-player has permission "{PERM_ADMIN}"
        send "&5[Deseos] &fNuevo deseo &d#%{{_k}}% &fde &e%name of player%&f (%{{_t}}%, %{{_c}}%): &7%{{_m}}%" to loop-player
        {_tell("%name of loop-player%", _button('[Ver pendientes]', 'light_purple', '/deseos'))}

function deseo_linea(admin: player, k: text):
    set {{_j}} to {{astral.deseos::%{{_k}}%::jugador}}
    set {{_t}} to {{astral.deseos::%{{_k}}%::tipo}}
    set {{_c}} to {{astral.deseos::%{{_k}}%::cat}}
    send "&d#%{{_k}}% &e%{{_j}}% &8(%{{_t}}%, %{{_c}}%, renacimiento %{{astral.deseos::%{{_k}}%::renac}}%) &f%{{astral.deseos::%{{_k}}%::texto}}%" to {{_admin}}
    {_tell("%name of {_admin}%", "['  ',{text:'[Aprobar]',color:'green',click_event:{action:'run_command',command:'/deseos aprobar %{_k}%'}},' ',{text:'[Rechazar]',color:'red',click_event:{action:'suggest_command',command:'/deseos rechazar %{_k}% '}}]")}

command /deseos [<text>] [<text>] [<text>]:
    permission: {PERM_ADMIN}
    trigger:
        if arg-1 is not set:
            send "&5&l--- Deseos pendientes ---" to player
            set {{_c}} to 0
            loop {{astral.deseos.pend::*}}:
                add 1 to {{_c}}
                deseo_linea(player, "%loop-value%")
            if {{_c}} is 0:
                send "&7No hay deseos pendientes." to player
            send "&7Aprobar no entrega nada: cumplilo a mano. Historial: &f/deseos historial" to player
            stop
        if arg-1 is "historial":
            set {{_n}} to {{astral.deseos.n}} ? 0
            set {{_d}} to max(1, {{_n}} - 14)
            loop ({{_n}} - {{_d}} + 1) times:
                set {{_k}} to {{_d}} + loop-number - 1
                {{astral.deseos::%{{_k}}%::jugador}} is set
                send "&d#%{{_k}}% &e%{{astral.deseos::%{{_k}}%::jugador}}% &8%{{astral.deseos::%{{_k}}%::estado}}% &7%{{astral.deseos::%{{_k}}%::texto}}%" to player
            stop
        set {{_k}} to arg-2
        if {{astral.deseos.pend::%{{_k}}%}} is not set:
            send "&cEse deseo no esta pendiente." to player
            stop
        set {{_u}} to {{astral.deseos::%{{_k}}%::uuid}}
        if arg-1 is "aprobar":
            set {{astral.deseos::%{{_k}}%::estado}} to "aprobado"
            delete {{astral.deseos.pend::%{{_k}}%}}
            deseo_aviso({{_u}}, "&a✦ Tu deseo #%{{_k}}% fue &laprobado&a. El Admin lo va a cumplir pronto.")
            send "&aDeseo #%{{_k}}% aprobado. Recorda cumplirlo a mano." to player
        else if arg-1 is "rechazar":
            set {{_mot}} to arg-3 ? "sin motivo"
            set {{astral.deseos::%{{_k}}%::estado}} to "rechazado: %{{_mot}}%"
            delete {{astral.deseos.pend::%{{_k}}%}}
            # Puede volver a pedir otro deseo del mismo tipo.
            set {{astral.deseo.tiene::%{{_u}}%}} to {{astral.deseos::%{{_k}}%::tipo}}
            deseo_aviso({{_u}}, "&c✦ Tu deseo #%{{_k}}% fue rechazado (&f%{{_mot}}%&c). Podes pedir otro con &f/deseo&c.")
            send "&eDeseo #%{{_k}}% rechazado." to player

function deseo_aviso(u: text, m: text):
    loop all players:
        "%uuid of loop-player%" is {{_u}}
        send {{_m}} to loop-player
        play sound "block.note_block.chime" to loop-player
        stop
    add {{_m}} to {{astral.deseos.aviso::%{{_u}}%::*}}

on join:
    wait 5 seconds
    player is online
    loop {{astral.deseos.aviso::%uuid of player%::*}}:
        send loop-value to player
    delete {{astral.deseos.aviso::%uuid of player%::*}}
    if player has permission "{PERM_ADMIN}":
        set {{_c}} to size of {{astral.deseos.pend::*}}
        if {{_c}} > 0:
            send "&5[Deseos] &fHay &d%{{_c}}% &fdeseos esperando tu respuesta." to player
            {_tell("%name of player%", _button('[Ver pendientes]', 'light_purple', '/deseos'))}
    if {{astral.deseo.tiene::%uuid of player%}} is set:
        send "&d✦ Tenes un deseo sin pedir." to player
        {_tell("%name of player%", boton_deseo)}

# ------------------------------------------------------------------ Deseo lite (fin de la historia)
# misiones.py pone la etiqueta aq.deseo_lite al terminar el epilogo.
every 3 seconds:
    loop all players:
        scoreboard tags of loop-player contains "aq.deseo_lite"
        remove "aq.deseo_lite" from scoreboard tags of loop-player
        deseo_lite(loop-player)

function deseo_lite(p: player):
    if {{astral.deseo.tiene::%uuid of {{_p}}%}} is not "completo":
        set {{astral.deseo.tiene::%uuid of {{_p}}%}} to "lite"
    wait 4 seconds
{lite_msg}
    {_tell("%name of {_p}%", boton_deseo)}
    wait 2 seconds
    astral_deseo_abrir({{_p}})
'''


def commands():
    return '\n'.join([
        '# Renacimiento y deseos (generado por datapack-src/renacimiento.py). Consola, una vez.',
        f'lp group default permission set {VENCIDO} false',
        '# /deseos: los OP lo tienen solos (permiso sin definir). NO ponerlo en false para default:',
        '# eso tambien se lo quita al dueno. Para otro admin no OP:',
        f'# lp user Trainx permission set {PERM_ADMIN} true',
        '# Para mostrar el renacimiento en TAB/chat: %luckperms_meta_astral_renacimiento% o el sufijo ✦N.',
    ]) + '\n'


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'astral_renacimiento.sk').write_text(skript(), encoding='utf-8')
    (OUT / 'comandos.txt').write_text(commands(), encoding='utf-8')
    print('renacimiento:', OUT / 'astral_renacimiento.sk')


if __name__ == '__main__':
    generate()
