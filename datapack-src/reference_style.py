"""Sprites de la lamina facilitada por el usuario, sin los bloques de muestra.

La referencia tiene pixeles ampliados exactamente 10x. Se recuperan los texeles
originales por vecino mas cercano y se quita solo el fondo gris uniforme.
"""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / 'pack-source/ref/style-reference.png'


def sheet():
    im = Image.open(REFERENCE).convert('RGBA')
    if im.size != (2240, 2340):
        raise ValueError('La referencia debe conservar sus dimensiones originales')
    im = im.resize((224, 234), Image.Resampling.NEAREST)
    bg = im.getpixel((0, 0))
    im.putdata([(0, 0, 0, 0) if p == bg else p for p in im.getdata()])
    return im


def hud():
    im = sheet()
    out = {}
    prefix = 'sprites/hud/'

    def cut(x, y):
        return im.crop((x, y, x + 9, y + 9))

    def put(name, image):
        out[prefix + name + '.png'] = image

    def half(image, right=False):
        image = image.copy()
        ImageDraw.Draw(image).rectangle((0 if right else 5, 0, 3 if right else 8, 8), fill=(0, 0, 0, 0))
        return image

    variants = {'': 25, 'withered_': 66, 'poisoned_': 92, 'frozen_': 118, 'absorbing_': 144}
    for variant, y in variants.items():
        for hardcore in ('', 'hardcore_'):
            full = cut(17 if not variant else 124, y if not hardcore or not variant else y - 13)
            for part, icon in [('full', full), ('half', half(full))]:
                for blink in ('', '_blinking'):
                    sprite = icon.copy()
                    if blink:
                        pixels = sprite.load()
                        for j in range(9):
                            for i in range(9):
                                r, g, b, a = pixels[i, j]
                                if a:
                                    pixels[i, j] = (min(255, r + 35), min(255, g + 35), min(255, b + 35), a)
                    put(f'heart/{variant}{hardcore}{part}{blink}', sprite)
    empty = cut(89, 25)
    for hardcore in ('', '_hardcore'):
        for blink in ('', '_blinking'):
            put(f'heart/container{hardcore}{blink}', empty.copy())
    for part in ('container', 'full', 'half'):
        icon = empty.copy() if part == 'container' else cut(124, 144)
        put('heart/vehicle_' + part, half(icon) if part == 'half' else icon)
    for part, x in [('full', 17), ('half', 73), ('empty', 89)]:
        put('armor_' + part, cut(x, 15))
    for hunger in ('', '_hunger'):
        full = cut(138, 24) if not hunger else cut(140, 41)
        put('food_full' + hunger, full)
        put('food_half' + hunger, half(full, right=True))
        put('food_empty' + hunger, cut(122, 24) if not hunger else cut(124, 41))
    put('air', cut(147, 14))
    # Las dos gotas oscuras de la referencia indican aire agotado.
    put('air_empty', cut(120, 14))
    put('air_bursting', cut(137, 14))
    return out


def item_sprites():
    im = sheet()
    out = {}
    for col, material in enumerate(('leather', 'chainmail', 'iron', 'golden', 'diamond', 'netherite')):
        for row, part in enumerate(('helmet', 'chestplate', 'leggings', 'boots')):
            out[f'{material}_{part}'] = im.crop((16 + col * 16, 102 + row * 16, 32 + col * 16, 118 + row * 16))
    for material, x, y in [('wooden', 31, 175), ('stone', 31, 191), ('iron', 31, 207),
                           ('golden', 112, 175), ('diamond', 112, 191), ('netherite', 112, 207)]:
        for col, tool in enumerate(('sword', 'axe', 'pickaxe', 'shovel', 'hoe')):
            out[f'{material}_{tool}'] = im.crop((x + col * 16, y, x + (col + 1) * 16, y + 16))
    return out


def preview(path, vanilla=None):
    sprites = hud()
    canvas = Image.new('RGBA', (1040, 720), '#24251f')
    d = ImageDraw.Draw(canvas)
    d.text((32, 20), 'ASTRAL RPG / REFERENCIA APLICADA - HUD E ITEMS VANILLA', fill='#f8d178')

    def paste(icon, x, y, scale=4):
        canvas.alpha_composite(icon.resize((icon.width * scale, icon.height * scale), Image.Resampling.NEAREST), (x, y))

    for row, names in enumerate([('armor_empty', 'armor_full'), ('heart/container', 'heart/full'),
                                 ('food_empty', 'food_full'), ('air_empty', 'air')]):
        for i in range(10):
            paste(sprites['sprites/hud/' + names[0] + '.png'], 50 + i * 32, 60 + row * 44)
            if i < 8:
                paste(sprites['sprites/hud/' + names[1] + '.png'], 50 + i * 32, 60 + row * 44)
    if vanilla:
        paste(vanilla['hotbar'], 50, 250)
        paste(vanilla['selection'], 48, 246)
        d.text((50, 344), 'Barra inferior y experiencia: Minecraft vanilla', fill='#ead8aa')
    for index, (name, icon) in enumerate(item_sprites().items()):
        col, row = index % 12, index // 12
        paste(icon, 30 + col * 84, 385 + row * 64, scale=3)
    canvas.convert('RGB').save(path)


def menu_preview(path):
    from escape_menu import preview as escape_preview
    escape_preview(path)


def items_preview(path):
    from PIL import ImageFont
    icons = item_sprites()
    canvas = Image.new('RGBA', (1400, 1030), (141, 144, 151, 255))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=25)
    font = ImageFont.load_default(size=16)
    draw.text((30, 25), 'ICONOS EXACTOS DE LA REFERENCIA', font=title, fill='#191c25')
    materials = [('leather', 'Cuero'), ('chainmail', 'Malla'), ('iron', 'Hierro'),
                 ('golden', 'Oro'), ('diamond', 'Diamante'), ('netherite', 'Netherita')]
    for col, (material, label) in enumerate(materials):
        draw.text((30 + col * 112, 100), label, font=font, fill='#191c25')
        for row, part in enumerate(('helmet', 'chestplate', 'leggings', 'boots')):
            icon = icons[f'{material}_{part}']
            canvas.alpha_composite(icon.resize((96, 96), Image.Resampling.NEAREST), (20 + col * 112, 140 + row * 130))
    for row, (material, label) in enumerate([('wooden', 'Madera'), ('stone', 'Piedra'), ('iron', 'Hierro'),
                                            ('golden', 'Oro'), ('diamond', 'Diamante'), ('netherite', 'Netherita')]):
        draw.text((760, 110 + row * 130), label, font=font, fill='#191c25')
        for col, tool in enumerate(('sword', 'axe', 'pickaxe', 'shovel', 'hoe')):
            icon = icons[f'{material}_{tool}']
            canvas.alpha_composite(icon.resize((96, 96), Image.Resampling.NEAREST), (750 + col * 124, 140 + row * 130))
    draw.text((35, 760), '24 armaduras + 30 armas y herramientas', font=title, fill='#191c25')
    draw.text((35, 805), 'Sin reinterpretar el dibujo ni suavizar los pixeles.', font=font, fill='#191c25')
    draw.text((35, 840), 'El fondo gris se retira en los PNG del pack.', font=font, fill='#191c25')
    canvas.convert('RGB').save(path)


if __name__ == '__main__':
    import argparse
    import io
    import zipfile
    parser = argparse.ArgumentParser()
    parser.add_argument('--client-jar', required=True)
    args = parser.parse_args()
    with zipfile.ZipFile(args.client_jar) as client:
        vanilla = {name: Image.open(io.BytesIO(client.read('assets/minecraft/textures/gui/sprites/hud/' + filename))).convert('RGBA')
                   for name, filename in [('hotbar', 'hotbar.png'), ('selection', 'hotbar_selection.png')]}
    output = HERE.parent / 'build'
    preview(output / 'HUD-preview.png', vanilla)
    menu_preview(output / 'Menu-style-preview.png')
    items_preview(output / 'Items-reference-preview.png')
