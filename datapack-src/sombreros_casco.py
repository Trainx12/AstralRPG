"""Sombrero sobre el casco (pedido del dueno 13/11/2026): el casco puesto sigue en la casilla y protege,
pero el personaje se ve sin casco y con el sombrero, tambien para el propio jugador en F5.

Como funciona:
- AstralDecor cambia el casco PUESTO: item_model = astral:cosmeticos/casco_<sombrero>, custom_model_data
  (strings[0]) = item_model original y quita el asset_id del equippable (asi no dibuja la armadura).
- Este archivo arma esas definiciones: en la cabeza ("head") dibujan el sombrero; en cualquier otro lugar
  (inventario, mano, suelo) eligen por custom_model_data el modelo del casco original, asi el icono no cambia.
- El plugin devuelve el casco original apenas sale de la cabeza o se quita el sombrero.
- Sin casco: astral:cosmeticos/solo_<sombrero> (sombrero en la cabeza, nada en el inventario).

Entrega privada sobre el FINAL publicado (las definiciones nombran modelos de sombreros privados):
python sombreros_casco.py -> ASTRAL_PRIVADO/build/entregas/sombreros-casco/AstralRPG-Textures.zip
"""
import hashlib
import json
import zipfile
from terceros import privado
from pack_audit import audit

BASE = 'build/entregas/esc-cofres/AstralRPG-Textures.zip'
BASE_SHA = 'e35b949e32665f51262b48661397c45b582325fc'
DELIVERY = 'build/entregas/sombreros-casco'
STAMP = (2026, 11, 13, 0, 0, 0)
# Cascos vanilla (por si alguien usa uno que no es Astral). El de cuero lleva su tinte.
VANILLA = ('chainmail_helmet', 'iron_helmet', 'golden_helmet', 'diamond_helmet', 'netherite_helmet',
           'turtle_helmet', 'copper_helmet')


def vanilla_model(name):
    model = {'type': 'minecraft:model', 'model': 'minecraft:item/' + name}
    if name == 'leather_helmet':
        model['tints'] = [{'type': 'minecraft:dye', 'default': -6265536}]
    return model


def helmets(files):
    """{item_model original: modelo a dibujar fuera de la cabeza}."""
    out = {'minecraft:' + v: vanilla_model(v) for v in VANILLA + ('leather_helmet',)}
    for name, data in files.items():
        if name.startswith('assets/astral/items/') and name.endswith('_helmet.json') and name.count('/') == 3:
            out['astral:' + name.split('/')[-1][:-5]] = json.loads(data)['model']
    return out


def definitions(files):
    cases = [{'when': key, 'model': model} for key, model in sorted(helmets(files).items())]
    out = {}
    prefix = 'assets/astral/items/cosmeticos/sombrero_'
    for name in sorted(files):
        if not (name.startswith(prefix) and name.endswith('.json')):
            continue
        key = name[len(prefix):-5]
        hat = json.loads(files[name])['model']
        out[f'assets/astral/items/cosmeticos/casco_{key}.json'] = {'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': 'head', 'model': hat}],
            'fallback': {'type': 'minecraft:select', 'property': 'minecraft:custom_model_data', 'index': 0,
                         'cases': cases, 'fallback': hat}}}
        # Sin casco: objeto que en la cabeza dibuja el sombrero y en cualquier otro lado no se ve
        # (la casilla de casco parece vacia). AstralDecor no deja agarrarlo.
        out[f'assets/astral/items/cosmeticos/solo_{key}.json'] = {'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': 'head', 'model': hat}], 'fallback': {'type': 'minecraft:empty'}}}
    return out


def main():
    base = privado() / BASE
    if hashlib.sha1(base.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('La base no es el FINAL publicado (esc-cofres)')
    with zipfile.ZipFile(base) as z:
        files = {n: z.read(n) for n in z.namelist()}
    added = definitions(files)
    if any(n in files for n in added):
        raise ValueError('La entrega pisaria archivos existentes')
    for name, data in added.items():
        files[name] = json.dumps(data, ensure_ascii=False, indent=1).encode()
    dest = privado() / DELIVERY
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / 'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name, STAMP), data, compress_type=zipfile.ZIP_DEFLATED)
    refs = audit(target)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    (dest / 'pack.sha1').write_text(sha + '\n')
    (dest / 'procedencia.json').write_text(json.dumps(dict(base_sha1=BASE_SHA, final_sha1=sha,
        added=sorted(added), removed=[], references=refs), indent=2), encoding='utf8')
    print('FINAL', target, 'SHA-1', sha, 'definiciones', len(added), 'cascos', len(helmets(files)))


if __name__ == '__main__':
    main()
