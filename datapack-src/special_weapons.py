"""Armas independientes de las clases; balance y recursos generados."""
from pathlib import Path

WEAPONS = {
    'espada_tormenta': dict(name='Filo de la Tormenta', base='netherite_sword', color='#79dfff', damage=9, speed=1.6,
        lore=['Al golpear: 25% de invocar un rayo.', 'Rayo: +30% del golpe en radio de 2 bloques.'],
        cost=[('c','shadowsteel',4),('c','gema_luminica',2),('v','minecraft:lightning_rod',1)]),
    'espada_sombras': dict(name='Danza del Ender', base='netherite_sword', color='#b174ff', damage=10, speed=1.6,
        lore=['Click derecho: hasta 6 enemigos distintos.', '6 saltos y golpes en 1,5 segundos; alcance 12.', '15 mana | Recarga: 5 segundos.', 'No atraviesa paredes. Usable en mazmorras.'],
        cost=[('c','shadowsteel',5),('c','gema_umbria',3),('v','minecraft:ender_pearl',8)]),
    'espada_destello': dict(name='Filo del Destello', base='netherite_sword', color='#61ffe0', damage=7, speed=1.8,
        lore=['Click derecho: avanza 3 bloques segun tu mirada.', '10 mana | Sin recarga.', 'No atraviesa paredes. No usable en mazmorras.'],
        cost=[('c','cristal_refinado',3),('c','nucleo_eolico',1),('v','minecraft:ender_pearl',4)]),
    'hacha_terremoto': dict(name='Hacha del Sismo', base='netherite_axe', color='#dda65d', damage=11, speed=1.0,
        lore=['Click derecho: onda de 10 de dano hasta 5 bloques.', 'Levanta el suelo a tu alrededor.', '10 mana | Recarga: 6 segundos.'],
        cost=[('c','netherita_reforzada',4),('c','gema_luminica',2),('v','minecraft:obsidian',8)]),
    'varita_estallido': dict(name='Varita del Estallido', base='stick', color='#ff8673', damage=6, speed=1.5,
        lore=['Al golpear: explosion en radio de 2 bloques.', 'Click derecho: proyectil explosivo; alcance 16.', 'Explosion: 6 de dano | 5 mana por uso.', 'Recarga del disparo: 1 segundo.'],
        cost=[('c','palo_reforzado',1),('c','cristal_arcano',3),('v','minecraft:blaze_powder',8)]),
}


def register(add_item, recipes, txt, weapon_mods):
    for iid, w in WEAPONS.items():
        add_item(iid, 'minecraft:'+w['base'], w['name'], w['color'],
                 [txt('Arma especial - cualquier clase', w['color'])] + [txt(s) for s in w['lore']] +
                 [txt('Habilidades: mobs; jugadores solo en arena PvP.', 'yellow')],
                 {'type':'weapon', 'special':iid}, model='astral:'+iid, kind='weapon',
                 pdc={'auraskills:ignore_interact':True},
                 extra={'minecraft:max_stack_size':1, 'minecraft:attribute_modifiers':weapon_mods(iid,w['damage'],w['speed'])})
        recipes.append((iid,1,w['cost'],'Especiales'))


def generate(files):
    lines=['tag @s remove astral.special'] + [f'tag @s remove astral.special.{iid}' for iid in WEAPONS]
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
    (out/'astral_armas_especiales.sk').write_text((root/'special_weapons.sk').read_text(encoding='utf-8'),encoding='utf-8')
    skills=root.parent/'build/mythicmobs/skills'
    skills.mkdir(parents=True,exist_ok=True)
    (skills/'armas_especiales.yml').write_text('''# Puente sin addons para consultar el saldo real de AuraSkills.
ASW_LEER_MANA:
  Skills:
  - 'command{c="asw_mana <target.name> %auraskills_mana_int%"} @self'
''',encoding='utf-8')
