"""Escenarios de ruleta CSGO (27 casillas); no reemplaza la GUI vanilla."""
from pathlib import Path
from PIL import Image, ImageDraw
from escape_menu import text
from market_ui import THEMES, TITLE_Y, TITLE_OUTLINE, band_color
from services_ui import png

ROOT = Path(__file__).resolve().parent
KINDS = ('gacha_rpg', 'gacha_monturas', 'gacha_cosmeticos')
START, END = '\ue540', '\ue541'
GLYPHS = {kind: tuple(chr(0xe550+i*4+j) for j in range(4)) for i,kind in enumerate(KINDS)}
SOUNDS = {
    'gacha_rpg': ('block.amethyst_block.chime', 'block.enchantment_table.use'),
    'gacha_monturas': ('block.note_block.banjo', 'entity.experience_orb.pickup'),
    'gacha_cosmeticos': ('block.note_block.chime', 'ui.toast.challenge_complete'),
}


def title(kind):
    return '<reset><white>'+START+''.join(GLYPHS[kind])+END


def panel(kind):
    caption, fill, edge = THEMES[kind]
    source = Image.open(ROOT/f'pack-source/ref/{kind}-frame.png').convert('RGBA')
    sx = [0, round(source.width*.13), round(source.width*.87), source.width]
    sy = [0, round(source.height*.20), round(source.height*.92), source.height]
    dx, dy = [0,24,200,224], [0,56,202,224]
    im = Image.new('RGBA', (224,224))
    ImageDraw.Draw(im).rectangle((24,36,199,56), fill=fill)
    for r in range(3):
        for c in range(3):
            piece = source.crop((sx[c],sy[r],sx[c+1],sy[r+1]))
            im.alpha_composite(piece.resize((dx[c+1]-dx[c],dy[r+1]-dy[r]),Image.Resampling.NEAREST),(dx[c],dy[r]))
    d = ImageDraw.Draw(im)
    d.rectangle((24,56,199,202),fill=fill)
    for x,y in ((-1,0),(1,0),(0,-1),(0,1)):
        text(im,caption,(112+x,TITLE_Y[kind]+y),color=TITLE_OUTLINE[kind])
    text(im,caption,(112,TITLE_Y[kind]),color='#fff0d5')
    d.rectangle((65,43,158,54),fill=fill)
    text(im,'INVOCANDO...',(112,45),color=edge)
    # Los adornos ocupan las filas vacias. La cinta real gira en slots 9..17.
    for y in (58,96):
        for x in (39,57,75,147,165,183):
            if kind == 'gacha_rpg':
                d.polygon([(x,y),(x+4,y+6),(x,y+12),(x-4,y+6)],fill='#69438f',outline=edge)
                d.line((x,y+2,x,y+9),fill='#dfc6ff')
                d.line((x-7,y+6,x-5,y+6),fill=edge)
            elif kind == 'gacha_monturas':
                d.line((x-8,y+10,x+7,y+3),fill='#806b39',width=2)
                d.ellipse((x-6,y+1,x,y+6),fill='#597a46',outline=edge)
                d.ellipse((x,y+6,x+6,y+11),fill='#385e3d',outline=edge)
            else:
                d.line((x-4,y+6,x+4,y+6),fill=edge)
                d.line((x,y+2,x,y+10),fill='#ffe9cc')
                d.point((x-6,y+1),fill='#9cbce3')
    # Carril oscuro continuo, con una hornacina luminosa para el resultado.
    d.rectangle((29,74,194,93),fill='#0d101b',outline=edge)
    for col in range(1,9):
        d.line((30+col*18,76,30+col*18,91),fill=fill)
    d.rectangle((102,73,121,94),outline='#fff0d5')
    d.line((104,73,119,73),fill=edge)
    d.polygon([(106,65),(117,65),(112,71)],fill='#fff0d5')
    d.polygon([(106,103),(117,103),(112,97)],fill='#fff0d5')
    # Inventario del jugador: las mismas coordenadas que un cofre de tres filas.
    d.rectangle((31,114,192,123),fill=band_color(edge))
    for row in range(4):
        for col in range(9):
            x,y = 31+col*18,125+row*18+(4 if row==3 else 0)
            d.rectangle((x,y,x+17,y+17),outline=edge)
            d.rectangle((x+1,y+1,x+16,y+16),fill=(0,0,0,0))
    return im


def assets():
    files, providers = {}, []
    advances = {START:-32, END:32}
    for kind,(a,b,c,d) in GLYPHS.items():
        im = panel(kind)
        for n,(top,bottom,ascent,char,rewind) in enumerate(((0,56,53,a,b),(56,224,-3,c,d))):
            part = im.crop((0,top,224,bottom))
            resource = f'font/gachas/{kind}_{n}.png'
            files['assets/astral/textures/'+resource] = png(part)
            providers.append({'type':'bitmap','file':'astral:'+resource,'height':part.height,'ascent':ascent,'chars':[char]})
            advances[rewind] = -(part.getbbox()[2]+1)
    providers.append({'type':'space','advances':advances})
    return files, providers


def previews(client_jar=None):
    from lobby import GACHAS, icon
    from contextlib import ExitStack
    import zipfile
    folder = ROOT.parent/'build/Servicios-preview'
    folder.mkdir(parents=True,exist_ok=True)
    sheet = Image.new('RGBA',(224*3,224),'#171920')
    with ExitStack() as stack:
        pack = stack.enter_context(zipfile.ZipFile(ROOT.parent/'build/AstralRPG-Textures.zip'))
        vanilla = stack.enter_context(zipfile.ZipFile(client_jar)) if client_jar else None
        for i,kind in enumerate(KINDS):
            im = Image.new('RGBA',(224,224),'#25252d')
            im.alpha_composite(panel(kind))
            rewards = GACHAS[kind]['rewards']()
            for col,reward in enumerate(rewards[:9]):
                material,model,_ = icon(reward[3])
                path = f'assets/astral/textures/item/{model}.png' if model else f'assets/minecraft/textures/item/{material}.png'
                archive = pack if path in pack.namelist() else vanilla
                if archive and path in archive.namelist():
                    import io
                    sprite = Image.open(io.BytesIO(archive.read(path))).convert('RGBA').resize((16,16),Image.Resampling.NEAREST)
                    im.alpha_composite(sprite,(32+col*18,76))
            text(im,'Inventario',(64,115),color='#383c40')
            sheet.alpha_composite(im,(i*224,0))
            (folder/f'{kind}-ruleta.png').write_bytes(png(im.resize((672,672),Image.Resampling.NEAREST)))
    (folder/'gachas-ruletas.png').write_bytes(png(sheet.resize((2016,672),Image.Resampling.NEAREST)))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-jar',type=Path)
    previews(parser.parse_args().client_jar)
