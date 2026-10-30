# Mazmorras nuevas: preparacion y recorrido de revision

Estado local: generadores y recortes preparados. **Ningun mundo se modifico en Aternos.** Las entradas nuevas
estan deshabilitadas hasta revisar piso, llegada, altura libre y espacio de combate dentro de Minecraft.
El usuario pidio preparar ubicaciones sugeridas para hacer esa revision.

## Orden y ubicaciones propuestas

Son centros de salas, no coordenadas ya probadas con un jugador. Puede ser necesario moverlos o construir
un piso/puente. Primero recorrer en creativo; despues probar el combate en supervivencia.

| Mundo | Salas sugeridas (X, Y, Z) | Final |
|---|---|---|
| `bosque` | (1440.5,104,1568.5) → (1504.5,107,1504.5) → (1600.5,97,1440.5) | Chaman |
| `tumba` | (-192.5,83,128.5) → (-128.5,72,-64.5) → (96.5,73,-192.5) | Momia |
| `mina` | Se conservan sus cuatro salas e identificadores actuales | Guardian |
| `cumbre` | (-128.5,79,0.5) → (0.5,115,0.5) → (96.5,97,0.5) | Yeti |
| `forja` | (1536.5,224,1900.5) → (1456.5,210,2032.5) → (1536.5,200,2304.5) | Golem de Forja |
| `santuario` | (-329.5,51,65.5), una arena con cinco oleadas de un jefe cada una | Cangrejo → Chaman → Momia → Yeti → Golem, todos Ancestrales |
| `arena` | Entrada propuesta (-171.5,-44,-2282.5) | Solo PvP, sin premios ni progreso |

En la Forja hay lava y magma. Preparar plataformas y revisar especialmente la segunda y tercera sala.
Se usa **un solo volcan: el del sur** de `volcan gigante.zip`. El recorte preparado excluye el volcan
del norte; las tres salas pertenecen al mismo recorrido de la Forja. No importar el mapa completo.
Decision confirmada por el usuario para evitar que los jugadores se pierdan.
En el bosque hay arboles altos y desniveles; el Yeti necesita una superficie mas amplia que la del jugador.
En el Santuario se conserva la isla inicial y la construccion del reloj para ambientacion; la arena sugerida
esta en la isla inicial y necesita comprobar que los jefes grandes no caigan al vacio.

El spawn original de la arena (-32,70,48) cae en el vacio. La propuesta usa la zona de estadio donde estaba
el jugador guardado, y se comprobo que hay piedra a Y=-46. En el desierto el spawn original (35531,60,35496)
es una plataforma de servicio; las salas se proponen en el escenario principal, cerca del origen.

El Cangrejo sigue en las playas del mundo normal. `volcan.zip` sigue de reserva.
El Santuario se abre despues del titulo Portador de la Estrella; no bloquea el epilogo inicial.

## Recortes privados preparados

Estan en `.local/mapas/preparados/`, ignorados por Git. **No publicar ni agregar al repo.**

| Archivo | Uso | Tamaño aproximado |
|---|---|---|
| `bosque-regiones.zip` | Bosque Sombrio | 1.6 MB |
| `desierto-regiones.zip` | Tumba del Rey de Arena | 2.0 MB |
| `nieve-regiones.zip` | Cumbre Helada | 1.5 MB |
| `forja-regiones.zip` | Corazon de la Forja | 5.9 MB |
| `santuario-regiones.zip` | Santuario Celestial | 0.8 MB |
| `arena-regiones.zip` | Arena PvP | 3.7 MB |

Cada ZIP contiene solo `region/*.mca` recortados por chunks; no incluye `level.dat`, jugadores, entidades,
datapacks ni configuraciones originales. La limpieza reemplaza command blocks, structure blocks, jigsaw
y spawners por ladrillos de piedra, quita su logica y vacia inventarios/loot de los cofres originales.
Los bloques y la decoracion restantes se conservan. Los archivos descargados no se modificaron.

`datapack-src/mapas.py` permite repetir la inspeccion y los recortes sin dependencias aparte de Pillow,
que el proyecto ya usa. Las vistas topograficas estan en `.local/mapas/` y tampoco se publican.

Ejemplo (desde `datapack-src`):

```text
python mapas.py <carpeta-Downloads> --map bosque
python mapas.py <carpeta-Downloads> --map bosque --prepare 1360 1360 1695 1647 --out ../.local/mapas/preparados
```

Limites usados: desierto `-272 -272 191 223`, nieve `-208 -96 191 95`, forja `1360 1792 1647 2399`,
santuario `-432 -144 143 271`, arena `-560 -2624 15 -2129`.

## Instalar y revisar una a la vez

1. Crear un mundo nuevo con el nombre del cuadro, usando los comandos generados en
   `build/mazmorras/<nombre>/comandos.txt`. Para PvP: `build/arena/comandos.txt`.
2. Apagar el servidor. Confirmar en el panel cual es la carpeta de ese mundo nuevo; en la disposicion
   26.1 del servidor sera `world/dimensions/minecraft/<nombre>/region`. Subir ahi los `.mca` del recorte.
   **Nunca Worlds → Upload sobre `world`, ni reemplazar `mina`, ni subir el ZIP original entero.**
3. Encender. Aplicar reglas del mundo y recorrer las coordenadas propuestas con OP en creativo.
   Los comandos de teletransporte del recorrido estan comentados en el `.txt`; cambiar `<jugador>`.
4. Ajustar centros, llegadas y radios en `datapack-src/mobs/mazmorras_data.py`.
   Para habilitar una mazmorra revisada, agregar `enabled=True` a su definicion en `DEFINITIONS`.
   En la arena, cambiar `ARENA['enabled']` a `True` y confirmar `arrival`.
5. Regenerar con `python mobs/mazmorra.py`, subir los YAML de esa mazmorra en `mobs/` y `skills/`,
   y hacer `mm reload`. Crear sus controladores y NPC una sola vez con los comandos del `.txt`.
6. Probar todas las oleadas, abandonar una sala para probar su reinicio, terminarla con dos jugadores,
   volver durante el cooldown y comprobar el credito de historia. Recien entonces abrir el acceso.

Las nuevas mazmorras son compartidas, como las Minas; no hay instancias separadas por grupo.
Su dificultad aumenta la cantidad de enemigos cuando hay dos o mas jugadores. Los jefes reutilizan
sus modelos, fases, stats y drops existentes. Los recuerdos de historia se acreditan a los jugadores
cercanos al limpiar la sala final, aunque el cofre este en cooldown.

El Santuario usa una sola sala con cinco oleadas: evita que se activen cinco controladores a la vez.
Sus Ancestrales conservan el combate y los afijos; no anuncian un evento global ni desaparecen por tiempo.

La arena tiene `keep_inventory`, PvP solo en ese mundo y sin mobs naturales; se guardan las mascotas
al entrar. Las misiones excluyen ese mundo. Los comandos para apagar PvP en los demas mundos estan
en su `.txt`, pero solo se ejecutan para los mundos que existan.
