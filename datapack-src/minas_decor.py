"""Decoracion de cada Mina Astral con su propio mineral (pedido del dueno 20/11/2026).

El 18/11 cada tier copio la decoracion de su mina de Carbon (1, 7 y 14), asi que todas tenian
carbon en paredes, columnas y montones. Esto cambia SOLO el carbon de la decoracion por el
mineral de la mina (mena -> mena, bloque -> bloque), con WorldEdit desde la consola.
El monton de minerales mezclados detras de la venta rapida (tiers I y II) queda igual.

Uso:  python minas_decor.py  ->  build/minas/decor-menas.txt (comandos de consola, uno por linea)
Las minas de Carbon no se tocan. Las del pozo no tienen carbon (salvo Carbon), asi que se puede
reemplazar en toda la caja de la mina.
"""
from pathlib import Path

from minas import MINES, SPACING, WORLD

ROOT = Path(__file__).resolve().parents[1]
BOX = dict(x1=0, x2=200, y1=64, y2=185, z1=0, z2=185)     # misma caja que la copia del 18/11
# Monton de minerales mezclados detras del aldeano de venta rapida (tiers I y II, coordenadas locales).
# En el tier III ese monton no tiene carbon y la caja pisaria el monton de carbon de al lado: sin mascara.
KEEP_HASTA = 13
KEEP = dict(x1=86, x2=100, y1=90, y2=106, z1=53, z2=60)

# mapa de la mina -> (mena, bloque). El cobre va encerado para que no se ponga verde.
MATERIAL = {
    "cobre": ("copper_ore", "waxed_copper_block"),
    "hierro": ("iron_ore", "iron_block"),
    "oro": ("gold_ore", "gold_block"),
    "esmeralda": ("emerald_ore", "emerald_block"),
    "diamante": ("diamond_ore", "diamond_block"),
    "netherita": ("ancient_debris", "netherite_block"),
}


def commands():
    out = [f"//world {WORLD}"]
    for i, (name, *_rest) in enumerate(MINES, 1):
        mapa = MINES[i - 1][4]
        if mapa not in MATERIAL:
            continue
        ore, block = MATERIAL[mapa]
        b = (i - 1) * SPACING
        k = KEEP
        out += [
            f"//pos1 {b + BOX['x1']},{BOX['y1']},{BOX['z1']}",
            f"//pos2 {b + BOX['x2']},{BOX['y2']},{BOX['z2']}",
            # Mascara: todo menos el monton de la venta rapida (coordenadas absolutas).
            (f"//gmask =!(x>={b + k['x1']}&&x<={b + k['x2']}&&y>={k['y1']}&&y<={k['y2']}"
             f"&&z>={k['z1']}&&z<={k['z2']})") if i <= KEEP_HASTA else "//gmask",
            f"//replace coal_ore {ore}",
            f"//replace coal_block {block}",
        ]
    out.append("//gmask")
    return out


def main():
    path = ROOT / "build/minas/decor-menas.txt"
    path.write_text("\n".join(commands()) + "\n", encoding="utf8")
    print(f"{path.relative_to(ROOT)}: {len(commands())} comandos")


if __name__ == "__main__":
    main()
