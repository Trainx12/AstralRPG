"""Seleccion de FINAL: rechazar bases antiguas salvo eleccion explicita --base."""
from pathlib import Path
from terceros import privado


def select_base(expected=None, output=None, explicit=None):
    if explicit is not None:
        p=Path(explicit).resolve()
        if not p.is_file():raise FileNotFoundError(p)
        return p
    candidates=[p for p in (privado()/'build/entregas').glob('*/AstralRPG-Textures.zip')
                if output is None or p.parent.resolve()!=Path(output).resolve()]
    if not candidates:raise FileNotFoundError('No hay FINAL privado en entregas/')
    newest=max(candidates,key=lambda p:(p.stat().st_mtime_ns,p.as_posix()))
    if expected is not None and Path(expected).resolve()!=newest.resolve():
        raise ValueError(f'Base antigua: {expected}; mas nueva: {newest}. Usar la mas nueva o --base explicita.')
    return newest
