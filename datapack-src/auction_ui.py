"""Marco del catalogo real de CrazyAuctions, conservando la configuracion existente.

Sin argumentos exporta el parche de titulos; con --config prepara una copia
completa del config.yml del servidor, preservando comentarios y economia.
No lee ni escribe data.yml (publicaciones, jugadores y objetos).
"""
import argparse
import re
from pathlib import Path
from market_ui import title, CATALOG_TAGS

ROOT=Path(__file__).resolve().parent.parent
KEYS=('GUIName','Players-Current-Items','Cancelled/Expired-Items')


def patch_config(source):
    for key in KEYS:
        source,count=re.subn(rf'(?m)^  {re.escape(key)}:.*$',
            lambda _:f"  {key}: '{title('subastas_catalogo')+CATALOG_TAGS[key]}'",source)
        if count!=1:raise ValueError(f'Esquema CrazyAuctions no reconocido: {key} ({count})')
    return source


def generate():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path)
    args=parser.parse_args()
    out=ROOT/'build/menus/CrazyAuctions';out.mkdir(parents=True,exist_ok=True)
    patch='Settings:\n'+''.join(f"  {key}: '{title('subastas_catalogo')+CATALOG_TAGS[key]}'\n" for key in KEYS)
    (out/'titulos.patch.yml').write_text(patch,encoding='utf-8')
    (out/'INSTALAR.txt').write_text(
        'Este archivo es un parche: NO reemplazar config.yml por titulos.patch.yml.\n'
        'Cambiar solamente los tres titulos de Settings en el config.yml existente.\n'
        'Alternativa: python auction_ui.py --config <copia-del-config.yml>\n'
        'La copia completa se prepara en .local/auction-ui-deploy/config.yml.\n'
        'No modificar data.yml. No cambiar impuestos, tiempos ni permisos.\n'
        'Subir el resource pack y luego recargar CrazyAuctions con /ah reload.\n',encoding='utf-8')
    if args.config:
        dest=ROOT/'.local/auction-ui-deploy/config.yml';dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(patch_config(args.config.read_text(encoding='utf-8-sig')),encoding='utf-8')
        print('Configuracion preparada:',dest)
    print('Parche de apariencia:',out)


if __name__=='__main__':generate()
