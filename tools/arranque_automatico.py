"""Tarea del panel "Arranque automatico": power start cada minuto (25/11/2026).

Va junto con datapack-src/reinicio_vacio.py: el Skript apaga el server vacio con cambios pendientes y esta
tarea lo vuelve a prender. Con el server prendido o arrancando, el panel ignora el start.
Por eso un stop manual tambien vuelve a prender en 1 minuto: usar --apagar para dejarlo apagado de verdad.

    python tools/arranque_automatico.py               # muestra el estado (sin cambios)
    python tools/arranque_automatico.py --yes         # crea la tarea o la activa
    python tools/arranque_automatico.py --yes --apagar
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from empower_api import Client  # noqa: E402
from credenciales_locales import fields, require  # noqa: E402

NOMBRE = 'Arranque automatico (reinicio por server vacio)'


def buscar(client):
    data = json.loads(client.request('GET', '/schedules?include=tasks'))
    for item in data['data']:
        if item['attributes']['name'] == NOMBRE:
            return item['attributes']
    return None


def guardar(client, sid, activa):
    body = {'name': NOMBRE, 'is_active': activa, 'only_when_online': False,
            'minute': '*', 'hour': '*', 'day_of_month': '*', 'month': '*', 'day_of_week': '*'}
    route = '/schedules' + (f'/{sid}' if sid else '')
    return json.loads(client.request('POST', route, json.dumps(body).encode()))['attributes']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--yes', action='store_true')
    parser.add_argument('--apagar', action='store_true')
    args = parser.parse_args()
    client = Client(require(fields('Clave de API del panel'), 'Clave'))
    actual = buscar(client)
    if not args.yes:
        print('No existe.' if not actual else f"Existe id={actual['id']} activa={actual['is_active']}")
        return
    sched = guardar(client, actual and actual['id'], not args.apagar)
    tareas = sched.get('relationships', {}).get('tasks', {}).get('data', []) if actual is None else \
        actual['relationships']['tasks']['data']
    if not tareas:
        client.request('POST', f"/schedules/{sched['id']}/tasks", json.dumps(
            {'action': 'power', 'payload': 'start', 'time_offset': 0, 'continue_on_failure': False}).encode())
    print(f"OK id={sched['id']} activa={not args.apagar}")


if __name__ == '__main__':
    main()
