# Bazar: ventanas con diseño (25/11/2026)

Las 11 ventanas del Bazar con los diseños Gemini del dueño (`datapack-src/ventanas_bazar.py`). Sigue OCULTO:
solo ByTrainx (`astral.bazar.usar`), `publico: false`.

## Qué cambia
- `AstralBazar.jar` 1.1.0: el título de cada ventana es su dibujo (glifos del pack, `ventanas.yml` dentro del jar)
  y los botones dibujados se atrapan con ítems invisibles en todos sus casilleros. Cantidad, Precio, Confirmar
  orden y Orden pasan a 5 filas; Categorías a 6; Productos muestra 36 por página. `diseno: false` en config.yml
  vuelve a las ventanas simples sin recompilar (`/bazar admin recargar`).
- Pack FINAL `entregas/bazar-ventanas-25-11` **0fc136199bb2e3d95a305766f601c15d0066756d** = 6d57177d (Renacer de
  Minas + su ventana + insignias Dueño/Cazador, nunca subido) + fondos `font/bazar/*` (0xF600..0xF6AF).

## Subida
1. `plugins/update/AstralBazar.jar` (SHA-1 68a5b9f9…) — YA SUBIDO; entra en el próximo reinicio.
2. Justo antes de reiniciar: `python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/entregas/bazar-ventanas-25-11/AstralRPG-Textures.zip`,
   verificar la descarga pública y poner `resource-pack-sha1=0fc136199bb2e3d95a305766f601c15d0066756d`.
3. Reiniciar (aviso con tellraw + title). Sin el pack nuevo, las ventanas se ven vacías.

## Pruebas
`tools/probar_bazar_paper.py`: 722 comprobaciones, 0 fallas (incluye las 11 ventanas: filas, título-dibujo y
cada casillero de cada botón). El chequeo "sin tirar equipo al piso" ahora mira solo el equipo de la prueba
(antes contaba cualquier ítem suelto del mundo y fallaba a veces).
