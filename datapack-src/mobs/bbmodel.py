# -*- coding: utf-8 -*-
"""
Mini-generador de modelos de Blockbench (.bbmodel, formato 'free') para BetterModel.
Unidades: 16 = 1 bloque. El frente del modelo mira al norte (-Z).
Cada cubo se pinta con un color base, ruido suave, borde mas oscuro y 'calcos' (ojos, rayas, etc).
"""
import base64
import io
import json
import math
import random
import uuid as _uuid

from PIL import Image

FACES = ("north", "east", "south", "west", "up", "down")


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def uid(seed):
    return str(_uuid.uuid5(_uuid.NAMESPACE_URL, seed))


class Model:
    def __init__(self, name):
        self.name = name
        self.bones = {}      # nombre -> {origin, parent, rotation}
        self.order = []
        self.cubes = []      # dicts
        self.anims = {}      # nombre -> (length, loop, {bone: {channel: (x,y,z)}})

    def bone(self, name, origin, parent=None, rotation=(0, 0, 0)):
        self.bones[name] = {"origin": list(origin), "parent": parent, "rotation": list(rotation)}
        self.order.append(name)
        return name

    def cube(self, bone, frm, to, color, decals=None, shade=0.0, rotation=None, origin=None, glow=False, pat=None):
        """pat: patron de textura (fur, feather, straw, brick, scale, chitin, wrap, stone, cloth, shell, wood, membrane)."""
        self.cubes.append({"bone": bone, "from": list(frm), "to": list(to), "color": color,
                           "decals": decals or {}, "shade": shade, "rotation": rotation, "origin": origin,
                           "pat": pat})

    def rcube(self, bone, frm, to, color, decals=None, r=None, pat=None):
        """Caja con bordes redondeados: 4 cajas encimadas (3 achaflanadas + 1 que redondea la esquina).
        Mantiene el tamano total, asi los detalles pegados a la superficie siguen en su lugar."""
        a = [min(frm[k], to[k]) for k in range(3)]
        b = [max(frm[k], to[k]) for k in range(3)]
        d = [b[k] - a[k] for k in range(3)]
        if r is None:
            r = round(min(min(d) / 4, 2.5) * 2) / 2
        r = min(r, min(d) / 2 - 0.05)
        if r < 0.45:
            self.cube(bone, a, b, color, decals, pat=pat)
            return
        decals = decals or {}
        sh = int(round(r))

        def shifted(faces):
            out = {}
            for f in faces:
                out[f] = [(dx - sh, dy - sh, dw, dh, c) for (dx, dy, dw, dh, c) in decals.get(f, [])]
            return out

        for axis, faces in ((0, ("east", "west")), (1, ("up", "down")), (2, ("north", "south"))):
            lo = [a[k] + (0 if k == axis else r) for k in range(3)]
            hi = [b[k] - (0 if k == axis else r) for k in range(3)]
            self.cube(bone, lo, hi, color, shifted(faces), pat=pat)
        q = r * 0.3
        self.cube(bone, [v + q for v in a], [v - q for v in b], color, pat=pat)

    def blob(self, bone, center, radius, color, pat=None, axis=1, levels=3, decals=None, flat=None):
        """Elipsoide escalonado: varias cajas redondeadas encajadas, largas y finas adentro, cortas y anchas afuera.
        axis: eje largo de las capas (0=x, 1=y, 2=z). flat: (lado, 0..1) recorta media forma (ej. ('down', 0.3))."""
        prof = {2: [(1.0, 0.62), (0.62, 1.0)],
                3: [(1.0, 0.5), (0.8, 0.86), (0.45, 1.0)],
                4: [(1.0, 0.42), (0.88, 0.72), (0.66, 0.92), (0.36, 1.0)]}[levels]
        for i, (fa, fc) in enumerate(prof):
            lo, hi = [], []
            for k in range(3):
                f = fa if k == axis else fc
                lo.append(center[k] - radius[k] * f)
                hi.append(center[k] + radius[k] * f)
            if flat:
                side, keep = flat
                k = {"down": 1, "up": 1, "north": 2, "south": 2, "west": 0, "east": 0}[side]
                cut = center[k] + (-1 if side in ("down", "north", "west") else 1) * radius[k] * keep
                if side in ("down", "north", "west"):
                    lo[k] = max(lo[k], cut)
                else:
                    hi[k] = min(hi[k], cut)
                if hi[k] - lo[k] < 0.3:
                    continue
            self.rcube(bone, lo, hi, color, decals if i == len(prof) - 1 else None, pat=pat)

    def anim(self, name, length, channels, loop="loop"):
        self.anims[name] = (length, loop, channels)

    # ------------------------------------------------------------------ export
    def _face_size(self, c, face):
        dx = abs(c["to"][0] - c["from"][0])
        dy = abs(c["to"][1] - c["from"][1])
        dz = abs(c["to"][2] - c["from"][2])
        w, h = {"north": (dx, dy), "south": (dx, dy), "east": (dz, dy), "west": (dz, dy),
                "up": (dx, dz), "down": (dx, dz)}[face]
        return max(1, int(math.ceil(w))), max(1, int(math.ceil(h)))

    def _pack(self):
        rects = []
        for i, c in enumerate(self.cubes):
            for f in FACES:
                w, h = self._face_size(c, f)
                rects.append((h, w, i, f))
        rects.sort(key=lambda r: (-r[0], -r[1]))
        for size in (64, 128, 256, 512, 1024):
            x = y = shelf = 0
            pos = {}
            ok = True
            for (h, w, i, f) in rects:
                if w > size:
                    ok = False
                    break
                if x + w > size:
                    x, y, shelf = 0, y + shelf, 0
                if y + h > size:
                    ok = False
                    break
                pos[(i, f)] = (x, y, w, h)
                x += w
                shelf = max(shelf, h)
            if ok:
                return size, pos
        raise ValueError("modelo demasiado grande para la textura")

    def _paint(self, size, pos):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        px = img.load()
        rnd = random.Random(self.name)
        for (i, f), (x0, y0, w, h) in pos.items():
            c = self.cubes[i]
            base = hexc(c["color"])
            mult = {"up": 1.08, "down": 0.75, "north": 1.0, "south": 0.92, "east": 0.88, "west": 0.88}[f]
            pat = c.get("pat")
            side = f not in ("up", "down")
            cols = [rnd.uniform(-1, 1) for _ in range(w)]   # vetas por columna (pelaje, paja, madera)
            for yy in range(h):
                for xx in range(w):
                    n = rnd.uniform(-0.05, 0.05)
                    edge = 0.85 if (xx == 0 or yy == 0 or xx == w - 1 or yy == h - 1) and w > 2 and h > 2 else 1.0
                    grad = (1.06 - 0.14 * (yy / max(1, h - 1))) if side and h > 3 else 1.0
                    k = (mult + n) * edge * grad * pattern(pat, xx, yy, w, h, f, rnd, cols)
                    px[x0 + xx, y0 + yy] = tuple(max(0, min(255, int(v * k))) for v in base) + (255,)
            for (dx, dy, dw, dh, col) in c["decals"].get(f, []):
                if f in ("west", "south"):
                    # se espeja para que el mismo dibujo quede simetrico con la cara este / norte
                    dx = w - dx - dw
                cc = hexc(col)
                for yy in range(int(dy), int(dy + dh)):
                    for xx in range(int(dx), int(dx + dw)):
                        if 0 <= xx < w and 0 <= yy < h:
                            k = 1.0 + rnd.uniform(-0.04, 0.04)
                            px[x0 + xx, y0 + yy] = tuple(max(0, min(255, int(v * k))) for v in cc) + (255,)
        return img

    def export(self):
        size, pos = self._pack()
        img = self._paint(size, pos)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        src = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        elements = []
        for i, c in enumerate(self.cubes):
            faces = {}
            for f in FACES:
                x, y, w, h = pos[(i, f)]
                faces[f] = {"uv": [x, y, x + w, y + h], "texture": 0}
            org = c["origin"] or [(c["from"][k] + c["to"][k]) / 2 for k in range(3)]
            e = {"name": f"c{i}", "box_uv": False, "render_order": "default", "locked": False,
                 "allow_mirror_modeling": True, "from": c["from"], "to": c["to"], "autouv": 0, "color": 0,
                 "origin": org, "faces": faces, "type": "cube", "uuid": uid(f"{self.name}/c{i}")}
            if c["rotation"]:
                e["rotation"] = c["rotation"]
            elements.append(e)
        groups = []
        for b in self.order:
            info = self.bones[b]
            groups.append({"uuid": uid(f"{self.name}/b/{b}"), "export": True, "locked": False,
                           "origin": info["origin"], "rotation": info["rotation"], "color": 0, "name": b,
                           "children": [], "reset": False, "shade": True, "mirror_uv": False, "selected": False,
                           "visibility": True, "autouv": 0, "isOpen": True, "primary_selected": False})

        def node(b):
            kids = [uid(f"{self.name}/c{i}") for i, c in enumerate(self.cubes) if c["bone"] == b]
            kids += [node(o) for o in self.order if self.bones[o]["parent"] == b]
            return {"uuid": uid(f"{self.name}/b/{b}"), "isOpen": True, "children": kids}

        outliner = [node(b) for b in self.order if self.bones[b]["parent"] is None]
        animations = []
        for an, (length, loop, chans) in self.anims.items():
            animators = {}
            for b, ch in chans.items():
                kfs = []
                for channel, xyz in ch.items():
                    kfs.append({"channel": channel, "data_points": [{"x": str(xyz[0]), "y": str(xyz[1]), "z": str(xyz[2])}],
                                "uuid": uid(f"{self.name}/{an}/{b}/{channel}"), "time": 0, "color": -1,
                                "interpolation": "linear"})
                animators[uid(f"{self.name}/b/{b}")] = {"name": b, "type": "bone", "rotation_global": False,
                                                       "quaternion_interpolation": False, "keyframes": kfs}
            animations.append({"uuid": uid(f"{self.name}/anim/{an}"), "name": an, "loop": loop, "override": False,
                               "length": length, "snapping": 24, "selected": False, "anim_time_update": "",
                               "blend_weight": "", "start_delay": "", "loop_delay": "", "animators": animators})
        return {
            "meta": {"format_version": "5.0", "model_format": "free", "box_uv": False},
            "name": self.name, "model_identifier": "", "visible_box": [2, 2, 0],
            "variable_placeholders": "", "variable_placeholder_buttons": [], "timeline_setups": [],
            "unhandled_root_fields": {}, "resolution": {"width": size, "height": size},
            "elements": elements, "groups": groups, "outliner": outliner,
            "textures": [{"name": f"{self.name}.png", "path": "", "folder": "", "namespace": "", "id": "0",
                          "group": "", "width": size, "height": size, "uv_width": size, "uv_height": size,
                          "particle": False, "use_as_default": False, "layers_enabled": False, "sync_to_project": "",
                          "render_mode": "default", "render_sides": "auto", "pbr_channel": "color", "frame_time": 1,
                          "frame_order_type": "loop", "frame_order": "", "frame_interpolate": False, "visible": True,
                          "internal": True, "saved": False, "uuid": uid(f"{self.name}/tex"), "source": src}],
            "animations": animations,
        }, img


def save(model, path):
    data, img = model.export()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return img


# ---------------------------------------------------------------- patrones de textura
def pattern(pat, x, y, w, h, face, rnd, cols):
    """Multiplicador de brillo por pixel segun el material."""
    if not pat:
        return 1.0
    if pat == "fur":        # mechones verticales, mas oscuros en la punta
        k = 1.0 + 0.10 * cols[x]
        if (x * 7 + y * 3) % 5 == 0:
            k *= 0.86
        return k
    if pat == "shag":       # pelo largo que cuelga (yeti)
        k = 1.0 + 0.12 * cols[x]
        if y >= h - 2 and (x % 2):
            k *= 0.8
        if (x + y * 2) % 4 == 0:
            k *= 0.9
        return k
    if pat == "feather":    # plumas en escamas
        row = y // 2
        if y % 2 == 1 and (x + row) % 3 != 0:
            return 0.82
        if y % 2 == 0 and (x + row) % 3 == 1:
            return 1.1
        return 1.0
    if pat == "straw":      # paja: tiras verticales claras y oscuras
        k = 1.0 + 0.16 * cols[x]
        if (x * 5 + y) % 7 == 0:
            k *= 1.15
        return k
    if pat == "brick":      # ladrillos con junta
        if y % 4 == 3:
            return 0.62
        off = 0 if (y // 4) % 2 == 0 else 3
        if (x + off) % 6 == 5:
            return 0.66
        return 1.0 + 0.05 * ((x // 6 + y // 4) % 2)
    if pat == "scale":      # escamas en rombo
        if (x + y) % 4 == 0 or (x - y) % 4 == 0:
            return 0.86
        return 1.04
    if pat == "chitin":     # caparazon por placas con brillo arriba
        if y % 4 == 0:
            return 1.18
        if y % 4 == 3:
            return 0.78
        return 1.0
    if pat == "wrap":       # vendas en diagonal
        if (x + 2 * y) % 6 == 0:
            return 0.72
        if (x + 2 * y) % 6 == 1:
            return 1.12
        return 1.0
    if pat == "stone":
        return 1.0 + 0.12 * ((x * 13 + y * 7) % 5 - 2) / 2
    if pat == "cloth":      # tela con trama y algun remiendo
        k = 0.94 if (x + y) % 2 else 1.0
        if (x * 11 + y * 5) % 23 == 0:
            k *= 0.8
        return k
    if pat == "shell":      # caracol: anillos concentricos
        cx, cy = (w - 1) / 2, (h - 1) / 2
        r = int(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5)
        return 0.8 if r % 3 == 0 else 1.05
    if pat == "wood":
        k = 1.0 + 0.1 * cols[x]
        if y % 5 == 0 and x % 3 == 0:
            k *= 0.8
        return k
    if pat == "membrane":   # ala de piel con nervaduras
        if x % 4 == 0:
            return 0.78
        return 1.0 + 0.04 * (y % 2)
    return 1.0


# ---------------------------------------------------------------- ayudas de animacion
def swing(amp, speed=1.0, phase=0):
    return f"math.sin(q.anim_time * 360 * {speed} + {phase}) * {amp}"
