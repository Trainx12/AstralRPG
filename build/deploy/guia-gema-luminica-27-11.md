# Gema Luminica en la Guia Astral — 27/11/2026

La ampliacion conservaba solo recetas y eliminaba `guia/drops`, incluida la ficha
de la Gema Luminica. Se conserva el indice actual y se recupera el acceso desde
Materiales > Donde se consiguen. No cambia recetas, drops ni resource pack.

Fuente: `datapack-src/guia_ampliacion.py`. Menus regenerados con `guia_cofre.menus()`.

Instalacion pendiente de confirmar el panel activo (Aternos o Empower):

- Subir `build/menus/DeluxeMenus/gui_menus/g_atlas_seccion_materiales.yml`,
  `g_guia_materiales.yml` y `g_guia_drops.yml` a `plugins/DeluxeMenus/gui_menus/`.
- Comprobar que `gui_menus` en `plugins/DeluxeMenus/config.yml` registra los tres;
  ya figuran en `build/menus/DeluxeMenus/config-guia.yml`.
- Ejecutar `dm reload`; revisar consola y abrir Guia > Materiales > Donde se consiguen.
- Confirmar la ficha Gema Luminica: cofres de estructuras del Overworld (25%).
- Probar Volver. No requiere reinicio ni archivos del mundo.

Anuncio listo para cuando este instalado: «La Guia Astral vuelve a mostrar donde
conseguir los materiales, incluida la Gema Luminica. Entra en Materiales y luego
en Donde se consiguen».

Pruebas: `python -m unittest test_guia_cofre test_guia_atlas`.
Despliegue y anuncio pendientes; no se enviaron mensajes a Discord.
