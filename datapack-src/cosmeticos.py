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
        legacy={'carnivora':'carnivora','diablo':'asura'}.get(key)
        if legacy:
            req['minimum_requirements']=1
            req['requirements']['compensacion']={'type':'has permission','permission':'astral.cosmetico.alas.'+legacy}
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
    items['sombreros']={'slot':0,'material':'LEATHER_HELMET','display_name':'&dSombreros','click_commands':['[openguimenu] cosmeticos_sombreros']}
    items['sombreros']['item_model']='astral:menu/icon_cosmeticos'
    items['sombreros']['display_name']='&d&lGORROS / SOMBREROS'
    items['titulos']={'slot':1,'material':'PAPER','item_model':'astral:menu/icon_titulos',
        'display_name':'&6&lTITULOS','lore':['&7Tu coleccion de insignias esta debajo.']}
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

def equipment_menu(kind):
    from cosmeticos_catalogo import catalog
    items={}
    for index,(_,key,name,rarity,model) in enumerate(r for r in catalog() if r[0]==kind):
        perm=f'astral.cosmetico.{kind}.{key}'
        req={'requirements':{'obtenido':{'type':'has permission','permission':perm}}}
        legacy={'carnivora':'carnivora','diablo':'asura'}.get(key)
        if legacy:
            req['minimum_requirements']=1
            req['requirements']['compensacion']={'type':'has permission','permission':'astral.cosmetico.alas.'+legacy}
        items[key]={'slot':9+index,'material':'PAPER','item_model':'astral:'+model,'priority':1,
            'display_name':'&d'+name,'lore':['&7Rareza: '+RARITIES[rarity][0],
            '&7No da proteccion ni estadisticas.', '&7Solo visible sin casco.' if kind=='sombrero' else '&7Deja libres tus dos manos.',
            '&eClic para equipar.'], 'view_requirement':req,
            'click_requirement':dict(req,deny_commands=['[message] &cTodavia no lo desbloqueaste.']),
            'click_commands':['[close]',f'[player] astralcosmetic {kind} {key}']}
        items[key+'_locked']={'slot':9+index,'material':'GRAY_DYE','item_model':'astral:menu/icon_lock','priority':2,
            'display_name':'&8'+name,'lore':['&7Se consigue en la Gacha de Cosmeticos.'],
            'click_commands':['[message] &7Todavia no lo desbloqueaste.']}
    items['clear']={'slot':49,'material':'BARRIER','item_model':'astral:menu/icon_clear','display_name':'&eQuitar',
        'click_commands':['[close]',f'[player] astralcosmetic {kind} quitar']}
    items['back']={'slot':45,'material':'ARROW','item_model':'astral:menu/icon_titulos','display_name':'&fTitulos',
        'click_commands':['[openguimenu] cosmeticos']}
    items['gacha']={'slot':53,'material':'CHEST','item_model':'astral:menu/icon_gacha_cosmeticos','display_name':'&dGacha de Cosmeticos',
        'click_commands':['[openguimenu] gacha_cosmeticos']}
    from gorros_ui import title as hat_title
    return {'menu_title':hat_title(), 'size':54,'items':items}


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
    for kind in ('sombreros',):
        dest=menu.with_name('cosmeticos_'+kind+'.yml')
        dest.write_text(json.dumps(equipment_menu('sombrero' if kind=='sombreros' else 'alas'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    retired=menu.with_name('cosmeticos_alas.yml')
    if retired.exists():retired.unlink()
    # La unica salida de CrazyCrates es lobby.py: no reusar respaldos privados viejos.


if __name__=='__main__':generate()
