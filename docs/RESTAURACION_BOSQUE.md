# Restauracion selectiva del Bosque Sombrio

El 05/11/2026 el dueno informo que faltaba el mapa. La consola confirmo aire
en el bloque del piso de la llegada `1440 102 1569`. Multiverse conserva
`bosque` con generador FLAT de aire, sin estructuras, respawn en lobby.
No es necesario recrear el mundo ni cambiar su generador.

`datapack-src/restaurar_bosque.py` toma las cuatro regiones privadas preparadas
de `bosque.zip` en `.local/mapas/subida/bosque/region/` y escribe una copia
verificada en `.local/bosque-restaurado-2026-11-05/region/`.
Son 378 chunks, sin command blocks, spawners ni bloques de estructura activos.
El informe privado incluye hashes SHA-256. No publicar mapas de terceros.

Las tres llegadas tienen piso y dos bloques de aire en la copia original:

| Sala | Llegada | Piso |
|---|---|---|
| Sendero de las raices | `1440.5 103 1569.5` | Cesped |
| Claro corrompido | `1504.5 107 1504.5` | Grava |
| Altar del Chaman | `1600.5 97 1440.5` | Piedra |

Respaldar primero las regiones actuales. Con el servidor apagado, subir solo
`r.2.2.mca`, `r.2.3.mca`, `r.3.2.mca` y `r.3.3.mca` a
`world/dimensions/minecraft/bosque/region/`. Conservar los demas archivos,
entidades, permisos y progreso. No usar Worlds > Upload ni reemplazar world.

Encender, comprobar las tres llegadas y poner el spawn del mundo en la primera.
Mantener el respawn en lobby. Revisar los tres controladores existentes antes
de crear los que falten; no duplicarlos. Retirar todas las cargas temporales y
guardar. El recorrido y combate con jugadores se comprueban por separado.

En la misma tarea se termino de aplicar la llegada del Nether del commit
`73fcfd7`: script guardado y recargado sin errores; aldeano existente trasladado
a `-2189.114 81 179.263`, yaw 90, dos bloques al este de la llegada.
La posicion se consulto por consola. Se retiraron las dos cargas temporales.
