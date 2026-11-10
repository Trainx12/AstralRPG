# Tanda 3b v2: esqueletos detallados y creeper fantasma

Implementacion sobre `5978cde`, sin desplegar. Fuentes: `datapack-src/mobs/creatures_tanda3b.py`,
`tanda3b.py`, `preview_tanda3b.py` y `entrega_tanda3b.py`. Instalacion exacta:
[build/deploy/tanda3b.md](../build/deploy/tanda3b.md).

## Decision tecnica: fantasma, sin variante nuclear

Minecraft Java 26.1 admite translucidez en modelos: selecciona la pasada segun el alfa del sprite.
La documentacion de migracion de NeoForged precisa que los items usan `Sheets#translucentItemSheet`
cuando hay pixeles parcialmente transparentes en el area UV de la cara. BetterModel usa paquetes
`item_display` y conserva esos pixeles al convertir nuestros modelos. Por eso se implemento el
paso A; no hace falta recurrir al nuclear ni agregar shaders.

Fuentes primarias consultadas para esta revision:

- [Mojang, Minecraft Java 26.1, Block Model Format](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-1).
- [NeoForged, cambios vanilla de materiales y seleccion de capas en 26.1](https://docs.neoforged.net/primer/docs/26.1/#materials-and-dynamic-layer-selection).
- [BetterModel, descripcion oficial del motor basado en item-display](https://github.com/toxicity188/BetterModel).
- [BetterModel, mecanicas MythicMobs compatibles, incluida brightness](https://github.com/toxicity188/BetterModel/wiki/MythicMobs-Compatibility).

Se comprobo tambien `BrightnessMechanic` del jar 3.6.0 local: admite `b`/`block`, `s`/`sky`
y filtro de parte `pid`. Creeper: brillo 15/15 tras crear el modelo tanto en spawn como en load.
Nigromante: brillo 15/15 solo en `orb`. Esto mantiene visibles esas partes en oscuridad;
no emite luz sobre los bloques ni produce bloom.

Hielo con azul neon `#2f8dff`, `#5fb6ff`, `#a8e3ff`, alfa 115/125/140/145/153
(45-60%) y destellos blancos opacos. Polvo celeste de tres particulas cada 12 ticks.
Se conserva `astral_creeper_fantasma`. El soporte tecnico esta documentado y el alfa convertido
esta comprobado; falta la inspeccion visual en un cliente Minecraft 26.1.2 con el pack instalado.
La vista CPU aproxima la mezcla sobre el fondo, sin simular shaders ni certificar el cliente.

## Referencias, diferencias iniciales y tres rondas

Se observaron las referencias locales antes de editar. Diferencias iniciales: craneos planos,
armas y brazos de reposo, escarcha sin cristales, casco y torso sin suficiente relieve,
orbe pequeno, tunica regular, sable poco expresivo, escudo musgoso angosto y fantasma palido.
Las texturas y la geometria nuevas son originales. No se copiaron pixeles de las referencias.

Paleta orientada por las muestras del trabajo anterior: hueso `#d0d89c` (270,117),
sombra fria `#317776` (89,59), tunica `#47411d` (443,189), musgo `#4e7033` (750,197).
Se conservan hueso `#d8d2b4`/`#b9b28f`, sombra `#7f8a7c`, tela marron y metal gris azulado;
el azul neon es el solicitado en v2. Las muestras son de la referencia local de esqueletos.

1. Ronda 1: se agregaron cejas, pomulos, mandibula escalonada, vertebras, esternon,
   pelvis, costuras y flecos; piernas asimetricas y brazos en accion. Al renderizar,
   el arco rotaba acostado con el brazo y las espadas no conservaban una pose legible.
2. Ronda 2: pivote propio para el arco vertical grande con cuerda tensa y flecha;
   cristales y pelo en hombros, cota en anillos separados, capucha profunda,
   orbe grande escalonado con nucleo blanco y ocho rayos, cuerda y faldones rasgados,
   espiral del baston, bolsitas y cresta/musgo. El render mostro que faltaba separar
   la orientacion de las hojas de la del brazo y ensanchar el escudo del guardian.
3. Ronda 3: pivotes de armas y canales de ataque, cimitarra a la cintura con punta
   curva hacia arriba, espada del guardian elevada, codo/mano ajustados a la empunadura,
   una sola hombrera del espadachin y escudo cuadrado con marco turquesa grueso y relieve.
   Se corrigio un hueso alzado que competia visualmente con la espada; se volvieron a
   generar frente, costado, 3/4 y aproximacion al angulo de foto para los seis modelos.

## Detalles y diferencias finales

| Modelo | Implementado | Diferencias restantes frente a la referencia |
|---|---|---|
| Arquero | Craneo frio con cejas/pomulos, cristales en cabeza/brazos, hombros con pelo por mechones, arco largo curvo oscuro tensado, flecha, carcaj con tres flechas y plumas, tiras y desgaste | Brazos mas frontales y arco al lado derecho del render; la flecha no toma toda la diagonal de la foto. Cristales y pelo son escalonados. |
| Escudero | Casco con borde y laterales, hombreras remachadas, cota de anillos, escudo claro de tablas/clavos con marco de metal adelantado | Cota con anillos cuadrados propios; el casco cubre mas coronilla. Escudo mas bajo y menos girado que en la foto. |
| Nigromante | Capucha profunda oscura y ojos claros, faldones con jirones finos, cinturon de cuerda anudado, baston con espiral y gemas rojas, gran orbe dorado con nucleo blanco y ocho rayos | Baston y orbe espejados respecto de la referencia. Orbe redondeado escalonado, sin bloom; la gema roja lleva reflejos pintados. |
| Espadachin | Vendas/panuelo, cuero con costuras, bolsas y cierres, una hombrera, cimitarra curva ancha con filo claro y mango envuelto, ataque de corte | Curva construida por segmentos de cubos, mas angular que la foto; postura menos abierta y panuelo mas corto. |
| Guardian | Musgo en craneo, hombros y piernas, casco con cresta, espada recta elevada, escudo cuadrado verde de marco turquesa grueso con relieve central y clavos | Escudo lleva relieve propio en cruz y una inclinacion menor; espada al otro lado del render. Musgo hecho de parches en relieve. |
| Fantasma | Forma vanilla sin rostro marcado, hielo azul neon con alfa parcial, luces blancas, brillo maximo y polvo celeste suave | No reproduce el shader, la refraccion ni el bloom de la captura. Falta aceptar el aspecto final en cliente. |

Desgaste determinista por cara: grietas de hueso, luces superiores, sombras de borde,
puntadas de tela, flecos independientes, madera con vetas y metal con oxido/remaches.
Animaciones `idle`, `walk`, `attack`; creeper `idle`, `walk`, `swell`.

Vista publica propia: `build/previews/tanda3b.png`, escala comun 80 px/bloque y jugador de 1,8 bloques.
Comparaciones con referencias de terceros solo locales e ignoradas por Git:
`build/previews/astral_esq_<variante>-comparacion.png` y
`build/previews/astral_creeper_fantasma-comparacion.png`. No publicar esas referencias.

## Combate e integracion

Valores v2: `GHOST_CHANCE=30`, `GHOST_DAMAGE=2`, `GHOST_POWER=2`, `NORMAL_POWER=3`.
Potencia nativa **6** y multiplicador de dano **x2**, antes de la escala/defensa HIGH del
Skript de gameplay. La potencia tambien afecta el radio y el dano vanilla: el dano final
a cada distancia no equivale a exactamente dos veces el creeper de potencia 3.
Solo reemplaza creepers NATURAL en `world`; excluye el resto de mundos y no repite CUSTOM.

Se conservan los pesos de esqueletos 30/20/15/20/15, el relevo de reservas, las plazas de oleadas,
los ayudantes y las etiquetas de sala. Vida base 20, guardian 26, tirada de tier 87/3/10.
Arquero aplica lentitud corta; nigromante lanza hechizo sin invocar; escudero recibe 45% del dano
por delante, espadachin rapido y guardian normal. Hitbox uniforme por alto del modelo/equipo:
el ancho de la caja vanilla no coincide exactamente con escudos y armas. Creeper con caja vanilla.

No se modificaron Santuario, Forja, controladores, datapack ni mundos en esta revision.
Para instalacion completa de 3b se conserva el manifiesto anterior de archivos/controladores;
para actualizar 3b ya instalada alcanza con seis modelos, mobs/skills tanda3b.yml, Skript,
resource pack y SHA-1. Requiere reinicio por cambio del pack en propiedades.

## Verificaciones y pendientes

Pasaron 163 pruebas en 48,758 s (`python -m unittest discover -p "test_*.py"`),
`python verify.py` y `git diff --check`. Los tests cubren pesos, plazas/topes con 1/2/5 jugadores,
identidad de sala, limites del spawn, potencia 6, multiplicador x2, animaciones y alfa convertido.
Comprobacion adicional del pack: las seis texturas convertidas coinciden pixel por pixel con
sus bbmodel y todas las referencias de submodelos de los seis mobs existen.

Carga local v2: 34 modelos convertidos; 176 mobs y 433 skills cargados en la instancia completa
de prueba; Skript recargado correctamente. Se invocaron nigromante, espadachin y fantasma con
las nuevas skills sin errores de esas mecanicas. Consulta NBT real: `ExplosionRadius: 6b`.
131 archivos de los seis modelos copiados del convertidor al arbol fuente del pack.
El servidor aislado usa Paper 26.1.2, BetterModel 3.6.0, MythicMobs 5.13.0 y Skript 2.17.1. No tiene
ExcellentEnchants: los errores de referencias a sus encantamientos en el datapack son una
limitacion conocida del entorno de prueba, ajena a los cambios de esta tarea. Al apagar tras
recargas, MythicMobs emitio `Plugin attempted to register task while disabled`; el servidor
termino de guardar y cerrar. `verify.py` emite un aviso de depreciacion de Pillow sin fallar.

Pendientes: revision visual del dueno, cliente para mezcla alfa y animaciones, combate real con
defensa/tier, subir a R2, actualizar archivos y propiedades del servidor, reiniciar y revisar consola.
No se desplego en Empower ni Aternos.
