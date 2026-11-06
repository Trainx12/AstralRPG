"""Preparar el ZIP de Santuario confirmado por el dueno, sin mapas en GitHub."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from portales_mapas import load_litematic, sanitize, write_world
from restaurar_mundos import read_at

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT/'.local/santuario-correcto-2026-11-05'


def main():
    if OUTPUT.exists():
        raise SystemExit('La salida ya existe; conservarla y usar una carpeta nueva.')
    archive = Path.home()/'Downloads/mapa_Santuari_Mazmorra.zip'
    with ZipFile(archive) as source:
        names = [n for n in source.namelist() if n.endswith('.litematic')]
        if len(names) != 1:
            raise ValueError('Se espera un solo litematic en el ZIP confirmado.')
        raw = source.read(names[0])
    OUTPUT.mkdir(parents=True)
    schematic = OUTPUT/'interstellar.litematic'
    schematic.write_bytes(raw)
    palette, blocks = load_litematic(schematic)
    sanitize(palette, blocks)
    region = OUTPUT/'region'
    write_world(region, palette, blocks, (-152, 48, -152))
    for x, y, z in [(34, 180, 40), (46, 180, 48)]:
        assert read_at(region, x, y-1, z) == 'minecraft:iron_block'
        for height in (0, 1, 2):
            assert read_at(region, x, y+height, z) == 'minecraft:air'
    for x in range(42, 51):
        for z in range(44, 53):
            assert read_at(region, x, 179, z) == 'minecraft:iron_block'
            for y in range(180, 186):
                assert read_at(region, x, y, z) == 'minecraft:air'
    report = {'original': archive.name, 'sha256_original': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'archivos_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in region.glob('*.mca')},
              'llegada': [34.5, 180, 40.5], 'controlador': [46.5, 180, 48.5],
              'area_9x9_altura_6': True, 'instalado': False}
    (OUTPUT/'informe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
