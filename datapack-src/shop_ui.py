"""Aplica SOLO apariencia a copias locales de EconomyShopGUI (requiere PyYAML).

Las copias originales y los archivos de despliegue quedan en .local: pueden
contener opciones privadas del servidor. Nunca se incluyen en el resource pack.
"""
from pathlib import Path
import re
import yaml
from services_ui import title

ROOT=Path(__file__).resolve().parent.parent
LOCAL=ROOT/'.local'
OUT=LOCAL/'shop-ui-deploy'


def dump(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=150),encoding='utf-8')


def clear_fill(data):
    if not isinstance(data,dict):return
    for key,value in data.items():
        if key=='material' and str(value).upper()=='GRAY_STAINED_GLASS_PANE':data[key]='AIR'
        else:clear_fill(value)


def generate():
    config=(LOCAL/'economyshop-before-gui.yml').read_text(encoding='utf-8')
    data=yaml.safe_load(config)
    patch={'language-file':'lang-es.yml','locale':'es-AR'}
    for key in ['main-menu','main-menu-nav-bar','shops-nav-bar','transaction-screens-nav-bar',
                'buy-screen','sell-screen','buy-stacks-screen']:
        block=data[key]
        clear_fill(block)
        if key=='main-menu':block['gui-rows']=5
        if key.endswith('-screen'):
            block['menu-size']=5
            for button in block['items'].values():
                action=button.get('action','')
                if action in {'REMOVE1','REMOVE16','REMOVE32','ADD1','ADD16','ADD32'}:
                    button['slot']={'REMOVE1':'10-11','REMOVE16':'19-20','REMOVE32':'28-29','ADD1':'13-14','ADD16':'22-23','ADD32':'31-32'}[action]
                    button['material']='PAPER'
                    button.pop('stack-size',None)
                elif action=='CONFIRM_TRANSACTION':button['slot']='42-45'
                elif button.get('type')=='SELECTED_ITEM':button['slot']=25
                elif action in {'OPEN_BUY_STACKS','SELL_ALL'}:button['slot']=38
        patch[key]=block
    # Mantener comentarios y opciones ajenas; reemplazar solo bloques concretos.
    for key,value in patch.items():
        replacement=yaml.safe_dump({key:value},allow_unicode=True,sort_keys=False,width=150).rstrip()+'\n'
        pattern=rf'^{re.escape(key)}:.*?(?=^[A-Za-z][A-Za-z0-9_-]*:|\Z)'
        config,count=re.subn(pattern,lambda _:replacement+'\n',config,flags=re.M|re.S)
        assert count==1,key
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'config.yml').write_text(config,encoding='utf-8')
    lang=(LOCAL/'shop-lang-es-before.yml').read_text(encoding='utf-8')
    for key,kind in [('inventory-main-shop-title','tienda'),('inventory-buystacks-title','compra'),
                     ('inventory-howmuchbuy-title','compra'),('inventory-howmuchsell-title','venta_tienda')]:
        lang,count=re.subn(rf'^{key}:.*$',lambda _:f"{key}: '{title(kind)}'",lang,flags=re.M)
        assert count==1,key
    (OUT/'lang-es.yml').write_text(lang,encoding='utf-8')
    for path in (LOCAL/'shop-sections-before').rglob('*.yml'):
        section=yaml.safe_load(path.read_text(encoding='utf-8'))
        section['title']=title('tienda')
        clear_fill(section)
        if 'item-layout' in section:
            layout=section['item-layout']
            if len(layout)==6 and set(layout[-1].replace(' ',''))=={'0'}:section['item-layout']=layout[:-1]
        dump(OUT/'sections'/path.relative_to(LOCAL/'shop-sections-before'),section)
    for path in (LOCAL/'shop-catalog').rglob('*.yml'):
        before=yaml.safe_load(path.read_text(encoding='utf-8'))
        shop=yaml.safe_load(path.read_text(encoding='utf-8'))
        for page in shop.get('pages',{}).values():
            page['gui-rows']=5
            for item in page.get('items',{}).values():assert int(item.get('slot',1))<=45,(path,item)
        # Solo cambiamos el tamaño: precios, componentes y permisos intactos.
        for page in shop.get('pages',{}).values():page.pop('gui-rows',None)
        for page in before.get('pages',{}).values():page.pop('gui-rows',None)
        assert shop==before,path
        for page in shop.get('pages',{}).values():page['gui-rows']=5
        dump(OUT/'shops'/path.relative_to(LOCAL/'shop-catalog'),shop)
    print('Apariencia EconomyShopGUI preparada en',OUT)


if __name__=='__main__':generate()
