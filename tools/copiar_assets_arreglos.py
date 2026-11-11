"""Copia exclusivamente los cuatro modelos propios corregidos desde BetterModel local."""
import argparse
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
MODELS=tuple('astral_esq_'+k for k in ('arquero','escudero','espadachin','guardian'))


def copy(assets):
    source=assets.resolve()/'bettermodel'
    target=ROOT/'datapack-src/pack-source/bettermodel/assets/bettermodel'
    count=0
    for path in source.rglob('*'):
        if not path.is_file() or not any(path.stem==mid or path.stem.startswith(mid+'_') for mid in MODELS):continue
        if path.suffix not in ('.png','.json'):raise ValueError(path)
        dest=target/path.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,dest);count+=1
    if count==0:raise ValueError('No se encontraron modelos propios en '+str(source))
    print('Assets propios copiados:',count)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('assets',type=Path)
    copy(parser.parse_args().assets)
