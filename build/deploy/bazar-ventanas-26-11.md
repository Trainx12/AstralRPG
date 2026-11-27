# Bazar 1.3.0 — ventanas con el arte Gemini nuevo (26/11, privado)

Arte: 7 imagenes pedidas a Gemini (una por ventana + tarjetas de cantidad), privadas en
`.local/gemini/refs-26-11/bazar/g_*.jpg`. Armado: `python datapack-src/ventanas_bazar26.py` (deforma cada imagen a la
grilla del cofre). Confirmar orden, Vender equipo y Confirmar equipo siguen con el arte de 1.1.0.

| Que | Local | Destino |
|---|---|---|
| Plugin 1.3.0 (titulos-glifo nuevos + botones ubicados como el dibujo) | `build/bazar/AstralBazar.jar` | `plugins/update/AstralBazar.jar` |
| Pack FINAL 0312be09 (= 0fc13619 en vivo + fuentes del Bazar nuevas) | `<privado>/build/entregas/bazar-ventanas-26-11/AstralRPG-Textures.zip` | R2 (`tools/subir_pack_r2.py`) + `resource-pack-sha1` |

Jar y pack van JUNTOS en el mismo reinicio (los caracteres de las ventanas viejas cambiaron de lugar).
Pack: subirlo justo antes de reiniciar. Sigue `publico: false` (solo ByTrainx).

Prueba local Paper 26.1.2: 634 comprobaciones, 0 fallas (`tools/probar_bazar_paper.py`).

Casilleros nuevos: Inicio categorias 0-1/9-10/.., abajo 45 Buscar, 46 Mis ordenes, 47 Vender inventario, 48 Vender
equipo, 49 <, 50 pagina, 51 >, 53 Cerrar. Producto: item en 4, tarjetas 4x2. Cantidad: 4 ventanas (instantanea
compra/venta, orden compra/venta), tarjetas 3x2, A mano 28-34. Precio: tarjetas 2x3 (columna 4 libre).
Mis ordenes: Cobrar 45-46, < 47, pagina 48, > 49, Volver 50-51, Cerrar 52-53. Vender inventario: Volver 45-46,
Confirmar 48-50, Cerrar 52-53.
