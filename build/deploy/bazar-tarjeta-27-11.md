# Tarjeta Bazar privada - 27/11/2026

Preparado localmente. Sin instalar en servidor, sin R2 y sin Discord.

## Archivo de servidor

- Local: `build/menus/DeluxeMenus/gui_menus/bazar.yml`
- Destino: `plugins/DeluxeMenus/gui_menus/bazar.yml` (menu `astralmenu_bazar`).
- SHA-256: `4eb0b599f759f82d06869b98b7ffd60db6970ea0ff08a2bd2bd74a5245e168c9`.
- Subir exclusivamente este YAML; no reemplazar la carpeta completa ni config.yml.
- Recarga de consola: `dm reload`. El menu solo no requiere apagar ni reiniciar.
- AstralBazar ya debe estar instalado, con `publico: false`; no cambia su JAR ni configuracion.
- Comprobar `dm open bazar ByTrainx`, permiso `astral.bazar.usar`, clic y apertura de `/bazar`.
- Con jugador sin permiso, comprobar que sigue viendo Intercambio en los ocho slots.
- Revisar consola por errores de requisitos o menus y comprobar el arte con cliente real.

## Pack FINAL privado

- Base local: `.local/terceros/AstralRPG-privado/build/entregas/abrir-todo-27-11/AstralRPG-Textures.zip`.
- SHA-1 base: `7ed24a98670fa21cbb13f559c9d0cda41f806422`.
- FINAL local: `.local/terceros/AstralRPG-privado/build/entregas/bazar-tarjeta-27-11/AstralRPG-Textures.zip`.
- SHA-1 FINAL: `799e337a060e63317de40b9d03252e5e6e24ff5b`.
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
