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
    items['info']={'slot':4,'material':'PAPER','item_model':'astral:cosmeticos/nav_info','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&b&lTu coleccion de insignias',
                   'lore':['&7Pasa el cursor por una insignia para leer su titulo.',
                           '&7Clic en una desbloqueada para equiparla.',
                           '&7Las apagadas con candado aun no son tuyas.',
                           '&7Cambiar de titulo conserva toda tu coleccion.']}
    items['gacha']={'slot':8,'material':'PAPER','item_model':'astral:cosmeticos/nav_gacha','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&6&lConseguir mas titulos',
                    'lore':['&7Abre la gacha Galeria Celeste.','&7Consulta sus precios y premios antes de tirar.'],
                    'click_commands':['[openguimenu] gacha_cosmeticos']}
    items['back']={'slot':45,'material':'PAPER','item_model':'astral:cosmeticos/nav_back','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&fVolver a Cosmeticos','click_commands':['[openguimenu] cosmeticos']}
    items['close']={'slot':53,'material':'PAPER','item_model':'astral:cosmeticos/nav_close','item_flags':['HIDE_ATTRIBUTES'],'display_name':'&cCerrar','click_commands':['[close]']}
    return {'menu_title':title(),'open_command':['titulos'],'register_command':True,'size':54,'items':items}


def hub_data():
    """/cosmeticos: dos tarjetas grandes, Titulos y Sombreros (referencia del dueno 12/11/2026)."""
    from cosmeticos_ui import hub_title, HUB_CARDS
    items={}
    texts={'titulos':('&6&lTITULOS',['&7Insignias que se muestran','&7junto a tu nombre en el chat.','','&eClic para ver tu coleccion.'],
                      'cosmeticos_titulos'),
           'sombreros':('&d&lSOMBREROS',['&7Gorros que se ven en tu cabeza.','&7Se ven sobre tu casco.','','&eClic para elegir uno.'],
                        'cosmeticos_sombreros')}
    for key,slots in HUB_CARDS.items():
        name,lore,target=texts[key]
        for i,slot in enumerate(slots):
            items[key if i==0 else f'{key}_hit_{i}']={'slot':slot,'material':'PAPER','item_model':f'astral:cosmeticos/hub_{key}_{i}',
                'item_flags':['HIDE_ATTRIBUTES'],'display_name':name,'lore':lore,
                'click_commands':['[sound] UI_BUTTON_CLICK',f'[openguimenu] {target}']}
    items['back']={'slot':45,'material':'PAPER','item_model':'astral:cosmeticos/nav_back','item_flags':['HIDE_ATTRIBUTES'],
                   'display_name':'&fVolver al Menu Astral','click_commands':['[openguimenu] principal']}
    items['gacha']={'slot':49,'material':'PAPER','item_model':'astral:cosmeticos/nav_gacha','item_flags':['HIDE_ATTRIBUTES'],
                    'display_name':'&6&lGacha de Cosmeticos','lore':['&7Titulos y gorros nuevos.'],
                    'click_commands':['[openguimenu] gacha_cosmeticos']}
    items['close']={'slot':53,'material':'PAPER','item_model':'astral:cosmeticos/nav_close','item_flags':['HIDE_ATTRIBUTES'],
                    'display_name':'&cCerrar','click_commands':['[close]']}
    return {'menu_title':hub_title(),'open_command':['cosmeticos'],'register_command':True,'size':54,'items':items}

def equipment_menu(kind):
    from cosmeticos_catalogo import catalog
    from gorros_ui import title as hat_title, HAT_SLOTS, CLEAR_SLOTS, BACK_SLOT, GACHA_SLOT
    items={}
    for index,(_,key,name,rarity,model) in enumerate(r for r in catalog() if r[0]==kind):
        perm=f'astral.cosmetico.{kind}.{key}'
        req={'requirements':{'obtenido':{'type':'has permission','permission':perm}}}
        legacy={'carnivora':'carnivora','diablo':'asura'}.get(key)
        if legacy:
            req['minimum_requirements']=1
            req['requirements']['compensacion']={'type':'has permission','permission':'astral.cosmetico.alas.'+legacy}
        slot=HAT_SLOTS[index]
        items[key]={'slot':slot,'material':'PAPER','item_model':'astral:cosmeticos/menu_sombrero_'+key,'priority':1,
            'display_name':'&d'+name,'lore':['&7Rareza: '+RARITIES[rarity][0],
            '&7No da proteccion ni estadisticas.','&7Se ve sobre tu casco.','&eClic para equipar.'],
            'view_requirement':req,
            'click_requirement':dict(req,deny_commands=['[message] &cTodavia no lo desbloqueaste.']),
            'click_commands':['[close]',f'[player] astralcosmetic {kind} {key}']}
        items[key+'_locked']={'slot':slot,'material':'GRAY_DYE','item_model':'astral:menu/icon_lock','priority':2,
            'display_name':'&8'+name,'lore':['&7Rareza: '+RARITIES[rarity][0],'&7Se consigue en la Gacha de Cosmeticos.'],
            'click_commands':['[message] &7Todavia no lo desbloqueaste.']}
    for index,slot in enumerate(CLEAR_SLOTS):
        items['clear' if index==0 else f'clear_hit_{index}']={'slot':slot,'material':'PAPER',
            'item_model':f'astral:cosmeticos/quitar_sombrero_{index}','item_flags':['HIDE_ATTRIBUTES'],
            'display_name':'&eQuitar sombrero','lore':['&7Deja tu cabeza sin gorro.','&7Tu casco sigue puesto.'],
            'click_commands':['[close]',f'[player] astralcosmetic {kind} quitar']}
    items['back']={'slot':BACK_SLOT,'material':'PAPER','item_model':'astral:cosmeticos/nav_back','item_flags':['HIDE_ATTRIBUTES'],
        'display_name':'&fVolver a Cosmeticos','click_commands':['[openguimenu] cosmeticos']}
    items['gacha']={'slot':GACHA_SLOT,'material':'PAPER','item_model':'astral:cosmeticos/nav_gacha','item_flags':['HIDE_ATTRIBUTES'],
        'display_name':'&dGacha de Cosmeticos','lore':['&7Titulos y gorros nuevos.'],
        'click_commands':['[openguimenu] gacha_cosmeticos']}
    return {'menu_title':hat_title(), 'size':54,'items':items}


def script():
    lines=['# Generado por cosmeticos.py. Equipar cambia solo el prefijo cosmetico de prioridad 100.',
           'command /titulo [<text>]:','    executable by: players','    trigger:',
           '        if arg-1 is not set:','            execute console command "dm open cosmeticos_titulos %name of player%"','            stop',
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
    menu.write_text(json.dumps(hub_data(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    menu.with_name('cosmeticos_titulos.yml').write_text(json.dumps(menu_data(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    out=ROOT/'build/gameplay';out.mkdir(parents=True,exist_ok=True)
    (out/'astral_cosmeticos.sk').write_text(script(),encoding='utf-8')
    for kind in ('sombreros',):
        dest=menu.with_name('cosmeticos_'+kind+'.yml')
        dest.write_text(json.dumps(equipment_menu('sombrero' if kind=='sombreros' else 'alas'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    retired=menu.with_name('cosmeticos_alas.yml')
    if retired.exists():retired.unlink()
    # La unica salida de CrazyCrates es lobby.py: no reusar respaldos privados viejos.


if __name__=='__main__':generate()
