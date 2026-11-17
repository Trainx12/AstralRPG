"""Desactiva solo gui.toggle en una copia local del config del servidor."""
import argparse
from pathlib import Path
import re


def patch(content):
    # Mantener comentarios, orden y todas las otras claves, incluidos CRLF.
    section = re.search(r'^gui:[^\r\n]*\r?\n(?:(?:[ \t]+[^\r\n]*|[ \t]*)\r?\n)*', content, re.M)
    if not section:
        raise ValueError('No hay seccion gui; no se modifica el archivo')
    value, count = re.subn(r'^(  toggle: )[\w]+', r'\g<1>false', section[0], flags=re.M)
    if count != 1:
        raise ValueError('gui.toggle no es unico o tiene formato desconocido')
    return content[:section.start()] + value + content[section.end():]


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('config', type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    if args.config.resolve() == args.output.resolve():
        p.error('Usar una salida diferente para conservar el original')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patch(args.config.read_bytes().decode('utf-8')).encode('utf-8'))
    print('Copia preparada; instalar como plugins/CrazyCrates/config.yml y ejecutar crates reload.')
