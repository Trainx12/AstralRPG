"""Lee campos de una seccion Markdown sin mostrar contenido privado."""
import re
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / 'docs/CREDENCIALES.local.md'


class LocalError(ValueError):
    """Error redactado por nosotros, sin datos privados de librerias o respuestas."""


def fields(section, path=DEFAULT):
    try:
        text = Path(path).read_text(encoding='utf-8-sig')
    except OSError:
        raise LocalError('No se puede leer el archivo local de credenciales.') from None
    lines = text.splitlines()
    result, active, level = {}, False, 0
    for line in lines:
        header = re.match(r'^(#{1,6})\s+(.+?)\s*$', line)
        if header:
            if active and len(header[1]) <= level:
                break
            if header[2].strip() == section:
                active, level = True, len(header[1])
            continue
        if not active:
            continue
        clean = line.strip().lstrip('- ').replace('**', '')
        if clean.startswith('|'):
            cells = [c.strip().strip('`') for c in clean.strip('|').split('|')]
            if len(cells) >= 2:
                result[cells[0].rstrip(':')] = cells[1]
        elif ':' in clean:
            key, value = clean.split(':', 1)
            result[key.strip().strip('`')] = value.strip().strip('`')
    return result


def require(data, key):
    value = data.get(key, '').strip()
    if not value or value.startswith('<'):
        raise LocalError(f'Falta completar el campo {key} en las credenciales locales.')
    return value
