"""Arte Gemini del 21/11: tarjetas de las segundas paginas de Portales y Minas, y flechas de pagina.

Fuentes (locales, no van al repo): .local/gemini/refs-21-11/tarjetas_v1.jpg (Oceano, Mazmorra del End, Bosque)
y flechas_v1.jpg (flecha astral y flecha de mina). Salida: pack-source/ref/portales2-cards.png,
minas2-cards.png y pack-source/ref/gemini/flecha_{portales,minas}.png.
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
REFS = HERE.parent / '.local/gemini/refs-21-11'
REF = HERE / 'pack-source/ref'


def magenta(p):
    return p[0] > 200 and p[1] < 70 and p[2] > 200


def paneles(im, n):
    """Cajas de los n paneles separados por franjas magenta (columnas casi todas magenta)."""
    rgb = im.convert('RGB')
    w, h = rgb.size
    px = rgb.load()
    ys = range(h // 4, 3 * h // 4, 8)
    col = [sum(not magenta(px[x, y]) for y in ys) > len(ys) * .8 for x in range(w)]
    runs, start = [], None
    for x, ok in enumerate(col + [False]):
        if ok and start is None: start = x
        if not ok and start is not None:
            if x - start > w // 20: runs.append((start, x))
            start = None
    assert len(runs) == n, runs
    out = []
    for x0, x1 in runs:
        xm = (x0 + x1) // 2
        rows = [y for y in range(h) if not magenta(px[xm, y])]
        # margen de 6 px para no arrastrar el borde rosado del antialias
        out.append((x0 + 6, rows[0] + 6, x1 - 6, rows[-1] - 6))
    return out


def tarjetas():
    im = Image.open(REFS / 'tarjetas_v1.jpg').convert('RGBA')
    cajas = paneles(im, 3)
    pinturas = [im.crop(c).resize((180, 280), Image.Resampling.LANCZOS) for c in cajas]
    for nombre, idx in (('portales2', (0, 1)), ('minas2', (2,))):
        hoja = Image.new('RGBA', (180 * len(idx), 280))
        for i, k in enumerate(idx):
            hoja.alpha_composite(pinturas[k], (i * 180, 0))
        hoja.save(REF / f'{nombre}-cards.png')


def flechas():
    src = REFS / 'flechas_v1.jpg'
    if not src.exists():
        return
    im = Image.open(src).convert('RGBA')
    for nombre, caja in zip(('portales', 'minas'), paneles(im, 2)):
        x0, y0, x1, y1 = caja
        lado = min(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        pieza = im.crop((cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2))
        pieza.resize((64, 64), Image.Resampling.LANCZOS).save(REF / f'gemini/flecha_{nombre}.png')


if __name__ == '__main__':
    tarjetas()
    flechas()
    print('ok')
