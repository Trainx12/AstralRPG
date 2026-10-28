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
    # norte visto de frente (+X a la izquierda); este visto desde el costado (+Z a la izquierda)
    for face, axis_u, axis_depth, flip in (("north", 0, 2, True), ("east", 2, 0, True)):
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


FACE_GEOM = {
    # cara: (esquina del pixel 0,0 ; direccion u ; direccion v ; normal) con a=from, b=to
    "north": (lambda a, b: (b[0], b[1], a[2]), (-1, 0, 0), (0, -1, 0), (0, 0, -1)),
    "south": (lambda a, b: (a[0], b[1], b[2]), (1, 0, 0), (0, -1, 0), (0, 0, 1)),
    "east": (lambda a, b: (b[0], b[1], b[2]), (0, 0, -1), (0, -1, 0), (1, 0, 0)),
    "west": (lambda a, b: (a[0], b[1], a[2]), (0, 0, 1), (0, -1, 0), (-1, 0, 0)),
    "up": (lambda a, b: (a[0], b[1], a[2]), (1, 0, 0), (0, 0, 1), (0, 1, 0)),
    "down": (lambda a, b: (a[0], a[1], b[2]), (1, 0, 0), (0, 0, -1), (0, -1, 0)),
}


def preview3d(model, img, yaw=35, pitch=25, scale=4):
    """Vista 3D ortografica con z-buffer (sin numpy). yaw>0 muestra el frente y el costado +X."""
    import math
    data = model.export()[0]
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def eul(p, org, r):
        x, y, z = p[0] - org[0], p[1] - org[1], p[2] - org[2]
        if r[0]:
            c, s = math.cos(math.radians(r[0])), math.sin(math.radians(r[0]))
            y, z = y * c - z * s, y * s + z * c
        if r[1]:
            c, s = math.cos(math.radians(r[1])), math.sin(math.radians(r[1]))
            x, z = x * c + z * s, -x * s + z * c
        if r[2]:
            c, s = math.cos(math.radians(r[2])), math.sin(math.radians(r[2]))
            x, y = x * c - y * s, x * s + y * c
        return x + org[0], y + org[1], z + org[2]

    def chain(bone, p):
        while bone:
            info = model.bones[bone]
            if any(info["rotation"]):
                p = eul(p, info["origin"], info["rotation"])
            bone = info["parent"]
        return p

    def cam(p):
        x, y, z = p
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp + z * sp, -y * sp + z * cp
        return x, y, z

    faces = []
    for i, e in enumerate(data["elements"]):
        a, b = e["from"], e["to"]
        bone = model.cubes[i]["bone"]
        er = e.get("rotation")

        def T(p, bone=bone, er=er, org=e["origin"]):
            if er and any(er):
                p = eul(p, org, er)
            return cam(chain(bone, p))
        for face, (corner, du, dv, nrm) in FACE_GEOM.items():
            lu = abs(sum((b[k] - a[k]) * du[k] for k in range(3)))
            lv = abs(sum((b[k] - a[k]) * dv[k] for k in range(3)))
            if lu <= 0 or lv <= 0:
                continue
            o = corner(a, b)
            O = T(o)
            U = [q - w for q, w in zip(T(tuple(o[k] + du[k] * lu for k in range(3))), O)]
            V = [q - w for q, w in zip(T(tuple(o[k] + dv[k] * lv for k in range(3))), O)]
            N = [q - w for q, w in zip(T(tuple(o[k] + nrm[k] for k in range(3))), O)]
            if N[2] >= 0:
                continue
            faces.append((O, U, V, e["faces"][face]["uv"]))
    xs_all = [p[0] + du for (O, U, V, _) in faces for p in (O,) for du in (0, U[0], V[0], U[0] + V[0])]
    ys_all = [p[1] + dv for (O, U, V, _) in faces for p in (O,) for dv in (0, U[1], V[1], U[1] + V[1])]
    minx, maxx, miny, maxy = min(xs_all), max(xs_all), min(ys_all), max(ys_all)
    W, H = int((maxx - minx) * scale) + 8, int((maxy - miny) * scale) + 8
    zbuf = [[1e9] * W for _ in range(H)]
    out = Image.new("RGBA", (W, H), (50, 50, 60, 255))
    px = out.load()
    tex = img.load()
    for (O, U, V, uv) in faces:
        u0, v0, u1, v1 = uv
        tw, th = u1 - u0, v1 - v0
        ox, oy = (O[0] - minx) * scale + 4, (maxy - O[1]) * scale + 4
        ux, uy = U[0] * scale, -U[1] * scale
        vx, vy = V[0] * scale, -V[1] * scale
        det = ux * vy - uy * vx
        if abs(det) < 1e-6:
            continue
        xs = [ox, ox + ux, ox + vx, ox + ux + vx]
        ys = [oy, oy + uy, oy + vy, oy + uy + vy]
        for Y in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
            for X in range(max(0, int(min(xs))), min(W, int(max(xs)) + 1)):
                dx, dy = X + 0.5 - ox, Y + 0.5 - oy
                s = (dx * vy - dy * vx) / det
                t = (ux * dy - uy * dx) / det
                if not (0 <= s < 1 and 0 <= t < 1):
                    continue
                d = O[2] + s * U[2] + t * V[2]
                if d >= zbuf[Y][X]:
                    continue
                c = tex[min(u1 - 1, int(u0 + s * tw)), min(v1 - 1, int(v0 + t * th))]
                if c[3] == 0:
                    continue
                zbuf[Y][X] = d
                px[X, Y] = c
    o2 = out.copy()
    p2 = o2.load()
    for Y in range(1, H - 1):
        for X in range(1, W - 1):
            z = zbuf[Y][X]
            if z >= 1e9:
                continue
            for (nx, ny) in ((X + 1, Y), (X - 1, Y), (X, Y + 1), (X, Y - 1)):
                if zbuf[ny][nx] - z > 2.5:
                    c = p2[X, Y]
                    p2[X, Y] = (int(c[0] * .55), int(c[1] * .55), int(c[2] * .55), 255)
                    break
    return o2


def main(preview_path=None):
    os.makedirs(OUT, exist_ok=True)
    previews = []
    for fn in creatures.ALL:
        m = fn()
        img = save(m, os.path.join(OUT, f"{m.name}.bbmodel"))
        if preview_path and preview_path.endswith("3d.png"):
            only = os.environ.get("ONLY")
            if only and not any(o in m.name for o in only.split(",")):
                continue
            sc = int(os.environ.get("SC", 8 if only else 4))
            v1, v2 = preview3d(m, img, 35, 25, sc), preview3d(m, img, 215, 25, sc)
            p = Image.new("RGBA", (v1.size[0] + v2.size[0] + 10, max(v1.size[1], v2.size[1]) + 16), (40, 40, 48, 255))
            p.paste(v1, (0, 16)); p.paste(v2, (v1.size[0] + 10, 16))
            ImageDraw.Draw(p).text((4, 2), m.name, fill=(255, 255, 255))
            previews.append(p)
        else:
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
