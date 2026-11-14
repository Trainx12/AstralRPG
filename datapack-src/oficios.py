"""Ropa de oficio (14/11/2026): sets de Minero y Talador, tier 1. Arte propio (pixel art por codigo).

Se obtienen crafteando (Forja/mesa, grupo "Oficios", materiales baratos) o en /shop -> Oficios
(seccion de EconomyShopGUI que AstralDecor redirige al menu de DeluxeMenus `oficios`, que cobra con Vault).

Minero: cada pieza +1 eficiencia de mineria y +5% velocidad de rotura. Casco: vision nocturna.
        Set completo: Prisa I y 10% de mineral extra en las Minas Astrales (minas.sk, tag astral.ofi_minero).
Talador: cada pieza +5% velocidad de rotura. Gorro con hacha en la mano: Prisa I.
        Set completo con hacha: Prisa II y 20% de tronco extra en el Bosque Astral (bosque_talar.py, tag astral.ofi_talador).

python oficios.py  ->  build/previews/oficios.png (preview para el dueno)
"""
import io
import json
import random
from pathlib import Path

from escala import VIDA_PIEZA, defensa_pieza

ROOT = Path(__file__).resolve().parent.parent
TIER = 1
PIECES = ['helmet', 'chestplate', 'leggings', 'boots']
SLOT = {'helmet': 'head', 'chestplate': 'chest', 'leggings': 'legs', 'boots': 'feet'}
ARMOR_SLOT = {'helmet': 'armor.head', 'chestplate': 'armor.chest', 'leggings': 'armor.legs', 'boots': 'armor.feet'}
SHOP_TITLE = 'Astral - Oficios'
SHOP_SLOT = 43          # libres en /shop: 1,13,15,21..35 ocupados; 39 Peluches, 40 Proteccion, 41 misc, 42 Mochilas
PRECIO = {'helmet': 800, 'chestplate': 1200, 'leggings': 1200, 'boots': 800}
PRECIO_SET = 3500

SETS = {
    'minero': {
        'color': '#e0a83a', 'label': 'Minero',
        'names': {'helmet': 'Casco de Minero', 'chestplate': 'Chaleco de Minero',
                  'leggings': 'Pantalon de Minero', 'boots': 'Botas de Minero'},
        'help': {'helmet': ['Picas mas rapido.', 'Ves en la oscuridad.'], 'chestplate': ['Picas mas rapido.'],
                 'leggings': ['Picas mas rapido.'], 'boots': ['Picas mas rapido.']},
        'set': 'Set completo: Prisa I y 10% de mineral extra en las Minas.',
        'recipes': {
            'helmet': [('v', 'minecraft:iron_ingot', 3), ('v', 'minecraft:lantern', 1), ('c', 'cuero_tratado', 1)],
            'chestplate': [('c', 'cuero_tratado', 4), ('v', 'minecraft:iron_ingot', 2), ('v', 'minecraft:coal', 4)],
            'leggings': [('c', 'cuero_tratado', 3), ('v', 'minecraft:copper_ingot', 4)],
            'boots': [('c', 'cuero_tratado', 2), ('v', 'minecraft:iron_ingot', 2)]},
        'menu_icon': 'LANTERN',
    },
    'talador': {
        'color': '#d2483a', 'label': 'Talador',
        'names': {'helmet': 'Gorro de Talador', 'chestplate': 'Camisa de Talador',
                  'leggings': 'Pantalon de Talador', 'boots': 'Botas de Talador'},
        'help': {'helmet': ['Rompes mas rapido.', 'Con hacha en la mano: Prisa I.'], 'chestplate': ['Rompes mas rapido.'],
                 'leggings': ['Rompes mas rapido.'], 'boots': ['Rompes mas rapido.']},
        'set': 'Set completo con hacha: Prisa II y 20% de tronco extra en el Bosque.',
        'recipes': {
            'helmet': [('v', 'minecraft:green_wool', 3), ('c', 'cuero_tratado', 1)],
            'chestplate': [('v', 'minecraft:red_wool', 4), ('v', 'minecraft:black_wool', 2), ('c', 'cuero_tratado', 2)],
            'leggings': [('v', 'minecraft:blue_wool', 4), ('c', 'cuero_tratado', 2)],
            'boots': [('c', 'cuero_tratado', 2), ('v', 'minecraft:oak_log', 4)]},
        'menu_icon': 'IRON_AXE',
    },
}
ROTURA = 0.05            # minecraft:block_break_speed por pieza (+5%)
MINERIA = 1.0            # minecraft:mining_efficiency por pieza (minero)


def item_ids():
    return [f'{s}_{p}' for s in SETS for p in PIECES]


# ------------------------------------------------------------------------------------- items y recetas
def register(items, fichas, recipes, add_item, txt, armor_attrs):
    for sid, sdef in SETS.items():
        for piece in PIECES:
            iid = f'{sid}_{piece}'
            mods = armor_attrs(iid, piece, 'iron', {}, vida=VIDA_PIEZA[TIER])
            extra_attrs = [('block_break_speed', ROTURA, 'rotura')]
            if sid == 'minero':
                extra_attrs.append(('mining_efficiency', MINERIA, 'mineria'))
            for attr, amount, suffix in extra_attrs:
                mods.append({'type': f'minecraft:{attr}', 'id': f'astral:{iid}.{suffix}', 'amount': amount,
                             'operation': 'add_value', 'slot': SLOT[piece]})
            lore = [txt(f"Ropa de {sdef['label']} {'I' * TIER}")]
            lore += [txt(line, 'aqua') for line in sdef['help'][piece]]
            lore.append(txt(sdef['set'], 'gold'))
            add_item(iid, 'minecraft:iron_' + piece, sdef['names'][piece], sdef['color'], lore,
                     {'type': 'armor', 'set': sid, 'tier': TIER, 'piece': piece, 'def': defensa_pieza(TIER, piece)},
                     extra={'minecraft:attribute_modifiers': mods,
                            # casco y gorro: sin asset_id, asi se dibuja el modelo 3D del item en la cabeza
                            'minecraft:equippable': {'slot': SLOT[piece],
                                                     **({} if piece == 'helmet' else {'asset_id': 'astral:' + sid})}},
                     model='astral:' + iid, kind='armor')
            recipes.append((iid, 1, sdef['recipes'][piece], 'Oficios'))


# ------------------------------------------------------------------------------------- efectos (datapack)
def check_lines():
    """Funcion astral:oficios/check (cada segundo, como @a): cuenta piezas, tags y efectos."""
    L = []
    for sid, obj in (('minero', 'astral.ofi_min'), ('talador', 'astral.ofi_tal')):
        L.append(f'scoreboard players set @s {obj} 0')
        for sl in ARMOR_SLOT.values():
            L.append(f'execute if items entity @s {sl} *[minecraft:custom_data~{{astral:{{set:"{sid}"}}}}] '
                     f'run scoreboard players add @s {obj} 1')
        L += [f'tag @s remove astral.ofi_{sid}', f'execute if score @s {obj} matches 4 run tag @s add astral.ofi_{sid}']
    L += [
        # Minero: casco = vision nocturna (15 s renovados: no parpadea); set = Prisa I.
        'execute if items entity @s armor.head *[minecraft:custom_data~{astral:{id:"minero_helmet"}}] '
        'run effect give @s minecraft:night_vision 15 0 true',
        'execute if score @s astral.ofi_min matches 4 run effect give @s minecraft:haste 3 0 true',
        # Talador: con hacha en la mano. Gorro = Prisa I; set completo = Prisa II.
        'execute unless score @s astral.ofi_tal matches 4 if items entity @s weapon.mainhand #minecraft:axes '
        'if items entity @s armor.head *[minecraft:custom_data~{astral:{id:"talador_helmet"}}] '
        'run effect give @s minecraft:haste 2 0 true',
        'execute if score @s astral.ofi_tal matches 4 if items entity @s weapon.mainhand #minecraft:axes '
        'run effect give @s minecraft:haste 2 1 true',
    ]
    return L


def load_lines():
    return ['scoreboard objectives add astral.ofi_min dummy', 'scoreboard objectives add astral.ofi_tal dummy']


# ------------------------------------------------------------------------------------- tienda
def shop_files():
    """Seccion de EconomyShopGUI (AstralDecor la redirige al menu `oficios`)."""
    section = {'enable': True, 'slot': SHOP_SLOT, 'title': SHOP_TITLE,
               'item': {'material': 'IRON_PICKAXE', 'name': '&6Oficios',
                        'lore': ['&7Ropa de Minero y de Talador.', f'&e$800 a $1.200 por pieza, set $3.500.']}}
    shop = {'pages': {'page1': {'gui-rows': 3, 'items': {'1': {'material': 'IRON_PICKAXE',
                                                                'displayname': '&6Abriendo oficios...', 'sell': -1, 'buy': -1}}}}}
    return {'sections/Oficios.yml': section, 'shops/Oficios.yml': shop}


def menu_yaml(item, menu, q, money, requisito_plata):
    P = '%player_name%'

    def dar(iids):
        return [f'[console] execute as {P} at @s run loot spawn ~ ~ ~ loot astral:item/{i}' for i in iids]
    lines = item('saldo', 'GOLD_NUGGET', 4, '&6Tu saldo', ['&e%vault_eco_balance_formatted%$'], extra={'update': 'true'})
    for row, (sid, sdef) in enumerate(SETS.items()):
        col = sdef['color'].replace('#', '&#')
        base = 9 + row * 18
        lines += item(f'{sid}_info', sdef['menu_icon'], base, f"{col}&l{sdef['label']}",
                      ['&7Ropa de trabajo tier I.', '&6' + sdef['set'], '', '&7Tambien se craftea en la Forja.'])
        for i, piece in enumerate(PIECES):
            iid = f'{sid}_{piece}'
            costo = PRECIO[piece]
            lines += item(iid, 'IRON_' + piece.upper(), base + 2 + i, f"{col}{sdef['names'][piece]}",
                          ['&7' + l for l in sdef['help'][piece]] + ['', f'&7Precio: &e{money(costo)}', '&eClic para comprar'],
                          extra={'item_model': q('astral:' + iid), 'click_requirement': requisito_plata(costo),
                                 'click_commands': [f'[takemoney] {costo}', *dar([iid]), '[sound] ENTITY_PLAYER_LEVELUP',
                                                    q(f"[message] &aCompraste: &f{sdef['names'][piece]}&a.")]})
        lines += item(f'{sid}_set', 'CHEST', base + 7, f"{col}&lSet completo de {sdef['label']}",
                      ['&7Las 4 piezas juntas.', '', f'&7Precio: &e{money(PRECIO_SET)} &8(ahorras {money(sum(PRECIO.values()) - PRECIO_SET)})',
                       '&eClic para comprar'], glow=True,
                      extra={'click_requirement': requisito_plata(PRECIO_SET),
                             'click_commands': [f'[takemoney] {PRECIO_SET}', *dar(f'{sid}_{p}' for p in PIECES),
                                                '[sound] ENTITY_PLAYER_LEVELUP',
                                                q(f"[message] &aCompraste el set completo de {sdef['label']}.")]})
    lines += item('ayuda', 'BOOK', 31, '&fSi tenes el inventario lleno', ['&7Lo que compres cae a tus pies.'])
    lines += item('cerrar', 'BARRIER', 35, '&cCerrar', extra={'click_commands': ['[close]']})
    return menu('Oficios', 'astralmenu_oficios', 36, lines)


# ------------------------------------------------------------------------------------- arte propio
def _hex(c):
    c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


def _mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)


class Raw(tuple):
    """Color que se pinta tal cual (brillos, metal, luz): no recibe el sombreado por cara."""


class Box:
    """Caras de una caja del modelo humanoide (u, v, ancho, alto, profundidad)."""

    def __init__(self, u, v, w, h, d):
        self.faces = {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'right': (u, v + d, d, h),
                      'front': (u + d, v + d, w, h), 'left': (u + d + w, v + d, d, h), 'back': (u + d + w + d, v + d, w, h)}
        self.h = h


HEAD, BODY, ARM, LEG = Box(0, 0, 8, 8, 8), Box(16, 16, 8, 12, 4), Box(40, 16, 4, 12, 4), Box(0, 16, 4, 12, 4)
# Luz arriba y a la izquierda: el frente es lo mas claro, la espalda y los costados bajan, abajo es sombra.
_FACE_K = {'front': 1.0, 'back': 0.93, 'right': 0.9, 'left': 0.9, 'top': 1.08, 'bottom': 0.7}


def _lit(c, face, x, y, w, h, rng=None, amt=0.035, inner=False):
    """Sombreado de una tela: por cara, degradado hacia abajo, bordes mas oscuros y un poco de grano."""
    if isinstance(c, Raw):
        return tuple(c)
    k = _FACE_K[face] * (0.86 if inner else 1.0)
    if face in ('top', 'bottom'):
        if x in (0, w - 1) or y in (0, h - 1):
            k *= 0.92
    else:
        k *= 1.08 - 0.18 * y / max(1, h - 1)
        if x in (0, w - 1):
            k *= 0.91
        if face == 'front':
            k *= 1.03 - 0.06 * x / max(1, w - 1)
    if rng:
        k *= 1 + rng.uniform(-amt, amt)
    return _shade(c, k)


def _paint(px, box, rows, fn, faces=('right', 'front', 'left', 'back'), rng=None, inner=None):
    """Pinta las caras laterales en las filas `rows` (0 = arriba) con fn(x_global_en_vuelta, y, face, xl).
    `inner` es la cara que queda contra el cuerpo (mas oscura)."""
    ring = 0
    for face in ('right', 'front', 'left', 'back'):
        fu, fv, fw, fh = box.faces[face]
        if face in faces:
            for y in rows:
                for x in range(fw):
                    c = fn(ring + x, y, face, x)
                    if c:
                        px[fu + x, fv + y] = _lit(c, face, x, y, fw, fh, rng, inner=(face == inner))
        ring += fw


def _cap(px, box, face, fn, rng=None):
    fu, fv, fw, fh = box.faces[face]
    for y in range(fh):
        for x in range(fw):
            c = fn(x, y)
            if c:
                px[fu + x, fv + y] = _lit(c, face, x, y, fw, fh, rng)


def _noise(rng, c, amt=0.08):
    return _shade(c, 1 + rng.uniform(-amt, amt))


def _mapa(rows, pal):
    """Dibujo por letras: devuelve fn(x, y) -> color o None ('.' deja lo que haya debajo)."""
    def fn(x, y):
        return pal.get(rows[y][x]) if y < len(rows) else None
    return fn


def textures():
    """Devuelve {sid: (capa humanoid, capa humanoid_leggings)} y los iconos {iid: imagen 16x16}.
    El casco y el gorro no van en la capa: son modelos 3D (ver _sombreros)."""
    from PIL import Image
    out, icons = {}, {}
    rng = random.Random(1411)
    gris, gris_o, gris_c, gris_oo = _hex('#8d939a'), _hex('#5e646b'), _hex('#b9bec3'), _hex('#43484f')
    carbon, carbon_o, carbon_c = _hex('#41454d'), _hex('#292c32'), _hex('#5a5f69')
    cuero, cuero_o, cuero_c, suela = _hex('#8a5530'), _hex('#5c3519'), _hex('#ad7242'), _hex('#2b1d13')
    blanco, blanco_o, blanco_oo = _hex('#ece9e2'), _hex('#c9c5bb'), _hex('#a39e93')
    oro, oro_c, oro_o, luz = _hex('#f2c43d'), _hex('#fff1a0'), _hex('#b8862a'), _hex('#fffbe2')
    metal, metal_c, metal_o = _hex('#b9bcc2'), _hex('#e4e6ea'), _hex('#7c8088')
    polvo, cordon = _hex('#6a6055'), _hex('#dcc296')
    R = Raw

    def tirador(i):
        return cuero_c if i % 3 == 1 else cuero

    def botas(estilo):
        """Botas de cuero: cana, puntera y suela. Minero: puntera de acero y hebilla. Talador: cordones y media."""
        def fn(r, y, face, xl):
            if y == 11:
                return R(_shade(suela, 1.25 if r % 2 else 1.0))
            if y == 7:
                return cuero_c if face != 'back' or xl in (0, 3) else cuero_o      # vuelta de la cana + tirador
            if estilo == 'minero':
                if y == 10 and (face == 'front' or (face == 'right' and xl == 3) or (face == 'left' and xl == 0)):
                    return R(metal if (face == 'front' and xl == 1) else metal_o)
                if y == 8 and face in ('front', 'right'):
                    return R(metal) if (face == 'right' and xl == 1) else cuero_o   # correa con hebilla
            else:
                if face == 'front' and y in (8, 9) and xl in (1, 2):
                    return R(cordon) if (xl + y) % 2 else cuero_o
                if face == 'front' and y == 10:
                    return cuero_c
            if face == 'back' and y == 10:
                return cuero_o                                                 # talon
            if face == 'back' and y in (8, 9) and xl in (1, 2):
                return _shade(cuero, 0.9) if xl == 1 else cuero                # costura de atras
            if face in ('right', 'left') and y == 9 and xl in (1, 2):
                return _shade(cuero, 0.88)                                     # arruga del tobillo
            return cuero
        return fn

    def suela_px(x, y):
        return R(suela if (x + y) % 2 else _shade(suela, 1.4)) if y not in (1,) else R(_shade(suela, 0.8))

    # ================================================================== Minero
    hum = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); px = hum.load()

    # Chaleco gris oscuro abierto sobre camisa blanca, tirantes con broches y cinturon con hebilla.
    pal = {'C': carbon, 'c': carbon_c, 'k': carbon_o, 'W': blanco, 'w': blanco_o, 'S': cuero, 's': cuero_c,
           'B': cuero_c, 'b': cuero_o, 'H': R(oro), 'h': R(oro_c), 'j': R(oro_o), 'G': R(metal), 'M': R(metal_c),
           'm': R(metal_o), 'p': _mix(carbon, polvo, 0.5)}
    frente = _mapa(['CSWWWWSC',
                    'CscWWcsC',
                    'CSCcwcSC',
                    'CSCkCCSC',
                    'CsCkGCsC',
                    'CSCkCCSC',
                    'cSckGcSc',
                    'CsCkCCsC',
                    'CMCkGCMC',
                    'BBBhHBBB',
                    'bbbHjbbb',
                    'kpkkkkpk'], pal)
    espalda = _mapa(['CSCCCCSC',
                     'CsCCCCsC',
                     'kkSkkSkk',
                     'CCsCCsCC',
                     'CCCSSCCC',
                     'CCCMmCCC',
                     'CCCSSCCC',
                     'CCCssCCC',
                     'CcCSSCcC',
                     'BBBBBBBB',
                     'bbbmmbbb',
                     'kkpkkpkk'], pal)

    def chaleco(r, y, face, xl):
        if face == 'front':
            return frente(xl, y)
        if face == 'back':
            return espalda(xl, y)
        if y == 9:
            return cuero_c
        if y == 10:
            return cuero_o
        if y == 11:
            return carbon_o
        if y < 2:
            return blanco_o if y == 0 else carbon_c                            # sisa: asoma la camisa
        return carbon_o if xl == (1 if face == 'right' else 2) else carbon     # costura del costado
    _paint(px, BODY, range(12), chaleco, rng=rng)

    def hombros(x, y):
        if x in (1, 6):
            return tirador(y)
        if x in (3, 4) and y in (1, 2):
            return blanco_o
        if x in (2, 5) and y in (1, 2) or x in (3, 4) and y in (0, 3):
            return blanco
        return carbon
    _cap(px, BODY, 'top', hombros, rng=rng)
    _cap(px, BODY, 'bottom', lambda x, y: carbon_o)

    # Mangas blancas arremangadas: pliegues en el codo, rollo grueso y algo de tierra.
    def manga(r, y, face, xl):
        if y == 8:
            return blanco_oo
        if y == 7:
            return R(blanco if r % 4 != 2 else blanco_o)
        if (y == 3 and xl in (1, 2)) or (y == 4 and xl == 2) or (y == 5 and xl in (0, 1)):
            return blanco_o
        if y == 0 and xl in (0, 3):
            return blanco_o
        if (face, xl, y) in (('front', 1, 6), ('right', 2, 5), ('back', 2, 6), ('right', 1, 2)):
            return _mix(blanco_o, polvo, 0.35)
        return blanco
    _paint(px, ARM, range(9), manga, rng=rng, inner='left')
    _cap(px, ARM, 'top', lambda x, y: blanco_o if y == 0 else blanco, rng=rng)

    _paint(px, LEG, range(7, 12), botas('minero'), rng=rng, inner='left')
    _cap(px, LEG, 'bottom', suela_px)

    leg = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); pl = leg.load()

    # Pantalon de trabajo: bolsillos, rodillera reforzada, bolsillo cargo al costado y polvo abajo.
    def pantalon(r, y, face, xl):
        if y >= 9 and (r * 5 + y * 3) % 7 < 2:
            return _mix(carbon, polvo, 0.55)
        if y == 11:
            return carbon_o
        if face == 'front':
            if (xl, y) in ((0, 1), (1, 0)):
                return carbon_o                                                # boca del bolsillo
            if y in (5, 6):
                return carbon_c                                                # rodillera
            if y in (4, 7):
                return carbon_o
            if y == 9 and xl in (1, 2):
                return carbon_o
        if face == 'back':
            if xl in (1, 2) and y == 1:
                return carbon_c
            if xl in (1, 2) and y == 3:
                return carbon_o
            if y == 6 and xl in (1, 2):
                return carbon_o
        if face == 'right':                                                    # lado de afuera
            if y == 3:
                return carbon_c
            if y == 6:
                return carbon_o
            if y in (4, 5) and xl in (0, 3):
                return carbon_o
            if y == 4 and xl == 2:
                return R(metal_o)
        return carbon
    _paint(pl, LEG, range(12), pantalon, rng=rng, inner='left')
    _cap(pl, LEG, 'top', lambda x, y: carbon)

    def cintura_minero(r, y, face, xl):
        if y < 8:                                                              # tirantes solos (sin el chaleco)
            c = (frente if face == 'front' else espalda)(xl, y) if face in ('front', 'back') else None
            return c if c in (cuero, cuero_c) or isinstance(c, Raw) and y in (5, 8) else None
        if face == 'front':
            return frente(xl, y) if y > 8 else (R(metal_c) if xl in (1, 6) else carbon_c)
        if face == 'back':
            return espalda(xl, y) if y > 8 else (cuero if xl in (3, 4) else carbon_c)
        return {8: carbon_c, 9: cuero_c, 10: cuero_o, 11: carbon_o}[y]
    _paint(pl, BODY, range(12), cintura_minero, rng=rng)
    out['minero'] = (hum, leg)

    # ================================================================== Talador
    verde, verde_o, verde_c, verde_oo = _hex('#3f8a3a'), _hex('#2c6a2b'), _hex('#5cab50'), _hex('#1f4d21')
    rojo, rojo_o, rojo_c, negro = _hex('#c93a30'), _hex('#96271f'), _hex('#dc5144'), _hex('#33201f')
    azul, azul_o, azul_c, azul_cc = _hex('#3b5ea8'), _hex('#2a447c'), _hex('#5878bd'), _hex('#8aa3d6')
    hilo = _hex('#b9955a')
    hum = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); px = hum.load()

    # Camisa lenadora: cuadros rojo/negro, cuello, tapeta con botones, bolsillos con solapa y tiradores.
    def cuadros(r, y):
        a, b = (r % 4) in (0, 1), (y % 4) in (0, 1)
        if a and b:
            return negro
        if a or b:
            return rojo_o
        return rojo_c if (r + y) % 4 == 1 else rojo
    boton = R(_hex('#ead9b0'))
    pal = {'T': cuero, 't': cuero_c, 'K': _shade(rojo_o, 0.8), 'W': blanco, 'w': blanco_o, 'P': _shade(rojo_o, 0.62),
           'O': boton, 'F': rojo_c, 'f': negro, 'M': R(metal), 'X': R(cuero_o)}
    frente_t = _mapa(['.TKWWKT.',
                      '.t.KwKt.',
                      '.T.P..T.',
                      '.T.PO.T.',
                      '.t.P..t.',
                      '.T.P..T.',
                      '.T.PO.T.',
                      '.t.P..t.',
                      '.T.P..T.',
                      '.T.PO.T.',
                      '.M.P..M.',
                      '........'], pal)
    espalda_t = _mapa(['.T....T.',
                       '.t....t.',
                       '.T....T.',
                       '.tTtTTt.',
                       '.T....T.',
                       '.T....T.',
                       '.t....t.',
                       '.T....T.',
                       '.T....T.',
                       '.t....t.',
                       '.M....M.',
                       '........'], pal)

    def camisa(r, y, face, xl):
        c = frente_t(xl, y) if face == 'front' else espalda_t(xl, y) if face == 'back' else None
        if c:
            return c
        c = cuadros(r, y)
        if y == 11:
            return _shade(c, 0.78)                                             # ruedo
        if face in ('right', 'left') and y == 0:
            return _shade(c, 0.8)                                              # costura de la sisa
        return c
    _paint(px, BODY, range(12), camisa, rng=rng)

    def hombros_t(x, y):
        if x in (1, 6):
            return tirador(y)
        if x in (3, 4) and y in (1, 2):
            return blanco_o
        if x in (2, 5) and y in (1, 2) or x in (3, 4) and y in (0, 3):
            return pal['K']
        return cuadros(x + 4, y)
    _cap(px, BODY, 'top', hombros_t, rng=rng)
    _cap(px, BODY, 'bottom', lambda x, y: rojo_o)

    # Mangas: cuadros hasta el codo, arremangadas, y debajo la camiseta termica blanca con puno.
    def manga_t(r, y, face, xl):
        if y > 10:
            return None
        if y == 10:
            return R(_shade(blanco_o if r % 2 else blanco, 0.92))               # puno acanalado
        if y in (8, 9):
            return blanco_o if (xl + y) % 5 == 0 else blanco
        if y == 7:
            return R(_shade(rojo_c if r % 4 != 3 else rojo_o, 1.0 if face == 'front' else 0.88))   # rollo
        if y == 6:
            return _shade(cuadros(r, y), 0.8)
        c = cuadros(r, y)
        return _shade(c, 0.82) if y == 0 and xl in (0, 3) else c
    _paint(px, ARM, range(12), manga_t, rng=rng, inner='left')
    _cap(px, ARM, 'top', lambda x, y: cuadros(x, y), rng=rng)

    _paint(px, LEG, range(7, 12), botas('talador'), rng=rng, inner='left')
    _cap(px, LEG, 'bottom', suela_px)

    leg = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); pl = leg.load()

    # Jean: sarga en diagonal, costuras con hilo dorado, bolsillos, rodillas gastadas y botamanga doblada.
    def jean(r, y, face, xl):
        if y >= 10:
            return azul_cc if y == 10 else _shade(azul_c, 0.9)                 # botamanga
        if face == 'front':
            if (xl, y) in ((0, 1), (1, 0)):
                return hilo                                                    # boca del bolsillo
            if (xl, y) == (0, 0):
                return azul_o
            if y in (4, 5, 6) and xl in (1, 2):
                return azul_cc if y == 5 else azul_c                           # rodilla gastada
            if y == 8 and xl in (0, 3):
                return azul_o
        if face == 'back':
            if xl in (1, 2) and y == 1:
                return azul_c
            if (xl, y) == (2, 2):
                return hilo
            if xl in (1, 2) and y == 3:
                return azul_o
            if y == 6 and xl in (1, 2):
                return azul_o                                                  # pliegue de la corva
        if face == 'right':
            if xl == 2:
                return azul_c                                                  # costura lateral
            if xl == 1:
                return azul_o
        return azul_o if (r + y) % 4 == 0 else azul
    _paint(pl, LEG, range(12), jean, rng=rng, inner='left')
    _cap(pl, LEG, 'top', lambda x, y: azul)

    def cintura_talador(r, y, face, xl):
        if y < 8:                                                              # tiradores solos (sin la camisa)
            c = (frente_t if face == 'front' else espalda_t)(xl, y) if face in ('front', 'back') else None
            return c if c in (cuero, cuero_c, pal['X']) else None
        if y == 8:
            if face in ('front', 'back') and xl in (1, 6):
                return R(metal)
            return azul_c
        if y == 9:
            if face == 'front' and xl == 3:
                return R(hilo)                                                 # boton del jean
            return azul_o if r % 6 == 2 else azul                              # presillas
        if face == 'front' and xl == 4:
            return azul_o                                                      # cierre
        if face == 'front' and (xl, y) in ((0, 11), (1, 10), (7, 11), (6, 10)):
            return hilo
        if face == 'back' and y == 10:
            return azul_o                                                      # canesu
        return azul_o if (r + y) % 4 == 0 else azul
    _paint(pl, BODY, range(12), cintura_talador, rng=rng)
    out['talador'] = (hum, leg)
    # ---------------- Iconos 16x16
    icons.update(_icons())
    return out, icons


# ------------------------------------------------------------------------------------- sombreros 3D
# El casco y el gorro son modelos de item que se dibujan en la cabeza (como el casco de Agua): el item no lleva
# asset_id y `items/<id>.json` elige el modelo 3D con display_context=head y el icono plano en el resto.
# Medidas en pixeles de cabeza: x -4..4 (ancho), y 0..8 (0 = menton, 8 = coronilla), z -4..4 (-4 = cara).
# En el modelo de item 1 pixel de cabeza = 1.6 unidades y el centro de la cabeza cae en (8, 8, 8).
_HAT_TEX = 64


def _sombreros():
    """{sid: {'tex': imagen 64x64, 'model': json del modelo, 'parts': [((x0,y0,z0,x1,y1,z1), {cara: imagen})]}}"""
    from PIL import Image
    rng = random.Random(1412)
    gris, gris_o, gris_c, gris_oo = _hex('#8d939a'), _hex('#666c73'), _hex('#b9bec3'), _hex('#43484f')
    cuero, cuero_o, cuero_c = _hex('#8a5530'), _hex('#5c3519'), _hex('#ad7242')
    oro, oro_c, oro_o, luz = _hex('#f2c43d'), _hex('#fff1a0'), _hex('#b8862a'), _hex('#fffbe2')
    metal, metal_o = _hex('#b9bcc2'), _hex('#6f737b')
    verde, verde_o, verde_c, verde_oo = _hex('#3f8a3a'), _hex('#2f702d'), _hex('#5cab50'), _hex('#1f4d21')
    lados = ('north', 'south', 'east', 'west')

    def punto(i, j):
        return verde if (i + j) % 2 == 0 else verde_o

    # ---- Minero: copa en dos escalones, correa de cuero, ala ancha y lampara que sobresale al frente.
    def copa(f, i, j, w, h):
        if f == 'up':
            return gris_o if i in (0, w - 1) or j in (0, h - 1) else gris
        if f == 'down':
            return gris_oo
        if j == 0:
            return gris_c if i not in (0, w - 1) else gris
        if j == 1 and i % 4 == 2:
            return gris_oo                                                     # remaches
        if i == w // 2:
            return gris_c                                                      # nervio
        return gris_o if (i * 7 + j * 3) % 11 == 0 else gris

    def copa_alta(f, i, j, w, h):
        if f == 'up':
            if i == w // 2:
                return gris_c
            if (i, j) in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
                return gris_oo
            return gris if i not in (0, w - 1) and j not in (0, h - 1) else _mix(gris, gris_c, 0.5)
        return _mix(gris, gris_c, 0.7) if i != w // 2 else gris_c

    def correa(f, i, j, w, h):
        if f in ('up', 'down'):
            return cuero_o
        if f == 'south' and i in (w // 2 - 1, w // 2):
            return metal if i == w // 2 else metal_o                           # hebilla de atras
        return cuero_c if i % 3 == 1 else cuero

    def ala(f, i, j, w, h):
        if f == 'down':
            return gris_oo
        if f != 'up':
            return gris_c if f == 'north' else gris
        borde = i in (0, w - 1) or j in (0, h - 1)
        if j <= 1 and abs(i - (w - 1) / 2) < 2.6:
            return _mix(gris_c, oro_c, 0.55 if j == 0 else 0.3)                # la luz de la lampara
        if borde:
            return gris
        if i in (1, w - 2) or j in (1, h - 2):
            return gris_c
        return gris_o                                                          # sombra junto a la copa

    def lampara(f, i, j, w, h):
        if f == 'north':
            return [[oro_o, oro, oro_o], [oro, luz, oro_c], [oro_o, oro_c, oro_o]][j][i]
        if f == 'up':
            return metal
        if f == 'down':
            return metal_o
        return metal_o if j != 1 else cuero                                    # caja de la lampara y su correa

    # ---- Talador: doblez grueso acanalado, cuerpo tejido, coronilla corrida hacia atras y punta caida.
    def doblez(f, i, j, w, h):
        if f == 'up':
            return verde_o
        if f == 'down':
            return verde_oo
        c = verde_c if i % 2 == 0 else verde
        return _shade(c, 1.06 if j == 0 else 0.9)

    def cuerpo(f, i, j, w, h):
        if f in ('up', 'down'):
            return punto(i, j)
        return (verde_oo if i % 2 else verde_o) if j == h - 1 else punto(i, j)  # sombra sobre el doblez

    def coronilla(f, i, j, w, h):
        if f == 'up':
            if abs(i - (w - 1) / 2) == abs(j - (h - 1) / 2):
                return verde_o                                                 # disminuciones en diagonal
            return verde_c if (i + j) % 2 == 0 else verde
        return verde_c if (i + j) % 2 == 0 else verde

    def punta(f, i, j, w, h):
        if f == 'down':
            return verde_oo
        return _shade(punto(i, j), 0.92 if f != 'up' else 1.0)

    defs = {
        'minero': [((-4.5, 5.5, -4.5, 4.5, 8.5, 4.5), copa), ((-3.5, 8.5, -3.5, 3.5, 9.5, 3.5), copa_alta),
                   ((-4.75, 5.5, -4.75, 4.75, 6.5, 4.75), correa), ((-6, 4.75, -6.5, 6, 5.5, 6), ala),
                   ((-1.5, 5.5, -6, 1.5, 8.5, -4.5), lampara)],
        'talador': [((-4.75, 4.5, -4.75, 4.75, 6.5, 4.75), doblez), ((-4.4, 6.5, -4.4, 4.4, 8.5, 4.4), cuerpo),
                    ((-3.5, 8.5, -2.8, 3.5, 9.5, 4.2), coronilla), ((-2.5, 7.9, 2.6, 2.5, 9.9, 5.5), punta)],
    }
    out = {}
    for sid, parts in defs.items():
        tex = Image.new('RGBA', (_HAT_TEX, _HAT_TEX), (0, 0, 0, 0))
        cx = cy = shelf = 0
        elements, drawn = [], []
        for box, fn in parts:
            x0, y0, z0, x1, y1, z1 = box
            dx, dy, dz = (max(1, round(v)) for v in (x1 - x0, y1 - y0, z1 - z0))
            sizes = {'north': (dx, dy), 'south': (dx, dy), 'east': (dz, dy), 'west': (dz, dy), 'up': (dx, dz), 'down': (dx, dz)}
            faces, imgs = {}, {}
            for f, (w, h) in sizes.items():
                im = Image.new('RGBA', (w, h))
                for j in range(h):
                    for i in range(w):
                        c = fn(f, i, j, w, h)
                        if not isinstance(c, Raw) and c not in (luz, oro_c):
                            k = 1 + rng.uniform(-0.03, 0.03)
                            if f in lados and h > 1:
                                k *= 1.06 - 0.12 * j / (h - 1)
                            c = _shade(c, k)
                        im.putpixel((i, j), tuple(c))
                if cx + w > _HAT_TEX:
                    cx, cy, shelf = 0, cy + shelf, 0
                tex.paste(im, (cx, cy))
                q = 16 / _HAT_TEX
                faces[f] = {'uv': [cx * q, cy * q, (cx + w) * q, (cy + h) * q], 'texture': '#t'}
                imgs[f] = im
                cx, shelf = cx + w, max(shelf, h)
            u = lambda v, c=0: round(8 + 1.6 * (v - c), 3)
            elements.append({'from': [u(x0), u(y0, 4), u(z0)], 'to': [u(x1), u(y1, 4), u(z1)], 'faces': faces})
            drawn.append((box, imgs))
        name = f'astral:item/{sid}_helmet_3d'
        out[sid] = {'tex': tex, 'parts': drawn,
                    'model': {'textures': {'t': name, 'particle': name}, 'elements': elements,
                              'display': {'head': {'translation': [0, 0, 0], 'scale': [1, 1, 1]}}}}
    return out


def _icons():
    from PIL import Image
    O = _hex('#1b1b1f')
    pal = {
        'minero': {'H': _hex('#8d939a'), 'h': _hex('#b4b9be'), 'L': _hex('#f2c43d'), 'l': _hex('#fff1a0'),
                   'C': _hex('#3a3d44'), 'c': _hex('#555a63'), 'B': _hex('#8a5530'), 'b': _hex('#5c3519'),
                   'W': _hex('#e9e6df'), 'P': _hex('#3a3d44'), 'p': _hex('#555a63'), 'S': _hex('#c9c9c9')},
        'talador': {'H': _hex('#3f8a3a'), 'h': _hex('#58a84e'), 'L': _hex('#2a5f28'), 'l': _hex('#2a5f28'),
                    'C': _hex('#b8322b'), 'c': _hex('#2a1d1d'), 'B': _hex('#8a5530'), 'b': _hex('#5c3519'),
                    'W': _hex('#e9e6df'), 'P': _hex('#3b5ea8'), 'p': _hex('#5878bd'), 'S': _hex('#d8d0c0')},
    }
    shapes = {
        'minero_helmet': ['................', '................', '................', '.....OOOOOO.....',
                          '....OhhOOhhO....', '...OHHOllOHHO...', '...OHHOLLOHHO...', '..OHHHOLLOHHHO..',
                          '..OHHHHOOHHHHO..', '.OOOOOOOOOOOOOO.', '.ObbbbbbbbbbbbO.', '..OOOOOOOOOOOO..',
                          '................', '................', '................', '................'],
        'talador_helmet': ['................', '................', '.......OO.......', '......OhhO......',
                           '.....OHLHLO.....', '....OHLhHLHO....', '...OHHLHHLHHO...', '...OLLLLLLLLO...',
                           '...OHHLHHLHHO...', '..OLLLLLLLLLLO..', '..OhhhhhhhhhhO..', '..OLLLLLLLLLLO..',
                           '...OOOOOOOOOO...', '................', '................', '................'],
        'minero_chestplate': ['................', '..OOOO...OOOO...', '.OWWCOO.OOCWWO..', '.OWWCBWWWBCWWO..',
                              '.OWWCBCWCBCWWO..', '.OOWCBCcCBCWOO..', '..OOCBCCCBCOO...', '...OCBCcCBCO....',
                              '...OCBCCCBCO....', '...OBBBSBBBO....', '...OCCCCCCCO....', '...OOOOOOOOO....',
                              '................', '................', '................', '................'],
        'talador_chestplate': ['................', '..OOOO...OOOO...', '.OCCcOO.OOcCCO..', '.OccCCWWWCCccO..',
                               '.OCCcCCWCCcCCO..', '.OOcCCcSCcCCOO..', '..OOCCcCCcCOO...', '...OccCScCcO....',
                               '...OCCcCCcCO....', '...OCCcSCcCO....', '...OccCCCccO....', '...OOOOOOOOO....',
                               '................', '................', '................', '................'],
        'minero_leggings': ['................', '...OOOOOOOOO....', '...ObbbSbbbO....', '...OPPPPPPPO....',
                            '...OPPPOPPPO....', '...OPPpOpPPO....', '...OPPPOPPPO....', '...OPPPOPPPO....',
                            '...OpPPOPPpO....', '...OPPPOPPPO....', '...OPPPOPPPO....', '...OPPPOPPPO....',
                            '...OOOOOOOOO....', '................', '................', '................'],
        'talador_leggings': ['................', '...OOOOOOOOO....', '...OBbbbbbBO....', '...OBPPPPPBO....',
                             '...OPPPOPPPO....', '...OPpPOPpPO....', '...OPPPOPPPO....', '...OPpPOPpPO....',
                             '...OPPPOPPPO....', '...OPpPOPpPO....', '...OPPPOPPPO....', '...OPPPOPPPO....',
                             '...OOOOOOOOO....', '................', '................', '................'],
    }
    boots = ['................', '................', '................', '................',
             '...OOOO..OOOO...', '...OBBO..OBBO...', '...ObBO..ObBO...', '...OBBO..OBBO...',
             '...OBBO..OBBO...', '..OBBBO..OBBBO..', '.OBBBBO..OBBBBO.', '.ObbbbO..ObbbbO.',
             '.OOOOOO..OOOOOO.', '................', '................', '................']
    shapes['minero_boots'] = shapes['talador_boots'] = boots
    out = {}
    for iid, rows in shapes.items():
        p = pal[iid.split('_')[0]]
        im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == 'O':
                    im.putpixel((x, y), O)
                elif ch in p:
                    im.putpixel((x, y), p[ch])
        out[iid] = im
    return out


def own_textures():
    """Archivos del resource pack (bytes)."""
    files = {}

    def png(name, im):
        s = io.BytesIO(); im.save(s, 'PNG'); files['assets/astral/textures/' + name + '.png'] = s.getvalue()

    def put(name, obj):
        files['assets/' + name + '.json'] = json.dumps(obj).encode()
    layers, icons = textures()
    for sid, (hum, leg) in layers.items():
        png('entity/equipment/humanoid/' + sid, hum)
        png('entity/equipment/humanoid_leggings/' + sid, leg)
        put('astral/equipment/' + sid, {'layers': {'humanoid': [{'texture': 'astral:' + sid}],
                                                   'humanoid_leggings': [{'texture': 'astral:' + sid}]}})
    for iid, im in icons.items():
        png('item/' + iid, im)
        put('astral/models/item/' + iid, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'astral:item/' + iid}})
        put('astral/items/' + iid, {'model': {'type': 'minecraft:model', 'model': 'astral:item/' + iid}})
    # Casco y gorro 3D: en la cabeza se dibuja el modelo; en el inventario y la mano, el icono.
    for sid, hat in _sombreros().items():
        iid = sid + '_helmet'
        png(f'item/{iid}_3d', hat['tex'])
        put(f'astral/models/item/{iid}_3d', hat['model'])
        put('astral/items/' + iid, {'model': {
            'type': 'minecraft:select', 'property': 'minecraft:display_context',
            'cases': [{'when': 'head', 'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}_3d'}}],
            'fallback': {'type': 'minecraft:model', 'model': 'astral:item/' + iid}}})
    return files


# ------------------------------------------------------------------------------------- preview
def preview(path=ROOT / 'build/previews/oficios.png'):
    """Cada set de frente, de costado y de espalda (piel lisa), la cabeza en 3D con el sombrero y los 4 iconos."""
    import math
    from PIL import Image, ImageDraw
    layers, icons = textures()
    hats = _sombreros()
    S = 12
    MX, MY = 3, 3                      # margen (en pixeles del jugador) para que entren el ala y la copa
    FW, SW, FH = 16 + MX * 2, 8 + 8, 32 + MY
    GAP = 8
    ISO = 230
    W = (FW * 2 + SW) * S + GAP * 3 + ISO
    H = FH * S + 50
    sheet = Image.new('RGBA', (W * 2 + 60, H + 16 * 6 + 30), (34, 40, 52, 255))
    d = ImageDraw.Draw(sheet)
    skin, pelo, ropa, ojo = (214, 170, 130, 255), (84, 54, 34, 255), (120, 120, 140, 255), (40, 40, 60, 255)

    def face(img, box, f):
        u, v, w, h = box.faces[f]
        return img.crop((u, v, u + w, v + h))

    def hat_ortho(canvas, hat, view, cx):
        """Dibuja el sombrero en vista recta. cx = columna (en pixeles del jugador) del centro de la cabeza."""
        f, key, k = {'front': ('north', lambda b: -b[2], 1.0), 'back': ('south', lambda b: b[5], 0.93),
                     'side': ('east', lambda b: b[3], 0.9)}[view]
        for box, imgs in sorted(hat['parts'], key=lambda p: key(p[0])):
            x0, y0, z0, x1, y1, z1 = box
            a, b = (-z1, -z0) if view == 'side' else (x0, x1)
            im = imgs[f].point(lambda v: int(v * k)) if k != 1.0 else imgs[f]
            im.putalpha(255)
            w, h = round((b - a) * S), max(1, round((y1 - y0) * S))
            canvas.alpha_composite(im.resize((w, h), Image.NEAREST), (round((cx + a) * S), round((MY + 8 - y1) * S)))

    def figure(hum, leg, hat, side):
        fig = Image.new('RGBA', (16, 32), (0, 0, 0, 0)); bd = ImageDraw.Draw(fig)
        bd.rectangle((4, 0, 11, 7), fill=skin); bd.rectangle((4, 0, 11, 1), fill=pelo)
        if side == 'front':
            bd.point([(5, 4), (10, 4)], fill=ojo)
        else:
            bd.rectangle((4, 0, 11, 6), fill=pelo)
        bd.rectangle((4, 8, 11, 19), fill=ropa); bd.rectangle((0, 8, 3, 19), fill=skin); bd.rectangle((12, 8, 15, 19), fill=skin)
        bd.rectangle((4, 20, 11, 31), fill=(70, 70, 90, 255))
        f = 'front' if side == 'front' else 'back'
        # De espaldas el brazo y la pierna derechos quedan a la derecha de la imagen.
        own, mirror = ((0, 4), (12, 8)) if side == 'front' else ((12, 8), (0, 4))
        for img, box, pos, flip in ((leg, LEG, (own[1], 20), False), (leg, LEG, (mirror[1], 20), True), (leg, BODY, (4, 8), False),
                                    (hum, LEG, (own[1], 20), False), (hum, LEG, (mirror[1], 20), True), (hum, BODY, (4, 8), False),
                                    (hum, ARM, (own[0], 8), False), (hum, ARM, (mirror[0], 8), True)):
            part = face(img, box, f)
            if flip:
                part = part.transpose(Image.FLIP_LEFT_RIGHT)
            fig.alpha_composite(part, pos)
        canvas = Image.new('RGBA', (FW * S, FH * S), (0, 0, 0, 0))
        canvas.alpha_composite(fig.resize((16 * S, 32 * S), Image.NEAREST), (MX * S, MY * S))
        hat_ortho(canvas, hat, side, MX + 8)
        return canvas

    def costado(hum, leg, hat):
        """Lado derecho del jugador (mira hacia la derecha de la imagen)."""
        fig = Image.new('RGBA', (8, 32), (0, 0, 0, 0)); bd = ImageDraw.Draw(fig)
        bd.rectangle((0, 0, 7, 7), fill=skin); bd.rectangle((0, 0, 7, 1), fill=pelo); bd.rectangle((0, 0, 3, 5), fill=pelo)
        bd.point((6, 4), fill=ojo)
        bd.rectangle((2, 8, 5, 19), fill=skin); bd.rectangle((2, 20, 5, 31), fill=(70, 70, 90, 255))
        for img, box, pos in ((leg, LEG, (2, 20)), (hum, LEG, (2, 20)), (hum, BODY, (2, 8)), (hum, ARM, (2, 8))):
            fig.alpha_composite(face(img, box, 'right'), pos)
        canvas = Image.new('RGBA', (SW * S, FH * S), (0, 0, 0, 0))
        canvas.alpha_composite(fig.resize((8 * S, 32 * S), Image.NEAREST), (4 * S, MY * S))
        hat_ortho(canvas, hat, 'side', 8)
        return canvas

    def cabeza_3d(hat, size=ISO, yaw=-32, tilt=24):
        """La cabeza con el sombrero vista de tres cuartos (pixel por pixel, ordenado por profundidad)."""
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        ca, sa, ct, st = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)),
                          math.cos(math.radians(tilt)), math.sin(math.radians(tilt)))
        Z = size / 19

        def proj(x, y, z):
            xr, zr = x * ca - z * sa, x * sa + z * ca
            return (size / 2 + xr * Z, size * 0.62 - (y - 4) * ct * Z - zr * st * Z), zr * ct - (y - 4) * st
        head = Image.new('RGBA', (8, 8), skin); hd = ImageDraw.Draw(head)
        hd.rectangle((0, 0, 7, 1), fill=pelo); hd.point([(1, 4), (6, 4)], fill=ojo)
        lado = Image.new('RGBA', (8, 8), skin); ImageDraw.Draw(lado).rectangle((0, 0, 7, 1), fill=pelo)
        ImageDraw.Draw(lado).rectangle((4, 0, 7, 5), fill=pelo)
        parts = [((-4, 0, -4, 4, 8, 4), {'north': head, 'south': Image.new('RGBA', (8, 8), pelo), 'west': lado, 'east': lado, 'up': Image.new('RGBA', (8, 8), pelo)})] + hat['parts']
        quads = []
        for (x0, y0, z0, x1, y1, z1), imgs in parts:
            for f, k in (('north' if ca > 0 else 'south', 1.0), ('up', 1.12), ('west' if sa > 0 else 'east', 0.8)):
                tex = imgs[f].convert('RGBA'); w, h = tex.size
                for j in range(h):
                    for i in range(w):
                        a0, a1, b0, b1 = i / w, (i + 1) / w, j / h, (j + 1) / h
                        if f == 'north':     # izquierda de la imagen = +x
                            pts = [(x1 - (x1 - x0) * a, y1 - (y1 - y0) * b, z0) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                        elif f == 'south':   # izquierda de la imagen = -x
                            pts = [(x0 + (x1 - x0) * a, y1 - (y1 - y0) * b, z1) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                        elif f == 'up':      # arriba de la imagen = norte
                            pts = [(x0 + (x1 - x0) * a, y1, z0 + (z1 - z0) * b) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                        elif f == 'west':    # izquierda = norte
                            pts = [(x0, y1 - (y1 - y0) * b, z0 + (z1 - z0) * a) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                        else:                # east: izquierda = sur
                            pts = [(x1, y1 - (y1 - y0) * b, z1 - (z1 - z0) * a) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
                        pr = [proj(*p) for p in pts]
                        c = tex.getpixel((i, j))
                        quads.append((sum(p[1] for p in pr) / 4, [p[0] for p in pr], tuple(min(255, int(v * k)) for v in c[:3]) + (255,)))
        for _, poly, c in sorted(quads, key=lambda q: -q[0]):
            dr.polygon(poly, fill=c)
        return im
    for i, (sid, (hum, leg)) in enumerate(layers.items()):
        x0 = 20 + i * (W + 20)
        hat = hats[sid]
        d.text((x0, 8), f"Ropa de {SETS[sid]['label']}  (frente, costado, espalda y sombrero en 3D)", fill=(255, 230, 160, 255))
        sheet.alpha_composite(figure(hum, leg, hat, 'front'), (x0, 24))
        sheet.alpha_composite(costado(hum, leg, hat), (x0 + FW * S + GAP, 24))
        sheet.alpha_composite(figure(hum, leg, hat, 'back'), (x0 + (FW + SW) * S + GAP * 2, 24))
        sheet.alpha_composite(cabeza_3d(hat), (x0 + (FW * 2 + SW) * S + GAP * 3, 24))
        sheet.alpha_composite(cabeza_3d(hat, yaw=-150), (x0 + (FW * 2 + SW) * S + GAP * 3, 24 + ISO))
        for j, piece in enumerate(PIECES):
            sheet.alpha_composite(icons[f'{sid}_{piece}'].resize((64, 64), Image.NEAREST), (x0 + j * 84, H - 10))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


if __name__ == '__main__':
    print(preview())
