"""Armaduras vanilla propias: placas, capuchas y cinturones sin mods.

Usan el atlas vanilla 64x32 y su geometria original. No incluyen modelos ni
archivos de Armored Legacy: la foto sirve de direccion visual.
"""
from PIL import Image, ImageDraw
import random

PALETTES = {
    'leather': ('#47351e', '#816032', '#aa8241', '#28251b'),
    'copper': ('#65392e', '#b46e4b', '#e19a65', '#3d3228'),
    'chainmail': ('#515457', '#a3a8a4', '#dfdfc9', '#393b39'),
    'iron': ('#555b61', '#abb6b9', '#e3e9e4', '#30363a'),
    'gold': ('#8b5915', '#d5a52d', '#ffe177', '#563424'),
    'diamond': ('#086368', '#1bbdb2', '#7eede2', '#173c40'),
    'netherite': ('#282329', '#4e454b', '#77666a', '#211c23'),
}
HEAD = [(8, 0, 16, 8), (16, 0, 24, 8), (0, 8, 8, 16), (8, 8, 16, 16), (16, 8, 24, 16), (24, 8, 32, 16)]
TORSO = [(20, 16, 28, 20), (28, 16, 36, 20), (16, 20, 20, 32), (20, 20, 28, 32), (28, 20, 32, 32), (32, 20, 40, 32)]
ARM = [(44, 16, 48, 20), (48, 16, 52, 20), (40, 20, 44, 32), (44, 20, 48, 32), (48, 20, 52, 32), (52, 20, 56, 32)]
LEG = [(4, 16, 8, 20), (8, 16, 12, 20), (0, 20, 4, 32), (4, 20, 8, 32), (8, 20, 12, 32), (12, 20, 16, 32)]


def equipment():
    out = {}
    for material, (shadow, base, shine, cloth) in PALETTES.items():
        for layer in ('humanoid', 'humanoid_leggings'):
            im = Image.new('RGBA', (64, 32))
            d = ImageDraw.Draw(im)

            def panel(box, chain=False):
                x0, y0, x1, y1 = box
                d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=base)
                d.line((x0, y0, x1 - 1, y0), fill=shine)
                d.line((x0, y0 + 1, x0, y1 - 1), fill=shine)
                d.line((x1 - 1, y0, x1 - 1, y1 - 1), fill=shadow)
                d.line((x0, y1 - 1, x1 - 1, y1 - 1), fill=shadow)
                # Facetas anchas y reflejos cortados, a resolucion de Minecraft.
                for y in range(y0 + 1, y1 - 1):
                    for x in range(x0 + 1, x1 - 1):
                        color = Image.new('RGB', (1, 1), base).getpixel((0, 0))
                        delta = random.Random(x * 619 + y * 1709).randint(-6, 6)
                        d.point((x, y), fill=tuple(max(0, min(255, c + delta)) for c in color))
                if x1 - x0 >= 8:
                    d.line((x0 + 2, y0 + 1, x0 + 2, y1 - 3), fill=shine)
                    d.point((x1 - 3, y0 + 2), fill=shine)
                if chain:
                    for y in range(y0 + 1, y1 - 1):
                        for x in range(x0 + 1, x1 - 1):
                            d.point((x, y), fill=shine if (x + y) % 2 else shadow)

            for box in (HEAD + TORSO + ARM + LEG if layer == 'humanoid' else TORSO + LEG):
                panel(box, material == 'chainmail')
            if layer == 'humanoid':
                # Casco con abertura real (la cara del jugador se ve debajo).
                d.rectangle((9, 11, 14, 14), fill=(0, 0, 0, 0))
                d.line((9, 10, 14, 10), fill=shadow)
                if material == 'netherite':
                    d.rectangle((9, 12, 14, 14), fill=shadow)
                    d.line((9, 11, 14, 11), fill=cloth)
                    d.point((12, 12), fill=shine)
                if material == 'gold':
                    # Corona pintada: almenas de oro, banda y gema roja.
                    for x0 in (0, 8, 16, 24):
                        d.rectangle((x0, 11, x0 + 7, 15), fill=(0, 0, 0, 0))
                        d.line((x0, 10, x0 + 7, 10), fill=shadow)
                        for x in range(x0 + 1, x0 + 7, 2):
                            d.point((x, 8), fill=shine)
                    d.point((11, 9), fill='#bf2f28')
                for x0 in (40, 44, 48, 52):
                    # Hombreras estratificadas y brazales.
                    d.line((x0, 23, x0 + 3, 23), fill=shadow)
                    d.line((x0, 24, x0 + 3, 24), fill=shine)
                    d.rectangle((x0, 26, x0 + 3, 28), fill=cloth)
                    d.line((x0, 29, x0 + 3, 29), fill=shine)
                for x0, width in ((20, 8), (32, 8)):
                    d.line((x0 + 2, 22, x0 + width - 3, 22), fill=shine)
                    d.line((x0 + 1, 25, x0 + width - 2, 25), fill=shadow)
            # Cinturon de cuero y hebilla, ambos lados del torso.
            for x0, width in ((16, 4), (20, 8), (28, 4), (32, 8)):
                d.rectangle((x0, 28, x0 + width - 1, 29), fill=cloth)
            d.rectangle((23, 28, 24, 29), fill='#d6b56a')
            d.point((23, 29), fill=shadow)
            if layer == 'humanoid':
                # Cuello, peto facetado y faldones: evitar el aspecto de cajas
                # lisas pintadas del primer intento.
                d.rectangle((23, 20, 24, 21), fill=cloth)
                d.line((20, 21, 22, 23), fill=shine)
                d.line((27, 21, 25, 23), fill=shadow)
                d.line((21, 24, 23, 25), fill=shadow)
                d.line((24, 25, 26, 24), fill=shine)
                d.line((22, 26, 25, 26), fill=shine)
                d.rectangle((20, 30, 27, 31), fill=cloth)
                d.polygon([(20, 30), (22, 30), (22, 31), (20, 31)], fill=base)
                d.polygon([(25, 30), (27, 30), (27, 31), (26, 31)], fill=shine)
                for x0 in (40, 44, 48, 52):
                    d.line((x0, 22, x0 + 3, 21), fill=shine)
                    d.line((x0, 25, x0 + 3, 25), fill=shadow)
                if material in ('gold', 'netherite', 'copper'):
                    for x0 in (40, 44, 48, 52):
                        d.rectangle((x0, 26, x0 + 3, 28), fill='#542c2d')
            for x0 in (0, 4, 8, 12):
                if layer == 'humanoid':
                    # Solo el calzado usa las piernas de esta capa.
                    d.rectangle((x0, 20, x0 + 3, 26), fill=(0, 0, 0, 0))
                    d.line((x0, 28, x0 + 3, 28), fill=shine)
                else:
                    d.line((x0, 25, x0 + 3, 25), fill=cloth)
                    d.line((x0, 26, x0 + 3, 26), fill=shine)
                    d.line((x0, 31, x0 + 3, 31), fill=cloth)
            if material == 'leather':
                # La capa base se tine con el color que el jugador elija.
                im = im.convert('LA').convert('RGBA')
                im.putdata([(min(255, round(r * 1.6)), min(255, round(g * 1.6)), min(255, round(b * 1.6)), a)
                            for r, g, b, a in im.getdata()])
            out[f'assets/minecraft/textures/entity/equipment/{layer}/{material}.png'] = im
            if material == 'leather':
                overlay = Image.new('RGBA', (64, 32))
                od = ImageDraw.Draw(overlay)
                od.rectangle((20, 28, 27, 29), fill='#5f4126')
                od.rectangle((23, 28, 24, 29), fill='#c5a260')
                out[f'assets/minecraft/textures/entity/equipment/{layer}/leather_overlay.png'] = overlay
    return out


def preview(path):
    textures = equipment()
    canvas = Image.new('RGBA', (1120, 470), '#e4d5b8')
    d = ImageDraw.Draw(canvas)
    d.text((20, 16), 'ARMADURAS PUESTAS / VISTA FRONTAL / GEOMETRIA VANILLA SIN MODS', fill='#3d2a1e')
    for i, material in enumerate(PALETTES):
        armor = textures[f'assets/minecraft/textures/entity/equipment/humanoid/{material}.png']
        pants = textures[f'assets/minecraft/textures/entity/equipment/humanoid_leggings/{material}.png']
        if material == 'leather':
            armor, pants = armor.copy(), pants.copy()
            for atlas in (armor, pants):
                atlas.putdata([(r * 160 // 255, g * 101 // 255, b * 64 // 255, a)
                               for r, g, b, a in atlas.getdata()])
        figure = Image.new('RGBA', (16, 32))
        fd = ImageDraw.Draw(figure)
        fd.rectangle((4, 0, 11, 7), fill='#a17c54')
        fd.rectangle((4, 8, 11, 19), fill='#4f493e')
        for part, atlas, xy in [(HEAD[3], armor, (4, 0)), (TORSO[3], armor, (4, 8)),
                                (ARM[3], armor, (0, 8)), (ARM[3], armor, (12, 8)),
                                (LEG[3], pants, (4, 20)), (LEG[3], pants, (8, 20)),
                                (LEG[3], armor, (4, 20)), (LEG[3], armor, (8, 20))]:
            figure.alpha_composite(atlas.crop(part), xy)
        canvas.alpha_composite(figure.resize((144, 288), Image.Resampling.NEAREST), (i * 158 + 8, 70))
        d.text((i * 158 + 25, 395), material.upper(), fill='#3d2a1e')
    canvas.convert('RGB').save(path)


def preview3d(path):
    """Render con UV reales y el volumen de armadura vanilla, sin inventar piezas."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / 'mobs'))
    from build_models import preview3d as render
    textures = equipment()
    output = Image.new('RGBA', (1200, 950), '#d4ccbd')
    draw = ImageDraw.Draw(output)
    draw.text((30, 20), 'ASTRAL RPG / ARMADURAS SIN MODS - RENDER DE LA GEOMETRIA VANILLA', fill='#3d3025')

    class Mannequin:
        def __init__(self):
            self.bones = {'root': {'origin': [0, 0, 0], 'rotation': [0, 0, 0], 'parent': None}}
            self.cubes = []
            self.elements = []

        def add(self, a, b, uv):
            self.cubes.append({'bone': 'root'})
            self.elements.append({'from': a, 'to': b, 'origin': [0, 0, 0],
                                  'faces': {face: {'uv': uv[index]} for face, index in
                                            [('north', 3), ('east', 4), ('south', 5), ('west', 2), ('up', 0), ('down', 1)]}})

        def export(self):
            return ({'elements': self.elements}, None)

    order = [('gold', 220, 70), ('diamond', 500, 70), ('netherite', 780, 70),
             ('leather', 70, 510), ('copper', 350, 510), ('chainmail', 630, 510), ('iron', 910, 510)]
    for material, x, y in order:
        atlas = Image.new('RGBA', (128, 64))
        for layer, offset in [('humanoid', 0), ('humanoid_leggings', 32)]:
            texture = textures[f'assets/minecraft/textures/entity/equipment/{layer}/{material}.png'].copy()
            if material == 'leather':
                texture.putdata([(r * 160 // 255, g * 101 // 255, b * 64 // 255, a) for r, g, b, a in texture.getdata()])
            atlas.alpha_composite(texture, (0, offset))
            if material == 'leather':
                atlas.alpha_composite(textures[f'assets/minecraft/textures/entity/equipment/{layer}/leather_overlay.png'], (0, offset))
        ad = ImageDraw.Draw(atlas)
        ad.rectangle((64, 0, 79, 15), fill='#907449')
        for j in (2, 5, 9, 13):
            ad.line((65, j, 77, j), fill='#a78a5b')
        wood = [(64, 0, 80, 16)] * 6
        m = Mannequin()
        body_parts = [((-4, 24, -4), (4, 32, 4), HEAD),
                      ((-4, 12, -2), (4, 24, 2), TORSO),
                      ((-8, 12, -2), (-4, 24, 2), ARM), ((4, 12, -2), (8, 24, 2), ARM),
                      ((-4, 0, -2), (0, 12, 2), LEG), ((0, 0, -2), (4, 12, 2), LEG)]
        m.add((-6, -1, -5), (6, 0, 5), wood)
        for a, b, _ in body_parts:
            m.add(a, b, wood)
        for index, (a, b, uv) in enumerate(body_parts):
            inflation = 1.0
            m.add(tuple(v - inflation for v in a), tuple(v + inflation for v in b), uv)
            if index >= 4:
                uv2 = [(u0, v0 + 32, u1, v1 + 32) for u0, v0, u1, v1 in uv]
                m.add(tuple(v - .5 for v in a), tuple(v + .5 for v in b), uv2)
        sprite = render(m, atlas, yaw=24, pitch=12, scale=9)
        sprite.putdata([(0, 0, 0, 0) if p == (50, 50, 60, 255) else p for p in sprite.getdata()])
        output.alpha_composite(sprite, (x, y))
        draw.text((x + 60, y + 380), material.upper(), fill='#3d3025')
    output.convert('RGB').save(path)
