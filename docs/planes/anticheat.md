# Plan: anticheat (xray, movimiento y combate) con avisos al staff

Pedido del dueno (21/11/2026): "Agrega plugins anticheat como de xray y esas cosas para que no puedan hacer
trampa o se me notifique". Implementa Codex con `--publish`. Despliegue en Empower aparte (no lo hace este plan).

## Objetivo
Tres capas, todas generadas desde `datapack-src/` como el resto del repo:
1. **Anti-Xray de Paper** (incluido en Paper, sin plugin): esconde los minerales que no se ven, asi el xray no muestra nada.
2. **GrimAC** (gratis, Modrinth, soporta Paper 26.1): detecta fly, speed, killaura, reach, nofall, timer, etc. y avisa al staff.
   Las primeras semanas **solo avisa, no echa ni banea** (el servidor tiene monturas, saltos y empujes de MythicMobs,
   atributos enormes por tier, y eso puede dar falsos positivos).
3. **Alerta de minado sospechoso** (Skript propio): si alguien saca demasiadas vetas de diamante/esmeralda/escombro
   antiguo en poco tiempo, avisa a los OP en el chat con coordenadas y deja registro.

## Archivos
- Nuevo `datapack-src/anticheat.py` -> `build/anticheat/`:
  - `config/paper-world-defaults.patch.yml`: solo la seccion `anticheat.anti-xray` (no reemplazar el archivo entero del server).
    - `enabled: true`, `engine-mode: 2`, `max-block-height: 64`, `update-radius: 2`, `lava-obscures: false`,
      `use-permission: false`. `hidden-blocks`: minerales de overworld (carbon, hierro, cobre, oro, redstone,
      lapislazuli, diamante, esmeralda, en piedra y pizarra profunda) + `chest`; `replacement-blocks`: stone, deepslate, tuff.
    - Nether (`world/dimensions/minecraft/the_nether/...` o el archivo por mundo que use Paper 26.1: **verificar la ruta real
      en el server de prueba**): `ancient_debris`, `nether_gold_ore`, `nether_quartz_ore`, `max-block-height: 128`,
      reemplazo `netherrack`, `basalt`, `blackstone`.
    - **Apagado** en mundos donde no hace falta o molesta: `lobby`, `astral_minas`, `infinita`, arenas/duelos, mazmorras
      y copias, fosa*, oceano, cavernas, bosque. Sacar la lista real de mundos de `plugins/Multiverse-Core/worlds.yml`
      que ya conocen los generadores (no inventar nombres).
  - `plugins/GrimAC/config.yml` + `punishments.yml` (o como se llamen en la version descargada: partir del archivo
    que genera el plugin al primer arranque en el server de prueba y parchear solo lo necesario):
    - alertas activas para quien tenga `grim.alerts`; en consola tambien.
    - todos los castigos = solo alerta (sin `kick`/`ban`), con un comentario de como activarlos despues.
    - mensajes en espanol (prefijo `&8[&cAntiTrampas&8]`), sumarlo a `datapack-src/traducciones.py` si encaja ahi.
  - `gameplay/astral_antixray.sk` (Skript, sin skript-reflect):
    - `on break` de `diamond_ore`, `deepslate_diamond_ore`, `emerald_ore`, `deepslate_emerald_ore`, `ancient_debris`.
    - Ignorar: creativo, mundos `astral_minas`/`lobby` y los mundos de mazmorra, y jugadores con `astral.antixray.exento`.
    - Contar **vetas**, no bloques: un bloque cuenta como veta nueva si esta a mas de 4 bloques del ultimo minado de ese tipo.
    - Ventana de 15 min en variables de memoria `{-axr::<uuid>::...}` (nunca variables guardadas).
    - Umbrales (constantes arriba del script): diamante 8 vetas, esmeralda 6, escombro antiguo 5 en 15 min.
      Ademas, proporcion: si en la ventana rompio menos de 40 bloques de piedra/pizarra/netherrack por veta, avisar antes.
    - Aviso a jugadores con `astral.antixray.alertas` (los OP lo tienen): `[AntiTrampas] <jugador> saco 9 vetas de diamante
      en 15 min (mundo x y z)` con texto clickeable que ejecuta `/tp <jugador>`. Sonido suave. Maximo un aviso cada
      5 min por jugador para no spamear (respetar la trampa del spam de OP de CLAUDE.md).
    - Registro en `plugins/Skript/logs/antixray.log` (efecto `log ... to "antixray"`).
    - `/antitrampas alertas` (prender/apagar avisos para uno mismo) y `/antitrampas ver <jugador>` (conteo actual),
      permiso `astral.antixray.alertas`.
  - `luckperms.txt`: comandos para dar `grim.alerts` y `astral.antixray.alertas` al grupo de admin/staff si existe,
    y comprobar que `default` NO tiene `grim.exempt` ni `grim.*`.
- `build/deploy/anticheat.md`: entrega paso a paso para Empower: bajar el `.jar` de GrimAC (version exacta compatible
  con Paper 26.1.2, anotar version y enlace de Modrinth), subirlo a `plugins/`, mezclar el parche en
  `config/paper-world-defaults.yml` (y los archivos por mundo), subir el `.sk`, comandos de LuckPerms, reiniciar,
  y como probar en vivo. **No** subir el jar al repo.
- `docs/SERVIDOR.md`: fila de GrimAC en la tabla de plugins + seccion "Anti-trampas" (que hace cada capa, comandos,
  como pasar de solo-avisos a castigos, como silenciar falsos positivos con `grim.exempt` para un jugador puntual).
- `CLAUDE.md`: linea `python anticheat.py` en Comandos de generacion; trampa nueva si aparece algo en las pruebas.

## Cuidados
- PacketEvents ya esta instalado (lo usan AuthMe y ExcellentEnchants). Comprobar que GrimAC convive con ese PacketEvents
  (version compatible o la que Grim pida); no romper `/premium` de AuthMe ni los encantamientos.
- Medir memoria con spark antes/despues (regla de CLAUDE.md).
- Repo publico: sin credenciales, sin jars de terceros.
- No tocar archivos de otras tareas ni el trabajo local previo.

## Pruebas (server de prueba local, como `tools/probar_*_paper.py`)
Nuevo `tools/probar_anticheat_paper.py`:
1. Paper 26.1.2 arranca con GrimAC + PacketEvents + AuthMe + Skript + LuckPerms sin errores en el log; Grim reporta cargado.
2. Anti-xray: con el parche, en el overworld un jugador de prueba (o lectura del chunk enviado) no recibe diamantes
   ocultos; en `lobby`/`astral_minas` sigue apagado. Si no se puede automatizar el envio del chunk, verificar que Paper
   lee la config (`/paper` o log) y dejarlo dicho en el resultado.
3. Skript: el script carga sin errores; simular roturas (comando de prueba o eventos) que superen el umbral -> aparece
   el aviso a un OP y la linea en el log; por debajo del umbral, sin aviso; en `astral_minas`, sin aviso; un segundo
   aviso dentro de 5 min no se repite.
4. Grim: en el arranque no hay alertas para un jugador quieto. Si es posible, activar fly por comando y comprobar el aviso.
5. `python datapack-src/anticheat.py` es reproducible (dos corridas = mismos archivos).

## Criterios de aceptacion
- `build/anticheat/` y `build/deploy/anticheat.md` generados, prueba local pasada (o lo que no se pudo probar, dicho).
- Commit + push a GitHub con estos archivos. Resultado en `.local/coordination/latest-result.md` con: version de GrimAC,
  rutas reales de config de Paper 26.1, que se probo y que no.
