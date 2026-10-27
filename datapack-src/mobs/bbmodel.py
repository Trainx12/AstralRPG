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

    def cube(self, bone, frm, to, color, decals=None, shade=0.0, rotation=None, origin=None, glow=False):
        self.cubes.append({"bone": bone, "from": list(frm), "to": list(to), "color": color,
                           "decals": decals or {}, "shade": shade, "rotation": rotation, "origin": origin})

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
        for size in (64, 128, 256, 512):
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
            for yy in range(h):
                for xx in range(w):
                    n = rnd.uniform(-0.06, 0.06)
                    edge = 0.85 if (xx == 0 or yy == 0 or xx == w - 1 or yy == h - 1) and w > 2 and h > 2 else 1.0
                    k = (mult + n) * edge
                    px[x0 + xx, y0 + yy] = tuple(max(0, min(255, int(v * k))) for v in base) + (255,)
            for (dx, dy, dw, dh, col) in c["decals"].get(f, []):
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


# ---------------------------------------------------------------- ayudas de animacion
def swing(amp, speed=1.0, phase=0):
    return f"math.sin(q.anim_time * 360 * {speed} + {phase}) * {amp}"
