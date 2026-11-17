"""Consolida las entregas del 16/11 sin conectar ni modificar servicios remotos."""
import hashlib
import json
import re
from pathlib import Path

from terceros import ROOT, privado

ENTREGAS = ('tanda-xp-cuchillo', 'balance-especiales-agua',
            'correcciones-goblin-golems', 'crop-kettle',
            'mascotas-aurora-botones', 'cargar-arte-16-11', 'modelos-3d-efectos')
OUT = ROOT / 'build/deploy'


def manifest():
    privados = privado().relative_to(ROOT).as_posix()
    files = {}
    for entrega in ENTREGAS:
        text = (OUT / (entrega + '.md')).read_text(encoding='utf8')
        for line in text.splitlines():
            match = re.match(r'\| `([^`]+)`[^|]*\| `([^`]+)`', line)
            if not match:
                continue
            local, remote = match.groups()
            local = local.replace('ASTRAL_PRIVADO', privados)
            if not remote.startswith(('plugins/', 'world/datapacks/')):
                continue
            if remote.endswith('/'):
                remote += Path(local).name
            files[remote] = local
    # Configs privadas nuevas, no las reservas publicas ni las copias historicas.
    for relative in ('skills/astral.yml', 'skills/mascotas.yml', 'mobs/astral.yml'):
        files['plugins/MythicMobs/' + relative] = (
            privados + '/build/entregas/modelos-3d-efectos/mythicmobs/' + relative)
    # Integrar estas secciones conservando las demas claves remotas.
    merge = [
        ('build/menus/DeluxeMenus/config-gui_menus.yml', 'plugins/DeluxeMenus/config.yml', 'gui_menus'),
        ('build/tanda5a/AstralProgression/config.yml', 'plugins/AstralProgression/config.yml', 'structure-namespaces: agregar cnk'),
        ('build/lobby/TAB/secciones-config.yml', 'plugins/TAB/config.yml', 'secciones TAB; combinar placeholders y reemplazos'),
    ]
    rows = []
    for remote, local in sorted(files.items()):
        path = ROOT / local
        if not path.is_file():
            raise FileNotFoundError(local)
        rows.append(dict(local=local, destino=remote, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for local, remote, section in merge:
        if not (ROOT / local).is_file():
            raise FileNotFoundError(local)
    return dict(reemplazar=rows, integrar=[dict(local=a, destino=b, seccion=c) for a,b,c in merge],
                retirar=['plugins/DeluxeMenus/gui_menus/' + n + '.yml' for n in (
                    'mascota_lobo', 'mascota_zorro', 'mascota_golem', 'mascota_cuervo', 'mascota_dragon', 'mascotas_4')])


def generate():
    data = manifest()
    (OUT / 'deploy-16-11-archivos.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf8')
    lines = ['# Archivos acumulados del 16/11', '',
             'Generado por `python datapack-src/deploy_1611.py`. Instalar una sola vez cada destino con el servidor apagado.',
             'Los SHA-256 corresponden a los archivos locales actuales; ninguna fila acredita una subida.', '',
             '| Archivo local | Destino |', '|---|---|']
    lines += [f"| `{r['local']}` | `{r['destino']}` |" for r in data['reemplazar']]
    lines += ['', '## Integrar sin reemplazar el archivo remoto', '']
    lines += [f"- `{r['local']}` → `{r['destino']}`: {r['seccion']}." for r in data['integrar']]
    lines += ['', '## Retirar con respaldo', '',
              'Quitar tambien estos seis registros de `gui_menus` en DeluxeMenus. Conservar todos los demas.', '']
    lines += ['- `' + p + '`' for p in data['retirar']]
    (OUT / 'deploy-16-11-archivos.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
    print(len(data['reemplazar']), 'reemplazos; 3 integraciones; 6 retiros limitados')


if __name__ == '__main__':
    generate()
