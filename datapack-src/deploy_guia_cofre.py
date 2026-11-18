"""Guia Astral en cofre (18/11): FINAL nuevo = ultimo FINAL + fondo de la guia en la fuente default.

Uso: python deploy_guia_cofre.py [--base <FINAL.zip>]
"""
import argparse
import hashlib
import json
from pathlib import Path
from deploy_guia_esc import rewrite
from final_base import select_base
from guia_cofre import assets
from terceros import privado

OUT = privado() / 'build/entregas/guia-cofre-18-11'
DATAPACK = Path(__file__).resolve().parents[1] / 'build/AstralRPG-Items.zip'


def change(names, z):
    files, providers = assets(DATAPACK)
    font = json.loads(z.read('assets/minecraft/font/default.json'))
    mine = {p['file'] for p in providers if 'file' in p}
    chars = {c for p in providers for c in (p.get('chars') or []) + list(p.get('advances', {}))}
    # Rearmar sin versiones viejas de la guia (si se corre dos veces sobre su propio FINAL).
    old = [p for p in font['providers'] if p.get('file') not in mine
           and not ({c for c in (p.get('chars') or []) + list(p.get('advances', {}))} & chars)]
    font['providers'] = providers + old
    out = dict(files)
    out['assets/minecraft/font/default.json'] = json.dumps(font, ensure_ascii=False).encode()
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base')
    args = ap.parse_args()
    base = select_base(output=OUT, explicit=args.base)
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(base, final, change)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n')
    print('base', base)
    print('FINAL', final, sha)
