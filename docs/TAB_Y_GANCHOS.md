# Tabulador y dos ganchos de prueba (05/11/2026)

Cambios preparados localmente; sin commit, push ni instalacion en Aternos.

El tabulador comparte titulo, degradado azul/violeta, separadores, textos claros
y colores secundarios con `sidebar.py`. Conserva jugadores, vida, oro, poder,
ping, TPS y ubicacion; fecha e IP tambien salen del mismo estilo del panel.
Los nombres y el poder de cada fila usan esa paleta. Las antiguas animaciones
siguen disponibles con el estilo compartido y la IP del panel.

Hay dos objetos independientes:

- `gancho`: Gancho de Escalada original, conserva el impulso por mirada.
- `gancho_realista`: Gancho realista, caña vanilla con anzuelo e hilo reales.
  Usar en la mano principal: clic derecho lanza, otro clic recoge. Solo tira
  del jugador si el anzuelo esta clavado en un bloque o engancho una entidad.
  La direccion depende del anclaje, aunque cambies la mirada. Recoger en el
  aire o pescar en agua no impulsa. Es un tiron con velocidad y colisiones
  normales, no un teletransporte ni un sistema de balanceo permanente.

El nuevo gancho tiene alcance de tiron de 32 bloques, comparte recarga de dos
segundos con el anterior y proteccion de caida durante el lanzamiento. Ambos
siguen bloqueados en mazmorras. No tiene receta, precio ni premios de gacha:
es una variante para probar. Usa el modelo nativo, sin cambiar el resource pack.
Su identidad se comprueba por `custom_data`, no por el nombre de un yunque;
el lanzamiento se vincula al UUID del jugador y del anzuelo.

Para obtenerlos en Minecraft (OP), una vez instalado:

```mcfunction
/loot give @s loot astral:item/gancho
/loot give @s loot astral:item/gancho_realista
```

Tambien estan en `/function astral:admin/kit_especiales`.

Instalacion:

1. Con el servidor apagado, reemplazar `world/datapacks/AstralRPG-Items.zip`
   por `build/AstralRPG-Items.zip`.
2. Reemplazar `plugins/Skript/scripts/astral_gameplay.sk` con el de
   `build/gameplay/astral_gameplay.sk`.
3. Aplicar las secciones generadas en `build/lobby/TAB/secciones-config.yml`
   al config de TAB, reemplazar `groups.yml` y las dos animaciones Astral.
4. Arrancar, ejecutar `tab reload` y probar ambos objetos.

Generacion: `python datapack-src/build.py` y `python datapack-src/lobby.py`.
Validacion automatica: 4 pruebas del nuevo gancho, 8 de gameplay y 13 de
misiones; `verify.py` comprueba JSON y referencias. Paper 26.1.2 y Skript 2.17.1
cargaron el datapack y el script; la recarga termino sin errores (registro en
`build/gameplay/gancho-validacion-local.txt`). La sensacion del tiron,
las colisiones y la apariencia del tabulador requieren prueba con jugador.
