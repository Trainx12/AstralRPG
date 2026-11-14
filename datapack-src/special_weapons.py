"""Armas independientes de las clases; balance y recursos generados."""
from pathlib import Path

WEAPONS = {
    'espada_tormenta': dict(name='Filo de la Tormenta', base='netherite_sword', color='#79dfff', damage=9, speed=1.6,
        cost=[('c','shadowsteel',4),('c','gema_luminica',2),('v','minecraft:lightning_rod',1)]),
    'espada_sombras': dict(name='Danza del Ender', base='netherite_sword', color='#b174ff', damage=10, speed=1.6,
        cost=[('c','shadowsteel',5),('c','gema_umbria',3),('v','minecraft:ender_pearl',8)]),
    'espada_destello': dict(name='Filo del Destello', base='netherite_sword', color='#61ffe0', damage=7, speed=1.8,
        cost=[('c','cristal_refinado',3),('c','nucleo_eolico',1),('v','minecraft:ender_pearl',4)]),
    'hacha_terremoto': dict(name='Hacha del Sismo', base='netherite_axe', color='#dda65d', damage=11, speed=1.0,
        cost=[('c','netherita_reforzada',4),('c','gema_luminica',2),('v','minecraft:obsidian',8)]),
    # Cura: no pega fuerte (dano 1). Modelo vanilla de palo con brillo hasta tener textura propia.
    'varita_curacion': dict(name='Varita de Curación', base='stick', color='#7dff9a', damage=1, speed=1.6,
        model='minecraft:stick', glint=True,
        cost=[('c','cristal_refinado',2),('c','gema_luminica',1),('v','minecraft:ghast_tear',2)]),
    'varita_estallido': dict(name='Varita del Estallido', base='stick', color='#ff8673', damage=6, speed=1.5,
        cost=[('c','palo_reforzado',1),('c','cristal_arcano',3),('v','minecraft:blaze_powder',8)]),
}

# Números de las habilidades actuales, separados de su presentación.
from escala import FACTOR_ARMA, TIER_ESPECIAL, fmt, MANA_ESPECIAL, CD_DANZA, MANA_HECHIZO, CURACION
_scale = FACTOR_ARMA[TIER_ESPECIAL]
ABILITIES = {
    'espada_tormenta': [dict(name='Rayo de la Tormenta', trigger='AL GOLPEAR',
        description=['25% de invocar un rayo.', 'Daño: 30% del golpe (mínimo 1), radio 2 bloques.'])],
    'espada_sombras': [dict(name='Danza del Ender', trigger='CLIC DERECHO', mana=MANA_ESPECIAL['danza'], cooldown=CD_DANZA,
        description=['Salta y golpea hasta 6 enemigos a 12 bloques.',
                     f'Cada golpe causa {fmt(10*_scale)} de daño; un salto cada 4 ticks.'],
        notes=['No atraviesa paredes. Usable en mazmorras.'])],
    'espada_destello': [dict(name='Transmisión Instantánea', trigger='CLIC DERECHO', mana=MANA_ESPECIAL['destello'],
        description=['Teletransporta hasta 12 bloques hacia adelante', 'y da +50 de Velocidad por 3 segundos.'],
        notes=['Sin recarga. No usable en mazmorras.'])],
    'hacha_terremoto': [dict(name='Onda Sísmica', trigger='CLIC DERECHO', mana=MANA_ESPECIAL['sismo'], cooldown=6,
        description=[f'Onda de {fmt(10*_scale)} de daño hasta 5 bloques.', 'Levanta el suelo a tu alrededor.'])],
    'varita_curacion': [dict(name='Curación', trigger='CLIC DERECHO', mana=MANA_ESPECIAL['curacion'], cooldown=1,
        description=[f"Cura el {CURACION['pct']}% de tu vida máxima por segundo",
                     f"durante {CURACION['segundos']} s, a vos y a los jugadores a {CURACION['radio']} bloques."],
        notes=['Las curaciones de varita no se acumulan. Usable en el lobby.'])],
    'varita_estallido': [dict(name='Estallido', trigger='AL GOLPEAR', mana=MANA_ESPECIAL['estallido'],
        description=[f'Explosión de {fmt(6*_scale)} de daño en radio 2.']),
        dict(name='Proyectil Explosivo', trigger='CLIC DERECHO', mana=MANA_ESPECIAL['estallido'], cooldown=1,
        description=['Disparo instantáneo hasta 16 bloques.', f'Explosión de {fmt(6*_scale)} de daño en radio 2.'])],
}
for _iid, _weapon in WEAPONS.items():
    _weapon['abilities'] = ABILITIES[_iid]


def register(add_item, recipes, txt, weapon_mods):
    from escala import FACTOR_ARMA, TIER_ESPECIAL
    for iid, w in WEAPONS.items():
        add_item(iid, 'minecraft:'+w['base'], w['name'], w['color'],
                 [txt('Arma especial - cualquier clase', w['color'])] +
                 [txt('Habilidades: mobs; jugadores solo en arena PvP.', 'yellow')],
                 {'type':'weapon', 'special':iid, 'tier':TIER_ESPECIAL}, model=w.get('model','astral:'+iid),
                 glint=w.get('glint'), kind='weapon',
                 pdc={'auraskills:ignore_interact':True},
                 extra={'minecraft:max_stack_size':1, 'minecraft:attribute_modifiers':weapon_mods(iid,w['damage']*FACTOR_ARMA[TIER_ESPECIAL],w['speed'])})
        recipes.append((iid,1,w['cost'],'Especiales'))


def script_options(text):
    """Completa en el .sk el mana y las recargas de escala.py (una sola fuente de numeros)."""
    import re
    values={'mana_destello':MANA_ESPECIAL['destello'],'mana_danza':MANA_ESPECIAL['danza'],'cd_danza':CD_DANZA,
            'mana_sismo':MANA_ESPECIAL['sismo'],'mana_estallido':MANA_ESPECIAL['estallido'],
            'mana_curacion':MANA_ESPECIAL['curacion'],'cura_pct':CURACION['pct'],
            'cura_segundos':CURACION['segundos'],'cura_radio':CURACION['radio'],
            **{f'mana_baston_{t}':v for t,v in MANA_HECHIZO.items()}}
    from minijuegos import arena_worlds
    arenas=' or '.join(f'"{w}" or "minecraft:{w}"' for w in arena_worlds())
    assert text.count('__ARENAS__')==1
    text=text.replace('__ARENAS__',arenas)
    for key,value in values.items():
        text,n=re.subn(rf'^(    {key}): .*$',rf'\g<1>: {value}',text,flags=re.M)
        assert n==1,key
    return text


def generate(files):
    lines=['tag @s remove astral.special'] + [f'tag @s remove astral.special.{iid}' for iid in WEAPONS]
    # Bastones de Mago: tier en la mano y si el hechizo esta en recarga (lo lee Skript para cobrar mana).
    lines+=['tag @s remove astral.staff','tag @s remove astral.spell.cd']+[f'tag @s remove astral.staff.t{t}' for t in range(1,11)]
    for t in range(1,11):
        staff=f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{id:"baston_{t}"}}}}]'
        lines+=[staff+' run tag @s add astral.staff',staff+f' run tag @s add astral.staff.t{t}']
    lines.append('execute if score @s astral.cd matches 1.. run tag @s add astral.spell.cd')
    for iid in WEAPONS:
        check=f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{astral:{{id:"{iid}"}}}}]'
        lines += [check+' run tag @s add astral.special', check+f' run tag @s add astral.special.{iid}']
    files['data/astral/function/special/identify.mcfunction']='\n'.join(lines)+'\n'
    import json
    # Caja dedicada: solo las cinco armas pedidas, aparte de los especiales anteriores.
    files['data/astral/loot_table/kit/armas_especiales.json']=json.dumps({'type':'minecraft:command','pools':[{'rolls':1,'entries':[
        {'type':'minecraft:item','name':'minecraft:cyan_shulker_box','functions':[
            {'function':'minecraft:set_contents','component':'minecraft:container','entries':[
                {'type':'minecraft:loot_table','value':'astral:item/'+iid} for iid in WEAPONS]},
            {'function':'minecraft:set_components','components':{'minecraft:item_name':{'text':'Kit: Armas Especiales','color':'aqua','italic':False}}}]}]}]})
    files['data/astral/function/admin/kit_armas_especiales.mcfunction']='loot give @s loot astral:kit/armas_especiales\n'
    root=Path(__file__).resolve().parent
    out=root.parent/'build/gameplay'
    out.mkdir(parents=True,exist_ok=True)
    (out/'astral_armas_especiales.sk').write_text(script_options((root/'special_weapons.sk').read_text(encoding='utf-8')),encoding='utf-8')
    (out/'fichas-despliegue.txt').write_text('''Fichas / Transmisión Instantánea / Defensa (ITEM_VERSION 11)
Destino: Empower, Paper 26.1.2, Skript 2.17.1, AuraSkills 2.4.0.

1. Apagar el servidor y reemplazar únicamente:
   build/AstralRPG-Items.zip -> world/datapacks/AstralRPG-Items.zip
   build/gameplay/astral_armas_especiales.sk -> plugins/Skript/scripts/special_weapons.sk
   No dejar una segunda copia con otro nombre.
2. Reemplazar solo el bloque action_bar de plugins/AuraSkills/messages/global.yml
   por build/gameplay/AuraSkills/global-action_bar.yml. Conservar el resto del archivo.
   Verificar action_bar.placeholder_api: true en plugins/AuraSkills/config.yml
   y la expansión ScoreboardObjectives de PlaceholderAPI.
3. Iniciar el servidor. El arranque carga el datapack y el script.
   Si se cambia el script con el servidor encendido: skript:skript reload special_weapons
   Recargar los mensajes: skills reload
   No usar Worlds > Upload ni reemplazar ningún mundo.
4. Revisar consola: sin errores de funciones, item modifiers ni Skript.
   loot give <jugador> loot astral:item/espada_1
   loot give <jugador> loot astral:item/espada_5
   loot give <jugador> loot astral:item/espada_destello
   Comprobar mejora +7 y migración conservando encantamientos/desgaste.
   Comprobar Defensa con/sin armadura; XP conserva su texto sin añadir defensa.
   Destello: 12 bloques, pared, techo, lava, mirada vertical, maná insuficiente,
   50 de maná por uso válido, +50% velocidad por 60 ticks sin acumular, reconexión,
   región WorldGuard que cancela teleport, lobby y mazmorras bloqueados.

Resource pack sin cambios: no actualizar URL ni SHA-1.
Encantamientos nativos visibles para conservar los añadidos por yunque/mesa.
Bastones sin estrellas: muestran el daño de spell/cast sin bonus de armadura.
Arcos/lanzas sin attack_damage propio no inventan un daño fijo; mantienen la
explicación de sus efectos. La mejora multiplica el daño final del encantamiento.
Vista previa ilustrativa: build/previews/fichas-armas.png (no instalar en servidor).
''',encoding='utf-8')
    skills=root.parent/'build/mythicmobs/skills'
    skills.mkdir(parents=True,exist_ok=True)
    (skills/'armas_especiales.yml').write_text('''# Puente sin addons para consultar el saldo real de AuraSkills.
ASW_LEER_MANA:
  Skills:
  - 'command{c="asw_mana <target.name> %auraskills_mana_int%"} @self'
''',encoding='utf-8')
