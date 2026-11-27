"""Entrega aislada de la tarjeta Bazar; conserva todas las entradas del FINAL privado."""
import argparse
import hashlib
from pathlib import Path

from deploy_guia_esc import rewrite
from final_base import select_base
from services_ui import assets
from terceros import privado

ROOT = Path(__file__).resolve().parents[1]
OUT = privado() / 'build/entregas/bazar-tarjeta-27-11'


def card_assets():
    files, _ = assets()
    return {n: b for n, b in files.items() if '/bazar_bazar_' in n}


def generate(base=None):
    source = select_base(output=OUT, explicit=base)
    delta = card_assets()
    assert len(delta) == 24  # ocho tiles: textura, modelo y definicion de item
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'AstralRPG-Textures.zip'
    rewrite(source, final, lambda names, z: delta)
    sha = hashlib.sha1(final.read_bytes()).hexdigest()
    (OUT / 'pack.sha1').write_text(sha + '\n', encoding='utf8')
    menu = ROOT / 'build/menus/DeluxeMenus/gui_menus/bazar.yml'
    menu_sha = hashlib.sha256(menu.read_bytes()).hexdigest()
    base_sha = hashlib.sha1(source.read_bytes()).hexdigest()
    note = ROOT / 'build/deploy/bazar-tarjeta-27-11.md'
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text(f"""# Tarjeta Bazar privada - 27/11/2026

Preparado localmente. Sin instalar en servidor, sin R2 y sin Discord.

## Archivo de servidor

- Local: `build/menus/DeluxeMenus/gui_menus/bazar.yml`
- Destino: `plugins/DeluxeMenus/gui_menus/bazar.yml` (menu `astralmenu_bazar`).
- SHA-256: `{menu_sha}`.
- Subir exclusivamente este YAML; no reemplazar la carpeta completa ni config.yml.
- Recarga de consola: `dm reload`. El menu solo no requiere apagar ni reiniciar.
- AstralBazar ya debe estar instalado, con `publico: false`; no cambia su JAR ni configuracion.
- Comprobar `dm open bazar ByTrainx`, permiso `astral.bazar.usar`, clic y apertura de `/bazar`.
- Con jugador sin permiso, comprobar que sigue viendo Intercambio en los ocho slots.
- Revisar consola por errores de requisitos o menus y comprobar el arte con cliente real.

## Pack FINAL privado

- Base local: `{source.relative_to(ROOT).as_posix()}`.
- SHA-1 base: `{base_sha}`.
- FINAL local: `{final.relative_to(ROOT).as_posix()}`.
- SHA-1 FINAL: `{sha}`.
- Solo agrega/reemplaza los 24 recursos propios `bazar_bazar_0` a `bazar_bazar_7`.
  Todas las otras entradas conservan sus bytes. No usar el ZIP publico como FINAL.
- Claude debe incorporar el arte final y volver a generar antes de publicar en R2.
  Si existe un FINAL posterior, usar esa base para conservar las otras entregas.
- Al publicar: mismo objeto/URL de resource pack, verificar descarga y actualizar
  `resource-pack-sha1` en `server.properties` con el SHA-1 del FINAL realmente publicado.
  Esto requiere reinicio completo coordinado con el dueno o el reinicio diario;
  no reiniciar ahora. Los clientes deben cargar el pack nuevo.
- Sin el pack actualizado puede verse el item de reserva (PAPER); el comando sigue funcionando.
- No subir mundos, no sustituir `world` ni usar Worlds > Upload.
- El principal documentado es Empower; confirmar el destino remoto antes de instalar.

## Arte Gemini y apertura futura

Guardar la tarjeta terminada, incluyendo texto, en
`datapack-src/pack-source/ref/gemini/tarjeta_bazar.png`.
Tamano final exacto: **72 x 36 px, proporcion 2:1**. Recomendado dibujar a
**1152 x 576 px** (misma proporcion). El generador recorta al centro y escala;
con proporcion distinta se pierde contenido en los bordes. Sin imagen se usa BAZAR / ORDENES provisorio.

`BAZAR_PUBLICO = False` en `datapack-src/menus.py` conserva Intercambio para jugadores
sin `astral.bazar.usar`; Bazar tiene prioridad 1 y el respaldo prioridad 2.
Al autorizar la apertura, poner True y regenerar: solo queda Bazar, sin requisito.
Coordinar tambien `publico: true` de AstralBazar, que valida el acceso por separado.
`/trade <jugador>` se conserva en ayuda y el comando AxTrade no cambia.

## Reproduccion y verificacion

Desde datapack-src: `python menus.py`, `python build_pack.py pack-source`,
`python deploy_bazar_tarjeta.py`, `python -m unittest test_bazar_tarjeta`.
El armado FINAL sigue el patron privado de delta sobre el ultimo FINAL;
no recompone los assets privados de BetterModel ni los copia al pack publico.
Antes del commit publico, desde raiz: `python tools/verificar_terceros.py`.

Pendientes: arte definitivo, prueba visual del dueno, R2, instalacion y consola remota.
No anunciar en Discord mientras siga privado.
""", encoding='utf8')
    print('Base:', source)
    print('FINAL:', final, sha)
    return source, final, sha


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='FINAL privado de partida; por defecto el mas reciente')
    generate(parser.parse_args().base)
