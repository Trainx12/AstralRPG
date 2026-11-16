# Correcciones XP, Goblin Mercader, golemcitos y Heroe — 16/11/2026

Preparado localmente; despliegue remoto y R2 pendientes. Paper 26.1.2 / Java 25. Empower es el principal segun SERVIDOR.md; Aternos es copia. Claude debe confirmar el panel y hash instalado. Nunca reemplazar mundos ni usar Worlds > Upload en world.

## Cambios

Ballestas retiradas: I, II, VI–X. III–V conservan receta, carga, encantamientos y modelos del 15/11. No requieren migracion porque las retiradas no se desplegaron.
XP vanilla: Pequeno 60 / $3.000; Grande 200 / $9.000; Gigante 550 / $25.000; Barril 5.500 / $220.000. Stack 16, clic uno, Shift+clic todos los de esa mano. Dos PNG provisorios reemplazables en pack-source/provisorias. Todas las gachas, cofres de jefe, rankings, eventos ancestrales e Infinita VI+ usan los cuatro tamanos. En cofres/Infinita: 35/18/8/1%; en ancestrales: 65/35/20/2,5%. Tiradas independientes.
Mercader: cada 40–60 minutos, solo Survival world, cerca de un jugador en supervivencia. Anuncio a 64 bloques; visita 5 minutos. Clic derecho abre DeluxeMenus. Solo bienes Astral; stock por UUID y producto por visita, validado junto con distancia, dinero y espacio por el runtime. Primer agresor (incluidos proyectiles) fija su unico objetivo; se retira a los 30 segundos de ser atacado. Sin robo de inventario. El estado de visita se limpia al reiniciar/cargar chunks.
Golemcitos: sustituyen 2–4 zombis por oleada sin aumentar su total. Bosque -> bosque, Minas -> cristal, Cumbre -> hielo. Reservas y conversion sincronica igual que los esqueletos: tags de sala, cola, tope, limpieza, escala, elite, nombre/vida, drops normales y XP AuraSkills siguen el circuito existente. Animaciones idle/walk/attack/death privadas. Mantener CUSTOM en exempt-spawn-reasons de ClearLag. No aumentar topes.
Infinita no tiene salas secuenciales: la oleada especial ocurre cada diez tandas de aparicion. Aparecen los tres juntos cuando hay tres plazas; espera si el tope esta lleno. Usan tier y extra actuales de esa copia, cuentan para limite y bajas.
Cosmeticos: Horquilla y Balde raros; Barril y Rueda epicos, en Gacha de Cosmeticos y /cosmeticos -> Espaldas. Desbloqueo permanente con permisos, botones bloqueados/desbloqueados; solo visual, sin ocupar manos/casco. La variante wooden_wheel_blocking se conserva privada como modelo alternativo; no duplica premios. El Barril de XP usa el mismo barril 3D en la mano.
Espada del Heroe Errante: T2, dano 500, Combate 12, Forja/mesa con Espada I + materiales de Espada II. Giro del Heroe: clic derecho, radio 3, 150% de ataque actual con mejoras, mana 30, recarga 8 s. Valor del Heroe: +10% en golpe directo con vida llena. Ficha con ambas habilidades; ITEM_VERSION 24.

## Tienda del mercader

| Item | Precio | Stock por jugador/visita |
|---|---:|---:|
| `frasco_xp_pequeno` | 2550 | 4 |
| `frasco_xp_grande` | 7650 | 4 |
| `frasco_xp_gigante` | 21250 | 4 |
| `barril_xp` | 187000 | 1 |
| `manzana_esmeralda` | 51000 | 4 |
| `cristal_arcano` | 1800 | 6 |
| `cristal_refinado` | 6500 | 3 |
| `esencia_elite` | 2500 | 4 |
| `llave_cosmeticos` | 425 | 3 |
| `cosmetico_balde` | 12000 | 1 |

## Drops de XP de golemcitos

Probabilidades independientes por muerte segun el tier REAL del mob (incluye su variacion de mazmorra). Base Bosque T1, Minas T2, Cumbre T4; Infinita usa el elegido. Fuente unica: correcciones_goblin.GOLEM_XP.

| Tier | Pequeno | Grande | Gigante | Barril |
|---|---:|---:|---:|---:|
| 1 | 26.0% | 9.5% | 3.2% | 0.5% |
| 2 | 32.0% | 14.0% | 5.4% | 0.9% |
| 3 | 38.0% | 18.5% | 7.6% | 1.3% |
| 4 | 44.0% | 23.0% | 9.8% | 1.7% |
| 5 | 50.0% | 27.5% | 12.0% | 2.1% |
| 6 | 56.0% | 32.0% | 14.2% | 2.5% |
| 7 | 62.0% | 36.5% | 16.4% | 2.9% |
| 8 | 68.0% | 41.0% | 18.6% | 3.3% |
| 9 | 74.0% | 45.5% | 20.8% | 3.7% |
| 10 | 80.0% | 50.0% | 23.0% | 4.1% |

## Instalacion con servidor apagado

Aplicar tambien los archivos de las entregas tanda-xp-cuchillo.md y balance-especiales-agua.md si no se instalaron. Esta lista contiene los reemplazos de la correccion actual; usar SIEMPRE el FINAL de abajo para el conjunto.

| Archivo local | Destino |
|---|---|
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` |
| `build/infinita/astral_infinita.sk` | `plugins/Skript/scripts/astral_infinita.sk` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_garantia_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` | `plugins/CrazyCrates/crates/gacha_cosmeticos_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas.yml` | `plugins/CrazyCrates/crates/gacha_monturas.yml` |
| `build/lobby/CrazyCrates/crates/gacha_monturas_suerte.yml` | `plugins/CrazyCrates/crates/gacha_monturas_suerte.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg.yml` | `plugins/CrazyCrates/crates/gacha_rpg.yml` |
| `build/lobby/CrazyCrates/crates/gacha_rpg_suerte.yml` | `plugins/CrazyCrates/crates/gacha_rpg_suerte.yml` |
| `build/menus/DeluxeMenus/gui_menus/consumibles.yml` | `plugins/DeluxeMenus/gui_menus/consumibles.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos_espaldas.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos_espaldas.yml` |
| `build/menus/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` | `plugins/DeluxeMenus/gui_menus/cosmeticos_sombreros.yml` |
| `build/menus/DeluxeMenus/gui_menus/goblin_mercader.yml` | `plugins/DeluxeMenus/gui_menus/goblin_mercader.yml` |
| `build/mythicmobs/mobs/astral.yml` | `plugins/MythicMobs/mobs/astral.yml` |
| `build/mythicmobs/mobs/bosque.yml` | `plugins/MythicMobs/mobs/bosque.yml` |
| `build/mythicmobs/mobs/correcciones-goblin.yml` | `plugins/MythicMobs/mobs/correcciones-goblin.yml` |
| `build/mythicmobs/mobs/cumbre.yml` | `plugins/MythicMobs/mobs/cumbre.yml` |
| `build/mythicmobs/mobs/mazmorra.yml` | `plugins/MythicMobs/mobs/mazmorra.yml` |
| `build/mythicmobs/mobs/santuario.yml` | `plugins/MythicMobs/mobs/santuario.yml` |
| `build/mythicmobs/skills/correcciones-goblin.yml` | `plugins/MythicMobs/skills/correcciones-goblin.yml` |
| `build/rankings/astral_rankings.sk` | `plugins/Skript/scripts/astral_rankings.sk` |
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` |
| `.local/terceros/AstralRPG-privado/build/entregas/correcciones-goblin-golems/models/astral_golem_bosque.bbmodel` | `plugins/BetterModel/models/astral_golem_bosque.bbmodel` |
| `.local/terceros/AstralRPG-privado/build/entregas/correcciones-goblin-golems/models/astral_golem_hielo.bbmodel` | `plugins/BetterModel/models/astral_golem_hielo.bbmodel` |
| `.local/terceros/AstralRPG-privado/build/entregas/correcciones-goblin-golems/models/astral_golem_cristal.bbmodel` | `plugins/BetterModel/models/astral_golem_cristal.bbmodel` |

En plugins/DeluxeMenus/config.yml agregar dentro de gui_menus: `goblin_mercader: {file: goblin_mercader.yml}` y `cosmeticos_espaldas: {file: cosmeticos_espaldas.yml}`. Conservar todo el resto; referencia build/menus/DeluxeMenus/config-gui_menus.yml.
No duplicar el script de armas especiales con otro nombre. Mantener sus destinos anteriores.
AstralDecor integra el catalogo de espaldas al config existente al arrancar; conserva la configuracion NPC. Requiere Vault con economia, DeluxeMenus, MythicMobs, BetterModel, LuckPerms y CrazyCrates. Las llaves son virtuales de CrazyCrates; el balde raro se desbloquea por permiso permanente y no se cobra si ya lo tenes. Mantener en spigot.yml settings.attribute.maxHealth.max y attackDamage.max en 1.0E12.

## FINAL privado acumulativo

Base instalada arreglos-16-11 SHA-1 `4322b8ca706b692d7d0d4f750312d079a5e7653a`. Se reconstruyo sobre esa base con los deltas de XP/cuchillos y balance/menus y esta correccion. Las entradas previas no modificadas se verifican byte por byte; conserva ballestas III–V privadas y los glifos privados de cofres/barril que no conocen los deltas publicos. La seleccion de base rechaza una base fija mas vieja que la ultima entrega por fecha, salvo --base manual. Los generadores historicos XP, balance y armas-mod tambien usan esta comprobacion.
FINAL local: `.local/terceros/AstralRPG-privado/build/entregas/correcciones-goblin-golems/AstralRPG-Textures.zip`. SHA-1 `5c82d87d9371feb6f68a608729b617b75b77d2e4`. No publicar en GitHub publico ni instalar el ZIP publico.
Publicar solo durante el despliegue autorizado: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/correcciones-goblin-golems/AstralRPG-Textures.zip"`. Verificar descarga publica y luego resource-pack-sha1 en server.properties, conservando URL fija.

## Inicio, comandos y validacion remota

Reinicio completo obligatorio: JAR, datapack, BetterModel y pack. No basta /reload. Al iniciar revisar consola de AstralDecor 1.13.0, MythicMobs, BetterModel, Skript y datapack. Si solo se retoca YAML despues: mm reload, dm reload, crates reload; skript reload special_weapons, skript reload astral_infinita, skript reload astral_rankings. BetterModel reload solo si cambia modelo; evitar recargas repetidas.
Pruebas con cliente pendientes: recorrer Bosque/Minas/Cumbre, confirmar brillo/astralfx/AuraSkills, golems en grupo, limites y limpieza; alcanzar tanda 10 de Infinita; mercader con dos jugadores (neutralidad, stock, compra sin dinero/inventario lleno y retiro), cosméticos en F5, barril en mano y Giro del Heroe contra mobs/arena con mana y recarga. Nunca afirmar despliegue sin revisar consola remota.

## Verificaciones locales

Suite Python: 308 pruebas completas aprobadas; control adicional de la oleada decima aprobado. Paper local: 30 comprobaciones aprobadas (XP unitaria/Shift, neutralidad/agresor, tier/vida/nombre/limite de tres golems), sin errores de carga de datapack, Skript, MythicMobs ni BetterModel. Auditar el indice publico con tools/verificar_terceros.py antes de publicar. El ensayo NMS local verifica eventos y atributos reales; no sustituye apariencia ni combate con cliente. Logs y modelos convertidos permanecen privados en .local.

Reproduccion: desde datapack-src ejecutar build.py, menus.py, mobs/mythic.py, mobs/mazmorra.py, lobby.py, infinita.py, rankings.py, correcciones_privado.py y build_pack.py pack-source. Compilar con build_runtime.py --jdk <JDK25/bin> --server <Paper-local>; desde la raiz tools/probar_correcciones_paper.py --java <java25> --base <Paper-local>. Finalmente datapack-src/deploy_correcciones_goblin.py --assets .local/correcciones-probe/paper/plugins/BetterModel/build/assets. Pruebas: python -m unittest discover -s datapack-src -p "test*.py". No subir CorreccionesProbe.jar.
