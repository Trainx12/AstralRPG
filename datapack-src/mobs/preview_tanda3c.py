"""Vistas previas de la tanda 3c (maquinas de Mini juegos y NPC)."""
import sys
from pathlib import Path
from PIL import Image, ImageOps
from bbmodel import save
from build_models import preview3d as _preview3d
from preview_tanda3a import player, text, BG
import creatures_tanda3c as T

ROOT = Path(__file__).resolve().parents[2]


def preview3d(*a, **kw):
    """El render de build_models sale espejado; se da vuelta para que coincida con el juego."""
    return ImageOps.mirror(_preview3d(*a, **kw))
OUT = ROOT / 'build/previews'
ANGLES = (('Frente', 0, 8), ('Tres cuartos', 35, 18), ('Costado', 90, 8), ('Otro lado', -35, 18), ('Espalda', 180, 8))


def maquinas(scale=12):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for fn in T.MAQUINAS:
        m = fn(); tex = save(m, ROOT / 'build/models' / f'{m.name}.bbmodel')
        tr = m.name.endswith('capsulas')
        views = [preview3d(m, tex, yaw, pitch, scale, background=BG, translucent=tr) for _, yaw, pitch in ANGLES]
        p = player(); views.append(preview3d(p, p.export()[1], 0, 8, scale, background=BG))
        rows.append((m.name, views))
    W = max(sum(v.width + 24 for v in views) for _, views in rows) + 16
    H = sum(max(v.height for v in views) + 70 for _, views in rows)
    sheet = Image.new('RGBA', (W, H), BG)
    y = 0
    for name, views in rows:
        hh = max(v.height for v in views)
        text(sheet, (10, y + 8), name, 20)
        x = 10
        for (label, v) in zip([a[0] for a in ANGLES] + ['Jugador (1,8 bloques)'], views):
            text(sheet, (x, y + 36), label, 14)
            sheet.paste(v, (x, y + 60 + hh - v.height), v); x += v.width + 24
        y += hh + 70
    sheet.save(OUT / 'maquinas-minijuegos.png')
    print(OUT / 'maquinas-minijuegos.png', sheet.size)


def npcs(only=None, scale=9):
    import npc_tanda3c as N
    figures = []
    for fn in N.NPCS:
        m = fn()
        if only and not any(o in m.name for o in only):
            continue
        tex = save(m, ROOT / 'build/models' / f'{m.name}.bbmodel')
        short = m.name.replace('astral_npc_', '')
        ref = Image.open(ROOT / '.local/coordination/ref/npc' / (N.REFS[m.name] + '.png')).convert('RGBA')
        k = min(430 / ref.width, 470 / ref.height)
        ref = ref.resize((int(ref.width * k), int(ref.height * k)), Image.LANCZOS)
        views = [preview3d(m, tex, yaw, pitch, scale, background=BG) for yaw, pitch in ((0, 5), (30, 15), (-30, 15), (90, 5), (180, 5))]
        im = Image.new('RGBA', (450 + sum(v.width + 18 for v in views), max(540, max(v.height for v in views) + 70)), BG)
        text(im, (8, 10), 'Referencia (solo local)', 15); im.paste(ref, (8, 50), ref)
        x = 450
        for title, v in zip(('Frente', 'Tres cuartos', 'Otro lado', 'Costado', 'Espalda'), views):
            text(im, (x, 10), title, 15); im.paste(v, (x, 50), v); x += v.width + 18
        im.save(OUT / f'npc-{short}-comparacion.png')
        figures.append((preview3d(m, tex, 25, 12, 8, background=BG), short))
    if only:
        return
    p = player(); figures.insert(0, (preview3d(p, p.export()[1], 25, 12, 8, background=BG), 'Jugador 1,8 bloques'))
    H = max(v.height for v, _ in figures) + 50
    sheet = Image.new('RGBA', (sum(max(v.width, 150) + 20 for v, _ in figures) + 10, H), BG)
    x = 10
    for v, label in figures:
        sheet.paste(v, (x, H - 36 - v.height), v); text(sheet, (x, H - 28), label, 14); x += max(v.width, 150) + 20
    sheet.save(OUT / 'npc-todos.png')
    print(sheet.size)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'npc':
        npcs(sys.argv[2:] or None)
    else:
        maquinas(12)
