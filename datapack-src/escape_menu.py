"""Arte ilustrado del menu de pausa, con zonas de clic vanilla.

Los botones normales usan el marco de la referencia. Los dos botones anchos
usan glifos bitmap para poder dibujar los personajes y el pergamino fuera del
rectangulo del boton, conservando las acciones originales de Minecraft.
"""
import io
import json
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw

ROOT = Path(__file__).resolve().parent / 'pack-source'


def art():
    return Image.open(ROOT / 'ref/escape-art.png').convert('RGBA').resize((1280, 1280), Image.Resampling.NEAREST)


def text(image, caption, center, color=(255, 249, 209, 255)):
    font = Image.open(ROOT / 'vanilla-base/font/ascii.png').convert('RGBA')
    chars = json.loads((ROOT / 'vanilla-base/font/ascii.json').read_text(encoding='utf-8'))['chars']
    glyphs = {}
    for row, line in enumerate(chars):
        for col, char in enumerate(line):
            glyph = font.crop((col * 8, row * 8, col * 8 + 8, row * 8 + 8))
            box = glyph.getbbox()
            glyphs[char] = (glyph, box[2] if box else 3)
    width = sum(glyphs.get(char, glyphs['?'])[1] + 1 for char in caption) - 1
    x, y = round(center[0] - width / 2), center[1]
    for char in caption:
        glyph, advance = glyphs.get(char, glyphs['?'])
        alpha = glyph.getchannel('A')
        shadow = Image.new('RGBA', (8, 8), '#51331d')
        shadow.putalpha(alpha)
        image.alpha_composite(shadow, (x + 1, y + 1))
        foreground = Image.new('RGBA', (8, 8), color)
        foreground.putalpha(alpha)
        image.alpha_composite(foreground, (x, y))
        x += advance + 1


def button(highlighted=False, disabled=False, width=200):
    source = art().crop((80, 276, 625, 385)).resize((100, 20), Image.Resampling.NEAREST)
    out = Image.new('RGBA', (width, 20))
    # Conservar los adornos laterales, sin estirar las gemas ni las esquinas.
    out.alpha_composite(source.crop((0, 0, 21, 20)), (0, 0))
    out.alpha_composite(source.crop((79, 0, 100, 20)), (width - 21, 0))
    center = source.crop((45, 0, 55, 20))
    for x in range(21, width - 21, 10):
        tile = center.crop((0, 0, min(10, width - 21 - x), 20))
        out.alpha_composite(tile, (x, 0))
    # Dejar espacio a nombres largos como Guia AstralRPG en botones de 98 px.
    # Las gemas quedan junto al marco, fuera del area del rotulo.
    for x in (10, width - 18):
        out.alpha_composite(source.crop((45, 6, 53, 14)), (x, 6))
    gem = source.crop((11, 6, 18, 14))
    out.alpha_composite(gem, (3, 6))
    out.alpha_composite(gem, (width - 10, 6))
    if disabled:
        out = ImageEnhance.Brightness(out).enhance(.55)
    elif highlighted:
        out = ImageEnhance.Brightness(out).enhance(1.15)
        ImageDraw.Draw(out).rectangle((0, 0, width - 1, 19), outline='#fff4aa')
    return out


def wide_button(caption, footer=False, english=False):
    source = art()
    if not footer:
        out = source.crop((70, 40, 1180, 270)).resize((220, 46), Image.Resampling.NEAREST)
        text(out, caption, (110, 30))
        return out
    out = Image.new('RGBA', (220, 90))
    # No arrastrar fragmentos de la fila anterior en el recorte. Conservar
    # solamente la enredadera y el personaje que sobresalen hacia arriba.
    clean = ImageDraw.Draw(source)
    for box in ((40, 590, 249, 632), (331, 590, 1025, 632), (1201, 590, 1230, 632)):
        clean.rectangle(box, fill=(0, 0, 0, 0))
    top = source.crop((40, 590, 1230, 800)).resize((220, 40), Image.Resampling.NEAREST)
    panel = source.crop((15, 790, 1250, 1225)).resize((220, 50), Image.Resampling.NEAREST)
    out.alpha_composite(top, (0, 0))
    out.alpha_composite(panel, (0, 40))
    text(out, caption, (110, 22))
    text(out, 'ASTRALRPG', (110, 51))
    text(out, 'YOUR NEXT ADVENTURE AWAITS' if english else 'TU PROXIMA AVENTURA TE ESPERA', (110, 64))
    return out


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


def assets():
    files = {}
    providers = []
    entries = [('return_es', '\ue410', 'VOLVER AL JUEGO', False, False),
               ('disconnect_es', '\ue411', 'DESCONECTARSE', True, False),
               ('return_en', '\ue412', 'BACK TO GAME', False, True),
               ('disconnect_en', '\ue413', 'DISCONNECT', True, True)]
    for name, char, caption, footer, english in entries:
        image = wide_button(caption, footer, english)
        files[f'assets/astral/textures/font/escape/{name}.png'] = png(image)
        providers.append({'type': 'bitmap', 'file': f'astral:font/escape/{name}.png',
                          'height': image.height, 'ascent': 27 if footer else 37, 'chars': [char]})
    # Mantener los proveedores vanilla, incluyendo fuente unicode y espacio.
    # El ancho logico queda dentro del boton para que Minecraft no active el
    # recorte/desplazamiento de textos largos. El dibujo puede sobresalir.
    providers += [{'type': 'space', 'advances': {'\ue414': -16}},
                  {'type': 'reference', 'id': 'minecraft:include/space'},
                  {'type': 'reference', 'id': 'minecraft:include/default', 'filter': {'uniform': False}},
                  {'type': 'reference', 'id': 'minecraft:include/unifont'}]
    files['assets/minecraft/font/default.json'] = json.dumps({'providers': providers}, ensure_ascii=False).encode('utf-8')
    for locale in ('es_es', 'es_mx', 'es_ar', 'en_us'):
        english = locale == 'en_us'
        translations = {'menu.returnToGame': '\ue414' + ('\ue412' if english else '\ue410') + '\ue414',
                        'menu.disconnect': '\ue414' + ('\ue413' if english else '\ue411') + '\ue414'}
        files[f'assets/minecraft/lang/{locale}.json'] = json.dumps(translations, ensure_ascii=False).encode('utf-8')
    for state in ('', '_highlighted', '_disabled'):
        image = button(state == '_highlighted', state == '_disabled')
        path = f'assets/minecraft/textures/gui/sprites/widget/button{state}.png'
        files[path] = png(image)
        files[path + '.mcmeta'] = json.dumps({'gui': {'scaling': {'type': 'nine_slice', 'width': 200, 'height': 20,
            'border': {'left': 21, 'right': 21, 'top': 3, 'bottom': 3}}}}).encode('utf-8')
    return files


def preview(path):
    """Simulacion de los sprites a escala GUI 3x; no es una captura de Minecraft."""
    canvas = Image.new('RGBA', (330, 300), '#242720')
    # En Minecraft las filas de botones se distancian 24 unidades.
    canvas.alpha_composite(wide_button('VOLVER AL JUEGO'), (55, 8))
    labels = [('Progresos', 'Estadisticas'), ('Danos tu opinion', 'Guia AstralRPG'), ('Opciones...', 'Denunciar jugador')]
    for row, pair in enumerate(labels):
        for col, caption in enumerate(pair):
            sprite = button(width=98)
            text(sprite, caption, (49, 6), color=(255, 85, 255, 255) if caption == 'Guia AstralRPG' else (255, 249, 209, 255))
            canvas.alpha_composite(sprite, (65 + col * 102, 56 + row * 24))
    canvas.alpha_composite(wide_button('DESCONECTARSE', True), (55, 114))
    text(canvas, 'MENU DE PAUSA / ASTRALRPG', (165, 245))
    text(canvas, 'VISTA DE TEXTURAS - NO CAPTURA', (165, 262))
    canvas.resize((990, 900), Image.Resampling.NEAREST).convert('RGB').save(path)
