# Santuario de companeros

Pagina artistica original de `/mascotas` para las seis primeras criaturas (el catalogo actual tiene 23 en tres paginas; ver `SERVIDOR.md`): Lobo del Bosque,
Cuervo Arcano, Golem de Piedra, Zorro Espectral, Dragoncito de Fuego y Fenix.
Paleta de madera oscura, bosque, piedra runica, bronce, cian y ambar; sin rosa.

El marco original se creo con ImageGen integrado. Fuente guardada en
`datapack-src/pack-source/ref/mascotas-illustrated-frame.png`.
La referencia de calidad fue el marco de expediciones.

Los retratos de las tarjetas se renderizan a partir de los modelos reales de
`mobs/creatures.py`, con el renderer existente de `mobs/build_models.py`.
El renderer admite ahora fondo transparente sin modificar su fondo predeterminado.

`mascotas_ui.py` genera el arte, modelos de item y fuentes. `menus.py` mantiene
los permisos, niveles, efectos e invocaciones. Cada parte de una tarjeta
verifica la misma mascota; las bloqueadas solo muestran ayuda. El boton ancho
DESCANSAR guarda la mascota actual con la orden existente (mascota 98).
Hay accesos al atlas y a la Gacha de Monturas. Se conservan todos los puntos
de obtencion de mascotas y el alcance de sus bonus en mazmorras.

Los glifos se dividen en imagenes menores a 256 px. El pie del marco es mas
alto para conservar al golem y al zorro debajo del inventario del jugador;
las posiciones de los huecos del cofre no cambian.

Vistas previas de colecciones de ejemplo (no son permisos de un jugador real):
`build/Servicios-preview/mascotas-completa.png` y `mascotas-mixta.png`.

Regenerar desde `datapack-src/`:

```text
python mascotas_ui.py
python menus.py
python build_pack.py pack-source
python -m unittest test_mascotas_ui test_cosmeticos_ui test_adventure_ui test_viajes_mazmorras test_market_ui test_gacha_ui
```

Las pruebas y renders locales no reemplazan revisar el menu dentro de Minecraft.

## Prompt del marco

```text
Use case: game-asset. Create one premium fantasy RPG PET SANCTUARY inventory FRAME texture. Reference image only for pixel-art craftsmanship and production quality, NOT an edit target. New portrait 4:5 front-on composition with genuine transparent exterior. A rich storybook sanctuary / magical companion refuge, carved dark oak branches and warm antique brass, mossy slate stone, deep forest teal interior, tiny warm amber lanterns, ivory accents and small cool cyan runes. NO PINK. Narrow ornate side borders with leaves, paw-print carvings, dangling charms and feathers. Incorporate exactly these six friendly Minecraft-style voxel companions into the BORDER, keeping center empty: upper left a small silver-gray wolf with yellow eyes looking inward; upper right a charcoal-black raven with violet glowing eyes perched on a branch; top center behind a large BLANK horizontal wood title plaque a small orange-and-gold phoenix with wings arched over the plaque; lower left a squat gray stone golem with a cyan crystal in its chest and a tiny moss tuft; lower right a cute pale icy-blue spectral fox with a fluffy tail; to the right of the title plaque a small red fire dragon curled around a brass lantern. All animals modest-sized and harmoniously integrated into the frame, NOT occupying the menu interior. Fine pixel-art material shading and tiny bright highlights, sumptuous carved details as polished as reference. Blank title plaque at x=28%..72%, y=13%..19%; large uninterrupted EMPTY dark forest/petroleum rectangular center at x=15%..85%, y=24%..91%. Footer with a small carved paw medallion and a warm folded blanket. Nature + arcane magic + companionship, welcoming rather than dangerous. No letters, numbers, buttons, slots, grid, perspective or watermark; no floating figures in interior.
```
