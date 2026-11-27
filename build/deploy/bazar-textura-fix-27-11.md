# Tarjeta Bazar privada - 27/11/2026

Publicado en GitHub y R2, con SHA-1 instalado en Empower. Activacion en el
reinicio diario del 28/11/2026 a las 05:00 Argentina; no se envio reinicio manual.
Prueba visual en Minecraft pendiente despues del reinicio. Sin Discord por ser privado.

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

- Base local: `.local/bazar-textura/pack-instalado.zip`.
- SHA-1 base: `7ed24a98670fa21cbb13f559c9d0cda41f806422`.
- FINAL local: `.local/terceros/AstralRPG-privado/build/entregas/bazar-textura-fix-27-11/AstralRPG-Textures.zip`.
- SHA-1 FINAL: `4ea7ae310735ffafc1e2086830cce2eb7289b31d`.
- Solo agrega/reemplaza los 24 recursos propios `bazar_bazar_0` a `bazar_bazar_7`.
  Todas las otras entradas conservan sus bytes. No usar el ZIP publico como FINAL.
- Arte actual: `datapack-src/pack-source/ref/gemini/bazar_bazar.png`, puesto Gemini
  con los textos BAZAR / ITEMS ASTRAL superpuestos por `services_ui.py`.
- Al corregir un servidor, usar `--base` con el ZIP descargado y verificado de R2;
  no incorporar entregas posteriores que todavia no fueron instaladas.
- Al publicar: mismo objeto/URL de resource pack, verificar descarga y actualizar
  `resource-pack-sha1` en `server.properties` con el SHA-1 del FINAL realmente publicado.
  Esto requiere reinicio completo coordinado con el dueno o el reinicio diario;
  no reiniciar ahora. Los clientes deben cargar el pack nuevo.
- Sin los recursos del cartel, el cliente muestra la textura faltante morada y negra.
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

Pendientes: carga del SHA-1 nuevo con el reinicio diario y prueba visual del dueno.
No anunciar en Discord mientras siga privado.

## Diagnostico y verificacion de esta correccion

- El servidor activo comprobado es Empower (Running); Aternos es la copia historica.
- El menu remoto coincide byte por byte con el YAML local y ya solicita las ocho piezas Bazar.
- R2 y server.properties usaban 7ed24a98: ese pack no contiene los 24 recursos del cartel.
- La imagen elegida por el dueno coincide byte por byte con bazar_bazar.png versionado.
- Se genero sobre el ZIP realmente descargado de R2, sin incorporar Corazon Astral ni otras entregas pendientes.
- Verificadas las ocho cadenas item -> modelo -> textura y la reconstruccion exacta del cartel.
- Verificado que todas las entradas previas fuera de los 24 recursos conservan sus bytes.
- Cuatro pruebas de test_bazar_tarjeta aprobadas.
- No requiere subir YAML, JAR ni mundos; solo publicar el FINAL y actualizar el SHA-1.
- No reiniciar por esta tarea: la carga del SHA-1 nuevo queda para el reinicio diario de las 05:00 Argentina.
- No anunciar en Discord: la tarjeta mantiene el permiso privado astral.bazar.usar.

Comando aislado desde la raiz:

```text
python datapack-src/deploy_bazar_tarjeta.py --base .local/bazar-textura/pack-instalado.zip --output .local/terceros/AstralRPG-privado/build/entregas/bazar-textura-fix-27-11 --note build/deploy/bazar-textura-fix-27-11.md
```

## Despliegue comprobado

- R2 actualizado; descarga publica verificada con SHA-1 `4ea7ae310735ffafc1e2086830cce2eb7289b31d`.
- `server.properties` releido: solo cambio `resource-pack-sha1` al mismo valor.
- Copia anterior de propiedades guardada exclusivamente en `.local/bazar-textura/`.
- Servidor Running; consola consultada sin avisos relacionados con Bazar, DeluxeMenus o el pack en las ultimas 120 lineas.
- Reinicio diario comprobado en la API: aviso a las 04:50 Argentina y reinicio diez minutos despues (05:00).
- No se enviaron comandos, recargas ni reinicios; no se tocaron permisos, plugins ni mundos.
- No se despliega en Aternos: la instancia activa comprobada es Empower.
