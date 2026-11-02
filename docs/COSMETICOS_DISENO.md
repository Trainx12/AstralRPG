# Galeria personal de cosmeticos

Paleta elegida por la correccion del dueno: azul petroleo, marfil y oro antiguo,
con gemas turquesa y ambar. El rosa de la primera propuesta fue reemplazado.

El marco se creo con la herramienta integrada ImageGen y se guardo en
`datapack-src/pack-source/ref/cosmeticos-illustrated-frame.png`.
La referencia de calidad fue el marco existente de la gacha de cosmeticos.
La propuesta inicial no se usa en el paquete final.

Generador del marco adaptado, emblemas y fuentes: `datapack-src/cosmeticos_ui.py`.
Integracion y permisos: `datapack-src/cosmeticos.py`. Se mantienen los catorce
titulos, sus colores originales al equiparlos y el comando `/titulo`.
La galeria usa seis filas, catorce insignias, un enlace a la gacha,
regreso al atlas y un boton ancho para quitar el titulo sin perder la coleccion.

Vistas previas: `build/Servicios-preview/cosmeticos-mixta.png` y
`build/Servicios-preview/cosmeticos-completa.png`. Son ejemplos de una coleccion
parcial y una completa; no representan los permisos de un jugador real.

Regenerar desde `datapack-src/`:

```text
python cosmeticos.py
python cosmeticos_ui.py
python build_pack.py pack-source
python -m unittest test_cosmeticos_ui test_adventure_ui test_viajes_mazmorras test_market_ui test_gacha_ui
```

## Prompt de la version final

```text
Use case: precise-object-edit / game-asset. Recolor and refine this fantasy RPG cosmetics collection inventory frame. Preserve the exact front-facing composition, silhouette, proportions, detailed pixel-art quality, empty center, blank title plaque and genuine transparency outside. User dislikes pink: REMOVE ALL pink, rose, magenta, mauve and purple anywhere. New sophisticated royal palette: DEEP PETROLEUM BLUE and DARK TEAL velvet/satin, AGED ANTIQUE GOLD metal (not rose gold), WARM IVORY columns and ribbons. Gemstones are TURQUOISE, icy pale cyan and a few WARM AMBER gems. Top-left crown on deep dark teal velvet cushion; top-right hand mirror with a deep blue starry glass and antique-gold filigree, tiny turquoise/amber perfume bottles and ivory feather. Side curtains dark petrol teal with ivory satin ribbons, fine gold stitching and small opaline turquoise pendants. Bottom brooches and rings antique gold with turquoise and amber, lower right crystal cluster cyan and honey amber instead of violet. Large uninterrupted EMPTY dark navy/petrol rectangular interior. Blank dark petrol title plaque unchanged. Elegant medieval heraldic wardrobe, prestigious cabinet of medals, sober and rich, NOT candy-colored. No new text, no grid, no slots, no buttons, no watermark. Keep all outer transparency; keep the whole frame visible.
```
