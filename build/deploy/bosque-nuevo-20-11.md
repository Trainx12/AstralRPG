# Bosque Astral nuevo 300x300 (20/11/2026)

Reemplaza el mundo `astral_bosque` (grilla de 64 árboles) por el recorte de Forested Plains.
Ver docs/BOSQUE.md. Respaldo del server previo: `.local/bosque-mapas/respaldo-server-20-11/`
(4 regiones + `astral_bosque.sk`).

## Archivos

| Local | Server |
|---|---|
| `.local/bosque-mapas/bosque-regiones.zip` (privado, 9 regiones) | `world/dimensions/minecraft/astral_bosque/region/` (descomprimir) |
| `build/bosque/astral_bosque.sk` | `plugins/Skript/scripts/astral_bosque.sk` |

## Pasos

1. Apagar el server.
2. Borrar en `world/dimensions/minecraft/astral_bosque/`: `region`, `entities`, `poi`.
3. Subir el ZIP a `.../astral_bosque/`, descomprimir (deja `region/`), borrar el ZIP.
4. Subir `astral_bosque.sk`. Prender.
5. Consola: los comandos de `build/bosque/instalacion.txt` desde `mv gamerule ...` (NPC de venta y viajes y
   cartel del ranking).
6. Revisar: `skript` sin errores en `astral_bosque.sk`; `/bosque` lleva a la plataforma; talar un árbol y que
   vuelva a los 3 minutos.

Deshacer: apagar, volver a poner las 4 regiones del respaldo y el `.sk` viejo.
