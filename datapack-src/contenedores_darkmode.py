"""Ventanas de mesas, hornos, aldeanos, etc. del pack "Darkmode Colourful Containers" (Kingybu, Chris_XENO,
BurntToast_). TERCEROS: el ZIP vive en ASTRAL_PRIVADO/originales/contenedores/ y los derivados solo en
ASTRAL_PRIVADO/build/entregas/contenedores-darkmode/. Nunca escribe en el repo publico.

Sin OptiFine/OptiGUI: solo se usan las rutas vanilla (gui/container/*.png y sus sprites). Lo de assets/optigui
(una ventana por oficio de aldeano o color de shulker) necesita el mod y se descarta.

Se conservan las nuestras (piedra y oro de gui_textures.py):
- inventory.png (inventario), generic_54.png (cofres y TODOS los menus de DeluxeMenus), creativo,
  botones/widgets, casilleros sueltos y libro de recetas.
Los titulos de las ventanas reemplazadas se ocultan (el pack los dibuja en el arte): lang-ocultar.json, que el
armado del FINAL suma a nuestros lang es_ar/es_es/es_mx/en_us.

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
VENTANAS = ('anvil', 'beacon', 'blast_furnace', 'brewing_stand', 'cartography_table', 'crafter', 'crafting_table',
            'dispenser', 'enchanting_table', 'furnace', 'grindstone', 'hopper', 'horse', 'loom', 'nautilus',
            'shulker_box', 'smithing', 'smoker', 'stonecutter', 'villager')
# Sprites propios de cada ventana (flechas, botones, barras). bundle, creative_inventory y slot quedan nuestros.
SPRITES = ('anvil', 'beacon', 'blast_furnace', 'brewing_stand', 'cartography_table', 'crafter', 'enchanting_table',
           'furnace', 'grindstone', 'horse', 'loom', 'smithing', 'smoker', 'stonecutter', 'villager')
OCULTAR = ('container.crafting', 'container.crafter', 'container.furnace', 'container.blast_furnace', 'container.smoker',
           'container.enchant', 'container.repair', 'container.brewing', 'container.beacon', 'container.hopper',
           'container.dispenser', 'container.dropper', 'container.shulkerBox', 'container.loom', 'container.grindstone_title',
           'container.cartography_table', 'container.stonecutter', 'container.upgrade', 'merchant.trades',
           'block.minecraft.beacon.primary', 'block.minecraft.beacon.secondary')


def elegidos(names):
    out = []
    for n in names:
        if not n.endswith('.png'):
            continue
        if n.startswith(GUI + 'container/') and n.count('/') == 5 and n[len(GUI + 'container/'):-4] in VENTANAS:
            out.append(n)
        elif n.startswith(GUI + 'sprites/container/') and n.split('/')[6] in SPRITES and n.count('/') >= 7:
            out.append(n)
    return sorted(out)


def generate():
    z = zipfile.ZipFile(SRC)
    files = elegidos(z.namelist())
    for n in files:
        d = OUT / n; d.parent.mkdir(parents=True, exist_ok=True); d.write_bytes(z.read(n))
    (OUT / 'lang-ocultar.json').write_text(json.dumps({k: '' for k in OCULTAR}, indent=1), encoding='utf-8')
    return OUT, len(files)


if __name__ == '__main__':
    print(generate())
