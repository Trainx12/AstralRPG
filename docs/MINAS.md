# Minas Astrales

## Mapas

Hay **siete construcciones para veinte minas**. Carbón, cobre, hierro, oro, esmeralda y diamante tienen cada uno su mapa, repetido en los tres tiers. El mapa de Netherita se usa para Restos ancestrales II y Netherita III. El pozo ocupa las mismas coordenadas locales en los siete mapas.

Para Hierro se usó el adjunto **mina.schem**, de 180 × 124 × 190 bloques. Se retiraron 16 bloques de comandos, el contenido de los contenedores y los datos interactivos de carteles y atriles. Se diseñaron las otras seis islas con terreno, edificios y paletas temáticas propias. Los otros adjuntos eran variantes PvP o mundos antiguos completos.

[Descargar los siete schematics](../build/minas/Mapas-Minas-Astrales.zip) · [Vista de las construcciones](../build/minas/Vista-Minas-Astrales.png)

También se compararon tres opciones públicas antes de elegir el adjunto.

- [15 Prison Mines de Premiere Setups](https://builtbybit.com/resources/free-15-prison-mines-premiere-setups.22712/). Pack gratuito de schematics individuales con descarga tras iniciar sesión.
- [4 Free Prison Mines de Jusserhead](https://www.planetminecraft.com/project/4-free-prison-mines-download-a-project-by-jusser-/). Cuatro temas y pozos de 31 × 31 × 21. El autor distribuye un mundo y aplica una licencia no comercial sin derivados.
- [27 Prison Mines de Horace Creations](https://www.planetminecraft.com/project/27-prison-mines/). Conjunto de construcciones de 250 × 250 con demo gratuita.

## Progresión inicial

El primer tier tiene piedra y mena. El segundo tiene mena y bloques compactos, seguido por Netherrack con restos ancestrales. El tercero se compone de bloques compactos y termina en bloques de netherita. La primera mina está abierta desde el inicio.

| Mina | Bloques en la anterior | Oro |
| --- | ---: | ---: |
| I · Carbón | — | — |
| I · Cobre | 350 | 55 |
| I · Hierro | 550 | 150 |
| I · Oro | 750 | 240 |
| I · Esmeralda | 1.000 | 350 |
| I · Diamante | 1.250 | 600 |
| II · Carbón | 1.600 | 1.000 |
| II · Cobre | 2.100 | 2.000 |
| II · Hierro | 2.600 | 3.500 |
| II · Oro | 3.200 | 4.800 |
| II · Esmeralda | 3.800 | 6.500 |
| II · Diamante | 4.500 | 10.000 |
| II · Restos ancestrales | 5.500 | 17.000 |
| III · Carbón | 6.500 | 26.000 |
| III · Cobre | 8.000 | 40.000 |
| III · Hierro | 9.500 | 60.000 |
| III · Oro | 12.000 | 95.000 |
| III · Esmeralda | 15.000 | 160.000 |
| III · Diamante | 20.000 | 300.000 |
| III · Netherita | 500.000 | 25.000.000 |

Netherita III exige además **25 horas de minería activa en Diamante III**. El tiempo avanza mientras el jugador está en esa mina y ha picado en los últimos diez segundos. El tiempo completo se guarda por minuto.

La progresión guarda el mayor rango abierto y los bloques de ese rango por UUID. El marcador muestra la mina actual, el siguiente desbloqueo, el lugar donde cuenta el progreso y su costo. El contador se detiene al cumplir el requisito y vuelve a cero al abrir el siguiente destino. La venta usa una lista de minerales, piedra y roca con precios propios y conserva el equipo y los objetos con datos personalizados. Las mezclas y los precios se ajustan en [minas.py](../datapack-src/minas.py).

Cada regeneración recorre 19.220 bloques en tandas de hasta 248 por tick. Se turnan las veinte minas, cada nueve minutos por mina a 20 TPS. Al comenzar se traslada a los jugadores del sector a la plataforma del vendedor. Los taladros reutilizan su área habitual dentro del pozo y cada bloque extra pasa por la misma protección y contador. Con Shift pican un bloque.

## Instalación

1. Los siete schematics están en el ZIP. Para regenerarlos localmente, ejecutar `python datapack-src/minas.py --schematic "C:/Users/Trainx/Downloads/mina.schem"`. Se preparan los siete mapas con origen en la esquina de la selección.
2. Extraer el ZIP y subir los siete archivos `.schem` a `plugins/WorldEdit/schematics/` y seguir [los comandos de instalación](../build/minas/instalacion.txt). Ejecutar los pegados en creativo con permisos de WorldEdit y `astral.minas.admin`. Comprobar el primer pozo en X 75–105, Y 73–92, Z 76–106 y la plataforma en X 89.5, Y 93, Z 70.5 antes de continuar.
3. Copiar [astral_minas.sk](../build/minas/Skript/scripts/astral_minas.sk) a `plugins/Skript/scripts/`. Requiere Skript, skript-reflect y Vault con EssentialsX. Actualizar [el datapack](../build/AstralRPG-Items.zip) para que en este mundo el área del taladro pase por la protección de minas.
4. Integrar la entrada `scoreboard.scoreboards.minas` antes de `astral` y las condiciones `am_*` de [la plantilla de TAB](../build/lobby/TAB/secciones-config.yml) en el `config.yml` activo. Mantener el orden para que el panel de minas tenga prioridad dentro de `astral_minas`. Usa la expansión ScoreboardObjectives de PlaceholderAPI, como el panel de diarias.
5. Verificar el piso del lobby en X 174.636, Y 100, Z 225.735 antes de invocar al aldeano, a cuatro bloques del de Expediciones. Recargar Skript y TAB. Ejecutar `/minasactivar` al terminar los pegados. Probar con un jugador en supervivencia el menú, la protección fuera del pozo, el contador y una venta mixta con herramientas y minerales.

## Estado en Aternos

Los siete schematics están cargados en WorldEdit. Se guardó la sección de TAB y se actualizó el datapack tras comparar el ZIP activo con el local. La única diferencia es la función que dirige el taladro al sistema de minas. Los dos scripts de minas quedaron deshabilitados después de probar el arranque. Aternos no ofrece skript-reflect en su catálogo y Skript rechazó las llamadas de esa dependencia. La dimensión, los pegados, los vendedores y el aldeano del lobby quedan pendientes de una implementación compatible con Aternos.
