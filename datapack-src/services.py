"""Backend de interfaces de servicios y Skript generado para Aternos."""
import json
import re
from pathlib import Path
from items import MEJORAS, MATERIALS
from services_ui import title

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'build/services'


def generate(files,items):
    def fn(name,lines):files[f'data/astral/function/mejora/gui/{name}.mcfunction']='\n'.join(lines)+'\n'
    mats=sorted({m for _,_,recipe in MEJORAS.values() for m,_ in recipe})
    inspect=['tag @s remove asgui.valid','tag @s remove asgui.max','tag @s remove asgui.ready',
             'tag @s remove asgui.attempted','tag @s remove asgui.success',
             'scoreboard players set @s astralmejok 0','scoreboard players set @s astralmejn 0']
    inspect += [f'tag @s remove asgui.next{n}' for n in MEJORAS]
    inspect += [f'tag @s remove asgui.mat.{m}' for m in mats]
    inspect += ['scoreboard players set #k astral.tmp 0',
        'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"weapon"}}] unless items entity @s weapon.mainhand minecraft:carrot_on_a_stick run scoreboard players set #k astral.tmp 1',
        'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{astral:{type:"armor"}}] run scoreboard players set #k astral.tmp 2',
        'execute if score #k astral.tmp matches 0 run return 0','tag @s add asgui.valid','scoreboard players set #l astral.tmp 0']
    for n in MEJORAS:
        for enchant in ('mejora_arma','mejora_armadura'):
            inspect += [f'execute if items entity @s weapon.mainhand *[minecraft:enchantments~[{{enchantments:"astral:{enchant}",levels:{n}}}]] run scoreboard players set #l astral.tmp {n}']
    inspect += ['execute if score #l astral.tmp matches 10.. run return run tag @s add asgui.max',
        'scoreboard players operation #n astral.tmp = #l astral.tmp','scoreboard players add #n astral.tmp 1']
    inspect += [f'execute if score #n astral.tmp matches {n} run function astral:mejora/gui/inspect/{n}' for n in MEJORAS]
    fn('inspect',inspect)
    for n,(_,_,recipe) in MEJORAS.items():
        lines=[f'tag @s add asgui.next{n}',f'scoreboard players set @s astralmejn {n}','scoreboard players set #falta astral.tmp 0']
        for material,amount in recipe:
            lines += [f'execute store result score #c astral.tmp run clear @s *[minecraft:custom_data~{{astral:{{id:"{material}"}}}}] 0',
                      f'execute if score #c astral.tmp matches {amount}.. run tag @s add asgui.mat.{material}',
                      f'execute unless score #c astral.tmp matches {amount}.. run scoreboard players set #falta astral.tmp 1']
        fn(f'inspect/{n}',lines+['execute if score #falta astral.tmp matches 0 run tag @s add asgui.ready'])
    fn('apply',['function astral:mejora/gui/inspect','execute unless entity @s[tag=asgui.ready] run return 0',
        'tag @s add asgui.attempted']+
        [f'execute if entity @s[tag=asgui.next{n}] run function astral:mejora/n/{n}' for n in MEJORAS]+
        ['execute if score @s astralmejok matches 1.. run tag @s add asgui.success'])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'astral_servicios.sk').write_text(script(),encoding='utf-8')


def script():
    # Los precios son SOLO vista previa. /economyshopgui:sellall hand valida
    # metadatos, permisos, limites y hace la transaccion economica real.
    catalog=json.loads((ROOT/'services_catalog.json').read_text())
    setup=['on load:', '    delete {asg.gui::*}', '    delete {asg.mode::*}', '    delete {asg.busy::*}',
           '    delete {asg.saleprice::*}', '    delete {asg.salemax::*}']
    for material,price in catalog.items():
        setup += [f'    set {{_type}} to "minecraft:{material.lower()}" parsed as item type',
                  '    if {_type} is set:',f'        set {{asg.saleprice::%{{_type}}%}} to {price["min"]}',
                  f'        set {{asg.salemax::%{{_type}}%}} to {price["max"]}']
    setup += ['    send "[AstralRPG] Interfaces Herrero/Venta cargadas." to console','']
    options=['options:',f'    forge-title: {title("herrero")}',f'    sale-title: {title("venta")}','']
    cost=['function asg_cost(n: number) :: number:']
    for n,(money,_,_) in MEJORAS.items():cost += [f'    if {{_n}} is {n}:',f'        return {money}']
    cost+=['    return 0','']
    render_mats=[]
    for n,(_,_,recipe) in MEJORAS.items():
        render_mats += [f'    if {{_n}} is {n}:']
        for index,(material,amount) in enumerate(recipe):
            name=MATERIALS[material][0]
            render_mats += [f'        set {{_mat}} to asg_icon("astral:{material}", "&e{name} x{amount}")',
                f'        set item amount of {{_mat}} to {amount}',
                f'        if "asgui.mat.{material}" is in scoreboard tags of {{_p}}:',
                '            set lore of {_mat} to "&aMateriales suficientes en tu inventario."',
                '        else:', '            set lore of {_mat} to "&cFaltan materiales en tu inventario."',
                f'        set slot {23+index} of {{_inv}} to {{_mat}}']
    core=r'''
function asg_icon(model: text, label: text) :: item:
    set {_i} to paper named colored {_label}
    set item model of {_i} to {_model}
    return {_i}

function asg_bar(p: player, model: text, label: text):
    set {_inv} to {asg.gui::%uuid of {_p}%}
    loop 7 times:
        set {_index} to loop-number - 1
        set {_slot} to loop-number + 27
        set slot {_slot} of {_inv} to asg_icon("astral:servicios/bar_%{_model}%_%{_index}%", {_label})

function asg_action(p: player, model: text, label: text, lines: texts):
    set {_inv} to {asg.gui::%uuid of {_p}%}
    set {_size} to 3
    set {_start} to 39
    if {asg.mode::%uuid of {_p}%} is "sale":
        set {_size} to 4
        set {_start} to 41
    loop {_size} times:
        set {_index} to loop-number - 1
        set {_slot} to {_start} + {_index}
        set {_i} to asg_icon("astral:servicios/%{_model}%_%{_index}%", {_label})
        set lore of {_i} to {_lines::*}
        set slot {_slot} of {_inv} to {_i}

function asg_return(p: player):
    set {_id} to uuid of {_p}
    set {_saved} to {asg.escrow::%{_id}%}
    delete {asg.escrow::%{_id}%}
    if {asg.gui::%{_id}%} is set:
        if {asg.mode::%{_id}%} is "forge":
            set slot 20 of {asg.gui::%{_id}%} to air
        else:
            set slot 24 of {asg.gui::%{_id}%} to air
    delete {asg.gui::%{_id}%}
    delete {asg.mode::%{_id}%}
    delete {asg.busy::%{_id}%}
    delete {asg.notice::%{_id}%}
    if {_saved} is set:
        if {_saved} is not air:
            if {_p} has enough space for {_saved}:
                give {_saved} to {_p}
            else:
                drop {_saved} at location of {_p}

function asg_inspect(p: player):
    set {_id} to uuid of {_p}
    set {_original} to {_p}'s tool
    set {_p}'s tool to {asg.escrow::%{_id}%}
    execute console command "execute as %name of {_p}% at @s run function astral:mejora/gui/inspect"
    set {_p}'s tool to {_original}

function asg_sale_allowed(i: item) :: boolean:
    if {_i} is air:
        return false
    set {_model} to item model of {_i}
    if {_model} is set:
        if {_model} starts with "astral:":
            return false
    if name of {_i} is set:
        return false
    if lore of {_i} is set:
        return false
    if enchantments of {_i} is set:
        return false
    set {_type} to type of {_i}
    if {asg.saleprice::%{_type}%} is not set:
        return false
    return true

function asg_refresh(p: player):
    set {_id} to uuid of {_p}
    set {_inv} to {asg.gui::%{_id}%}
    if {_inv} is not set:
        stop
    if {asg.busy::%{_id}%} is true:
        stop
    set {_held} to {asg.escrow::%{_id}%}
    if {asg.mode::%{_id}%} is "sale":
        set slot 24 of {_inv} to {_held}
        if {_held} is not set:
            asg_bar({_p}, "sale_empty", "&eColoca un objeto en el recuadro rojo.")
            asg_action({_p}, "sell_blocked", "&7VENDER", "&7Primero coloca un objeto.")
            set slot 20 of {_inv} to emerald named "&6Precio de venta"
            stop
        if asg_sale_allowed({_held}) is false:
            asg_bar({_p}, "invalid", "&cEste objeto no se admite en venta rapida.")
            asg_action({_p}, "sell_blocked", "&cVENDER", "&7No se venden objetos RPG, renombrados o encantados.")
            stop
        set {_type} to type of {_held}
        set {_price} to {asg.saleprice::%{_type}%}
        set {_amount} to item amount of {_held}
        set {_total} to {_price} * {_amount}
        set {_quote} to emerald named "&6&lTotal estimado: %{_total}%$"
        set lore of {_quote} to "&7Unidad: &e%{_price}%$", "&7Cantidad: &f%{_amount}%", "&7El vendedor valida el precio al confirmar." and "&7Cerrar devuelve tu objeto."
        set slot 20 of {_inv} to {_quote}
        asg_bar({_p}, "sale_ready", "&eRevisa el importe pasando el cursor por la esmeralda.")
        asg_action({_p}, "sell", "&a&lVENDER por %{_total}%$ (estimado)", "&7Confirma solo la venta del objeto depositado.")
        stop
    set slot 20 of {_inv} to {_held}
    set slot 23 of {_inv} to air
    set slot 24 of {_inv} to air
    if {_held} is not set:
        asg_bar({_p}, "empty", "&eColoca un arma o armadura de AstralRPG.")
        asg_action({_p}, "blocked", "&7MEJORAR", "&7Primero coloca tu equipo.")
        stop
    asg_inspect({_p})
    if "asgui.valid" is not in scoreboard tags of {_p}:
        asg_bar({_p}, "invalid", "&cSolo equipo de AstralRPG. Los bastones no se mejoran.")
        asg_action({_p}, "blocked", "&cMEJORAR", "&7Este objeto no es mejorable.")
        stop
    if "asgui.max" is in scoreboard tags of {_p}:
        asg_bar({_p}, "max", "&6Tu equipo ya alcanzo +10.")
        asg_action({_p}, "blocked", "&6NIVEL MAXIMO", "&7No hay mas mejoras.")
        stop
    set {_n} to 0
    loop 10 times:
        if "asgui.next%loop-number%" is in scoreboard tags of {_p}:
            set {_n} to loop-number
    if {_n} is 0:
        stop
    set {_cost} to asg_cost({_n})
    set {_coins} to gold nugget named "&6Costo: %{_cost}%$"
    set lore of {_coins} to "&7Tu saldo: &e%balance of {_p}%$" and "&7El dinero se cobra solo si la mejora tiene exito."
    set slot 26 of {_inv} to {_coins}
__MATERIALS__
    set {_model} to "blocked"
    set {_label} to "&cFaltan materiales o dinero"
    if "asgui.ready" is in scoreboard tags of {_p}:
        if balance of {_p} >= {_cost}:
            set {_model} to "improve"
            set {_label} to "&a&lMEJORAR A +%{_n}%"
    asg_bar({_p}, "level%{_n}%", "&eSiguiente mejora, dinero y probabilidad de exito.")
    if {asg.notice::%{_id}%} is set:
        asg_bar({_p}, {asg.notice::%{_id}%}, "&eResultado del ultimo intento. Tu equipo permanece en el slot.")
    asg_action({_p}, {_model}, {_label}, "&7Materiales en tu inventario, dinero y probabilidad arriba." and "&7Si falla: se pierden materiales, no el equipo ni el dinero.")

function asg_open(p: player, mode: text):
    close {_p}'s inventory
    asg_return({_p})
    set {_id} to uuid of {_p}
    if {_mode} is "forge":
        set {_inv} to a new chest inventory with 6 rows named colored "{@forge-title}"
    else:
        set {_inv} to a new chest inventory with 6 rows named colored "{@sale-title}"
    set {asg.gui::%{_id}%} to {_inv}
    set {asg.mode::%{_id}%} to {_mode}
    set slot 8 of {_inv} to book named "&eComo usar"
    set lore of slot 8 of {_inv} to "&71. Coloca el objeto en el recuadro.", "&72. Revisa los requisitos o el precio.", "&73. Pulsa el boton para confirmar." and "&7Cerrar o desconectarte devuelve tu objeto."
    set slot 45 of {_inv} to arrow named "&eDevolver objeto"
    set slot 53 of {_inv} to barrier named "&cCerrar y devolver"
    asg_refresh({_p})
    open {_inv} to {_p}

command /astralherrero [<player>]:
    trigger:
        if arg-1 is set:
            if sender is not console:
                stop
            asg_open(arg-1, "forge")
        else:
            if sender is a player:
                asg_open(player, "forge")

command /astralventa [<player>]:
    trigger:
        if arg-1 is set:
            if sender is not console:
                stop
            asg_open(arg-1, "sale")
        else:
            if sender is a player:
                asg_open(player, "sale")

on inventory click:
    set {_id} to uuid of player
    set {_inv} to {asg.gui::%{_id}%}
    if {_inv} is not set:
        stop
    if player's current inventory is not {_inv}:
        asg_return(player)
        stop
    cancel event
    if {asg.busy::%{_id}%} is true:
        stop
    set {_target} to 20
    if {asg.mode::%{_id}%} is "sale":
        set {_target} to 24
    if clicked inventory is player's inventory:
        if click type is left mouse button or right mouse button:
            uncancel event
            stop
        if click type is shift left mouse button or shift right mouse button:
            if {asg.escrow::%{_id}%} is not set:
                set {_item} to event-slot
                if {_item} is not air:
                    if {asg.mode::%{_id}%} is "forge":
                        if item amount of {_item} is not 1:
                            send "&cColoca una sola pieza de equipo." to player
                            stop
                    set {asg.escrow::%{_id}%} to {_item}
                    set event-slot to air
                    delete {asg.notice::%{_id}%}
                    asg_refresh(player)
        stop
    if clicked inventory is not {_inv}:
        stop
    if click type is not left mouse button:
        if click type is not right mouse button:
            stop
    set {_slot} to index of event-slot
    if {_slot} is 53:
        close player's inventory
        stop
    if {_slot} is 45:
        set {_saved} to {asg.escrow::%{_id}%}
        delete {asg.escrow::%{_id}%}
        set slot {_target} of {_inv} to air
        delete {asg.notice::%{_id}%}
        if {_saved} is set:
            if player has enough space for {_saved}:
                give {_saved} to player
            else:
                drop {_saved} at player's location
        asg_refresh(player)
        stop
    if {_slot} is {_target}:
        set {_cursor} to cursor slot of player
        set {_old} to {asg.escrow::%{_id}%}
        if {_cursor} is air:
            if {_old} is set:
                delete {asg.escrow::%{_id}%}
                set slot {_target} of {_inv} to air
                set cursor slot of player to {_old}
        else:
            if {asg.mode::%{_id}%} is "forge":
                if item amount of {_cursor} is not 1:
                    send "&cColoca una sola pieza de equipo." to player
                    stop
            set {asg.escrow::%{_id}%} to {_cursor}
            if {_old} is set:
                set cursor slot of player to {_old}
            else:
                set cursor slot of player to air
        delete {asg.notice::%{_id}%}
        asg_refresh(player)
        stop
    if {asg.mode::%{_id}%} is "sale":
        if {_slot} is between 41 and 44:
            set {_item} to {asg.escrow::%{_id}%}
            if {_item} is not set:
                stop
            if asg_sale_allowed({_item}) is false:
                send "&cEl vendedor no admite ese objeto. Podes retirarlo o cerrar." to player
                stop
            set {asg.busy::%{_id}%} to true
            set {_original} to player's tool
            set {_amount} to item amount of {_item}
            set {_money} to balance of player
            set player's tool to {_item}
            # La Estrella del Menu bloquea sellall (para no vender la estrella): esta venta es
            # solo del objeto depositado y la habilita con esta marca (08/11/2026).
            set {-asg.selling::%{_id}%} to true
            make player execute command "economyshopgui:sellall hand"
            delete {-asg.selling::%{_id}%}
            set {_rest} to player's tool
            set player's tool to {_original}
            delete {asg.escrow::%{_id}%}
            if {_rest} is not air:
                set {asg.escrow::%{_id}%} to {_rest}
            set slot 24 of {_inv} to {_rest}
            delete {asg.busy::%{_id}%}
            if balance of player > {_money}:
                send "&aVenta completada. Tu saldo y el objeto se actualizaron." to player
            else:
                send "&eNo se pudo vender. Tu objeto se conserva en el recuadro." to player
            asg_refresh(player)
        stop
    if {_slot} is between 39 and 41:
        if {asg.escrow::%{_id}%} is not set:
            stop
        asg_refresh(player)
        if "asgui.ready" is not in scoreboard tags of player:
            send "&cRevisa el equipo y los materiales indicados." to player
            stop
        set {_n} to 0
        loop 10 times:
            if "asgui.next%loop-number%" is in scoreboard tags of player:
                set {_n} to loop-number
        set {_cost} to asg_cost({_n})
        if {_n} is 0:
            stop
        if balance of player < {_cost}:
            send "&cNecesitas %{_cost}%$ para este intento." to player
            stop
        set {asg.busy::%{_id}%} to true
        set {_original} to player's tool
        set player's tool to {asg.escrow::%{_id}%}
        execute console command "execute as %player% at @s run function astral:mejora/gui/apply"
        set {_result} to player's tool
        set player's tool to {_original}
        set {asg.escrow::%{_id}%} to {_result}
        set slot 20 of {_inv} to {_result}
        if "asgui.success" is in scoreboard tags of player:
            remove {_cost} from player's balance
            set {asg.notice::%{_id}%} to "ok%{_n}%"
        else if "asgui.attempted" is in scoreboard tags of player:
            set {asg.notice::%{_id}%} to "fail%{_n}%"
        delete {asg.busy::%{_id}%}
        asg_refresh(player)

on inventory drag:
    if {asg.gui::%uuid of player%} is set:
        if player's current inventory is {asg.gui::%uuid of player%}:
            cancel event

on inventory close:
    if {asg.gui::%uuid of player%} is set:
        asg_return(player)

on quit:
    if {asg.gui::%uuid of player%} is set:
        asg_return(player)

on join:
    if {asg.escrow::%uuid of player%} is set:
        wait 1 tick
        asg_return(player)

on unload:
    loop all players:
        if {asg.gui::%uuid of loop-player%} is set:
            asg_return(loop-player)
            close loop-player's inventory

every 10 ticks:
    loop all players:
        if {asg.gui::%uuid of loop-player%} is set:
            asg_refresh(loop-player)
'''.replace('__MATERIALS__','\n'.join(render_mats))
    core=re.sub(r'"([^"\n]+)" is not in scoreboard tags of (\{_p\}|player)',r'\2 does not have the scoreboard tag "\1"',core)
    core=re.sub(r'"([^"\n]+)" is in scoreboard tags of (\{_p\}|player)',r'\2 has the scoreboard tag "\1"',core)
    core=core.replace('shift left mouse button or shift right mouse button','left mouse button with shift or right mouse button with shift')
    return '# Generado por datapack-src/services.py. Requiere Skript 2.17+, Vault y EconomyShopGUI.\n'+ '\n'.join(options+cost+setup)+core
