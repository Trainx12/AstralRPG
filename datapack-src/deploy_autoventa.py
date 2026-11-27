"""Entrega aditiva sin el datapack acumulado ni cambios previos de Minas.

python deploy_autoventa.py [--server-script copia-local-del-script-remoto.sk]
Con --server-script escribe una copia parcheada; nunca modifica el original.
"""
import argparse
import difflib
from pathlib import Path
import zipfile
import minas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/autoventa'
OLD_GIVE = '''function am_give(p: player, items: items):
    # AstralMinasLimite tira al piso lo que no entra (los minerales marcados no se apilan con los
    # comunes, por eso no se puede preguntar antes): se cuenta lo que hay en el piso antes y despues.
    set {_antes::*} to all dropped items in radius 1.5 around location of {_p}
    loop {_items::*}:
        # AstralMinasLimite: PDC invisible, interruptor privado y sobrantes marcados.
        astral mine give loop-value to {_p}
    set {_despues::*} to all dropped items in radius 1.5 around location of {_p}
    if size of {_despues::*} > size of {_antes::*}:
        am_aviso_lleno({_p})
    else:
        # Entro todo: hay lugar otra vez, el proximo llenado vuelve a avisar.
        delete {-am.lleno::%uuid of {_p}%}
'''


def patch_script(text):
    generated = minas.script()
    start = generated.index('command /am_autoventa_nivel ')
    end = generated.index('\n# 25/11 (dueno): cartel', start)
    replacement = generated[start:end].rstrip() + '\n'
    if 'command /autoventa ' in text or text.count(OLD_GIVE) != 1:
        raise ValueError('La copia no coincide con am_give anterior o ya incluye autoventa. Revisar el diff; no reemplazar a ciegas.')
    return text.replace(OLD_GIVE, replacement, 1)


def generate(server_script=None):
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as source:
        with zipfile.ZipFile(OUT / 'AstralRPG-Autoventa.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for name in ('pack.mcmeta', 'data/astral/loot_table/item/autoventa.json',
                         'data/astral/function/autoventa/identify.mcfunction'):
                info = zipfile.ZipInfo(name, (2026, 11, 27, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, source.read(name))
    # Diff limitado a esta tarea: incluso si el script local tiene Renacer u otros cambios pendientes.
    new = minas.script()
    start = new.index('command /am_autoventa_nivel ')
    end = new.index('\n# 25/11 (dueno): cartel', start)
    old = new[:start] + OLD_GIVE + new[end:]
    assert patch_script(old) == new
    patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                      fromfile='astral_minas.sk', tofile='astral_minas.sk', n=0))
    (OUT / 'astral_minas-autoventa.patch').write_text(patch, encoding='utf8', newline='\n')
    if server_script:
        target = OUT / 'astral_minas.sk'
        if target.resolve() == server_script.resolve():
            raise ValueError('Usar un archivo de entrada distinto del destino')
        target.write_text(patch_script(server_script.read_text(encoding='utf8')), encoding='utf8', newline='\n')
    print('Autoventa: ZIP aditivo, receta desactivada y parche ->', OUT)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--server-script', type=Path)
    generate(p.parse_args().server_script)
