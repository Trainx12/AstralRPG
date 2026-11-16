"""Regenera solo los dos disenos pedidos, sin mezclar otros cambios pendientes.

El ZIP es una superposicion de recursos, NO un resource pack instalable.
La compilacion completa habitual (build_pack.py) incorpora estos mismos recursos.
"""
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import menu_ui
import travel_ui
from menus import principal_menu

ROOT = Path(__file__).resolve().parents[1]


def update_public_pack(resources):
    """Conserva todas las entradas ajenas y la fuente; cambia solo esta entrega."""
    pack = ROOT / 'build/AstralRPG-Textures.zip'
    temporary = pack.with_suffix('.menu.tmp')
    try:
        with ZipFile(pack) as original, ZipFile(temporary, 'w', ZIP_DEFLATED) as updated:
            remaining = dict(resources)
            for entry in original.infolist():
                updated.writestr(entry, remaining.pop(entry.filename, original.read(entry.filename)))
            for name, blob in remaining.items():
                updated.writestr(name, blob)
        os.replace(temporary, pack)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    menu_ui.preview(ROOT / 'build/Servicios-preview')
    travel_ui.previews(ROOT / 'build/Interfaces-preview', kinds=('minas',))
    (ROOT / 'build/menus/DeluxeMenus/gui_menus/principal.yml').write_text(principal_menu(), encoding='utf-8')
    menu_files, _ = menu_ui.assets()
    travel_files, _ = travel_ui.assets()
    resources = {name: blob for name, blob in menu_files.items()
                 if name.startswith('assets/astral/textures/font/menu/principal_')
                 or name in ('assets/astral/textures/item/menu/icon_configuraciones.png',
                             'assets/astral/models/menu/icon_configuraciones.json',
                             'assets/astral/items/menu/icon_configuraciones.json')}
    resources.update({name: blob for name, blob in travel_files.items()
                      if name.startswith('assets/astral/textures/font/viajes/minas_')})
    update_public_pack(resources)
    out = ROOT / 'build/disenos-menu'
    out.mkdir(parents=True, exist_ok=True)
    with ZipFile(out / 'recursos-menu.zip', 'w', ZIP_DEFLATED) as archive:
        for name, blob in sorted(resources.items()):
            archive.writestr(name, blob)
    (out / 'archivos.json').write_text(json.dumps(sorted(resources), indent=2) + '\n', encoding='utf-8')
    print('Dos vistas, principal.yml y recursos-menu.zip generados. Sin despliegue.')


if __name__ == '__main__':
    main()
