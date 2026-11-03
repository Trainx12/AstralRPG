"""Arte de inventario 16/32px. Originales de ImageGen en art/items.

La capa se aplica al final del resource pack para que los generadores antiguos
de recolores no reemplacen estas texturas al reconstruir.
"""
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ART = HERE / 'pack-source' / 'art' / 'items'
DETAIL_ART = ART.parent / 'chainsaws'
DETAIL_IDS = [f'motosierra_{t}' for t in ('basica', 'avanzada', 'industrial', 'infernal', 'astral')] + ['gancho']
IDS = (
    [f'motosierra_{t}' for t in ('basica', 'avanzada', 'industrial', 'infernal', 'astral')]
    + [f'talisman_{t}_{lv}' for t in ('vida', 'furia', 'viento', 'roca') for lv in (1, 2, 3)]
    + ['gancho', 'chispa_astral', 'alma_corrupta', 'madera_estelar', 'palo_reforzado',
       'fragmento_cristal', 'fragmento_umbrio', 'gema_umbria_fragmentada', 'fragmento_astral',
       'fragmento_marea', 'fragmento_pantano', 'fragmento_arena', 'fragmento_hielo', 'fragmento_fuego']
)


def sprite(iid):
    """Talismanes nativos 16px; el resto del rediseño conserva sus 32px."""
    if iid in DETAIL_IDS:
        return detailed_frames(iid)[0]
    im = Image.open(ART / f'{iid}.png').convert('RGBA')
    if iid.startswith('talisman_'):
        # El arte ya se pide sobre una cuadrícula lógica 16x16; conservar el
        # lienzo completo para no desplazar esa cuadrícula al recortar.
        im = im.resize((16, 16), Image.Resampling.NEAREST)
        alpha = im.getchannel('A').point(lambda a: 255 if a >= 160 else 0)
        im = im.convert('RGB').quantize(colors=8, dither=Image.Dither.NONE).convert('RGBA')
        im.putalpha(alpha)
        return im
    box = im.getbbox()
    if not box:
        raise ValueError(f'Textura vacia: {iid}')
    im = im.crop(box)
    im.thumbnail((28, 28), Image.Resampling.NEAREST)
    out = Image.new('RGBA', (32, 32))
    out.paste(im, ((32 - im.width) // 2, (32 - im.height) // 2))
    # Eliminar el halo semitransparente al reducir: Minecraft usa recorte de alfa.
    out.putalpha(out.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    return out


def detailed_frames(iid):
    """Limita el retoque de ImageGen al sombreado interior del sprite original.

    El contorno, la paleta y todos los cuadros originales quedan fijados.
    Solo se transfiere la variacion de luz generada, con un limite de 20/255.
    """
    original = Image.open(DETAIL_ART / f'{iid}-original.png').convert('RGBA')
    detail = Image.open(DETAIL_ART / f'{iid}-detail.png').convert('RGBA')
    detail = detail.resize((32, 32), Image.Resampling.NEAREST)
    first = original.crop((0, 0, original.width, original.width)).resize((32, 32), Image.Resampling.NEAREST)
    offsets = []
    for base, edited in zip(first.getdata(), detail.getdata()):
        if not base[3] or edited[3] < 128:
            offsets.append(0)
            continue
        diff = sum(edited[:3]) / 3 - sum(base[:3]) / 3
        offsets.append(round(max(-20, min(20, diff)) / 4) * 4)
    frames = []
    for y in range(0, original.height, original.width):
        frame = original.crop((0, y, original.width, y + original.width)).resize((32, 32), Image.Resampling.NEAREST)
        frame.putdata([tuple(max(0, min(255, channel + delta)) for channel in pixel[:3]) + (pixel[3],)
                       if pixel[3] else (0, 0, 0, 0)
                       for pixel, delta in zip(frame.getdata(), offsets)])
        frames.append(frame)
    return frames


def assets():
    files = {}
    for iid in IDS:
        frames = detailed_frames(iid) if iid in DETAIL_IDS else [sprite(iid)]
        size = frames[0].width
        im = Image.new('RGBA', (size, size * len(frames)))
        for n, frame in enumerate(frames):
            im.paste(frame, (0, n * size))
        buf = io.BytesIO()
        im.save(buf, 'PNG')
        files[f'assets/astral/textures/item/redesign/{iid}.png'] = buf.getvalue()
        if len(frames) > 1:
            files[f'assets/astral/textures/item/redesign/{iid}.png.mcmeta'] = json.dumps({
                'animation': {'frametime': 3, 'interpolate': False},
            }).encode()
        parent = 'handheld' if iid.startswith('motosierra_') or iid == 'gancho' else 'generated'
        files[f'assets/astral/models/item/{iid}.json'] = json.dumps({
            'parent': f'minecraft:item/{parent}',
            'textures': {'layer0': f'astral:item/redesign/{iid}'},
        }).encode()
        files[f'assets/astral/items/{iid}.json'] = json.dumps({
            'model': {'type': 'minecraft:model', 'model': f'astral:item/{iid}'},
        }).encode()
    return files


def preview():
    out = Image.new('RGB', (1000, 6 * 160 + 55), '#191b28')
    d = ImageDraw.Draw(out)
    d.text((20, 15), 'ASTRAL RPG / TALISMANES 16 PX / OTROS ITEMS 32 PX', fill='#e3c68a')
    ordered = DETAIL_IDS + [iid for iid in IDS if iid not in DETAIL_IDS]
    for n, iid in enumerate(ordered):
        x, y = (n % 6) * 166 + 8, (n // 6) * 160 + 48
        d.rectangle((x, y, x + 156, y + 152), fill='#292b38', outline='#575266')
        im = sprite(iid).resize((128, 128), Image.Resampling.NEAREST)
        out.paste(im, (x + 14, y + 4), im)
        label = iid.replace('motosierra_', 'sierra_').replace('talisman_', 'tal_')
        d.text((x + 5, y + 136), label, fill='#e2deef')
    path = HERE.parent / 'build' / 'Items-redesign-preview.png'
    path.parent.mkdir(exist_ok=True)
    out.save(path)
    print(path)


def preview_talismans():
    """Muestra la cuadrícula real, ampliada x8 y también a tamaño nativo."""
    out = Image.new('RGB', (550, 824), '#191b28')
    d = ImageDraw.Draw(out)
    d.text((16, 14), 'TALISMANES / 16 x 16 / MAXIMO 8 COLORES', fill='#e3c68a')
    d.text((16, 32), 'Ampliados x8. Icono pequeno: tamano nativo.', fill='#c5c7d4')
    export = HERE.parent / 'build' / 'talismans-16px'
    export.mkdir(exist_ok=True)
    for row, kind in enumerate(('vida', 'furia', 'viento', 'roca')):
        for col, tier in enumerate((1, 2, 3)):
            iid = f'talisman_{kind}_{tier}'
            im = sprite(iid)
            im.save(export / f'{iid}.png')
            x, y = 10 + col * 180, 58 + row * 190
            d.rectangle((x, y, x + 169, y + 179), fill='#292b38', outline='#575266')
            large = im.resize((128, 128), Image.Resampling.NEAREST)
            out.paste(large, (x + 21, y + 8), large)
            d.text((x + 10, y + 151), f'{kind.upper()} {"I" * tier}', fill='#e2deef')
            d.rectangle((x + 137, y + 146, x + 162, y + 171), fill='#35332d', outline='#746b56')
            out.paste(im, (x + 142, y + 151), im)
    path = HERE.parent / 'build' / 'Talismans-16px-preview.png'
    out.save(path)
    with zipfile.ZipFile(export.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for png in sorted(export.glob('*.png')):
            z.write(png, png.name)
    print(path)


if __name__ == '__main__':
    preview()
    preview_talismans()
