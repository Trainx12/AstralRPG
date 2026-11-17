"""Armas que eran un dibujo plano -> 3D (pedido del dueno 16/11/2026).

- Cuchillos T1-T10: la textura de mod que eligio el dueno por tier (plan-cuchillos-mods.md) esculpida con volumen
  con el mismo motor de armas_mod.py (hoja con lomo y filo, mango redondo, brillo y animacion del mod intactos).
- Equipo de las Mareas (espada, hacha, pico y arco con sus 3 tensados): se esculpe desde las texturas que ya
  estan en el pack FINAL privado.
En el inventario se sigue viendo el dibujo plano. Todo es arte de terceros: sale SOLO al circuito privado
(ASTRAL_PRIVADO/build/entregas/modelos-3d-efectos). En el pack publico quedan las provisorias.

  python datapack-src/armas_planas3d.py     modelos + vista previa privada
"""
import io
import json
import os
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import armas_mod as A  # noqa: E402
from terceros import privado  # noqa: E402

MODS = Path(os.environ.get('ASTRAL_MODS', 'C:/Users/Trainx/Desktop/mods'))
OUT = privado() / 'build/entregas/modelos-3d-efectos'
BASE_FINAL = privado() / 'build/entregas/cargar-arte-16-11/AstralRPG-Textures.zip'
BIC = 'born_in_chaos_v1'
DAGGER = 'cuchillos/assets/dagger_mod/textures/item/safeimagekit-150px-cutlass_sprite_mcd_1_1.png'
# tier -> (mod, autor/licencia, textura). 'ruta:' = archivo suelto bajo MODS.
CUCHILLOS = {
    1: ('Dagger Mod', 'r2alsei/oofabo, All Rights Reserved', 'ruta:' + DAGGER),
    2: ('Born in Chaos', 'Mongoose Artist, licencia propia', f'{BIC}:item/intoxicating_dagger2'),
    3: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/soul_daggers/soul_dagger_soul_knife'),
    4: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/daggers/dagger_swift_striker'),
    5: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/daggers/dagger_void_touched_blade'),
    6: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/daggers/dagger_chill_gale_knife'),
    7: ('Born in Chaos', 'Mongoose Artist, licencia propia', f'{BIC}:item/intoxicating_dagger'),
    8: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/soul_daggers/soul_dagger_eternal_knife'),
    9: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/daggers/dagger_swiftstriker'),
    10: ('MC Dungeons Weapons', 'chronosacaria, licencia propia', 'mcdw:item/daggers/dagger_the_beginning_and_the_end'),
}
AGUA = {'agua_espada': ('espada', 'item/handheld'), 'agua_hacha': ('hacha', 'item/handheld'),
        'agua_pico': ('hacha', 'item/handheld')}
ARCO = ('', '_pulling_0', '_pulling_1', '_pulling_2')


def esculpido(S, name, im, glow, mc, fam, base):
    """Modelo con volumen del dibujo `im` (arma en diagonal, punta arriba a la derecha)."""
    disp, _ = A.resolver(base)
    girada, a, g = A.enderezar(im, glow)
    t = S.tex(name, girada, mc)
    model = {'textures': {'t': t, 'particle': t}, 'elements': A.esculpir(a, g, fam, im.size[0]),
             'display': A.display_parado(disp, 1)}
    S.vista[name] = (model, girada, im)
    solido = S.modelo(name, model)
    if fam == 'arco':
        solido = A.primera_persona(S, name, S.tex(name + '_icono_fp', im, mc), solido, fam)
    return solido


def cuchillos(S):
    for t, (_, _, ref) in CUCHILLOS.items():
        name = f'cuchillo_{t}'
        if ref.startswith('ruta:'):
            im, glow, mc = Image.open(MODS / ref[5:]).convert('RGBA'), None, None
        else:
            im, glow, mc = A.leer_textura(ref)
        plano = S.plano_gui(name, S.tex(name + '_icono', im, mc))
        S.item(name, A.por_contexto(plano, esculpido(S, name, im, glow, mc, 'cuchillo', 'item/handheld')))


def agua(S, base=None):
    base = base or BASE_FINAL
    with zipfile.ZipFile(base) as z:
        def tex(n):
            return Image.open(io.BytesIO(z.read(f'assets/astral/textures/item/{n}.png'))).convert('RGBA')

        def plano(n):
            return {'type': 'minecraft:model', 'model': f'astral:item/{n}'}
        for name, (fam, parent) in AGUA.items():
            S.item(name, A.por_contexto(plano(name), esculpido(S, name, tex(name), None, None, fam, parent)))
        solido = {s: esculpido(S, 'agua_arco' + s, tex('agua_arco' + s), None, None, 'arco', 'item/bow') for s in ARCO}

        def arbol(m):
            return {'type': 'minecraft:condition', 'property': 'minecraft:using_item', 'on_false': m(''),
                    'on_true': {'type': 'minecraft:range_dispatch', 'property': 'minecraft:use_duration',
                                'scale': 0.05, 'fallback': m('_pulling_0'),
                                'entries': [{'threshold': 0.65, 'model': m('_pulling_1')},
                                            {'threshold': 0.9, 'model': m('_pulling_2')}]}}
        S.item('agua_arco', A.por_contexto(arbol(lambda s: plano('agua_arco' + s)), arbol(lambda s: solido[s])))


def generar(base=None):
    S = A.Salida()
    cuchillos(S)
    agua(S, base)
    malos = A.revisar(S)
    if malos:
        raise SystemExit('Modelos fuera de -16..32: ' + ', '.join(malos))
    return S


def vista_previa(S, path):
    ids = [f'cuchillo_{t}' for t in CUCHILLOS] + list(AGUA) + ['agua_arco', 'agua_arco_pulling_2']
    viejo = A.ARMAS
    A.ARMAS = {i: ('3D',) for i in ids}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        A.vista_previa(S, path)
    finally:
        A.ARMAS = viejo
    return path


def main():
    if not privado().exists() or not BASE_FINAL.exists() or not (MODS / DAGGER).exists():
        print('Faltan los mods, el circuito privado o el FINAL base: no se genera nada.')
        return
    S = generar()
    for rel, data in S.files.items():
        p = OUT / 'pack' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    print(len(S.files), 'archivos ->', OUT / 'pack')
    print({k: len(v[0]['elements']) for k, v in S.vista.items()})
    print(vista_previa(S, OUT / 'previews/armas-3d.png'))


if __name__ == '__main__':
    main()
