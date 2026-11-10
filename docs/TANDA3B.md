# Esqueletos de mazmorra y creeper fantasma

Preparados sin desplegar. Generadores: `mobs/creatures_tanda3b.py`,
`mobs/tanda3b.py`, `mobs/tanda2.py`. Instalacion exacta en
[`build/deploy/tanda3b.md`](../build/deploy/tanda3b.md).

## Detalles visuales y diferencias finales

Geometria y pixel art propios. Huesos con ruido por cara, luces superiores,
bordes oscuros y desgaste; tela con costuras y flecos, metal con oxidacion,
tablones con vetas y remaches. Craneo cuadrado, ojos y nariz oscuros,
mandibula y cuatro dientes separados. Extremidades finas con articulaciones
y bandas de cuero. Idle, marcha y ataque distintos de la animacion del creeper.

| Modelo | Detalles implementados | Diferencias respecto de la foto |
|---|---|---|
| `astral_esq_arquero` | Huesos frios, pieles gris azuladas, falda de tiras, bandas, arco oscuro largo con cuerda y flecha, carcaj con tres astiles | Pose de reposo mas vertical; arco mas estrecho y flecha horizontal. Pieles menos voluminosas; no reproduce la pose de tiro diagonal de la foto. |
| `astral_esq_escudero` | Casco con protectores laterales, pechera, dos hombreras remachadas, escudo claro de cuatro tablones y borde | La referencia muestra la coronilla mas descubierta; nuestro casco cubre mas. Escudo algo mas estrecho y en posicion de reposo. |
| `astral_esq_nigromante` | Capucha abierta con interior oscuro, tunica larga de siete faldones desiguales, gema roja en pecho y baston curvo; brazo levantado sosteniendo orbe dorado con nucleo blanco y chispas | Baston al otro lado; orbe mas pequeno y sin bloom de shader. Capucha y manga mas regulares; roturas de tela propias. |
| `astral_esq_espadachin` | Cuero ligero, correa diagonal, una hombrera oxidada y sable ancho de filo escalonado curvo | Sable levantado, no horizontal como en la foto; curva escalonada mas angular. Postura mas simetrica. |
| `astral_esq_guardian` | Huesos verdosos, musgo asimetrico, casco, espada recta larga, escudo verde con borde celeste y remaches | Espada mas baja y escudo en reposo; musgo mas fragmentado. La franja del casco y el patron de tablones son propios. |
| `astral_creeper_fantasma` | Cabeza/cuerpo y cuatro patas cortas, sin cara, hielo celeste con manchas azules y destellos blancos; alfa parcial 110/155/160/180/235 y blancos opacos | La vista local no reproduce la iluminacion ni el hielo del shader de la referencia. BetterModel conserva el alfa al convertir, pero falta comprobar mezcla/transparencia desde un cliente. |

Los brillos estan pintados; no se afirma emision de luz real. Los patrones no
se importaron de las referencias. No hay assets ni mapas de terceros nuevos.

## Revision visual

Se miraron las dos referencias y se identificaron craneos cuadrados, huesos
finos vendados, cinco equipos distintos, hielo sin cara y cuatro patas.
Paleta principal del plan: `#d8d2b4`, `#b9b28f`, `#7f8a7c`,
`#3a86d9`, `#7fc8ff`, `#eaf6ff`.

Cuentagotas sobre las imagenes locales (coordenadas absolutas x,y):

| Muestra | Punto | RGB |
|---|---|---|
| Arquero, sombra fria | 89,59 | `#317776` |
| Escudero, hueso iluminado | 270,117 | `#d0d89c` |
| Nigromante, tunica | 443,189 | `#47411d` |
| Espadachin, hueso | 576,141 | `#c6daa9` |
| Guardian, musgo | 750,197 | `#4e7033` |
| Hielo celeste | 562,90 | `#89c9ff` |

Las muestras orientan el tono; se compenso el tinte verde y la iluminacion
de las capturas con los colores indicados por el plan. No son texturas copiadas.

1. Primera vuelta: rostros demasiado agrietados, sable fino y abertura de
   capucha poco oscura. Se protegieron ojos/nariz durante el desgaste,
   se ensancho el sable y se agrego sombra bajo la capucha.
2. Segunda vuelta: gema del baston tapada por la cabeza y orbe junto al
   hombro. Se alargo y desplazo el remate y se levanto el brazo del orbe.
3. Tercera vuelta: articulaciones beige en el arquero y espada del guardian
   oculta por el cuerpo. Se enfriaron/enverdecieron articulaciones y se separo
   la espada. Se renderizo nuevamente la lamina final y las cuatro vistas.

Vistas propias publicas: `build/previews/tanda3b.png`, con jugador de 1,8
bloques y escala comun de 80 px/bloque. Comparaciones locales ignoradas:
`build/previews/astral_esq_<variante>-comparacion.png` y
`build/previews/astral_creeper_fantasma-comparacion.png`, con referencia,
frente, costado, 3/4 y aproximacion ortografica al angulo de la foto.

## Integracion

El catalogo central conserva SKELETON/STRAY para contar las plazas originales.
Cada uno se invoca como reserva invisible, inmovil e invulnerable. Ocupa su
plaza de la cola desde el principio. El controlador activo revisa cada cinco
ticks y usa `foreach` para una tirada independiente 30/20/15/20/15 por reserva.
Consume su etiqueta antes de invocar y retirarla; la copia de cada clase para
esa sala recibe las etiquetas de pertenencia y llama `mob/roll` una sola vez.
No se infiere la sala buscando al controlador mas cercano. Los ayudantes del
jefe de Minas reciben `.companion`; los demas `.wave`. Reset y limpieza siguen
usando las mismas etiquetas. Wither de Forja y Santuario quedan sin cambios.

Vida base 20, guardian 26; escala 87/3/10 por el mecanismo existente. Se
conserva tambien la tirada de elite que ya hacia `mob/roll`. Escudero lento,
espadachin rapido, guardian normal; arquero y nigromante huyen a menos de
cuatro bloques. Flecha con lentitud de dos segundos; hechizo cada 80 ticks,
sin invocaciones. Escudero recibe 45% del dano en un cono frontal de 110 grados.

El Skript solo reemplaza spawns NATURAL de creepers en `world`: no aumenta
su cantidad ni vuelve a tirar para CUSTOM. Constantes `GHOST_CHANCE=30`,
`GHOST_DAMAGE=4`, `GHOST_POWER=4`, `NORMAL_POWER=3` en `mobs/tanda3b.py`.
Potencia nativa 12 y multiplicador adicional x4 en el evento de explosion,
antes de la escala/defensa HIGH de `astral_gameplay.sk`. La potencia nativa
tambien influye en alcance y dano: no se promete que el dano final a cada
distancia sea exactamente cuatro veces el de un creeper de potencia 3.

La hitbox de los esqueletos se escala segun el alto total de modelo y equipo;
el ancho no coincide exactamente porque `minecraft:scale` es uniforme. El
creeper mantiene su caja vanilla y no usa `Glowing`.

Referencias tecnicas: [foreach](https://wiki.mythiccraft.io/mythicmobs/skills/mechanics/ForEach),
[pesos de randomskill](https://wiki.mythiccraft.io/mythicmobs/skills/mechanics/randomskill),
[fleeplayers](https://wiki.mythiccraft.io/mythicmobs/Mobs/ai/goals/fleeplayers) y
[triggers](https://wiki.mythiccraft.io/mythicmobs/Skills/Triggers).

## Alcance de las pruebas

Pasaron 163 pruebas (`python -m unittest discover -p "test_*.py"`) y
`python verify.py`. Pruebas de cantidades para 1/2/5 jugadores, topes, pesos, pertenencia de sala,
animaciones, texturas y alfa convertido. Carga local real: Paper 26.1.2,
BetterModel 3.6.0 (34 modelos), MythicMobs 5.13.0 y Skript 2.17.1.
Prueba real de relevo: 20 reservas -> 20 variantes, sin reservas restantes y
con controlador conservado; aparecen distintas clases. Potencia NBT 12.
Skript recargado sin errores tras corregir la expresion de orientacion.

La instancia aislada no tiene todos los plugins de produccion: la primera
carga del datapack informa referencias de ExcellentEnchants ausentes en ese
entorno. No son errores de las funciones de Tanda 3b. Logs privados locales.
Quedan por probar con jugador: tiros, hechizos, huida, defensa frontal,
explosion con defensa/tier, spawn natural y aspecto/animaciones/transparencia
en cliente. No se modifico el servidor publico.
