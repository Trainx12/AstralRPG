# Economia E1 (7a): x100 estilo Hypixel, Netherita, muerte y Banco — 18/11/2026

Hecho por Claude directo (sin Codex). Fuente unica: `datapack-src/economia.py`. **DESPLEGADO 18/11 ~19:00 (hora AR): pack ecba9321, server reiniciado, Skript 22 scripts sin errores, 196 mobs, aldeano de Subastas y 16 carteles rehechos. Datapack = el del server + solo lo de economia (no se subio el cambio del Bosque). AstralProgression: config del server + precios x100. Rebase de saldos: NO se corre (el dueno va a reiniciar todo mas adelante).**

## Que cambia para los jugadores
- Toda la plata x100: tienda, gachas (100k / 250k / 50k por tirada), minas, consumibles, oficios, peluches,
  proteccion, mochilas, mercader, misiones, rankings, cofres de mazmorra, deseo (tope 2.500M / lite 625M).
- Mobs Astral del survival pagan segun su tier: T1 1.500, T2 3.000, T3 6.000, T4 12.000, T5 25.000, y el doble
  por tier hasta T10 (800.000). Elite x10, jefe del mundo x50, Ancestral x100. El renacimiento sigue sumando +100%.
- Mazmorras (tier del mundo): cada mob de oleada (tambien los vanilla, que antes pagaban 0) T1 300, T2 800,
  T3 2.000, T4 4.500, T5 10.000; elite x10. Jefe: 100k / 300k / 800k / 2M / 5M a cada jugador vivo a 64 bloques.
  Cada eco del Santuario: 3.000.000 a cada participante. La Fosa cuenta como mazmorra tier 3.
- Herrero: mejoras +1..+10 = 30k, 75k, 150k, 300k, 600k, 1,2M, 2,5M, 5M, 10M, 25M. Reparar x100.
- Netherita III: 15.000 por bloque (antes 4.000), abrirla cuesta 2.500.000.000 (+25 h de mineria, igual que antes).
  La tienda tiene tope: bloque 15.000, lingote 1.667, equipo de Netherita = equipo de diamante + lingote + plantilla.
- Morir en survival, nether, end, minas, bosque, oceano, mazmorras, Fosa o Infinita (incluida la caida con party)
  pierde el 50% de la plata encima. Lobby, arenas, duelos, parkour y mini juegos: sin perdida.
- **Banco Astral**: el aldeano de Subastas ahora abre "Subastas y Banco" (DeluxeMenus `subastas_inicio`):
  Casa de Subastas (la ventana de siempre) o Banco (ventana Skript; boton Volver). Tambien `/banco`.
  Depositar/retirar todo, mitad o cantidad (por chat).
  Interes 2% cada 24 h reales (max 2M por pago). Cuentas: Inicial 50M, Oro 100M (5M), Diamante 250M (20M),
  Esmeralda 500M (60M), Astral 1B (200M). Renacer tambien vacia el Banco (si no, renacer no costaria nada).
- Venta rapida: la vista previa ahora muestra el precio por unidad (antes no dividia por el paquete).

## Archivos a subir
| Local | Server |
|---|---|
| `build/economia/Skript/scripts/astral_economia.sk` (NUEVO) | `plugins/Skript/scripts/` |
| `build/renacimiento/astral_renacimiento.sk` (ya no tiene `astralplatamob`) | `plugins/Skript/scripts/` |
| `build/minas/Skript/scripts/astral_minas.sk`, `build/rankings/astral_rankings.sk`, `build/services/astral_servicios.sk`, `build/bosque/astral_bosque.sk` (precios de madera) | `plugins/Skript/scripts/` |
| `build/shop/EconomyShopGUI/shops/**` (vanilla x100 + Consumibles/Oficios/Peluches) | `plugins/EconomyShopGUI/shops/` |
| `build/tanda5a/AstralProgression/config.yml` | `plugins/AstralProgression/config.yml` |
| `build/menus/DeluxeMenus/gui_menus/*.yml` (subastas_inicio NUEVO, gachas, cofres, consumibles, oficios, deseo, renacer, goblin, principal, comandos) | `plugins/DeluxeMenus/gui_menus/` |
| `build/lobby/CrazyCrates/crates/gacha_*.yml` | `plugins/CrazyCrates/crates/` |
| MythicMobs: `mobs/{bosque,cumbre,forja,fosa,mazmorra,santuario,tanda4b,tumba}.yml`, `skills/{bosque,cumbre,forja,mazmorra,santuario,tumba}.yml` desde `build/mythicmobs/`; **`mobs/astral.yml` y `skills/astral.yml` desde la version PRIVADA** `.local/terceros/AstralRPG-privado/build/mythicmobs/` | `plugins/MythicMobs/` |
| `build/runtime/AstralDecor.jar` (1.22.0: precio del peluche desde balance.json) | `plugins/` |
| `build/AstralRPG-Items.zip` (Herrero y misiones del Cronista) | datapack del mundo |
| Pack FINAL `.local/terceros/AstralRPG-privado/build/entregas/economia-e1/AstralRPG-Textures.zip` (base `7dad4ba7` + 78 dibujos de precios) | R2 con `tools/subir_pack_r2.py` + `resource-pack-sha1` |

SHA1 del pack: ver `.../entregas/economia-e1/pack.sha1`. Generado con `python datapack-src/deploy_economia.py --base <FINAL 7dad4ba7>`.

## Orden
1. Respaldo del panel. Subir todo lo de arriba, pack a R2 y sha1, reiniciar.
2. DeluxeMenus `config.yml`: agregar `subastas_inicio: {file: subastas_inicio.yml}` (lista en
   `build/menus/DeluxeMenus/config-gui_menus.yml`). Despues `dm reload`.
   Lobby (cargado): `rg flag -w lobby __global__ mob-spawning allow`, `mm mobs kill astral_npc_subastas`,
   `mm mobs spawn astral_npc_subastas 1 lobby,205.466,100,175.476,2.7,0`, rehacer el cartel (lineas de carteles en
   `build/lobby/comandos.txt`: ahora dice "Subastas y Banco"), `mob-spawning deny`.
3. Revisar consola: Skript sin errores, MythicMobs cargado.
4. **Rebase de saldos (aparte, solo con OK del dueno, una sola vez):** en consola `astraleconomia rebase`.
   Multiplica x100 la plata de todos (online y offline) y el Banco. Log: `plugins/Skript/logs/astral-rebase.log`.
   No se repite aunque se escriba de nuevo. Subastas: no hay publicaciones activas (dueno 18/11), no se tocan.

## Pruebas
- `test_economia.py` (14): cobertura de pagos (sin cifras viejas, mobs por categoria), tablas del plan,
  tienda x100, venta <= compra, anti-arbitraje en cadenas de crafteo, topes de Netherita, catalogo por unidad,
  mundos con perdida, Banco y rebase.
- `tools/probar_economia_paper.py`: Paper local con Skript + Essentials + Vault: "All scripts loaded without errors",
  `astralbanco info` responde, el rebase corre una vez y se niega la segunda.
- Pruebas viejas actualizadas a x100: test_misiones, test_tanda5a, test_trainx_deseos. Siguen fallando 9 pruebas
  que YA fallaban en `ac0fdd4` sin estos cambios (tanda1 playtime, ajustes_menu_oleadas, arreglos_esqueleto_volcano,
  menu_principal, mesa, misiones DailySidebar, retiro_ventanas_1611, tanda_xp botones, travel_ui desafiar).
- Auditoria de terceros: sin arte privado.
- Falta con cliente: matar mobs (tier/elite/jefe), jefe de mazmorra con varios, morir con plata, Banco, NPC.

## Notas
- El arte del Banco es vanilla (bloques/tintes); si se quiere ventana con arte Gemini, va en otra tanda.
- El cofre de mazmorra paga x100 por ahora; el plan E2 (puntaje) lo redefine.
