"""Apaga los avisos de "hay una version nueva" de los plugins y ajusta ClearLag (23/11/2026, pedido del dueno).

No actualiza plugins solos a proposito: en Paper 26.1 una version nueva puede romper configs o no arrancar.
Los plugins se actualizan a mano cuando hace falta (ver docs/SERVIDOR.md).

Uso: python tools/sin_avisos_update.py <carpeta con copias de plugins/*/config.yml del server>
     Edita en el lugar las copias que encuentre; despues se suben con tools/empower_api.py.
ClearLag: limpia cada 15 min y avisa solo a los 15 min, 5 min, 1 min y 10 s.
"""
import re
import sys
from pathlib import Path


def leer(f):
    with open(f, encoding='utf-8', newline='') as h:
        return h.read()


def escribir(f, t):
    with open(f, 'w', encoding='utf-8', newline='') as h:
        h.write(t)

# (archivo relativo a plugins/, regex de la linea, reemplazo)
REGLAS = [
    ('AuraSkills/config.yml', r'^check_for_updates: true', 'check_for_updates: false'),
    ('DeluxeMenus/config.yml', r'^check_updates: true', 'check_updates: false'),
    ('PlaceholderAPI/config.yml', r'^check_updates: true', 'check_updates: false'),
    ('Duels/config.yml', r'^check-for-updates: true', 'check-for-updates: false'),
    ('GrimAC/config.yml', r'^check-for-updates: true', 'check-for-updates: false'),
    ('EconomyShopGUI/config.yml', r'^update-checking: true', 'update-checking: false'),
    ('Essentials/config.yml', r'^update-check: true', 'update-check: false'),
    ('nonchat/config.yml', r'^update-checker: true', 'update-checker: false'),
    ('sleep-most/config.yml', r'^update-checker-enabled: true', 'update-checker-enabled: false'),
    ('Skript/config.sk', r'^check for new version: true', 'check for new version: false'),
    ('MythicMobs/config/config-general.yml', r'^(\s*)CheckForUpdates: true', r'\1CheckForUpdates: false'),
    ('ProtocolLib/config.yml', r'^(\s*)notify: true', r'\1notify: false'),
]
# Bloques "update-notifier:" (AxGraves, AxTrade) y "auto-updater:" (ClearLag): enabled/on-join en false.
BLOQUES = [('AxGraves/config.yml', 'update-notifier:'), ('AxTrade/config.yml', 'update-notifier:'),
           ('ClearLag/config.yml', 'auto-updater:')]
CLEARLAG_INTERVALO = 900
CLEARLAG_AVISOS = [900, 300, 60, 10]


def bloque(text, cabeza):
    out, dentro = [], False
    for line in text.split('\n'):
        if line.rstrip() == cabeza:
            dentro = True
        elif dentro and line and not line.startswith((' ', '#')):
            dentro = False
        if dentro:
            line = re.sub(r'^(\s+)(enabled|on-join): true', r'\1\2: false', line)
        out.append(line)
    return '\n'.join(out)


def clearlag(text):
    text = re.sub(r'^(auto-clear:\n(?:.*\n)*?\s+interval-seconds:) \d+', rf'\1 {CLEARLAG_INTERVALO}', text, count=1,
                  flags=re.M)
    lista = ''.join(f'- {s}\n' for s in CLEARLAG_AVISOS)
    text, n = re.subn(r'^countdown-messages-at:\n(?:- \d+\n)+', 'countdown-messages-at:\n' + lista, text, flags=re.M)
    assert n == 1, 'ClearLag: no encontre countdown-messages-at'
    # Paper no acepta view-distance 1 (rango 2-32): ClearLag tiraba error cada vez que bajaba el TPS.
    text = re.sub(r'^(\s+- \d+) 1(\r?)$', r'\1 2\2', text, flags=re.M)
    return text


def main(base):
    base = Path(base)
    for rel, pat, rep in REGLAS:
        f = base / rel
        if not f.is_file():
            print('falta', rel)
            continue
        t = leer(f)
        t2, n = re.subn(pat, rep, t, count=1, flags=re.M)
        escribir(f, t2)
        print(('ok ' if n else 'ya estaba ') + rel)
    for rel, cabeza in BLOQUES:
        f = base / rel
        if f.is_file():
            escribir(f, bloque(leer(f), cabeza))
            print('ok', rel, cabeza)
    f = base / 'ClearLag/config.yml'
    if f.is_file():
        escribir(f, clearlag(leer(f)))
        print('ok ClearLag cada', CLEARLAG_INTERVALO, 's, avisos', CLEARLAG_AVISOS)


if __name__ == '__main__':
    main(sys.argv[1])
