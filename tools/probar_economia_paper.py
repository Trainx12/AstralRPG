"""Ensayo aislado de astral_economia.sk (Paper + Skript + Essentials + Vault). Solo 127.0.0.1; no toca el server remoto.

Uso: python tools/probar_economia_paper.py --java <bin/java.exe>
Revisa que el script cargue sin errores y prueba por consola: info del banco, rebase (una sola vez).
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.local/testsrv'


def main(java):
    work = ROOT / '.local/economia-probe'
    srv = work / 'paper'
    srv.mkdir(parents=True, exist_ok=True)
    for n in ('libraries', 'versions', 'cache'):
        if not (srv / n).exists():
            shutil.copytree(BASE / n, srv / n)
    shutil.copy2(BASE / 'paper.jar', srv / 'paper.jar')
    (srv / 'eula.txt').write_text('eula=true\n')
    (srv / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25631\nonline-mode=false\nlevel-type=minecraft:flat\n'
                                           'generate-structures=false\nmanagement-server-enabled=false\nview-distance=2\nsimulation-distance=2\n')
    plugins = srv / 'plugins'
    plugins.mkdir(exist_ok=True)
    for name in ('skript.jar', 'EssentialsX.jar', 'Vault.jar'):
        shutil.copy2(BASE / 'plugins' / name, plugins / name)
    scripts = plugins / 'Skript/scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    for old in scripts.glob('*.sk'):
        old.unlink()
    for src in (ROOT / 'build/economia/Skript/scripts/astral_economia.sk', ROOT / 'build/mazmorras/astral_puntaje.sk',
                ROOT / 'build/mazmorras/astral_mazmorras_copias.sk', ROOT / 'build/secretos/astral_secretos.sk',
                ROOT / 'build/services/astral_servicios.sk', ROOT / 'build/gemas/astral_gemas.sk'):
        shutil.copy2(src, scripts / src.name)
    log = work / 'paper.log'
    with log.open('w', encoding='utf8') as out:
        p = subprocess.Popen([str(java), '-Xms256M', '-Xmx2G', '-jar', 'paper.jar', '--nogui'], cwd=srv,
                             stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT, text=True)

        def cmd(s, wait=3):
            p.stdin.write(s + '\n')
            p.stdin.flush()
            time.sleep(wait)
        try:
            for _ in range(240):
                if 'For help, type' in log.read_text('utf8', errors='replace'):
                    break
                if p.poll() is not None:
                    raise RuntimeError('Paper termino: ' + str(log))
                time.sleep(1)
            time.sleep(8)
            cmd('astralbanco info Prueba')
            cmd('astraleconomia rebase')
            cmd('astraleconomia rebase')
            cmd('mazpuntaje inicio mina')
            cmd('mazpuntaje fin mina')
            cmd('scoreboard objectives list')
            cmd('secretos')
            cmd('astralgema')
            cmd('astralgema dar Nadie rubi 3')
            cmd('stop', 15)
        finally:
            if p.poll() is None:
                p.kill()
    text = log.read_text('utf8', errors='replace')
    lines = [l for l in text.splitlines() if 'astral_economia' in l or '[Banco]' in l or '[Economia]' in l or 'astral.nota' in l or 'mazpuntaje' in l or 'astral_puntaje' in l or 'mazmorras_copias' in l or 'astral_gemas' in l or 'Reforja' in l or 'astralgema' in l
             or 'error' in l.lower() or 'Line ' in l or 'scripts loaded' in l]
    sys.stdout.reconfigure(errors='replace')
    print('\n'.join(lines[-80:]))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--java', required=True)
    main(Path(ap.parse_args().java))
