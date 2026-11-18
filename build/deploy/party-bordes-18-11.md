# Party y bordes de pelea — 18/11/2026

Preparado para Paper 26.1.2 build 74 y Java 25, Skript 2.17.1 y PlaceholderAPI.
Instalacion remota PENDIENTE: esta tarea no accedio al panel ni modifico mundos.
La documentacion identifica Empower como principal y Aternos como copia; confirmar
el destino vigente con el dueno antes de instalar. No usar APIs privadas ni eludir
la restriccion de subida de JAR de Aternos. Si el panel no admite el JAR propio,
esa instalacion queda bloqueada; usar solo mecanismos permitidos por el proveedor.

## Implementacion

- AstralParty 1.1.0: chat con Aceptar/Rechazar/Abrir Party, titulo y sonido;
  Cancelar para el lider y aviso a ambos al vencer. Los botones de invitaciones
  anteriores no aceptan/cancelan una invitacion nueva.
- Cabeza del companero: submenu de 27 casillas, Echar con confirmacion,
  Pasar liderazgo y Volver. Revalida liderazgo al actuar y sincroniza
  `astralpartysync` para mazentrar/Infinita. Mirar companeros visible estando caido.
  Comandos anteriores conservados; se agregan `party lider <jugador>` y
  `party cancelar <jugador>`. No cambia ventanas ilustradas ni resource pack.
- Duelos ya tenia Aceptar/Rechazar y Ver resultado/Revancha clickeables.
  Se conserva AstralDuelos sin regenerar ni cambiar arte.
- Bordes integrados en AstralParty (no hay plugin adicional), con
  `Bukkit.createWorldBorder()` / `Player.setWorldBorder`, dano y buffer cero,
  advertencia de tres bloques. CSV incorporado: `fight-rooms.csv`.
- Todas las salas de todas las copias: seis por mazmorra y seis Infinita;
  tres Fosa. Controladores `.on` sin `.fin` mantienen la pelea entre oleadas.
  Infinita/Fosa se activan por enemigos etiquetados vivos; durante sus pausas
  sin enemigos el borde se oculta. No depende de Mythic Premium ni skript-reflect.
- Recuperacion al ultimo punto interior por movimiento/empuje/perla/lag.
  Viajes del plugin o comandos a otro destino permiten salir; no bloquea
  mazfin, la sala siguiente ni lobby. Caidos conservan camara y borde.
  La deteccion de salas se actualiza cada cinco ticks, sin cargar chunks.

## Archivos locales y destinos exactos

Apagar el servidor sin peleas en curso, guardar copia de estos cuatro destinos,
subir y volver a iniciar. El cambio de JAR exige reinicio completo: no usar PlugMan
ni `/reload` general de Bukkit.

| Archivo local (raiz del repo) | Destino relativo a la raiz del servidor |
|---|---|
| `build/runtime/AstralParty.jar` | `plugins/AstralParty.jar` (reemplazar solo este JAR) |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/skills/bosque.yml` | `plugins/MythicMobs/skills/bosque.yml` |
| `build/AstralRPG-Bosque-Bordes.zip` | `world/datapacks/AstralRPG-Bosque-Bordes.zip` (archivo adicional) |

El complemento contiene **solo tres funciones de oleada del Bosque** y `pack.mcmeta`.
No sustituye el ZIP principal ni incluye mapas, assets, credenciales o scripts de Minas.
Debe quedar despues del datapack principal para que el conteo use el radio 44.
Desde consola, tras iniciar:

```text
minecraft:datapack list enabled
```

Si aparece habilitado pero antes del principal, primero:

```text
minecraft:datapack disable "file/AstralRPG-Bosque-Bordes.zip"
```

Luego habilitarlo al final (si ya figura ultimo, omitir estos dos cambios):

```text
minecraft:datapack enable "file/AstralRPG-Bosque-Bordes.zip" last
minecraft:datapack list enabled
```

El reinicio carga JAR, MythicMobs y Skript. Si se instalaran SOLO los YAML con
el JAR nuevo ya cargado: `mm reload`, sin reinicio; no alcanza para instalar el JAR.
El Skript de copias se regenero sin diferencias: **ningun `.sk` nuevo que subir**.
Conservar el `astral_mazmorras_copias.sk` instalado y una sola version activa.
No recargar Skript innecesariamente porque las parties son solo de memoria.
No cambiar BetterModel, TAB, menus, R2 ni SHA-1 del resource pack.

**Mythic privado:** `mobs/astral.yml` y `skills/astral.yml` del servidor son las
versiones de `build_privado.private_configs`. Esta tarea no los cambia: conservarlos;
no sobrescribirlos con las versiones publicas ni ejecutar una instalacion masiva
de `build/mythicmobs/`. Los dos `bosque.yml` de esta tabla son configuracion propia.

El build completo futuro (`build.py`) incorpora naturalmente los mismos radios.
Al consolidarlo, comprobar que sus tres `tanda2/bosque/sala1/waveN` usan 44 y retirar
el complemento en esa misma actualizacion para que no tape cambios futuros de oleadas.

## Bosque vigente: dos salas, cuatro bloques mas por lado

El plan mencionaba los tres centros antiguos con radios 18/28. `tanda2.configure`
los reemplaza por dos salas de radio 40. Se aplica 40 → 44 despues de esa
configuracion, en `mazmorras_data.py`, sin editar `tanda2.py`, apariciones ni piso.
El borde es cuadrado de lado 88, centrado en el mismo controlador.

| Mundo | Sala | Centro X Y Z | Radio viejo → nuevo | Limites X | Limites Z |
|---|---|---|---|---|---|
| bosque | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |
| bosque_2 | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque_2 | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |
| bosque_3 | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque_3 | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |
| bosque_4 | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque_4 | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |
| bosque_5 | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque_5 | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |
| bosque_6 | Claro de las raices | 1465.5 101 1573.5 | 40 → 44 | 1421.5 .. 1509.5 | 1529.5 .. 1617.5 |
| bosque_6 | Altar del Chaman | 1604.5 101 1382.5 | 40 → 44 | 1560.5 .. 1648.5 | 1338.5 .. 1426.5 |

Claude debe mover/quitar las barreras manualmente en el servidor, usando estos
limites y revisando el terreno. No se quita ningun bloque automaticamente ni se
reemplaza un mundo. Nunca usar Worlds > Upload en la fila `world`.

## Reproduccion y verificacion

Verificado: 43 pruebas Python correctas (incluyen piso natural, todas las copias,
metadata del JAR y proteccion del ZIP principal). Los tres archivos del complemento
se compararon con el principal: la unica diferencia es `distance=..40` → `..44`.
El CSV del JAR contiene 99 salas. Auditoria focalizada de entregables sin arte privado.
Paper local: **80 comprobaciones, cero fallas**, Skript cargado sin errores.
Incluye botones con token real (y botones vencidos/reemplazados), cancelacion,
confirmacion de expulsion, traspaso, sincronizacion con mazentrar, dos bordes
distintos en el mismo mundo, aviso/dano, movimiento/perla/posicion exterior,
caido y camara, limpieza independiente e Infinita. Controles simulados con
los nombres, centros y tags del catalogo; sin MythicMobs ni cliente grafico.
Evidencia local: `.local/party-bordes-final-probe/paper.log` (no publicar).
Se corrigio una expectativa obsoleta de `test_mazmorras_copias`: desde la tanda
anterior `/party` pertenece al JAR, no a Skript; se prueba ahora el puente vigente.

SHA-256 de los cuatro archivos a instalar:

| Archivo | SHA-256 |
|---|---|
| `AstralParty.jar` | `ccfde88c88f7b5f88f0e4fb6fce49610210f2c0bbb3992c62517ccf9029227f1` |
| `mobs/bosque.yml` | `cb7b69e4c7ba490841ecb61a163d524a240166452e854018fee3853bc725df8d` |
| `skills/bosque.yml` | `762140e537ff2c2b4af46b70aa069bfdd58886c7447c452a71c46ece70bb8bde` |
| `AstralRPG-Bosque-Bordes.zip` | `2e81b1187d47753385a65dcb169ef0f756b3193b690141113fe707327c767a52` |

Desde `datapack-src` (Python con Pillow y PyYAML; Java 25 y Paper local):

```text
python mobs/mazmorra.py
python mazmorras_copias.py
python bosque_bordes.py
python party.py --java <java25> --server <Paper-local> --papi <PlaceholderAPI.jar>
python -m unittest test_party test_duelos test_mazmorras test_mazmorras_copias test_oleadas_tanda2 test_tanda2c test_viajes_mazmorras
```

Desde raiz, ensayo aislado (puerto 25629, solo 127.0.0.1):

```text
python tools/probar_party_paper.py --java <java25> --base <Paper-local> --papi <PlaceholderAPI.jar> --work .local/party-bordes-probe
```

No subir `PartyProbe.jar`, `.local`, logs ni mapas. Revisar consola remota al
iniciar y probar con dos clientes: invitacion/cancelacion/vencimiento, confirmar
expulsion, traspasar lider y entrar juntos con mazentrar/Infinita; dos salas
simultaneas, caer y mirar, perla hacia afuera, limpiar sala y avanzar sin borde.
Comprobar visualmente el borde y las barreras en Bosque y las arenas de Infinita/Fosa.
El ensayo de jugadores NMS no sustituye esa revision ni el combate con MythicMobs
y el conjunto completo de plugins remotos.
