# Movilidad y presentacion — 05/11/2026

- TAB: nombres legibles de todos los mundos conocidos y alias de restauraciones; mayusculas iniciales, acentos y centrado con espacios a ambos lados. El ancho se calcula con la fuente vanilla; fuentes personalizadas pueden variar el resultado.
- Items v9: `gancho` pasa a **Saltador**; `gancho_realista` a **Gancho de escalada**. La migracion existente actualiza los objetos conservando sus datos de mejora.
- Gancho de escalada: sin recarga compartida con el Saltador; cada recogida libera la boya antes de lanzar otra. Conserva limite de 32 bloques y restricciones de mazmorras. El anclaje compensa el -0.03 vertical propio de FishingHook, incluso con NoGravity, y restaura su posicion cada tick. Limpieza al salir, morir, cambiar de mundo y descargar Skript.
- Doble salto: segunda pulsacion despues de soltar la tecla, sin espera minima de 150 ms; conserva movimiento horizontal y un solo impulso por salto.
- Jefes y Ancestrales: escala absoluta 2.0 en BetterModel. Yeti de Cumbre: metaskill propia con escala 4.0 al aparecer y cargar. Capataz y golem de Minas sin modelo usan `Options.Scale: 2.0`.

## Verificacion

28 pruebas de movilidad, presentacion, gameplay y mazmorras. Carga real en Paper 26.1.2 / Skript 2.17.1 sin errores del script. Cliente de protocolo en plataforma local: anclaje a Y=103.43 durante 241 ticks con minimo=maximo; dos tirones separados por 749 ms aceptados; segundo salto pulsado a los 108 ms del primero, impulso recibido 39 ms despues, Y=0.650003. La latencia de red y sensacion visual requieren juego con cliente normal.

El servidor local minimo no incluye ExcellentEnchants; los modificadores de taladro que dependen de su encantamiento no se validan alli. La consola de Aternos es la comprobacion del datapack completo.

## Archivos de instalacion

`build/AstralRPG-Items.zip`, `build/gameplay/astral_gameplay.sk`, condiciones de ubicacion de `build/lobby/TAB/secciones-config.yml`, `build/mythicmobs/skills/astral.yml`, `build/mythicmobs/skills/mazmorra.yml`, `build/mythicmobs/mobs/mazmorra.yml` y solo las dos referencias del modelo del Yeti de `build/mythicmobs/mobs/cumbre.yml`. Conservar configuraciones vivas y recorridos de mapas. Reiniciar para cargar todo junto; no sustituir mundos ni resource pack.
