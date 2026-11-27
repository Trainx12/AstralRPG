"""Entrega aditiva sin el datapack acumulado ni cambios previos de Minas.

python deploy_autoventa.py [--server-script copia-local-del-script-remoto.sk]
Con --server-script escribe en build/autoventa/astral_minas.sk; admite esa misma ruta de entrada.
"""
import argparse
import difflib
import hashlib
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
    marker = 'command /am_autoventa_nivel '
    boundary = '\n# 25/11 (dueno): cartel'
    if marker in text:
        if text.count(marker) != 1 or text.count(boundary) != 1:
            raise ValueError('Bloque autoventa ambiguo; revisar la copia del servidor.')
        first = text.index(marker)
        last = text.index(boundary, first)
        block = text[first:last]
        for required in ('command /autoventa ', 'function am_autoventa(', 'function am_give('):
            if block.count(required) != 1:
                raise ValueError('Bloque autoventa incompleto: ' + required)
        return text[:first] + replacement + text[last:]
    if 'command /autoventa ' in text or text.count(OLD_GIVE) != 1:
        raise ValueError('La copia no coincide con am_give anterior. Revisar el diff; no reemplazar a ciegas.')
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
        patched = patch_script(server_script.read_text(encoding='utf8'))
        target.write_text(patched, encoding='utf8', newline='\n')
    manifest = ROOT / 'build/deploy/autoventa-27-11.md'
    sha = hashlib.sha256((OUT / 'AstralRPG-Autoventa.zip').read_bytes()).hexdigest()
    manifest.write_text(f'''# Nucleo de Venta Automatica: interruptor e icono (27/11/2026)

Preparado localmente. Despliegue remoto y prueba visual pendientes de Claude.
Sigue oculto: solo ByTrainx, salvo apertura explicita con `autoventa publico`.
La receta sigue desactivada y no aparece en la Guia.

## Archivos exactos

| Local | Destino |
| --- | --- |
| `build/autoventa/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |
| `build/autoventa/AstralRPG-Autoventa.zip` | `world/datapacks/AstralRPG-Autoventa.zip` |
| `.local/terceros/AstralRPG-privado/build/entregas/corazon-astral-27-11/AstralRPG-Textures.zip` | Resource pack FINAL en R2 (Claude); conservar URL fija |

ZIP aditivo SHA-256: `{sha}`.
FINAL esperado SHA-1: `575c6dc776f4ca270dc7e006a9d54dac799d600b`.
Su base fue `bazar-tarjeta-27-11` (SHA-1 `799e337a060e63317de40b9d03252e5e6e24ff5b`):
solo agrega/reemplaza las tres entradas `assets/astral/{{items/autoventa.json,models/item/autoventa.json,textures/item/autoventa.png}}`.
Si hay un FINAL posterior, regenerar sobre esa base antes de instalar.
No publicar el FINAL privado en GitHub. No subir `receta-desactivada.json`.

## Instalacion por Claude

El plan indica que el datapack anterior aun no cargo. Apagar para reemplazar el ZIP,
el FINAL y `resource-pack-sha1` de `server.properties`; iniciar con el reinicio diario
de las 05:00 o el autorizado por el dueno. No reiniciar por cuenta propia.
Con el datapack nuevo ya cargado, un cambio exclusivo de Skript basta con
`skript reload astral_minas` (alternativa sin alias: `skript:skript reload astral_minas`).
No usar reload global. No sustituir mundos ni Worlds > Upload.

La copia de servidor faltaba en build: se reconstruyo desde el respaldo pre-autoventa
y el bloque de HEAD; coincide exactamente con SHA-256
`317a43a8bfa2e75eb7be8e814536bf1ec37952177992abadd4d77e2d72f51240` del plan.
Se probo el reemplazo de ese bloque conservando el resto. Antes de subir, descargar
la copia remota vigente y comparar; si cambio, regenerar:
`python datapack-src/deploy_autoventa.py --server-script COPIA_REMOTA.sk`.
Tambien acepta la version sin autoventa y la ya actualizada (idempotente).
No subir el acumulado `build/minas` ni `build/AstralRPG-Items.zip` del workspace:
contienen cambios previos ajenos. Conservar las variables de Skript.

Revisar consola sin errores, `datapack list enabled`, prioridad aditiva al final.
Si hace falta: `datapack enable "file/AstralRPG-Autoventa.zip" last`.
Dar un Nucleo actualizado: `minecraft:loot give ByTrainx loot astral:item/autoventa`.
Los ya entregados conservan lore/icono anterior hasta reemplazarlos; el toggle
los reconoce por custom_data igualmente. No se migra todo el inventario.
Comprobar `papi parse ByTrainx %auraskills_mining%` numerico.

## Comportamiento y verificacion

Shift + clic derecho con el Nucleo en principal o secundaria alterna en cualquier mundo.
Sin Shift no cambia. Estado por UUID en `{{am.autoventa.off::UUID}}`, persistente;
ausencia = ENCENDIDO. APAGADO no vende y conserva el aviso habitual de inventario lleno.
Barra de accion ENCENDIDO/APAGADO y clic con tonos distintos. Brillo fijo: no se usa
como indicador por jugador. Identificacion real por custom_data, sin aceptar renombrados.

Pruebas: `python -m unittest test_autoventa` desde datapack-src;
`python tools/probar_autoventa_paper.py --java JAVA25 --base PAPER_LOCAL --work DIRECTORIO_NUEVO`;
`python tools/verificar_terceros.py`. El ensayo incluye segundo arranque para persistencia.
Usa un doble local DeluxeMenus/PAPI: la expansion real y la vista del icono quedan
pendientes de probar en servidor con cliente. No Discord mientras siga oculto.

Verificado el 27/11: cuatro pruebas Python y 48 comprobaciones Paper 26.1.2 con
Skript 2.17.1 aprobadas, incluyendo reinicio real y persistencia. Auditoria de
terceros del repo y del contenido aislado a publicar sin arte privado.
''', encoding='utf8', newline='\n')
    print('Autoventa: ZIP aditivo, receta desactivada y parche ->', OUT)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--server-script', type=Path)
    generate(p.parse_args().server_script)
