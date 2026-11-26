"""Reinicio automatico cuando el server queda vacio (25/11/2026, pedido del dueno).

Sirve para que los cambios que dejan otras sesiones (plugins/update, datapack, MythicMobs, pack...) entren
sin esperar al reinicio diario de las 05:00 y sin cortarle el juego a nadie.

Como funciona:
  1. Quien termina de subir algo que necesita reinicio corre por consola:
         reiniciopendiente <motivo>        (ej. reiniciopendiente AstralDecor 1.25.2)
     Eso deja la marca {astral::reinicio::pendiente} (persistente) y anota el motivo.
  2. Cada minuto, si hay marca y no hay NADIE conectado, suma un minuto. Si entra alguien vuelve a 0.
  3. A los MINUTOS seguidos vacio: save-all y minecraft:stop.
  4. El panel vuelve a prenderlo: tarea programada "Arranque automatico" (tools/arranque_automatico.py),
     power start cada minuto. Si el server ya esta prendido o arrancando, el panel lo ignora.
     OJO: por esa tarea, un stop manual vuelve a prender solo en 1 minuto. Para dejarlo apagado,
     desactivar la tarea en el panel (Schedules) o con `python tools/arranque_automatico.py --yes --apagar`.
  5. Al arrancar (on skript start) la marca se borra: los cambios ya entraron. El reinicio diario tambien la borra.

Otros comandos: `reiniciopendiente ver`, `reiniciopendiente quitar`.

26/11 (dueno): APAGADO por defecto. La marca se anota pero no reinicia; los cambios entran en el reinicio
diario de las 05:00. Prenderlo solo si el dueno lo pide: `reiniciopendiente activar` (apagar: `desactivar`).

    python reinicio_vacio.py   ->  build/gameplay/astral_reinicio_vacio.sk  (plugins/Skript/scripts/)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'build' / 'gameplay' / 'astral_reinicio_vacio.sk'
MINUTOS = 5


def script():
    return f'''# Generado por datapack-src/reinicio_vacio.py: no editar a mano.
# Reinicia solo si hay cambios pendientes y el server queda vacio {MINUTOS} minutos seguidos.

command /reiniciopendiente [<text>]:
    permission: op
    trigger:
        if arg-1 is not set:
            send "&eUso: reiniciopendiente <motivo> | ver | quitar | activar | desactivar"
            stop
        if arg-1 is "activar":
            set {{astral::reinicio::activo}} to true
            send "&6[Reinicio] &aActivado: con marca, reinicia tras {MINUTOS} min con el server vacio."
            stop
        if arg-1 is "desactivar":
            delete {{astral::reinicio::activo}}
            delete {{-astral::reinicio::vacio}}
            send "&6[Reinicio] &eDesactivado: los cambios esperan al reinicio de las 05:00."
            stop
        if arg-1 is "ver":
            if {{astral::reinicio::activo}} is true:
                send "&6[Reinicio] &aReinicio por server vacio: ACTIVADO"
            else:
                send "&6[Reinicio] &eReinicio por server vacio: DESACTIVADO (espera a las 05:00)"
            if {{astral::reinicio::pendiente}} is true:
                send "&6[Reinicio] &ePendiente: &f%{{astral::reinicio::motivos::*}}%"
                send "&6[Reinicio] &eMinutos vacio: &f%{{-astral::reinicio::vacio}} ? 0%/{MINUTOS}"
            else:
                send "&6[Reinicio] &aNo hay cambios pendientes."
            stop
        if arg-1 is "quitar":
            delete {{astral::reinicio::pendiente}}
            delete {{astral::reinicio::motivos::*}}
            delete {{-astral::reinicio::vacio}}
            send "&6[Reinicio] &aMarca quitada."
            stop
        set {{astral::reinicio::pendiente}} to true
        add "%now% %arg-1%" to {{astral::reinicio::motivos::*}}
        if {{astral::reinicio::activo}} is true:
            send "&6[Reinicio] &aAnotado. Se reinicia cuando el server quede vacio {MINUTOS} minutos."
        else:
            send "&6[Reinicio] &eAnotado. Reinicio por server vacio desactivado: entra a las 05:00."

on skript start:
    delete {{astral::reinicio::pendiente}}
    delete {{astral::reinicio::motivos::*}}
    delete {{-astral::reinicio::vacio}}

every 1 minute:
    if {{astral::reinicio::activo}} is not true:
        delete {{-astral::reinicio::vacio}}
        stop
    if {{astral::reinicio::pendiente}} is not true:
        delete {{-astral::reinicio::vacio}}
        stop
    if size of all players > 0:
        delete {{-astral::reinicio::vacio}}
        stop
    add 1 to {{-astral::reinicio::vacio}}
    if {{-astral::reinicio::vacio}} < {MINUTOS}:
        stop
    delete {{-astral::reinicio::vacio}}
    log "Reinicio por server vacio: %{{astral::reinicio::motivos::*}}%" to "astral_reinicio.log"
    execute console command "save-all"
    wait 5 seconds
    if size of all players > 0:
        stop
    execute console command "minecraft:stop"
'''


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(script(), encoding='utf-8')
    print(f'OK {OUT.relative_to(ROOT.parent)}')


if __name__ == '__main__':
    main()
