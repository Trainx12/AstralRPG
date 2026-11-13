"""Ventanas de mesas, hornos, aldeanos, etc. del pack "Darkmode Colourful Containers" (Kingybu, Chris_XENO,
BurntToast_). TERCEROS: el ZIP vive en ASTRAL_PRIVADO/originales/contenedores/ y los derivados solo en
ASTRAL_PRIVADO/build/entregas/contenedores-darkmode/. Nunca escribe en el repo publico.

Sin OptiFine/OptiGUI: solo se usan las rutas vanilla de gui/ (ventanas, sprites, widgets, recetas). Lo de assets/optigui
(una ventana por oficio de aldeano o color de shulker) necesita el mod y se descarta.

Pedido del dueno: TODO pasa a este pack salvo inventory.png (inventario de piedra y oro, de gui_textures.py).
- generic_54.png lo usan los cofres Y todos los menus de DeluxeMenus: se deja en gris oscuro neutro (el marron del
  cofre se pasa a gris) y el dibujo de cofre, cofre doble, barril y ender va en el TITULO, como hace el propio pack
  (glifos del font default + espacios negativos). Los menus tienen titulo propio, asi que no lo muestran.
  Un cofre renombrado muestra su nombre en lugar del dibujo.
Los titulos de las ventanas reemplazadas se ocultan o pasan a glifo: lang-ocultar.json, que el armado del FINAL
suma a nuestros lang es_ar/es_es/es_mx/en_us; font-extra.json se suma a nuestro minecraft:default.

python contenedores_darkmode.py  -> carpeta de la entrega
"""
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIV = Path(os.environ.get('ASTRAL_PRIVADO', ROOT / '.local/terceros/AstralRPG-privado'))
SRC = PRIV / 'originales/contenedores/darkmode-colourful-containers.zip'
OUT = PRIV / 'build/entregas/contenedores-darkmode'
GUI = 'assets/minecraft/textures/gui/'
OCULTAR = ('container.crafting', 'container.crafter', 'container.furnace', 'container.blast_furnace', 'container.smoker',
           'container.enchant', 'container.repair', 'container.brewing', 'container.beacon', 'container.hopper',
           'container.dispenser', 'container.dropper', 'container.shulkerBox', 'container.loom', 'container.grindstone_title',
           'container.cartography_table', 'container.stonecutter', 'container.upgrade', 'merchant.trades',
           'block.minecraft.beacon.primary', 'block.minecraft.beacon.secondary')
# Glifos propios (rango 0xEC1x libre en nuestro font). Alturas y subidas: las del pack.
ESP = {'\uec1a': -8, '\uec1b': -4, '\uec1c': -1}
GLIFOS = {'chest': ('\uec11', 91, 23), 'barrel': ('\uec13', 83, 14), 'ender_chest': ('\uec14', 91, 23),
          'large_chest': ('\uec15', 158, 34)}
TITULOS = {'container.chest': '\uec1a\uec1b\uec11', 'container.chestDouble': '\uec1a\uec1a\uec1b\uec15',
           'container.enderchest': '\uec1a\uec1b\uec14', 'container.barrel': '\uec1a\uec13'}


def elegidos(names):
    """Todas las texturas vanilla de gui/ del pack, menos el inventario (y lo que solo usa OptiGUI)."""
    out = []
    for n in names:
        if not n.endswith('.png') or not n.startswith(GUI):
            continue
        r = n[len(GUI):]
        if r in ('container/inventory.png', 'brown_recipe_book.png') or r.startswith(('container/inventory/', 'container/villagers/')):
            continue
        out.append(n)
    return sorted(out)


def gris(im):
    """generic_54 neutro: el marron del cofre pasa al gris oscuro de la parte del inventario."""
    import colorsys
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > 0.2 and 0.03 < h < 0.17:
                c = round(255 * v * 0.42)
                px[x, y] = (c, c, c + 2, a)
    return im


def generate():
    z = zipfile.ZipFile(SRC)
    files = elegidos(z.namelist())
    import io
    from PIL import Image
    for n in files:
        d = OUT / n; d.parent.mkdir(parents=True, exist_ok=True)
        if n.endswith('container/generic_54.png'):
            gris(Image.open(io.BytesIO(z.read(n)))).save(d)
        else:
            d.write_bytes(z.read(n))
    lang = {k: '' for k in OCULTAR}
    lang.update({k: '\u00a7f' + v for k, v in TITULOS.items()})
    (OUT / 'lang-ocultar.json').write_text(json.dumps(lang, indent=1), encoding='utf-8')
    font = [{'type': 'space', 'advances': ESP}]
    font += [{'type': 'bitmap', 'file': f'minecraft:gui/container/chests/{n}.png', 'height': h, 'ascent': a, 'chars': [c]}
             for n, (c, h, a) in GLIFOS.items()]
    (OUT / 'font-extra.json').write_text(json.dumps(font, indent=1), encoding='utf-8')
    return OUT, len(files)


if __name__ == '__main__':
    print(generate())
