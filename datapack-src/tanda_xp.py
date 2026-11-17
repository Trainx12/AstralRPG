"""Tanda del 16/11: valores, objetos y reservas propias reemplazables por PNG."""
import json
from pathlib import Path
from PIL import Image
from gacha_balance import FACTOR_SUERTE

ROOT = Path(__file__).resolve().parents[1]
XP = {'frasco_xp_pequeno': 60, 'frasco_xp_grande': 200, 'frasco_xp_gigante': 550, 'barril_xp': 5500}
PRECIOS = {'frasco_xp_pequeno': 3000, 'frasco_xp_grande': 9000, 'frasco_xp_gigante': 25000, 'barril_xp': 220000, 'manzana_esmeralda': 60000}
NOMBRES = {'frasco_xp_pequeno': 'Frasco de Experiencia Pequeno', 'frasco_xp_grande': 'Frasco de Experiencia Grande', 'frasco_xp_gigante': 'Frasco de Experiencia Gigante', 'barril_xp': 'Barril de Experiencia',
           'manzana_esmeralda': 'Manzana de la Suerte'}
SUERTE_SEGUNDOS = 300
MOCHILAS = dict(leather='#946545', copper='#b66a45', iron='#b9bfca', gold='#e6bb3c',
                diamond='#42c8cb', netherite='#49424d')


def register(add, txt):
    for iid, name in NOMBRES.items():
        apple = iid == 'manzana_esmeralda'
        extra = {'minecraft:max_stack_size': 16}
        if apple:
            extra.update({'minecraft:food': {'nutrition': 4, 'saturation': 2.4, 'can_always_eat': True}})
        desc = ([f'Raro, Epico y Legendario x{str(FACTOR_SUERTE).replace(".", ",")} durante {SUERTE_SEGUNDOS // 60} minutos.',
                 f'Cada manzana suma {SUERTE_SEGUNDOS // 60} minutos.'] if apple else
                [f'Clic derecho: +{XP[iid]} puntos de XP vanilla.', 'Shift + clic: consume todo el stack de esa mano.'])
        add(iid, 'minecraft:apple' if apple else 'minecraft:paper', name, 'green', [txt(s) for s in desc],
            {'type': 'consumable'}, extra=extra, model='astral:'+iid,
            pdc={'astral:consumible': iid})


def rewards(apple=False):
    out = [('common', 12, NOMBRES['frasco_xp_pequeno'], ['loot give %player% loot astral:item/frasco_xp_pequeno']),
           ('uncommon', 9, NOMBRES['frasco_xp_grande'], ['loot give %player% loot astral:item/frasco_xp_grande']),
           ('uncommon', 5, NOMBRES['frasco_xp_gigante'], ['loot give %player% loot astral:item/frasco_xp_gigante']),
           ('epic', 3, NOMBRES['barril_xp'], ['loot give %player% loot astral:item/barril_xp'])]
    if apple:
        out.append(('rare', 5, NOMBRES['manzana_esmeralda'], ['loot give %player% loot astral:item/manzana_esmeralda']))
    return out


def generate(files):
    files['data/astral/function/xp/cofre.mcfunction'] = '\n'.join(
        f'execute if predicate astral:xp/{iid} run loot give @s loot astral:item/{iid}' for iid in PRECIOS)+'\n'
    for iid, chance in [('frasco_xp_pequeno', .35), ('frasco_xp_grande', .18), ('frasco_xp_gigante', .08), ('barril_xp', .01), ('manzana_esmeralda', .03)]:
        files[f'data/astral/predicate/xp/{iid}.json'] = json.dumps({'condition':'minecraft:random_chance','chance':chance})
    files['data/astral/function/xp/infinita.mcfunction'] = '\n'.join(
        f'execute if predicate astral:xp/{iid} run loot give @s loot astral:item/{iid}' for iid in XP)+'\n'


def texture(name, color, size=32):
    """La reserva se crea una vez: el dueno reemplaza el PNG y el generador lo conserva."""
    path = ROOT/'datapack-src/pack-source/provisorias'/f'{name}.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        Image.new('RGBA', (size, size), color).save(path)
    with Image.open(path) as im:
        if im.size != (size, size):
            raise ValueError(f'{path}: se espera {size}x{size}')
    return path.read_bytes()


def assets(buttons=()):
    files = {}
    def model(iid, color, body=None):
        tex = f'astral:item/provisorias/{iid}'
        files[f'assets/astral/textures/item/provisorias/{iid}.png'] = texture(iid, color)
        obj = body or {'parent': 'minecraft:item/handheld' if iid.startswith('cuchillo') else 'minecraft:item/generated'}
        obj['textures'] = {'layer0':tex, 'all':tex, 'particle':tex}
        files[f'assets/astral/models/provisorias/{iid}.json'] = json.dumps(obj).encode()
        files[f'assets/astral/items/{iid}.json'] = json.dumps({'model':{'type':'minecraft:model','model':f'astral:provisorias/{iid}'}}).encode()
    for iid, color in [('frasco_xp_pequeno','#b1d87e'),('frasco_xp_grande','#98cf69'),('frasco_xp_gigante','#8acb5d'),('barril_xp','#517e32'),('manzana_esmeralda','#19b86b')]:
        model(iid,color)
    for t in range(1,11):
        model(f'cuchillo_{t}', f'#{80+t*12:02x}{80+t*10:02x}{100+t*9:02x}')
    elements=[]
    # Cuerpo, bolsillo frontal, tapa y dos correas traseras; UV 0..16, textura comun.
    for a,b in [([3,2,5],[13,13,10]),([4,3,3],[12,8,5]),([2.5,12,4.5],[13.5,14,10.5]),
                ([4,3,10],[5.5,12,12]),([10.5,3,10],[12,12,12])]:
        elements.append({'from':a,'to':b,'faces':{f:{'uv':[0,0,16,16],'texture':'#all'} for f in ('north','south','east','west','up','down')}})
    display={'gui':{'rotation':[20,140,0],'scale':[.85]*3},'ground':{'scale':[.5]*3}}
    for hand in ('right','left'):
        display[f'firstperson_{hand}hand']={'rotation':[0,35,0],'translation':[0,0,-2],'scale':[.65]*3}
        display[f'thirdperson_{hand}hand']={'rotation':[0,0,0],'translation':[0,2,0],'scale':[.55]*3}
    files['assets/astral/models/provisorias/mochila_base.json'] = json.dumps({'elements':elements,'display':display}).encode()
    for material, color in MOCHILAS.items():
        model('mochila_'+material,color,{'parent':'astral:provisorias/mochila_base'})
    for key in sorted(buttons):
        model('boton_'+key, '#796493')
    return files


def shop_files():
    return {'sections/Consumibles.yml': {'enable':True,'slot':44,'title':'Astral - Consumibles',
                'item':{'material':'EXPERIENCE_BOTTLE','name':'&aConsumibles Astrales'}},
            'shops/Consumibles.yml':{'pages':{'page1':{'gui-rows':3,'items':{'1':{'material':'PAPER','buy':-1,'sell':-1}}}}}}


def shop_menu(item, menu, q, requisito):
    out=[]
    for slot,(iid,price) in enumerate(PRECIOS.items(),11):
        out += item(iid,'PAPER',slot,'&a'+NOMBRES[iid],[f'&e{price:,}$','&7Necesitas un espacio libre.'],extra={
            'item_model':q('astral:'+iid), 'click_requirement':
            requisito(price).replace('      requirements:', '      requirements:\n        espacio:\n          type: javascript\n          expression: \'BukkitPlayer.getInventory().firstEmpty() >= 0\''),
            'click_commands':[f'[takemoney] {price}',f'[console] loot give %player_name% loot astral:item/{iid}','[close]']})
    out += item('cerrar','BARRIER',26,'&cCerrar',extra={'click_commands':['[close]']})
    return menu('&aConsumibles Astrales','astral_consumibles',27,out)
