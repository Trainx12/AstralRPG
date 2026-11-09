"""Estrella reservada del menu. Skript puro + identidad validada por el datapack."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREDICATE = '*[minecraft:custom_data~{astral_menu:1b}]'
STAR = 'minecraft:nether_star[minecraft:custom_data={astral_menu:1b},minecraft:custom_name={text:"Menu Astral",color:"aqua",bold:true,italic:false},minecraft:lore=[{text:"Clic derecho para abrir el menu.",color:"gray",italic:false},{text:"No se puede tirar ni vender.",color:"dark_gray",italic:false}],minecraft:enchantment_glint_override=true]'


def generate(files=None):
    if files is not None:
        def fn(name, lines):
            files[f'data/astral/function/menu_star/{name}.mcfunction'] = '\n'.join(lines) + '\n'
        fn('check', [
            'tag @s remove astral.menu.held',
            'tag @s remove astral.menu.slot',
            f'execute if items entity @s weapon.mainhand {PREDICATE} run tag @s add astral.menu.held',
            f'execute if items entity @s hotbar.8 {PREDICATE} run tag @s add astral.menu.slot'])
        # Mover primero a un slot libre conserva cantidad y todos los componentes.
        # Solo con inventario lleno se usa el respaldo en storage y el drop.
        fn('give', [
            f'execute if items entity @s hotbar.8 {PREDICATE} run return run function astral:menu_star/cleanup',
            f'clear @s {PREDICATE}',
            *[f'execute if items entity @s hotbar.8 * unless items entity @s container.{i} * run return run function astral:menu_star/move {{slot:"container.{i}"}}' for i in range(36) if i != 8],
            'data remove storage astral:menu_star displaced',
            'data modify storage astral:menu_star displaced set from entity @s Inventory[{Slot:8b}]',
            'data remove storage astral:menu_star displaced.Slot',
            f'item replace entity @s hotbar.8 with {STAR} 1',
            'execute if data storage astral:menu_star displaced.id run function astral:menu_star/restore with storage astral:menu_star',
            'data remove storage astral:menu_star displaced'])
        fn('move', ['$item replace entity @s $(slot) from entity @s hotbar.8', f'item replace entity @s hotbar.8 with {STAR} 1'])
        fn('cleanup', [f'execute if items entity @s container.{i} {PREDICATE} run item replace entity @s container.{i} with minecraft:air' for i in range(36) if i != 8] + [f'execute if items entity @s weapon.offhand {PREDICATE} run item replace entity @s weapon.offhand with minecraft:air'])
        fn('restore', ['$summon minecraft:item ~ ~ ~ {Item:$(displaced),PickupDelay:0s}'])
    out = ROOT / 'build/gameplay'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'astral_estrella.sk').write_text(script(), encoding='utf-8')
    (out / 'estrella-despliegue.txt').write_text('''Estrella del Menu: Paper 26.1.2 + Skript 2.17, sin addons.
APAGAR el servidor antes de reemplazar el datapack; luego arrancar.
build/AstralRPG-Items.zip -> world/datapacks/AstralRPG-Items.zip
build/gameplay/astral_estrella.sk -> plugins/Skript/scripts/astral_estrella.sk
build/menus/DeluxeMenus/gui_menus/principal.yml -> plugins/DeluxeMenus/gui_menus/principal.yml
build/menus/DeluxeMenus/gui_menus/comandos.yml -> plugins/DeluxeMenus/gui_menus/comandos.yml
Integrar la entrada portales de build/menus/DeluxeMenus/config-gui_menus.yml en plugins/DeluxeMenus/config.yml, dentro de gui_menus (sin borrar las otras).
portales:
  file: portales.yml
El archivo portales.yml existente debe estar en plugins/DeluxeMenus/gui_menus/portales.yml.
Si falta: build/menus/DeluxeMenus/gui_menus/portales.yml -> misma ruta del servidor.
Con el servidor iniciado, consola sin /:
dm reload
skript:skript reload astral_estrella
minecraft:reload solo si se requiere recargar el datapack tras el arranque (el arranque ya lo carga).
Reponer manualmente: estrella <jugador> (OP).
Revisar consola: sin errores Skript/DeluxeMenus/datapack.
Verificar supervivencia y creativo: ambos clics, Q, shift-clic, tecla 9, F, arrastre, doble clic, marcos/soportes, muerte con AxGraves, cambio de mundo, inventario lleno, /sellgui, venta rapida, /ah sell, /sell all, /trade.
No cambiar el resource pack ni su SHA-1. Nunca subir/reemplazar mundos.
''', encoding='utf-8')


def script():
    return '''# Generado por estrella_menu.py. Skript 2.17+, sin addons.
# Referencia completa obtenida SOLO de un slot validado por custom_data.
# Comparar items incluye componentes: una estrella vanilla o renombrada no coincide.
function astral_menu_refresh(p: player):
    if {_p} is dead:
        stop
    execute console command "execute as %name of {_p}% at @s run function astral:menu_star/give"
    execute console command "execute as %name of {_p}% run function astral:menu_star/check"
    if scoreboard tags of {_p} contains "astral.menu.slot":
        set {-astral.menu.reference} to slot 8 of inventory of {_p}

function astral_menu_item(i: item) :: boolean:
    if {-astral.menu.reference} is set:
        if {_i} is {-astral.menu.reference}:
            return true
    return false

# Identidad de cualquier slot, sin depender del nombre ni de su lore.
function astral_menu_slot(p: player, slot: text) :: boolean:
    remove "astral.menu.test" from scoreboard tags of {_p}
    execute console command "execute as %name of {_p}% if items entity @s %{_slot}% *[minecraft:custom_data~{astral_menu:1b}] run tag @s add astral.menu.test"
    if scoreboard tags of {_p} contains "astral.menu.test":
        remove "astral.menu.test" from scoreboard tags of {_p}
        return true
    return false

function astral_menu_held(p: player) :: boolean:
    if tool of {_p} is not nether star:
        return false
    execute console command "execute as %name of {_p}% run function astral:menu_star/check"
    if scoreboard tags of {_p} contains "astral.menu.held":
        return true
    return false

on load:
    loop all players:
        astral_menu_refresh(loop-player)

on join:
    wait 2 ticks
    astral_menu_refresh(player)

on respawn:
    wait 2 ticks
    astral_menu_refresh(player)

on world change:
    wait 2 ticks
    astral_menu_refresh(player)

every 5 seconds:
    loop all players:
        astral_menu_refresh(loop-player)

on right click:
    if astral_menu_held(player) is true:
        cancel event
        execute console command "dm open principal %player%"

on left click:
    if astral_menu_held(player) is true:
        cancel event
        execute console command "dm open principal %player%"

on break:
    if astral_menu_held(player) is true:
        cancel event

on right click on entity:
    if astral_menu_held(player) is true:
        cancel event
    if astral_menu_slot(player, "weapon.offhand") is true:
        cancel event

on damage:
    attacker is a player
    if astral_menu_held(attacker) is true:
        cancel event

on drop:
    # El ItemDrop aun no esta agregado al mundo: no usar selector de entidad aqui.
    if index of current hotbar slot of player is 8:
        cancel event
    if astral_menu_item(event-item) is true:
        cancel event

on swap hand items:
    if astral_menu_held(player) is true:
        cancel event
    if astral_menu_slot(player, "weapon.offhand") is true:
        cancel event

# Misma regla para cofres, sellgui, venta rapida, subastas y AxTrade.
on inventory click:
    if clicked inventory is inventory of player:
        if event-item is nether star:
            set {_slot} to index of event-slot
            if astral_menu_slot(player, "container.%{_slot}%") is true:
                cancel event
    if astral_menu_item(event-item) is true:
        cancel event
    if cursor slot of player is nether star:
        if astral_menu_slot(player, "player.cursor") is true:
            cancel event
    if astral_menu_item(cursor slot of player) is true:
        cancel event
    if hotbar button is 8:
        cancel event
    # F dentro de un inventario usa otro tipo de click.
    if click type is swap offhand:
        if astral_menu_slot(player, "weapon.offhand") is true:
            cancel event
    # Doble clic puede recolectar estrellas similares de otros slots.
    if click type is double click:
        if astral_menu_item(cursor slot of player) is true:
            cancel event

on inventory drag:
    if cursor slot of player is nether star:
        if astral_menu_slot(player, "player.cursor") is true:
            cancel event
    if astral_menu_item(cursor slot of player) is true:
        cancel event

# Antes de que AxGraves lea drops o inventario. Solo se elimina nuestra estrella.
on death of player with priority lowest:
    loop integers from 0 to 35:
        if slot loop-number of inventory of victim is nether star:
            if astral_menu_slot(victim, "container.%loop-number%") is true:
                set {_star} to slot loop-number of inventory of victim
                remove {_star} from drops
    if astral_menu_slot(victim, "weapon.offhand") is true:
        set {_star} to offhand item of victim
        remove {_star} from drops
    loop drops:
        if astral_menu_item(loop-item) is true:
            remove loop-item from drops
    execute console command "minecraft:clear %name of victim% *[minecraft:custom_data~{astral_menu:1b}]"

# Estos plugins pueden vender directamente sin pasar por InventoryClickEvent.
# Se bloquean sus comandos de venta aun con otro item seleccionado: /sell all incluye slot 9.
on command:
    # Venta rapida (/astralventa): vende solo el objeto del recuadro, no la estrella.
    if {-asg.selling::%uuid of player%} is set:
        stop
    set {_cmd} to lowercase command
    set {_parts::*} to {_cmd} split at ":"
    set {_cmd} to last element of {_parts::*}
    if {_cmd} is "sell" or "sellall" or "sellhand" or "sellinventory":
        cancel event
        send "&eUsa /sellgui: la Estrella del Menu no se vende." to player
    if {_cmd} is "ah" or "crazyauctions":
        set {_args} to lowercase "%arguments%"
        if {_args} starts with "sell":
            if astral_menu_held(player) is true:
                cancel event
                send "&cLa Estrella del Menu no se puede subastar." to player

command /estrella [<player>]:
    trigger:
        if sender is a player:
            if player is not op:
                stop
        set {_p} to arg-1
        if {_p} is not set:
            if sender is not a player:
                send "Indica el jugador: estrella <jugador>"
                stop
            set {_p} to player
        astral_menu_refresh({_p})
'''


if __name__ == '__main__':
    generate()
