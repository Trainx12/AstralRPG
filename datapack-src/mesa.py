"""Recetas de mesa derivadas, sin cambiar cantidades ni datos de la Forja."""
import json
from pathlib import Path


def fits(ingredients):
    return 0 < sum(count for _, _, count in ingredients) <= 9


def prepare(items, fichas, recipes, txt):
    uses = {}
    for out, _, ingredients, _ in recipes:
        for kind, ident, _ in ingredients:
            if kind == 'c':
                uses.setdefault(ident, []).append(items[out]['name'])
    craftable = {out: fits(ingredients) for out, _, ingredients, _ in recipes}
    for iid in set(uses) | set(craftable):
        lines = []
        if iid in uses:
            lines.append(txt('Material para: ' + ', '.join(dict.fromkeys(uses[iid]))[:150], 'dark_gray'))
        if iid in craftable:
            lines.append(txt('Se fabrica en la mesa de crafteo o en la Forja' if craftable[iid]
                             else 'Se fabrica solo en la Forja (supera 3x3)', 'gray'))
        lore = items[iid]['components']['minecraft:lore']
        if iid in fichas:
            lore[-1:-1] = lines  # Conservar rareza/tipo como ultima linea de la ficha.
        else:
            lore.extend(lines)
        if iid in fichas:
            # Las fichas de mejoras se regeneran desde su fuente original.
            fichas[iid]['original'].extend(lines)
    return craftable


def export(items, requirements, recipes, root):
    rows = []
    for out, count, ingredients, group in recipes:
        rows.append(dict(output=out, count=count, ingredients=ingredients, group=group,
                         table=fits(ingredients), requirements=requirements.get(out, {})))
    dest = Path(root) / 'build/runtime/mesa.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return rows
