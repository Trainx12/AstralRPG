"""Coleccion permanente de titulos y seleccion sin consumir otros cosmeticos."""
import json
from pathlib import Path
from lobby import TITLES
from cosmeticos_ui import title, TITLE_SLOTS, CLEAR_SLOTS, RARITIES, key_for

ROOT=Path(__file__).resolve().parent.parent

def menu_data():
    items={}
    if len(TITLES)>len(TITLE_SLOTS):
        raise ValueError('La galeria admite catorce titulos; ampliar el diseno antes de agregar mas.')
    for index,(rarity,name,color) in enumerate(TITLES):
        key=key_for(name);perm='astral.cosmetico.titulo.'+key
        req={'requirements':{'obtenido':{'type':'has permission','permission':perm}}}
        items[key]={'slot':TITLE_SLOTS[index],'material':'PAPER','item_model':'astral:cosmeticos/'+key,
                    'item_flags':['HIDE_ATTRIBUTES'],'priority':1,'display_name':color+name,
                    'lore':['&7Rareza: &f'+RARITIES[rarity][0],'','&aInsignia desbloqueada.',
                            '&7Se muestra como titulo junto a tu nombre.','&eClic para equipar. Tus otros titulos se conservan.'],
                    'view_requirement':req,'click_requirement':dict(req,deny_commands=['[message] &cTodavia no obtuviste este titulo.']),
                    'click_commands':['[close]',f'[player] titulo {key}']}
        items[key+'_locked']={'slot':TITLE_SLOTS[index],'material':'PAPER',
                             'item_model':'astral:cosmeticos/'+key+'_locked','item_flags':['HIDE_ATTRIBUTES'],
                             'priority':2,'display_name':'&8'+name,
                             'lore':['&7Rareza: &f'+RARITIES[rarity][0],'','&8Insignia sin desbloquear.',
                                     '&7Se consigue en la Galeria Celeste.','&7Usa el cofre de arriba para ver la gacha.'],
                             'click_commands':['[message] &7Todavia no obtuviste este titulo.','[sound] ENTITY_VILLAGER_NO']}
    for index,slot in enumerate(CLEAR_SLOTS):
        items['none' if index==0 else f'none_hit_{index}']={
            'slot':slot,'material':'PAPER','item_model':f'astral:cosmeticos/clear_{index}',
            'item_flags':['HIDE_ATTRIBUTES'],'display_name':'&eQuitar titulo activo',
            'lore':['&7Deja tu nombre sin titulo.','&7Conservas todas tus insignias desbloqueadas.'],
            'click_commands':['[close]','[player] titulo quitar']}
    items['info']={'slot':4,'material':'PAPER','item_model':'astral:cosmeticos/nav_info','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&b&lTu coleccion de insignias',
                   'lore':['&7Pasa el cursor por una insignia para leer su titulo.',
                           '&7Clic en una desbloqueada para equiparla.',
                           '&7Las apagadas con candado aun no son tuyas.',
                           '&7Cambiar de titulo conserva toda tu coleccion.']}
    items['gacha']={'slot':8,'material':'PAPER','item_model':'astral:cosmeticos/nav_gacha','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&6&lConseguir mas titulos',
                    'lore':['&7Abre la gacha Galeria Celeste.','&7Consulta sus precios y premios antes de tirar.'],
                    'click_commands':['[openguimenu] gacha_cosmeticos']}
    items['back']={'slot':45,'material':'PAPER','item_model':'astral:cosmeticos/nav_back','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&fVolver al atlas','click_commands':['[openguimenu] principal']}
    items['close']={'slot':53,'material':'PAPER','item_model':'astral:cosmeticos/nav_close','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&cCerrar','click_commands':['[close]']}
    return {'menu_title':title(),'open_command':['cosmeticos','titulos'],'register_command':True,'size':54,'items':items}

def script():
    lines=['# Generado por cosmeticos.py. Equipar cambia solo el prefijo cosmetico de prioridad 100.',
           'command /titulo [<text>]:','    executable by: players','    trigger:',
           '        if arg-1 is not set:','            execute console command "dm open cosmeticos %name of player%"','            stop',
           '        if arg-1 is "quitar":','            execute console command "lp user %name of player% meta removeprefix 100"','            stop']
    for _,name,col in TITLES:
        key=name.lower().replace(' ','_')
        lines += [f'        if arg-1 is "{key}":',
                  f'            if player does not have permission "astral.cosmetico.titulo.{key}":',
                  '                send "&cTodavia no obtuviste este titulo." to player','                stop',
                  f'            execute console command "lp user %name of player% meta setprefix 100 ""{col}«{name}»"""',
                  f'            send "&aTitulo equipado: {name}. Tus otros titulos siguen guardados." to player','            stop']
    lines += ['        send "&eUsa /cosmeticos para elegir un titulo." to player']
    return '\n'.join(lines)+'\n'

def generate():
    menu=ROOT/'build/menus/DeluxeMenus/gui_menus/cosmeticos.yml';menu.parent.mkdir(parents=True,exist_ok=True)
    menu.write_text(json.dumps(menu_data(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    out=ROOT/'build/gameplay';out.mkdir(parents=True,exist_ok=True)
    (out/'astral_cosmeticos.sk').write_text(script(),encoding='utf-8')
    import yaml
    for filename in ('gacha_cosmeticos.yml','gacha_cosmeticos_garantia.yml'):
        backup=ROOT/'.local/backups'/(filename+'-antes-coleccion.yml')
        if not backup.exists():continue
        data=yaml.safe_load(backup.read_text(encoding='utf-8'))
        for prize in data['Crate']['Prizes'].values():
            commands=[]
            for command in prize.get('Commands',[]):
                if ' meta setprefix 100 ' not in command:
                    commands.append(command);continue
                matched=False
                for _,name,_ in TITLES:
                    if '«'+name+'»' not in command:continue
                    key=name.lower().replace(' ','_')
                    commands += [f'lp user %player% permission set astral.cosmetico.titulo.{key} true',
                        'tellraw %player% '+json.dumps({'text':f'Titulo {name} desbloqueado. Elige con /cosmeticos sin perder los anteriores.','color':'light_purple'},ensure_ascii=False)]
                    matched=True;break
                if not matched:raise ValueError('Titulo remoto desconocido: '+command)
            prize['Commands']=commands
        path=out/'CrazyCrates'/filename;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding='utf-8')

if __name__=='__main__':generate()
