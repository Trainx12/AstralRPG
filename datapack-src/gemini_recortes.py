"""Recorta las hojas de Gemini con fondo magenta: quita el magenta y separa cada pieza.

Uso: python gemini_recortes.py <hoja.png> <prefijo> nombre1 nombre2 ...
Guarda pack-source/ref/gemini/<prefijo>_<nombre>.png (piezas en orden de lectura: filas de arriba a abajo,
de izquierda a derecha). Con un solo nombre guarda la hoja entera sin magenta (marcos).
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'pack-source/ref/gemini'


def sin_magenta(im):
    """Alfa 0 donde el pixel es magenta (con tolerancia y borde suavizado de 1 px)."""
    im = im.convert('RGBA')
    px = im.load(); w, h = im.size
    mask = Image.new('L', im.size, 255); m = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if r > 150 and b > 150 and g < 110 and abs(r - b) < 90:
                m[x, y] = 0
    # Quita el halo rosado: erosiona 1 px la mascara.
    mask = mask.filter(ImageFilter.MinFilter(3))
    im.putalpha(mask)
    return im


def piezas(im, minimo=2500):
    """Cajas de las piezas opacas (componentes por filas/columnas de alfa)."""
    alpha = im.getchannel('A').point(lambda v: 255 if v > 0 else 0)
    small = alpha.resize((alpha.width // 4, alpha.height // 4), Image.Resampling.BOX).point(lambda v: 255 if v > 40 else 0)
    w, h = small.size; data = small.load(); seen = set(); boxes = []
    for y in range(h):
        for x in range(w):
            if data[x, y] and (x, y) not in seen:
                stack = [(x, y)]; seen.add((x, y)); x0 = x1 = x; y0 = y1 = y; n = 0
                while stack:
                    cx, cy = stack.pop(); n += 1
                    x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h and data[nx, ny] and (nx, ny) not in seen:
                            seen.add((nx, ny)); stack.append((nx, ny))
                if n * 16 >= minimo:
                    boxes.append((x0 * 4, y0 * 4, (x1 + 1) * 4, (y1 + 1) * 4))
    # Orden de lectura: agrupar por fila con tolerancia de un tercio de la altura media.
    if not boxes:
        return []
    mean_h = sum(b[3] - b[1] for b in boxes) / len(boxes)
    boxes.sort(key=lambda b: (round(((b[1] + b[3]) / 2) / (mean_h * 0.9)), b[0]))
    return boxes


def recortar(sheet, prefix, names):
    im = sin_magenta(Image.open(sheet))
    OUT.mkdir(parents=True, exist_ok=True)
    if len(names) == 1:
        out = OUT / f'{prefix}_{names[0]}.png'; im.crop(im.getbbox()).save(out); return [out]
    boxes = piezas(im)
    if len(boxes) != len(names):
        raise SystemExit(f'Se esperaban {len(names)} piezas y hay {len(boxes)}: {boxes}')
    outs = []
    for name, box in zip(names, boxes):
        piece = im.crop(box); piece = piece.crop(piece.getbbox())
        out = OUT / f'{prefix}_{name}.png'; piece.save(out); outs.append(out)
    return outs


if __name__ == '__main__':
    for p in recortar(sys.argv[1], sys.argv[2], sys.argv[3:]):
        print(p.name, Image.open(p).size)
