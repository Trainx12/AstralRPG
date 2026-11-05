"""Preparar solo las cuatro regiones privadas de Bosque, sin reemplazar el mundo."""
import hashlib
import json
from pathlib import Path
import shutil

from mapas import chunk_records
from restaurar_mundos import read_at

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT/'.local/mapas/subida/bosque/region'
OUTPUT = ROOT/'.local/bosque-restaurado-2026-11-05'
REGIONS = ('r.2.2.mca', 'r.2.3.mca', 'r.3.2.mca', 'r.3.3.mca')
ARRIVALS = ((1440, 103, 1569), (1504, 107, 1504), (1600, 97, 1440))


def main():
    if OUTPUT.exists():
        raise SystemExit('La salida ya existe; conservarla para no pisar el respaldo.')
    for x, y, z in ARRIVALS:
        assert read_at(SOURCE, x, y-1, z) not in (
            'minecraft:air', 'minecraft:water', 'minecraft:lava')
        for height in (0, 1):
            assert read_at(SOURCE, x, y+height, z) == 'minecraft:air'
    chunks = 0
    forbidden = {'minecraft:command_block', 'minecraft:chain_command_block',
                 'minecraft:repeating_command_block', 'minecraft:spawner',
                 'minecraft:trial_spawner', 'minecraft:structure_block', 'minecraft:jigsaw'}
    for name in REGIONS:
        for chunk in chunk_records((SOURCE/name).read_bytes()):
            chunks += 1
            for section in chunk.get('sections', []):
                for entry in section.get('block_states', {}).get('palette', []):
                    assert entry['Name'] not in forbidden, (name, entry)
    destination = OUTPUT/'region'
    destination.mkdir(parents=True)
    hashes = {}
    for name in REGIONS:
        shutil.copyfile(SOURCE/name, destination/name)
        hashes[name] = hashlib.sha256((destination/name).read_bytes()).hexdigest()
    report = {'archivos_sha256': hashes, 'chunks': chunks, 'llegadas': ARRIVALS,
              'instalado': False, 'pisos_y_dos_aires': True}
    (OUTPUT/'informe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
