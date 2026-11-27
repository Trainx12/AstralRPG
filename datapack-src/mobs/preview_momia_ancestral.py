"""Comparacion CPU: el arreglo cambia el orden de escala, no el arte del modelo."""
from pathlib import Path
from PIL import Image, ImageDraw
from mobs.build_models import creatures, preview3d
from mobs.preview_arreglos import posed
from mobs.mythic import escala_mundo


def generate():
    model = next(fn() for fn in creatures.ALL if fn().name == 'astral_momia')
    sheet = Image.new('RGB', (1160, 500), '#171e27')
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 12), 'Momia ancestral - geometria local antes / despues (sin cambios de arte)', fill='white')
    for col, label in enumerate(('Antes: model -> scale', 'Despues: scale -> model')):
        draw.text((16 + col*580, 42), label, fill='#ffcc77')
        for index, (anim, time) in enumerate((('idle', .75), ('walk', .25), ('attack', .5))):
            m = posed(model, anim, time)
            render = preview3d(m, m.export()[1], yaw=25, pitch=5, scale=7)
            render.thumbnail((175, 340))
            x = col*580 + index*188 + 12
            sheet.paste(render, (x + (175-render.width)//2, 90 + (340-render.height)//2))
            draw.text((x, 68), anim, fill='white')
    draw.text((16, 454), f's del Survival: {escala_mundo("astral_momia")} | pivote head: Y24, hijo de body', fill='white')
    draw.text((16, 478), 'Render CPU con escala uniforme. No reproduce paquetes viejos de BetterModel; falta probar con cliente.', fill='white')
    dest = Path(__file__).resolve().parents[2] / 'build/previews/momia_ancestral_cabeza.png'
    sheet.save(dest)


if __name__ == '__main__':
    generate()
