"""Bloquea solo zombi -> ahogado; recargar unicamente astral_zombis_sin_ahogados.sk."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def script():
    return '''# Generado por datapack-src/zombis_sin_ahogados.py; no editar a mano.
# Evita que la conversion reinicie la vida de un zombi y conserve su tier.
# Los ahogados naturales y las otras transformaciones siguen funcionando.
on load:
    log "Activo: solo se bloquea la conversion de zombi a ahogado." to "astral_zombis_sin_ahogados.log"

on entity transform due to drowning:
    if type of event-entity is zombie:
        cancel event
'''


if __name__ == '__main__':
    out = ROOT / 'build/gameplay/astral_zombis_sin_ahogados.sk'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script(), encoding='utf8')
    print(out)
