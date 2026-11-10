"""Panel lateral dibujado con BetterHud (reemplaza el panel lateral de TAB).

Genera en build/plugins/BetterHud/ (se copia tal cual a plugins/BetterHud/ del server):
  assets/astral_panel.png   marco, gema, titulo, tarjetas e iconos (dibujado aca, pixel art)
  images/astral.yml, texts/astral.yml, layouts/astral.yml, huds/astral.yml
y build/gameplay/astral_panel.sk (/sb prende/apaga el panel y lo recuerda).

El pack de BetterHud (fuentes y glifos) se arma con estos mismos archivos en un Paper
local y se copia a pack-source/betterhud (ver docs/BETTERHUD_Y_DUELS.md).
Cualquier cambio aca obliga a regenerar ese pack.
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw

from misiones import CHAPTERS
from sidebar import world_labels

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "plugins" / "BetterHud"
HUD_ID = "astral_panel"
MINES_WORLD = "astral_minas"  # ahi se ve el panel de TAB de las minas

# Paleta de sidebar.py
BLUE, VIOLET = (0x52, 0x68, 0xC7), (0xD1, 0x7A, 0xFF)
TEXT, MUTED, PURPLE = "#F0E6FF", "#AA96C5", "#D6B4FF"

W = 154            # ancho: entra "Tumba del Rey de Arena" (121 px) en la fila de Lugar
PAD = 6            # margen interno del marco
TOP = 6            # espacio para la gema que sobresale
ROW = 10           # alto de cada fila
HEAD = 12          # alto del encabezado de cada tarjeta
GAP = 4            # espacio entre tarjetas

# Rango segun el poder de AuraSkills (mismos umbrales que lobby.RANKS)
RANKS = [(1500, "Leyenda", "#FFB347"), (800, "Héroe", "#FF77FF"), (400, "Veterano", "#55FFFF"),
         (150, "Aventurero", "#55FF55"), (0, "Novato", "#AAAAAA")]

SECTIONS = [
    ("JUGADOR", "sword", [
        ("heart", "Vida", "health"),
        ("shield", "Defensa", "defense"),
        ("bolt", "Poder", "power"),
        ("coin", "Oro", "gold"),
    ]),
    ("MUNDO", "globe", [
        ("pin", "", "world"),        # sin etiqueta: el nombre del lugar usa toda la fila
        ("people", "Conectados", "online"),
    ]),
    ("PROGRESO", "trophy", [
        ("crown", "Rango", "rank"),
        ("scroll", "Diarias", "daily"),
        ("book", "Historia", "story"),
        ("skull", "Monstruos", "kills"),
    ]),
]

# ------------------------------------------------------------------ iconos 9x9
# Letras = colores; '.' = transparente
ICON_COLORS = {
    "r": (0xE8, 0x3B, 0x5A), "R": (0xFF, 0x8F, 0xA3), "d": (0x8A, 0x1C, 0x36),
    "b": (0x5D, 0x8B, 0xF4), "B": (0xA8, 0xC8, 0xFF), "n": (0x2C, 0x45, 0x9E),
    "y": (0xFF, 0xD2, 0x4A), "Y": (0xFF, 0xF1, 0xA8), "o": (0xC7, 0x84, 0x1E),
    "v": (0xB0, 0x6C, 0xF5), "V": (0xE2, 0xC4, 0xFF), "p": (0x6B, 0x3F, 0xB0),
    "g": (0x4C, 0xC7, 0x6A), "G": (0xA6, 0xF2, 0xB5), "e": (0x2A, 0x7A, 0x45),
    "w": (0xF0, 0xE6, 0xFF), "s": (0x9C, 0x95, 0xB8), "k": (0x3A, 0x34, 0x55),
    "c": (0x96, 0x6B, 0x3F), "C": (0xD9, 0xAE, 0x78),
}
ICONS = {
    "heart": [".rr...rr.", "rRrr.rrrr", "rRrrrrrrr", "rrrrrrrrr", "rrrrrrrrd",
              ".rrrrrrd.", "..rrrrd..", "...rrd...", "....d...."],
    "shield": ["bbbbbbbbb", "bBBBbbbbn", "bBbbbbbbn", "bBbbbbbbn", "bbbbbbbbn",
               ".bbbbbbn.", ".bbbbbbn.", "..bbbbn..", "....n...."],
    "bolt": ["....yyyy.", "...yYyy..", "..yYyy...", ".yYyyyyy.", "yyyyyyyo.",
             "...yyyo..", "..yyo....", ".yyo.....", ".yo......"],
    "coin": ["..yyyyy..", ".yYYYyyo.", "yYyyyyyyo", "yYyoooyyo", "yYyoyyyyo",
             "yYyoooyyo", "yyyyyyyyo", ".yyyyyoo.", "..ooooo.."],
    "pin": ["..vvvvv..", ".vVVvvvp.", "vVvvvvvvp", "vVvwwvvvp", "vvvwwvvvp",
            ".vvvvvvp.", "..vvvvp..", "...vvp...", "....p...."],
    "people": ["...ss....", "..swws...", "..swws.s.", "...ss.sws", ".ssssss.s",
               "swwwwss..", "swwwwwss.", "swwwwwwws", "sssssssss"],
    "crown": ["y..y.y..y", "yy.yyy.yy", "yyyyyyyyy", "yYyyRyyyo", "yYyRRRyyo",
              "yyyyRyyyo", "yyyyyyyyo", "ooooooooo", "........."],
    "scroll": [".CCCCCCC.", "CCwwwwwCc", ".Cw.ssswC", ".CwwwwwwC", ".Cw.sssw.",
               ".CwwwwwwC", ".Cw.ssswC", "CCwwwwwCc", ".ccccccc."],
    "book": [".ppppppp.", "pvvvvvvVp", "pvVVVVvVp", "pvvvvvvVp", "pvVVVvvVp",
             "pvvvvvvVp", "pvvvvvvVp", "pwwwwwwwp", ".ppppppp."],
    "skull": ["..wwwww..", ".wwwwwwws", "wwwwwwwws", "wkkwwkkws", "wkkwwkkws",
              "wwwwkwwws", ".wwwwwws.", "..wswsw..", "..wswsw.."],
    "sword": ["......ww.", ".....wBw.", "....wBw..", "...wBw...", "c.wBw....",
              ".cwBw....", "..cc.....", ".ccc.....", "cc.c....."],
    "globe": ["..ggbbb..", ".gGgbbbn.", "gGgggbbbn", "gggbbggbn", "bbbbbggbn",
              "bbggbbbgn", "bbgggbbbn", ".bbggbbn.", "..nnnnn.."],
    "trophy": ["yyyyyyyyy", "yYyyyyyyo", "yYyyyyyyo", ".yYyyyyo.", "..yyyyo..",
               "...yyo...", "...yyo...", "..ooooo..", ".kkkkkkk."],
}

# Letras 5x7 para el titulo (dibujado, a 2x)
GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    " ": ["000", "000", "000", "000", "000", "000", "000"],
}
TITLE = "ASTRAL RPG"
TITLE_SCALE = 2


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def layout_rows():
    """Lista de (tipo, y, datos). y = arriba de cada fila dentro del panel."""
    rows = []
    y = TOP + 6
    rows.append(("title", y, None))
    y += 7 * TITLE_SCALE + 4
    for title, icon, items in SECTIONS:
        rows.append(("card", y, (title, icon, len(items))))
        rows.append(("head", y, (title, icon)))
        y += HEAD
        for item in items:
            rows.append(("row", y, item))
            y += ROW
        y += 2 + GAP
    height = y - GAP + PAD - 2
    return rows, height


ROWS, H = layout_rows()


# ------------------------------------------------------------------ dibujo
def draw_icon(img, name, x, y):
    for j, line in enumerate(ICONS[name]):
        for i, ch in enumerate(line):
            if ch != ".":
                img.putpixel((x + i, y + j), ICON_COLORS[ch] + (255,))


def draw_title(img, cx, y):
    width = sum(len(GLYPHS[c][0]) + 1 for c in TITLE) * TITLE_SCALE - TITLE_SCALE
    x0 = cx - width // 2
    x = x0
    for c in TITLE:
        glyph = GLYPHS[c]
        for j, line in enumerate(glyph):
            for i, bit in enumerate(line):
                if bit == "1":
                    t = (x + i * TITLE_SCALE - x0) / max(1, width)
                    col = lerp(BLUE, VIOLET, t)
                    light = lerp(col, (255, 255, 255), 0.45 if j < 2 else 0.15)
                    for dx in range(TITLE_SCALE):
                        for dy in range(TITLE_SCALE):
                            px, py = x + i * TITLE_SCALE + dx, y + j * TITLE_SCALE + dy
                            img.putpixel((px + 1, py + 1), (20, 14, 45, 255))  # sombra
                            img.putpixel((px, py), light + (255,))
        x += (len(glyph[0]) + 1) * TITLE_SCALE


def panel_image():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = TOP
    # Fondo
    d.rectangle((2, top + 2, W - 3, H - 3), fill=(13, 11, 30, 222))
    # Brillo exterior y borde con degradado vertical
    for yy in range(top, H):
        t = (yy - top) / (H - top)
        col = lerp(BLUE, VIOLET, t)
        glow = col + (90,)
        for xx in (0, W - 1):
            img.putpixel((xx, yy), glow)
        for xx in (1, 2, W - 2, W - 3):
            img.putpixel((xx, yy), col + (255,))
    for xx in range(0, W):
        t = xx / W
        col = lerp(BLUE, VIOLET, t)
        img.putpixel((xx, top), col + (90,))
        img.putpixel((xx, H - 1), lerp(BLUE, VIOLET, 1) + (90,))
        for yy in (top + 1, top + 2):
            img.putpixel((xx, yy), col + (255,))
        for yy in (H - 2, H - 3):
            img.putpixel((xx, yy), VIOLET + (255,))
    # Esquinas con remache
    for cx, cy in ((4, top + 4), (W - 5, top + 4), (4, H - 5), (W - 5, H - 5)):
        d.rectangle((cx - 1, cy - 1, cx + 1, cy + 1), fill=(0xE2, 0xC4, 0xFF, 255))
        img.putpixel((cx, cy), (255, 255, 255, 255))
    # Gema arriba al centro (rombo)
    gx, gy, r = W // 2, top, 6  # la punta toca la fila 0: BetterHud recorta filas vacias
    for j in range(-r, r + 1):
        span = r - abs(j)
        for i in range(-span, span + 1):
            edge = abs(i) == span
            t = (j + r) / (2 * r)
            col = (255, 255, 255) if edge and j < 0 else lerp((0x9F, 0xE8, 0xFF), VIOLET, t)
            if edge:
                col = lerp(col, (40, 30, 90), 0.5 if j >= 0 else 0)
            img.putpixel((gx + i, gy + j), col + (255,))
    img.putpixel((gx - 1, gy - 2), (255, 255, 255, 255))
    img.putpixel((gx - 2, gy - 1), (255, 255, 255, 255))
    # Titulo, tarjetas y filas
    for kind, y, data in ROWS:
        if kind == "title":
            draw_title(img, W // 2, y)
        elif kind == "card":
            _, _, n = data
            y1 = y + HEAD + n * ROW + 1
            d.rectangle((PAD, y, W - PAD - 1, y1), fill=(30, 25, 64, 215), outline=(0x3D, 0x3A, 0x7A, 255))
            for xx in range(PAD + 1, W - PAD - 1):
                t = (xx - PAD) / (W - 2 * PAD)
                col = lerp((0x3A, 0x45, 0x96), (0x6E, 0x45, 0xA8), t)
                for yy in range(y + 1, y + HEAD - 1):
                    img.putpixel((xx, yy), col + (235,))
                img.putpixel((xx, y + HEAD - 1), lerp(BLUE, VIOLET, t) + (255,))
        elif kind == "head":
            draw_icon(img, data[1], PAD + 3, y + 2)
        elif kind == "row":
            draw_icon(img, data[0], PAD + 3, y + 1)
            d.line((PAD + 2, y + ROW, W - PAD - 3, y + ROW), fill=(0x2E, 0x2A, 0x5A, 255))
    return img


# ------------------------------------------------------------------ YAML
def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


NOT_MINES = {"first": "world", "second": f"'{MINES_WORLD}'", "operation": "!="}


def cond_block(conds, indent):
    """conds: lista de dicts first/second/operation. Siempre se suma 'no estar en las minas'."""
    pad = " " * indent
    out = [f"{pad}conditions:"]
    for i, c in enumerate([NOT_MINES] + conds, 1):
        out.append(f"{pad}  {i}:")
        out.append(f"{pad}    first: {q(str(c['first']))}")
        out.append(f"{pad}    second: {q(str(c['second']))}")
        out.append(f"{pad}    operation: '{c['operation']}'")
    return out


def num(placeholder, op, value):
    return {"first": f"(number){placeholder}", "second": value, "operation": op}


def value_texts(key, x, y):
    """Textos (alineados a la derecha) de cada valor; algunos son varios con condiciones."""
    v = f"<{TEXT}>"
    simple = {
        "health": f"{v}[health] <{MUTED}>/ {v}[max_health]",
        "defense": f"{v}[papi:objective_score_{{astraldef}}]",
        "power": f"{v}[papi:auraskills_power]",
        "gold": f"{v}[papi:vault_eco_balance_formatted]",
        "online": f"{v}[papi:server_online]<{MUTED}>/{v}[papi:server_max_players]",
        "kills": f"{v}[papi:statistic_mob_kills]",
    }
    if key in simple:
        return [(simple[key], [])]
    if key == "rank":
        out, upper = [], None
        for threshold, name, color in RANKS:
            conds = [num("papi:auraskills_power", ">=", threshold)] if threshold else []
            if upper is not None:
                conds.append(num("papi:auraskills_power", "<", upper))
            out.append((f"<{color}>{name}", conds))
            upper = threshold
        return out
    if key == "daily":
        out = []
        for mask in range(8):
            done = bin(mask).count("1")
            conds = [num(f"papi:objective_score_aq.done{t}", ">=" if mask >> t & 1 else "<", 1)
                     for t in range(3)]
            color = PURPLE if done == 3 else TEXT
            out.append((f"<{color}>{done}<{MUTED}>/3", conds))
        return out
    if key == "story":
        total = len(CHAPTERS)
        out = [(f"{v}0<{MUTED}>/{total}", [num("papi:objective_score_aq.state", "<", 2)])]
        for done in range(1, total + 1):
            op = ">=" if done == total else "=="
            out.append((f"{v}{done}<{MUTED}>/{total}", [num("papi:objective_score_aq.state", op, done + 1)]))
        return out
    if key == "world":
        labels = {w: n for w, n in world_labels().items() if w != MINES_WORLD}
        out = [(f"{v}{name}", [{"first": "world", "second": f"'{world}'", "operation": "=="}])
               for world, name in labels.items()]
        out.append((f"{v}Exploración", [{"first": "world", "second": f"'{world}'", "operation": "!="}
                                         for world in labels]))
        return out
    raise KeyError(key)


def text_entry(i, pattern, x, y, align, conds):
    # En BetterHud "/" escapa al caracter siguiente: una barra literal se escribe "//"
    lines = [f"      {i}:", "        name: astral_font", f"        pattern: {q(pattern.replace('/', '//'))}",
             # La letra sale a 16 px de alto: scale 0.5 la deja en 8 px (como en los ejemplos de BetterHud)
             f"        x: {x}", f"        y: {y}", f"        align: {align}", "        scale: 0.5", "        outline: true",
             "        placeholder-string-format:", '          number: "#,###"']
    return lines + cond_block(conds, 8)


def layouts_yml():
    img = ["astral_panel_fondo:", "  images:", "    1:", "      name: astral_panel_fondo",
           # BetterHud centra las imagenes en su x: se corre medio ancho para que el borde izquierdo quede en 0
           f"      x: {W // 2}", "      y: 0"] + cond_block([], 6)
    texts = ["astral_panel_textos:", "  texts:"]
    n = 0
    for kind, y, data in ROWS:
        if kind == "head":
            n += 1
            texts += text_entry(n, f"<{PURPLE}><b>{data[0]}", PAD + 15, y + 2, "left", [])
        elif kind == "row":
            icon, label, key = data
            if label:
                n += 1
                texts += text_entry(n, f"<{MUTED}>{label}", PAD + 15, y + 1, "left", [])
            x, align = (W - PAD - 4, "right") if label else (PAD + 15, "left")
            for pattern, conds in value_texts(key, x, y + 1):
                n += 1
                texts += text_entry(n, pattern, x, y + 1, align, conds)
    header = "# Generado por datapack-src/betterhud.py: no editar a mano\n"
    return header + "\n".join(img) + "\n\n" + "\n".join(texts) + "\n"


def images_yml():
    return ("# Generado por datapack-src/betterhud.py\n"
            "astral_panel_fondo:\n  type: single\n  file: astral_panel.png\n")


def texts_yml():
    # Letra de Minecraft (con acentos); unifont de respaldo (sin el, BetterHud pide freetype)
    return ("# Generado por datapack-src/betterhud.py\n"
            "astral_font:\n  scale: 16\n  height: 8\n  ascent: 7\n"
            "  merge-default-bitmap: true\n  use-unifont: true\n  include: []\n")


def huds_yml():
    # Pegado al borde derecho y centrado en vertical (0/50/100 no se corre con la escala de GUI)
    px, py = -(W + 2), -(H // 2)
    out = ["# Generado por datapack-src/betterhud.py", f"{HUD_ID}:", "  layouts:"]
    for i, name in enumerate(("astral_panel_fondo", "astral_panel_textos"), 1):
        out += [f"    {i}:", f"      name: {name}", "      gui:", "        x: 100", "        y: 50",
                "      pixel:", f"        x: {px}", f"        y: {py}"]
    return "\n".join(out) + "\n"


# Claves de config.yml de BetterHud que hay que cambiar (el resto queda como viene)
CONFIG_KEYS = {
    "default-hud": "[]",
    "pack-type": "folder",
    "enable-self-host": "false",
    "metrics": "false",
    "load-minecraft-default-textures": "false",
}


def config_yml(original):
    """Aplica CONFIG_KEYS sobre el config.yml que trae BetterHud."""
    text = original
    for key, value in CONFIG_KEYS.items():
        pattern = re.compile(rf"^{re.escape(key)}:.*(?:\n\s*- .*)*", re.M)
        line = f"{key}:{value}" if value.startswith("\n") else f"{key}: {value}"
        if pattern.search(text):
            text = pattern.sub(line.replace("\\", "\\\\"), text, count=1)
        else:
            text += f"\n{line}\n"
    return text


SKRIPT = f"""# Generado por datapack-src/betterhud.py
# /sb prende o apaga el panel de TAB y lo recuerda.
command /sb:
    trigger:
        if {{astral::panel_off::%uuid of player%}} is set:
            delete {{astral::panel_off::%uuid of player%}}
            execute console command "tab scoreboard on %player% -s"
            send "&d✦ &fPanel encendido. &7/sb lo apaga." to player
        else:
            set {{astral::panel_off::%uuid of player%}} to true
            execute console command "tab scoreboard off %player% -s"
            send "&d✦ &fPanel apagado. &7/sb lo vuelve a mostrar." to player

on join:
    wait 2 seconds
    player is online
    execute console command "hud hud remove %player% {HUD_ID}"
    if {{astral::panel_off::%uuid of player%}} is set:
        execute console command "tab scoreboard off %player% -s"
    else:
        execute console command "tab scoreboard on %player% -s"
"""


def preview(img, font_png=None):
    """Vista previa con valores de ejemplo, a 4x (la letra sale del ascii.png del jar si esta)."""
    scale = 4
    base = Image.new("RGBA", (W + 40, H + 20), (70, 110, 60, 255))
    base.alpha_composite(img, (20, 10))
    sample = {"health": "120 / 120", "defense": "35", "power": "412", "gold": "15,230",
              "world": "Tumba del Rey de Arena", "online": "7/50", "rank": "Veterano",
              "daily": "2/3", "story": "4/9", "kills": "1,284"}
    colors = {"rank": "#55FFFF"}
    glyphs = None
    if font_png and Path(font_png).exists():
        sheet = Image.open(font_png).convert("RGBA")
        glyphs = {}
        for code in range(32, 127):
            cell = sheet.crop(((code % 16) * 8, (code // 16) * 8, (code % 16) * 8 + 8, (code // 16) * 8 + 8))
            bbox = cell.getbbox()
            glyphs[chr(code)] = (cell, (bbox[2] if bbox else 3) + 1)

    def write(text, x, y, color, align="left", bold=False):
        if not glyphs:
            ImageDraw.Draw(base).text((x, y - 2), text, fill=color)
            return
        text = text.translate(str.maketrans("áéíóúñÁÉÍÓÚÑ", "aeiounAEIOUN"))
        width = sum(glyphs.get(c, glyphs["?"])[1] + (1 if bold else 0) for c in text)
        if align == "right":
            x -= width
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        for c in text:
            cell, adv = glyphs.get(c, glyphs["?"])
            mask = cell.split()[3]
            for dx, col in ((1, (40, 40, 60)), (0, rgb)):
                for b in ((0, 1) if bold else (0,)):
                    layer = Image.new("RGBA", cell.size, col + (255,))
                    base.paste(layer, (x + dx + b, y + dx), mask)
            x += adv + (1 if bold else 0)

    for kind, y, data in ROWS:
        y += 10
        if kind == "head":
            write(data[0], 20 + PAD + 15, y + 2, PURPLE, bold=True)
        elif kind == "row":
            icon, label, key = data
            if label:
                write(label, 20 + PAD + 15, y + 1, MUTED)
                write(sample[key], 20 + W - PAD - 4, y + 1, colors.get(key, TEXT), "right")
            else:
                write(sample[key], 20 + PAD + 15, y + 1, colors.get(key, TEXT))
    return base.resize((base.width * scale, base.height * scale), Image.NEAREST)


def main():
    for sub in ("assets", "images", "texts", "layouts", "huds"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    img = panel_image()
    img.save(OUT / "assets" / "astral_panel.png")
    (OUT / "images" / "astral.yml").write_text(images_yml(), encoding="utf-8")
    (OUT / "texts" / "astral.yml").write_text(texts_yml(), encoding="utf-8")
    (OUT / "layouts" / "astral.yml").write_text(layouts_yml(), encoding="utf-8")
    (OUT / "huds" / "astral.yml").write_text(huds_yml(), encoding="utf-8")
    (OUT / "config-cambios.yml").write_text(
        "# Cambiar solo estas claves en plugins/BetterHud/config.yml (el resto como viene)\n"
        + "".join(f"{k}:{v}\n" if v.startswith("\n") else f"{k}: {v}\n" for k, v in CONFIG_KEYS.items()),
        encoding="utf-8")
    gameplay = ROOT / "build" / "gameplay"
    gameplay.mkdir(parents=True, exist_ok=True)
    (gameplay / "astral_panel.sk").write_text(SKRIPT, encoding="utf-8")
    font = ROOT / ".local" / "betterhud-jar" / "ascii.png"
    previews = ROOT / "build" / "previews"
    previews.mkdir(parents=True, exist_ok=True)
    preview(img, font).save(previews / "panel-betterhud.png")
    print(f"betterhud: panel {W}x{H} -> {OUT}")


if __name__ == "__main__":
    main()
