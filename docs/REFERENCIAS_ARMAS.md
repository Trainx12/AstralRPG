# Referencias para las armas 3D

Ideas del dueño para pasar las armas a modelos 3D (como los Bastones de Mago, ver `datapack-src/varitas3d.py`).

Las imágenes son de **otros autores** (Slime Studio, Voxel Spawns, Deka, mcmodels, etc.), así que **no se suben al repo**.
Están solo en la PC del dueño, en `.local/referencias/armas/` (Git ignora esa carpeta). Se usan como inspiración de
estilo y colores; los modelos se hacen de cero, sin copiar ningún diseño.

## Estilo que le gusta al dueño
- Modelos de bloques con piezas que flotan (cristales, chispas).
- Partes que brillan y se animan (textura animada: late, titila o corre una luz).
- Ejemplo animado que le gustó: `https://api.mcmodels.net/storage/product-images/14458/01JZE1H18NC9JAKBRJNJPFPBMD.gif`
  (rueda de varitas con partes que brillan).

## Qué hay en cada imagen y para qué arma sirve

| Archivo (`.local/referencias/armas/`) | Qué muestra | Idea para |
|---|---|---|
| `guadana_acero_cuero.webp` | Hoja de acero con púas y un hueco curvo, mango curvo con cuero, pincho abajo | **Guadaña Umbría Menor** (la más simple) |
| `guadana_calavera_cadenas.png` | Hoja negra dentada, vara en zigzag, calavera con clavos arriba, cadenas con candados | **Guadaña del Ritual** |
| `guadana_neon_violeta.png` | Negra con bordes violeta brillante, dos hojas curvas, aros en espiral, rombo con runa, guarda en D | **Guadaña del Vacío** |
| `espada_y_guadana_cristal_turquesa.png` (derecha) | Hoja de cristal turquesa/azul, mango oscuro con un marco abierto, gancho abajo | **Guadaña del Archimago** |
| `guadana_hueso_turquesa.png` | Hoja blanca de hueso que se oscurece a azul, mano de hueso, cristales turquesa, cadena que cuelga | **Guadaña Astral** |
| `espada_y_guadana_cristal_turquesa.png` (izquierda) | Espadón de cristal turquesa con dibujo diagonal, guarda con aletas, gema en la guarda, pomo en gancho | **Espada del Coloso** (lleva Cristal Refinado) |
| `arco_hueso_turquesa.png` | Brazos azul oscuro con cristales turquesa, puntas de hueso, cuerda que brilla | **Arco del Viento** o **Arco Astral** |
| `varitas_01` a `varitas_07` | Varitas usadas para los Bastones de Mago (ya hechos) | Si sobran ideas: cuernos rojos → Hacha del Apocalipsis; halo de sol con plumas → Espada del Dios de la Guerra |

## Pendiente
1. Guadañas (5) → `guadana_1` a `guadana_5` (hoy usan texturas planas de `textures.py`).
2. Espadas, hachas y arcos. Los arcos tienen animación de tensado: hacen falta 4 modelos (normal y 3 de tensado).
