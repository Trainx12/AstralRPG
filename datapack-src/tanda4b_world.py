"""Mena y planta: logica propia sin modificar los biomas de Stellarity."""
from copy import deepcopy
import json
from pathlib import Path
import yaml
from mobs.tanda3a import plant

ROOT=Path(__file__).resolve().parents[1]
ORE_STATE={'instrument':'banjo','note':'24','powered':'false'}
DROP_CHANCE={1:.30,2:.45,3:.60,4:.75,5:.90}


def generate(files):
    def put(path,value):
        files[path]=json.dumps(value,ensure_ascii=False,indent=1)
    put('data/astral/worldgen/configured_feature/asura_ore.json',{
        'type':'minecraft:ore','config':{'size':3,'discard_chance_on_air_exposure':.25,
        'targets':[{'target':{'predicate_type':'minecraft:block_match','block':'minecraft:end_stone'},
        'state':{'Name':'minecraft:note_block','Properties':ORE_STATE}}]}})
    state={'condition':'minecraft:block_state_property','block':'minecraft:note_block','properties':{'instrument':'banjo','note':'24'}}
    def loot(iid):
        return {'type':'minecraft:loot_table','value':'astral:item/' + iid}
    pick={'condition':'minecraft:match_tool','predicate':{'items':'#minecraft:pickaxes'}}
    table={'type':'minecraft:block','pools':[
        {'rolls':1,'conditions':[state,pick], 'entries':[{**loot('asura_moneda_emerald'), 'functions':[
            {'function':'minecraft:apply_bonus','enchantment':'minecraft:fortune','formula':'minecraft:ore_drops'}]}]},
        {'rolls':1,'conditions':[state,pick,{'condition':'minecraft:random_chance','chance':.08}],
         'entries':[loot('asura_moneda_' + k) for k in ('card','circle','square','triangle')]},
        {'rolls':1,'conditions':[{'condition':'minecraft:inverted','term':state},{'condition':'minecraft:survives_explosion'}],
         'entries':[{'type':'minecraft:item','name':'minecraft:note_block'}]}]}
    put('data/minecraft/loot_table/blocks/note_block.json',table)
    for tier,chance in DROP_CHANCE.items():
        put(f'data/astral/predicate/tanda4b/drop{tier}.json',{'condition':'minecraft:random_chance','chance':chance})
    files['data/astral/function/tanda4b/planta/drop.mcfunction']='\n'.join(
        f'execute if score @s astral.mt matches {tier} if predicate astral:tanda4b/drop{tier} run loot spawn ~ ~ ~ loot astral:item/colmillo_carnivoro' for tier in DROP_CHANCE)+'\n'
    m=deepcopy(plant()['astral_bosque_planta'])
    m['Options'].update(Despawn=True,Glowing=False)
    m['Skills'][0]='skill{s=AST_PLANTA_SALVAJE_INICIO} @self ~onSpawn'
    m['Skills']+=['command{c="execute as <caster.uuid> at @s run function astral:tanda4b/planta/drop"} @self ~onDeath']
    m['Drops']=['money 15 1']
    sk={'AST_PLANTA_SALVAJE_INICIO':{'Skills':['addtag{tag=astral.wildplant} @self',
        'command{c="execute as <caster.uuid> at @s run function astral:mob/roll"} @self',
        'skill{s=AST_PLANTA_MODELO} @self']}}
    for folder,value in [('mobs',{'astral_planta_salvaje':m}),('skills',sk)]:
        dest=ROOT/'build/mythicmobs'/folder/'tanda4b.yml'
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(yaml.safe_dump(value,sort_keys=False,allow_unicode=True),encoding='utf8')
    shop = ROOT/'build/shop/EconomyShopGUI'
    for folder, value in [('sections', {'enable':True,'slot':39,'title':'Astral - Peluches',
            'item':{'material':'RABBIT_HIDE','name':'&dPeluches','lore':['&7Seis modelos colocables.','&e$2.500 por unidad.']}}),
            ('shops', {'pages':{'page1':{'gui-rows':3,'items':{'1':{'material':'RABBIT_HIDE',
            'displayname':'&dAbriendo peluches...','sell':-1,'buy':-1}}}}})]:
        dest=shop/folder/'Peluches.yml'; dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(yaml.safe_dump(value,sort_keys=False,allow_unicode=True),encoding='utf8')


def own_textures():
    """Arte procedural original. No toma pixeles de Minecraft ni de terceros."""
    from PIL import Image,ImageDraw
    import io,random
    files={}
    def png(name,im):
        stream=io.BytesIO(); im.save(stream,'PNG'); files['assets/astral/textures/' + name + '.png']=stream.getvalue()
    im=Image.new('RGBA',(16,16)); draw=ImageDraw.Draw(im)
    draw.polygon([(4,2),(11,2),(10,7),(7,13),(4,15),(5,8)],fill='#c5ee68',outline='#295434')
    draw.line([(5,3),(9,3),(8,8),(6,12)],fill='#f6ffd6',width=1)
    draw.rectangle((4,2,10,4),fill='#a52b68'); draw.point((10,5),fill='#f04652')
    png('item/colmillo_carnivoro',im)
    rng=random.Random(411)
    im=Image.new('RGB',(16,16)); px=im.load()
    for y in range(16):
        for x in range(16):
            c=rng.randrange(158,210); px[x,y]=(min(255,c+25),min(255,c+23),c-44)
    draw=ImageDraw.Draw(im)
    for x,y in [(3,3),(10,4),(6,10),(12,12)]:
        draw.rectangle((x-1,y-1,x+1,y+1),fill='#546957'); draw.point((x,y),fill='#78ffcb'); draw.point((x+1,y),fill='#e6fff1')
    png('block/asura_ore',im)
    def put(name,obj): files['assets/' + name + '.json']=json.dumps(obj).encode()
    put('astral/models/block/asura_ore',{'parent':'minecraft:block/cube_all','textures':{'all':'astral:block/asura_ore'}})
    put('minecraft/blockstates/note_block',{'multipart':[
        {'when':{'instrument':'banjo','note':'24'},'apply':{'model':'astral:block/asura_ore'}},
        {'when':{'OR':[{'instrument':'|'.join(['harp','basedrum','snare','hat','bass','flute','bell','guitar','chime','xylophone','iron_xylophone','cow_bell','didgeridoo','bit','pling','zombie','skeleton','creeper','dragon','wither_skeleton','piglin','custom_head'])},{'note':'|'.join(str(n) for n in range(24))}]},'apply':{'model':'minecraft:block/note_block'}}]})
    put('astral/models/item/colmillo_carnivoro',{'parent':'minecraft:item/generated','textures':{'layer0':'astral:item/colmillo_carnivoro'}})
    put('astral/items/colmillo_carnivoro',{'model':{'type':'minecraft:model','model':'astral:item/colmillo_carnivoro'}})
    return files
