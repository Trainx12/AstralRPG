# Arsenal y marcos ilustrados

Los modelos finales se incluyen en `build/AstralRPG-Textures.zip`. Esta revision
no cambia daño, recetas, costos, clases ni permisos de descubrimiento.

## Armas

32 armas: cinco espadas, cinco bastones, seis guadañas (incluida la Umbría),
cinco hachas, cinco arcos, cinco lanzas y el guantelete. Los cuatro estados de
cada arco suman 47 modelos Minecraft.

- `espadas3d.py`: perfiles de hojas, sección con nervio y biseles, canales,
  guardas articuladas, monturas de gemas, cadenas abiertas y empuñaduras cruzadas.
  El Coloso usa facetas diagonales azul/turquesa; Dios de la Guerra usa un
  mosaico de calor rojo/naranja/dorado con una vena luminosa irregular.
- `weapon_details.py`: acabados de madera, metal, hueso, cuero y cristal;
  herrajes, grabados y engarces específicos para bastones, guadañas, hachas,
  arcos y guantelete. Las piezas de relieve siguen los giros locales de la hoja.
- `lanzas3d.py`: sustituye las cinco lanzas planas por modelos volumétricos:
  Recluta de acero, Centinela vegetal, Carmesí, guja del Vendaval y tridente Astral.
- `armas3d.py`: integra las espadas y acabados; las cuerdas diagonales usan pasos
  pequeños para que se mantengan continuas durante el tensado.
- `weapon_showcase.py`: renders con profundidad por píxel de los mismos elementos,
  giros y UV que se exportan. Genera PNG, un visor WebGL sin dependencias externas,
  fuentes `.bbmodel` editables y un ZIP de esas fuentes.

Las referencias privadas de otros autores permanecen en `.local/referencias/armas/`.
Los modelos, texturas y fuentes generados son originales; esas imágenes no se
incluyen en el paquete ni en los entregables.

Salidas para revisar:

- `build/previews/arsenal-detallado.png`: las 32 armas.
- `build/previews/espadas-antes-y-despues.png`: comparación con los modelos previos.
- `build/previews/*-detallados.png`: vistas ampliadas por familia.
- `build/previews/arcos-tensados.png`: los cinco arcos al máximo tensado.
- `build/armas3d/visor.html`: rotación, zoom y animación de materiales, sin servidor.
- `build/armas3d/blockbench/`: 32 archivos editables con atlas incorporado.
- `build/armas3d-editables.zip`: las fuentes para Blockbench.

## Menús

`adventure_ui.py` conserva las zonas de clic y reemplaza los marcos simples con
tres ilustraciones originales creadas con ImageGen a partir de la calidad visual
del Cronista y del Arsenal Arcano. Fuentes:
`pack-source/ref/{principal,expediciones,mazmorras}-illustrated-frame.png`.

- Atlas: observatorio azul y oro, libro estelar, astrolabio, constelaciones,
  pequeñas torres y cristales.
- Expediciones: nogal, latón, mapas, brújula, catalejo, vegetación y reliquias
  de distintos biomas.
- Mazmorras: basalto, columnas talladas, cadenas, calavera de guardián,
  braseros, amatistas y un sello cerrado en la base.

Los carteles se rotulan en el generador. Los cortes del marco se adaptan a la
grilla real del cofre; el inventario del jugador conserva sus huecos transparentes.
Los candados y sus requisitos se repiten en cada pieza de una tarjeta bloqueada.
Vista previa: `build/Servicios-preview/atlas-expediciones-mazmorras.png`.

## Regeneración y comprobación

Desde `datapack-src/`:

```text
python adventure_ui.py
python menus.py
python weapon_showcase.py
python build_pack.py pack-source
python -m unittest test_weapons3d test_adventure_ui test_viajes_mazmorras test_market_ui test_gacha_ui
python verify.py
```

Se comprueban coordenadas y giros del cliente, tamaño del icono, materiales y UV,
animaciones, estados del arco, modelos de tarjetas y permisos de viaje.
Las pruebas locales y los renders no sustituyen revisar escala en mano,
iluminación y navegación dentro de Minecraft después de instalar el paquete.
