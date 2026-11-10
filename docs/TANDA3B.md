# Tanda 3b v3: Creeper Nuclear y esqueletos de alta densidad

Implementacion sobre `315ab9d`, sin desplegar. Generadores propios:
`datapack-src/mobs/creatures_tanda3b.py`, `tanda3b.py`, `preview_tanda3b.py`,
`entrega_tanda3b.py`. Instalacion: [manifiesto](../build/deploy/tanda3b.md).
Santuario, Forja, controladores, cantidades y pesos de oleadas conservados.

## Diferencias iniciales contra las referencias

- Creeper: el hielo no corresponde al pedido. Faltaban camuflaje oliva/marron,
  rostro amarillo con fondo rojo, franjas de peligro y simbolo nuclear posterior.
- Todos los esqueletos: craneo chico respecto del cuerpo, huesos poco separados,
  poca superficie para fisuras, costuras y desgaste a 16 texeles/bloque.
- Arquero: empunadura del arco insuficientemente envuelta; escarcha y flecos poco legibles.
- Escudero: costillas demasiado continuas; hebilla sin hueco y cuencas poco profundas.
- Nigromante: faltaban espiral alrededor del baston y brillo separado en su gema.
- Espadachin: mango sin vendas individuales suficientes y correa cruzada incompleta.
- Guardian: faltaban mas costuras, articulaciones y contraste de los ojos bajo el casco.

## Tres vueltas de render y correccion

1. Texturas a **32 texeles/bloque como minimo** (caras redondeadas hacia arriba a texeles enteros),
   craneo 20% mayor, tronco/extremidades 10% mas compactos. Costillas delanteras y traseras
   separadas, hebilla hueca, correas cruzadas, costuras, nudos y vendas de empunaduras.
   Creeper opaco nuevo con sus cuatro patas cortas, luz facial y camuflaje original.
   Revision: franjas demasiado altas, paleta clara y placa de radiacion demasiado ancha.
2. Franjas limitadas al tercio central de cada pata, camuflaje mas oscuro, disco de radiacion
   integrado en la espalda y fisuras finas en el craneo. Revision: las cejas tapaban parte
   de las cuencas; faltaba ver la espalda en las comparaciones.
3. Cuencas profundas de geometria oscura bajo las cejas; vista trasera en cada comparacion.
   Baston con espiral de relieve y gema con hueso propio a brillo 15/15. Orbe conserva rayos,
   nucleo blanco y animacion de pulsacion. Render final revisado con escala de jugador.

Se conservaron las laminas de las vueltas 1 y 2 en `.local/coordination/`;
la tercera es `build/previews/tanda3b.png`. Las seis comparaciones nuevas estan en
`build/previews/<modelo>-comparacion.png`, con referencia, frente, costado, 3/4,
angulo de la foto y espalda. Contienen referencias ajenas: quedan locales e ignoradas.
Solo se publica la lamina conjunta de modelos propios y jugador de 1,8 bloques.

## Paleta y detalle final

Se miraron ambas referencias y sus zonas de hueso, metal, tela y camuflaje.
Muestreo del craneo azul cuantizado de la referencia: `#81c2a9`, `#64a287`,
`#49806c` (luces y sombras); se adaptaron a un tono mas frio para la escarcha.
La paleta nuclear pedida se mantiene como base: `#2f4a1c`, `#4c6b25`, `#6f8a2f`,
`#5a3d1a`, `#c9a227`; ruido por pixel y manchas propias, sin copiar el patron de la foto.
Rostro `#ffd21f`/`#ffe866` sobre `#7a1010`, peligro amarillo/negro y radiacion amarilla
sobre disco negro. Craneo base `#d8d2b4`, articulaciones `#b9b28f`, sombra `#7f8a7c`,
arquero azul `#8bbcc1`, guardian verdoso `#aab99a`, metal `#6d8582`, cuero `#43351f`.

| Modelo | Resultado | Diferencias finales contra la foto |
|---|---|---|
| Arquero | Craneo cuadrado grande, cuencas, dientes separados, fisuras, escarcha, tiras con flecos, carcaj, arco largo tensado con vendas y puntas | Arco y pose tienen curvas propias; el render no aplica luz ambiental ni shader de la foto. |
| Escudero | Casco y hombreras con remaches, cota en piezas, costillas separadas, hebilla hueca, escudo de tablones con clavos y marco metalico | Casco mas cerrado y escudo inclinado en otra pose; las abolladuras son desgaste pixelado y relieves cubicos. |
| Nigromante | Capucha profunda, dientes, tunica en capas rasgadas, cuerda y hebilla, baston espiral con gema luminosa, orbe grande y rayos | Orbe redondeado por cubos, no llamarada de shader; capucha propia y baston de otra curvatura. |
| Espadachin | Craneo grande, correas cruzadas, hombrera, bolsas, cimitarra curva con filo separado, guarda y mango envuelto | Cimitarra escalonada y pose abierta diferentes; no reproduce el sombreado fotografico. |
| Guardian | Huesos con musgo, casco, articulaciones, espada larga, escudo ancho con tablones, relieve, clavos y borde turquesa | Relieve en cruz propio; musgo cubico, sin vegetacion de shader. |
| Creeper Nuclear | Silueta vanilla, camuflaje oliva, cara amarilla sobre rojo oscuro, cuatro patas con chevron central, trebol nuclear atras | Manchas y ojos propios a mayor densidad; trebol simplificado al ancho del torso, franjas mas finas que la referencia. |

La densidad duplicada usa atlas 256x256 para cada esqueleto y 128x128 para el creeper.
Pack: **17.950.733 bytes** (17,12 MiB), frente a 17.705.571 bytes de v2: +245.162 bytes.
SHA-1: `a10a8bd6bbd4cbfd2f05a0cb007f4161aa833c61`. No cambia el formato de BetterModel.

## Comportamiento y migracion

ID activo `astral_creeper_nuclear`, nombre `&e&lCreeper Nuclear`.
`NUCLEAR_CHANCE=30`, `NUCLEAR_DAMAGE=2`, `NUCLEAR_POWER=2`, `NORMAL_POWER=3`.
Solo spawns NATURAL en el mundo Bukkit `world`. Potencia 6; multiplicador de dano x2
antes del tier y la defensa. Cara 15/15 en reposo; cuerpo con luz ambiental, 15/15 al
hincharse. Particulas verdes y amarillas suaves y refuerzo al preparar la explosion.

Se sustituyeron ID, etiqueta y skills en MythicMobs, Skript, tests, vistas y manifiesto.
El antiguo modelo de hielo y sus assets se retiran del pack. En una instalacion anterior
hay que retirar solo `plugins/BetterModel/models/astral_creeper_fantasma.bbmodel`.
El datapack se inspecciona sin modificarlo: no contiene el ID ni la etiqueta sustituidos.
Con 3b ya instalada no cambia el datapack ni se recrean controladores.

## Verificaciones y pendientes

Pasaron **163 pruebas en 53,226 s**, `python verify.py` y `git diff --check`.
Texturas de los seis modelos identicas pixel por pixel a sus bbmodel, 127 referencias
a submodelos resueltas en el ZIP y ningun asset del modelo retirado. Se copiaron 175
archivos de los seis modelos desde el convertidor local.

Pruebas automatizadas: pesos, cantidades/plazas por oleada, identidad de sala, limites de mundo,
potencia 6, dano x2, animaciones, densidad UV y ausencia del modelo retirado en el pack.
Conversion real con Paper 26.1.2, BetterModel 3.6.0, MythicMobs 5.13.0 y Skript 2.17.1,
recarga de Skript y spawn de las seis variantes. Consulta NBT: `ExplosionRadius: 6b`,
etiqueta `astral.nuclear`. Servidor de prueba solo en `127.0.0.1:25589`, detenido con `stop`.

El entorno local no tiene ExcellentEnchants: hay errores de sus modificadores de items,
sin relacion con esta tarea. MythicMobs emite avisos de ejemplos y al apagar puede intentar
registrar una tarea estando deshabilitado; se comprueba guardado y cierre completo.
Estos limites impiden afirmar que la consola completa este libre de errores.

Pendientes: revision visual del dueno, aspecto nocturno, animaciones y combate en cliente,
reemplazo natural real y protecciones de explosion en produccion; subida R2, instalacion,
reinicio y revision de consola. No desplegado en Empower ni Aternos.
