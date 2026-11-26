"""Publica un cambio en el canal de novedades del Discord por webhook (regla del dueno, 26/11/2026).

La URL del webhook es secreta: va en .local/discord_webhook.txt (ignorado por git), nunca en el repo.
Se crea en Discord: canal 🆕・novedades-del-juego -> Editar canal -> Integraciones -> Webhooks -> Nuevo
webhook -> Copiar URL (lo hace el dueno).

    python tools/discord_novedades.py "Titulo" "Linea 1" "Linea 2" ...   # simula
    python tools/discord_novedades.py --yes "Titulo" "Linea 1" ...        # publica
"""
import argparse
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
WEBHOOK = ROOT / '.local' / 'discord_webhook.txt'


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # consola de Windows con emojis
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--yes', action='store_true', help='publicar de verdad (sin esto solo muestra el mensaje)')
    ap.add_argument('titulo')
    ap.add_argument('lineas', nargs='*')
    a = ap.parse_args()
    texto = f'**{a.titulo}**\n' + '\n'.join(f'• {l}' for l in a.lineas)
    if len(texto) > 2000:
        raise SystemExit(f'El mensaje tiene {len(texto)} caracteres (Discord acepta 2000).')
    print(texto)
    if not a.yes:
        print('\n(simulado: agregar --yes para publicar)')
        return
    if not WEBHOOK.exists() or not WEBHOOK.read_text(encoding='utf-8').strip():
        raise SystemExit(f'Falta el webhook en {WEBHOOK} (ver arriba como crearlo).')
    url = WEBHOOK.read_text(encoding='utf-8').strip()
    cuerpo = json.dumps({'content': texto, 'allowed_mentions': {'parse': []}}).encode('utf-8')
    req = urllib.request.Request(url, data=cuerpo, method='POST',
                                 headers={'Content-Type': 'application/json', 'User-Agent': 'AstralRPG-novedades'})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f'Publicado en Discord (HTTP {r.status}).')


if __name__ == '__main__':
    main()
