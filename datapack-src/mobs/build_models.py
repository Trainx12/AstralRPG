# -*- coding: utf-8 -*-
"""Exporta las criaturas a ../../build/models/*.bbmodel y arma una vista previa (frente y costado)."""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creatures  # noqa: E402
from bbmodel import save  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "build", "models")


def preview(model, img, scale=4):
    data = model.export()[0]
    views = []
    for face, axis_u, axis_depth, flip in (("north", 0, 2, True), ("east", 2, 0, False)):
        els = data["elements"]
        xs = [v for e in els for v in (e["from"][axis_u], e["to"][axis_u])]
        ys = [v for e in els for v in (e["from"][1], e["to"][1])]
        w = int((max(xs) - min(xs) + 4) * scale)
        h = int((max(ys) - min(ys) + 4) * scale)
        canvas = Image.new("RGBA", (max(w, 8), max(h, 8)), (50, 50, 60, 255))
        order = sorted(els, key=lambda e: (-min(e["from"][axis_depth], e["to"][axis_depth])) if face == "north"
                       else max(e["from"][axis_depth], e["to"][axis_depth]))
        for e in order:
            u0, u1 = sorted((e["from"][axis_u], e["to"][axis_u]))
            y0, y1 = sorted((e["from"][1], e["to"][1]))
            uv = e["faces"][face]["uv"]
            tex = img.crop(tuple(uv))
            if flip:
                tex = tex.transpose(Image.FLIP_LEFT_RIGHT)
            x0 = (u0 - min(xs) + 2) * scale if not flip else (max(xs) - u1 + 2) * scale
            ww, hh = max(1, int((u1 - u0) * scale)), max(1, int((y1 - y0) * scale))
            tex = tex.resize((ww, hh), Image.NEAREST)
            canvas.paste(tex, (int(x0), int((max(ys) - y1 + 2) * scale)), tex)
        views.append(canvas)
    out = Image.new("RGBA", (sum(v.size[0] for v in views) + 30, max(v.size[1] for v in views) + 20), (40, 40, 48, 255))
    x = 10
    for v in views:
        out.paste(v, (x, 15))
        x += v.size[0] + 10
    ImageDraw.Draw(out).text((10, 2), model.name, fill=(255, 255, 255))
    return out


def main(preview_path=None):
    os.makedirs(OUT, exist_ok=True)
    previews = []
    for fn in creatures.ALL:
        m = fn()
        img = save(m, os.path.join(OUT, f"{m.name}.bbmodel"))
        previews.append(preview(m, img))
    print(len(previews), "modelos exportados a", os.path.abspath(OUT))
    if preview_path:
        cols = 4
        rows = [previews[i:i + cols] for i in range(0, len(previews), cols)]
        W = max(sum(p.size[0] for p in r) for r in rows)
        H = sum(max(p.size[1] for p in r) for r in rows)
        sheet = Image.new("RGBA", (W, H), (30, 30, 36, 255))
        y = 0
        for r in rows:
            x = 0
            for p in r:
                sheet.paste(p, (x, y))
                x += p.size[0]
            y += max(p.size[1] for p in r)
        sheet.save(preview_path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
