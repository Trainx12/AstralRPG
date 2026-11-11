"""Importar modelos Java originales solo en el repositorio privado."""
import json
import shutil
from terceros import privado
from tanda4b import CLONES, PLUSHIES, COINS


def prepare(base):
    out = base / 'item-pack/assets'
    x = privado() / 'x'
    # Namespaces originales conservados: todas sus referencias internas siguen validas.
    car = x / 'carnivoret/Weapons/RSS/assets/elitecreatures'
    asura = x / 'asura/Asura/assets/asura'
    plush = x / 'peluches/nm_plushies_starter_pack_rp/assets/nogs_menagerie'
    for source in (car, asura, plush):
        if not source.is_dir():
            raise FileNotFoundError(source)
        for path in source.rglob('*'):
            if path.suffix not in ('.png', '.json'):
                continue
            dest = out / source.name / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == '.json':
                d = json.loads(path.read_text(encoding='utf8'))
                d.pop('overrides', None)  # estados modernos declarados debajo
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
            'textures':{'layer0':'elitecreatures:carnivoret_weapon_set/carnivoret_' + piece}})
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
    for iid, tree in mappings.items():
        put('astral/items/' + iid + '.json', {'model':tree})
    for layer, part in ((1,'humanoid'),(2,'humanoid_leggings')):
        source = car / f'textures/carnivoret_weapon_set/carnivoret_armor_layer_{layer}.png'
        dest = out / f'astral/textures/entity/equipment/{part}/carnivora.png'
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source,dest)
    put('astral/equipment/carnivora.json', {'layers':{k:[{'texture':'astral:carnivora'}] for k in ('humanoid','humanoid_leggings')}})
    # Alas: equipo de pecho + player equipment model no admite geometria Java arbitraria.
    # El runtime dibuja el item_display sujeto al jugador; el item equipa en pecho.
    print('Tanda4b: modelos, estados y capas preparados exclusivamente en build privado.')
