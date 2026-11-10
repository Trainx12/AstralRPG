"""Vista aproximada de TAB: colores MiniMessage, negritas y degradados por tramo."""
import json
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from lobby import ASTRAL_ROWS
from sidebar import TITLE

ROOT = Path(__file__).resolve().parents[1]


def preview_panel(destination):
    samples = {
        '%condition:sidebar_world%': '<#F0E6FF>Refugio Astral', '%player%': 'ByTrainx',
        '%statistic_time_played%': '1d 5h 56m 1s',
        '%player_health_rounded%': '156', '%player_max_health_rounded%': '156',
        '%objective_score_{astraldef}%': '410', '%auraskills_power%': '1455',
        '%vault_eco_balance_formatted%': '100M', '%condition:rango%': 'Héroe',
        '%statistic_mob_kills%': '1284', '%condition:historia%': '■■□□□□□□ <#F0E6FF>1/9',
        '%date%': 'Martes', '%localtime_timezone_America/Argentina/Buenos_Aires,dd/MM/yy%': '10/11/26',
        '%time%': '11:27',
        **{f'%condition:diaria{i}%': '<#AA96C5>Sin aceptar' for i in range(3)},
    }
    folder = ROOT / 'datapack-src/pack-source/vanilla-base/font'
    sheet = Image.open(folder / 'ascii.png').convert('RGBA')
    chars = json.loads((folder / 'ascii.json').read_text(encoding='utf-8'))['chars']
    glyphs = {}
    for y, line in enumerate(chars):
        for x, char in enumerate(line):
            cell = sheet.crop((x*8, y*8, x*8+8, y*8+8))
            box = cell.getbbox()
            glyphs[char] = (cell.getchannel('A'), (box[2] if box else 3)+1)
    # Los simbolos Unicode usan una fuente del sistema; no reemplazarlos por '?'.
    symbols = ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf', 10)
    def glyph(char):
        if char in glyphs:
            return glyphs[char]
        box = symbols.getbbox(char)
        mask = Image.new('L', (max(10, box[2]), 12))
        ImageDraw.Draw(mask).text((0, -2), char, font=symbols, fill=255)
        return mask, max(4, round(symbols.getlength(char)))+1
    rows = []
    for row in [TITLE, *ASTRAL_ROWS]:
        for placeholder, value in samples.items():
            row = row.replace(placeholder, value)
        result, color, bold, gradient = [], '#F0E6FF', False, None
        for token in re.split('(<[^>]+>)', row):
            if token.startswith('<'):
                if token.startswith('<#'):
                    color = token[1:-1]
                elif token == '<bold>':
                    bold = True
                elif token == '</bold>':
                    bold = False
                elif token.startswith('<gradient:'):
                    gradient = (len(result), token[10:-1].split(':'))
                elif token == '</gradient>' and gradient:
                    start, colors = gradient
                    a, b = [tuple(bytes.fromhex(c[1:])) for c in colors]
                    for i in range(start, len(result)):
                        t = (i-start)/max(1, len(result)-start-1)
                        char, _, weight = result[i]
                        result[i] = (char, tuple(round(x+(y-x)*t) for x,y in zip(a,b)), weight)
                    gradient = None
            else:
                result.extend((char, color, bold) for char in token)
        rows.append(result)
    widths = [sum(glyph(c)[1]+int(b) for c, _, b in row) for row in rows]
    image = Image.new('RGBA', (max(widths)+16, len(rows)*12+12), '#24252c')
    for y, row in enumerate(rows):
        x = 8
        for char, color, bold in row:
            mask, advance = glyph(char)
            for offset in range(1+int(bold)):
                image.paste('#101015', (x+offset+1, 7+y*12), mask)
                image.paste(color, (x+offset, 6+y*12), mask)
            x += advance+int(bold)
    image = image.resize((image.width*3, image.height*3), Image.Resampling.NEAREST)
    image.save(destination / 'panel-tab.png')
    reference = ROOT / '.local/coordination/ref/panel-tab-original.jpg'
    if reference.exists():
        # Solo el panel de la captura; excluir la interfaz privada del telefono.
        original = Image.open(reference).convert('RGBA').crop((421, 618, 738, 880))
        original = original.resize((round(original.width*image.height/original.height), image.height))
        comparison = Image.new('RGBA', (original.width+image.width+24, image.height+30), '#17171c')
        draw = ImageDraw.Draw(comparison)
        draw.text((8, 8), 'Original (captura)', fill='white')
        draw.text((original.width+24, 8), 'Tanda 1b (vista aproximada)', fill='white')
        comparison.alpha_composite(original, (0, 30))
        comparison.alpha_composite(image, (original.width+24, 30))
        comparison.save(destination / 'panel-tab-comparacion.png')
