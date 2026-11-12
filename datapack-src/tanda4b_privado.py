"""Importar modelos Java originales solo en el repositorio privado."""
import json
import shutil
import math
import itertools
from terceros import privado
from tanda4b import CLONES, PLUSHIES, COINS


def rotate(point, origin, axis, angle):
    p=[point[i]-origin[i] for i in range(3)]
    a,b={'x':(1,2),'y':(2,0),'z':(0,1)}[axis]
    c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    p[a],p[b]=p[a]*c-p[b]*s,p[a]*s+p[b]*c
    return [p[i]+origin[i] for i in range(3)]


def wing_components(iid, raw, *, shoulder_tips=False):
    """Wrapper propio; shoulder_tips=False conserva la reproduccion de entregas historicas."""
    asura=iid=='asura_alas'
    ref='asura:asura_wings' if asura else 'elitecreatures:carnivoret_weapon_set/wing'
    scale=1 if asura else .9
    yaw=0 if asura else 90
    vertices=[]
    for e in raw['elements']:
        for p in itertools.product(*zip(e['from'],e['to'])):
            if rot:=e.get('rotation'):
                p=rotate(p,rot['origin'],rot['axis'],rot['angle'])
            vertices.append(rotate([(v-8)*scale for v in p],[0,0,0],'y',yaw))
    # Fijar el punto mas alto a la altura de hombros y el mas delantero al plano de espalda.
    tx=-(max(p[0] for p in vertices)+min(p[0] for p in vertices))/2
    # Las puntas superiores deben subir sobre los hombros. Anclar el MAXIMO al
    # hombro hacia que toda el ala colgara hasta las piernas (sobre todo Carnivora).
    top = 10.4 if shoulder_tips else 0  # 0,65 bloques sobre el anclaje del runtime.
    translation=[round(tx,5),round(top-max(p[1] for p in vertices),5),round(-max(p[2] for p in vertices),5)]
    wrapper={'parent':ref,'display':{'fixed':{'rotation':[0,yaw,0],'translation':translation,'scale':[scale]*3}}}
    tree={'type':'minecraft:select','property':'minecraft:display_context','cases':[
        {'when':['firstperson_lefthand','firstperson_righthand','thirdperson_lefthand','thirdperson_righthand'],
         'model':{'type':'minecraft:empty'}},
        {'when':'fixed','model':{'type':'minecraft:model','model':'astral:cosmetics/'+iid}}],
        'fallback':{'type':'minecraft:model','model':ref}}
    return tree,wrapper


def prepare(base):
    out = base / 'item-pack/assets'
    x = privado() / 'x'
    # Namespaces originales conservados: todas sus referencias internas siguen validas.
    car = x / 'carnivoret/Weapons/RSS/assets/elitecreatures'
    asura = x / 'asura/Asura/assets/asura'
    plush = x / 'peluches/nm_plushies_starter_pack_rp/assets/nogs_menagerie'
    # Los items solo leen texturas de la carpeta textures/item/ (atlas de items): las de estos packs se mueven
    # ahi y se reescriben sus referencias (sin esto el juego las muestra violeta y negro).
    NS = ('elitecreatures', 'asura', 'nogs_menagerie')
    def item_tex(ref):
        ns, _, p = ref.partition(':')
        return f'{ns}:item/{p}' if ns in NS and p and not p.startswith(('item/', 'block/')) else ref
    for source in (car, asura, plush):
        if not source.is_dir():
            raise FileNotFoundError(source)
        for path in source.rglob('*'):
            if path.suffix not in ('.png', '.json', '.mcmeta'):
                continue
            rel = path.relative_to(source)
            if rel.parts[0] == 'textures':
                rel = rel.relative_to('textures')
                rel = rel if rel.parts[0] in ('item', 'block') else ('item' / rel)
                rel = 'textures' / rel
            dest = out / source.name / rel
            old = out / source.name / path.relative_to(source)
            if old != dest and old.is_file():
                # Solo derivados de esta fuente, nunca originales ni carpetas ajenas.
                old.unlink()
            dest.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == '.json':
                d = json.loads(path.read_text(encoding='utf8'))
                d.pop('overrides', None)  # estados modernos declarados debajo
                if isinstance(d.get('textures'), dict):
                    d['textures'] = {k: item_tex(v) if isinstance(v, str) else v for k, v in d['textures'].items()}
                dest.write_text(json.dumps(d, ensure_ascii=False), encoding='utf8')
            else:
                shutil.copyfile(path, dest)
    def put(name, data):
        p = out / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf8')
    def model(name):
        return {'type':'minecraft:model', 'model':name}
    def car_model(name):
        return model('elitecreatures:carnivoret_weapon_set/' + name)
    mappings = {iid: car_model(m) for iid, (_, _, m) in CLONES.items() if iid.startswith('carnivora_')}
    mappings.update({'carnivora_' + k:car_model(v) for k,v in {'pico':'pickaxe','pala':'shovel','azada':'hoe','alas':'wing','helmet':'hat'}.items()})
    for piece in ('chestplate','leggings','boots'):
        put('elitecreatures/models/item/carnivora_' + piece + '.json', {'parent':'minecraft:item/generated',
            'textures':{'layer0':'elitecreatures:item/carnivoret_weapon_set/carnivoret_' + piece}})
        mappings['carnivora_' + piece] = model('elitecreatures:item/carnivora_' + piece)
    mappings['carnivora_arco'] = {'type':'minecraft:condition', 'property':'minecraft:using_item',
        'on_false':car_model('bow'), 'on_true':{'type':'minecraft:range_dispatch', 'property':'minecraft:use_duration', 'scale':.05,
        'fallback':car_model('bow_0'), 'entries':[{'threshold':.65,'model':car_model('bow_1')},{'threshold':.9,'model':car_model('bow_2')}]}}
    mappings['carnivora_cana'] = {'type':'minecraft:condition', 'property':'minecraft:fishing_rod/cast', 'on_true':car_model('fishing_rod_cast'), 'on_false':car_model('fishing_rod')}
    mappings['carnivora_escudo'] = {'type':'minecraft:condition', 'property':'minecraft:using_item', 'on_true':car_model('shield_blocking'), 'on_false':car_model('shield')}
    for iid, m in [('asura_espada','asura_sword'), ('asura_alas','asura_wings'), *[('asura_moneda_' + k,'asura_' + k + '_coin') for k in COINS]]:
        mappings[iid] = model('asura:' + m)
    for k in PLUSHIES:
        mappings['peluche_' + k] = model('nogs_menagerie:plushies/nm_plushie_' + k)
    for iid in ('carnivora_alas','asura_alas'):
        mappings[iid] = model('minecraft:item/feather')
        wrapper=out/'astral/models/cosmetics'/f'{iid}.json'
        if wrapper.exists():wrapper.unlink()
    for iid, tree in mappings.items():
        put('astral/items/' + iid + '.json', {'model':tree})
    for layer, part in ((1,'humanoid'),(2,'humanoid_leggings')):
        source = car / f'textures/carnivoret_weapon_set/carnivoret_armor_layer_{layer}.png'
        dest = out / f'astral/textures/entity/equipment/{part}/carnivora.png'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source,dest)
    put('astral/equipment/carnivora.json', {'layers':{k:[{'texture':'astral:carnivora'}] for k in ('humanoid','humanoid_leggings')}})
    # Alas: segunda mano, sin proteccion ni vuelo. AstralDecor monta el display.
    print('Tanda4b: modelos, estados y capas preparados exclusivamente en build privado.')
