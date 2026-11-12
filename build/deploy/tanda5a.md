# Tanda 5a — preparada, NO desplegada

Generar: `python build.py`, despues `python tanda5a.py --java <java25> --server <Paper-local>` desde datapack-src.
Conserva cosmeticos/skins y el pack FINAL privado: esta tanda no modifica texturas.

## Instalacion (Empower; si se usa Aternos, solo mediante funciones publicas permitidas)

Apagar. Respaldar archivos afectados y datos de plugins. No reemplazar mundos ni usar Worlds > Upload.
El runtime AstralProgression es propio: esta entrega requiere Empower u otro hosting que permita subir JAR. En Aternos, sin ese plugin en su catalogo, queda bloqueada; no instalar a medias ni usar APIs privadas.
Subir las siguientes rutas, conservando el resto de cada carpeta:

| Local | Destino |
|---|---|
| `build/runtime/AstralProgression.jar` | `plugins/AstralProgression.jar` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `build/tanda5a/AstralProgression/config.yml` | `plugins/AstralProgression/config.yml` |
| `build/tanda5a/BlzdBackpacks/config.yml` | `plugins/BlzdBackpacks/config.yml` |
| `build/tanda5a/BlzdBackpacks/messages.yml` | `plugins/BlzdBackpacks/messages.yml` |
| `build/tanda5a/EconomyShopGUI/sections/Mochilas.yml` | `plugins/EconomyShopGUI/sections/Mochilas.yml` |
| `build/tanda5a/EconomyShopGUI/sections/Proteccion.yml` | `plugins/EconomyShopGUI/sections/Proteccion.yml` |
| `build/tanda5a/EconomyShopGUI/shops/Mochilas.yml` | `plugins/EconomyShopGUI/shops/Mochilas.yml` |
| `build/tanda5a/EconomyShopGUI/shops/Proteccion.yml` | `plugins/EconomyShopGUI/shops/Proteccion.yml` |
| `build/tanda5a/ExpendableBackpacks/config.yml` | `plugins/ExpendableBackpacks/config.yml` |
| `build/tanda5a/GriefPreventionData/config.yml` | `plugins/GriefPreventionData/config.yml` |
| `build/tanda5a/GriefPreventionData/messages.yml` | `plugins/GriefPreventionData/messages.yml` |

GriefPreventionData/config.yml y messages.yml son ajustes: si ya existen, combinar las claves, no borrar claims ni PlayerData.
Comprobar que el mundo survival se llama `world`; si difiere, ajustar `survival-world` y Claims.Mode antes de arrancar.
Slots de tienda: 40 Proteccion, 42 Mochilas (41 lo usa misc en el server).

## Descargas verificadas en Modrinth (26.1.2, formato datapack o Paper)

- [griefprevention 16.18.7](https://modrinth.com/plugin/griefprevention/version/dGfCZHqk): [GriefPrevention.jar](https://cdn.modrinth.com/data/O4o4mKaq/versions/dGfCZHqk/GriefPrevention.jar) → `plugins/GriefPrevention.jar`. Local: `.local/tanda5a/GriefPrevention.jar`. SHA-1 `642c06bb3ef907a934e612914ad8397f56c7bbf4`.
- [dungeons-and-taverns 5.2.0](https://modrinth.com/datapack/dungeons-and-taverns/version/ohqJT0pv): [Dungeons and Taverns v5.2.0.zip](https://cdn.modrinth.com/data/tpehi7ww/versions/ohqJT0pv/Dungeons%20and%20Taverns%20v5.2.0.zip) → `world/datapacks/Dungeons and Taverns v5.2.0.zip`. Local: `.local/tanda5a/Dungeons and Taverns v5.2.0.zip`. SHA-1 `1d0f5d8fb7ca306fe0dd84ea11461dcc0db35885`.
- [explorify v1.6.6](https://modrinth.com/datapack/explorify/version/aQ2oh7MS): [Explorify v1.6.6.dp.zip](https://cdn.modrinth.com/data/HSfsxuTo/versions/aQ2oh7MS/Explorify%20v1.6.6.dp.zip) → `world/datapacks/Explorify v1.6.6.dp.zip`. Local: `.local/tanda5a/Explorify v1.6.6.dp.zip`. SHA-1 `383face9181f81ecf285deb1d9e6ca18b023b746`.
- [structory 1.3.17](https://modrinth.com/datapack/structory/version/OIcllpSf): [Structory_v1.3.7.zip](https://cdn.modrinth.com/data/aKCwCJlY/versions/OIcllpSf/Structory_v1.3.7.zip) → `world/datapacks/Structory_v1.3.7.zip`. Local: `.local/tanda5a/Structory_v1.3.7.zip`. SHA-1 `559a14234f8957360515a8967ed3b4e39025b5d3`.
- [structory-towers 1.0.17](https://modrinth.com/datapack/structory-towers/version/uxUF2h4B): [Structory_Towers_v1.0.17.zip](https://cdn.modrinth.com/data/j3FONRYr/versions/uxUF2h4B/Structory_Towers_v1.0.17.zip) → `world/datapacks/Structory_Towers_v1.0.17.zip`. Local: `.local/tanda5a/Structory_Towers_v1.0.17.zip`. SHA-1 `bbf5191cefbf4d538a6ae4695d2f88364390166e`.

Terceros nunca al Git publico. Mochilas: ExpendableBackpacks 1.2.0 (ya instalado en el server).
Structory y Towers son de Stardust Labs. No se superponen estructuras ni loot entre los cuatro packs. El tag load compartido se combina (sin replace).
Structory/Towers comparten data/c/worldgen/structure_icons.json: metadatos de iconos, ignorados por vanilla/Paper, prevalece el pack de mayor prioridad. No altera estructuras ni cofres; una futura integracion que lea esos iconos debe combinar ambos mapas.
Solo chunks nuevos. Paper comparte datapacks entre mundos; AstralProgression cancela AsyncStructureSpawnEvent de los cuatro namespaces fuera del survival.
No cambia estructuras ya existentes ni las vanilla. Nunca copiar ZIP a mundos de lobby/minas/mazmorras.
No apilar otra version de D&T si ya existe: reemplazar solo su ZIP anterior tras respaldo. Conservar Stellarity instalado.

Iniciar (Java 25). Requiere AuraSkills con preset legacy, MythicMobs, Vault, proveedor de economia, LuckPerms y EconomyShopGUI ya existentes.
Ejecutar `build/tanda5a/permisos.txt`; despues `sreload` y `skills reload`. Un reinicio carga el JAR y los datapacks; no usar PlugMan ni /reload general.
Verificar consola: AstralProgression habilitado, GriefPrevention y ExpendableBackpacks cargados, sin errores de datapacks.

## XP y ritmo

Copia local de AuraSkills: `.local/asw-native/server/plugins/AuraSkills/xp_requirements.yml`; corroborada con fichas-paper y testsrv.
Preset legacy no reemplaza xp_requirements. Formula: `100*(nivel_destino-2)^2+100`. No se pudo leer la configuracion remota en esta tarea: comparar antes de instalar.
25→26: 57.700 / 250 = 230,8 XP T5. A 200–300 mobs/h: 75–50 minutos. Estimacion sin bonus ni multiplicadores de permisos.
AuraSkills conserva los bonus Fighter/Archer: al nivel 25, el ensayo midio +50%. En esas skills 25→26 baja a 50–33,3 minutos (40 a 250 mobs/h). Hechiceria conserva ~60 minutos. Objetivo orientativo; medir ritmo real antes de retocar la tabla.

| Tier | Normal | Elite x1,5 | Jefe x8 |
|---|---:|---:|---:|
| 1 | 20 | 30.0 | 160 |
| 2 | 40 | 60.0 | 320 |
| 3 | 80 | 120.0 | 640 |
| 4 | 140 | 210.0 | 1120 |
| 5 | 230.8 | 346.2 | 1846.4 |

| Progreso | Tier supuesto | XP total | Minutos a 250 mobs/h |
|---|---:|---:|---:|
| 1→5 | 1 | 1800 | 21.6 |
| 10→11 | 2 | 8200 | 49.2 |
| 25→26 | 5 | 57700 | 60.0 |

Listener unico: mob tier por etiqueta astral.mt#, luego definicion Mythic generada, luego mundo de mazmorra.
Fighting/archery/sorcery se leen del PDC de requisitos del arma Astral. Flechas guardan skill al disparar; magia atribuida por /damage by jugador.
Se reemplaza la XP de EntityXpGainEvent solo para bajas gestionadas: sin premio fighting/archery duplicado. Sorcery por gastar mana del preset se conserva (fuente diferente).
Tier 0 y mobs vanilla sin escala conservan fuentes AuraSkills: zombi/esqueleto 7 XP base en fighting.yml y archery.yml. T1 gestionado da 20 (x2,86), T5 230,8 (x32,97). No inflar animales para farmear.
Jefe T3: 640 XP, menor que un nivel medio (14→15: 17.000); T5: 1.846,4 < 57.700. No se acumula bonus elite+jefe.

## Proteccion y mochila

Pala de oro: clic derecho en dos esquinas. Minimo 6x6, area 36. Todo de fondo a techo desde crear la zona; solo se cobra X*Z.
Inicio 36, sin bloques por tiempo. Comprar SUMA: 36+25=61, no 11x11. Se reparte entre varias zonas (cada una minimo 36).
`/trust jugador`, `/untrust jugador`, `/abandonclaim`; Bolt sigue controlando cofres y WorldGuard sigue controlando regiones.
`/buyclaimblocks` y venta de bloques desactivados. Precio unico en tanda5a.py; compra desde EconomyShopGUI abre menu propio y ejecuta `adjustbonusclaimblocks jugador cantidad` desde consola.
Paquetes: 25 bloques = $15,000, 100 bloques = $50,000, 1225 bloques = $500,000, 2500 bloques = $950,000, 10000 bloques = $3,500,000. Caros frente a minas: $80 → $700.000 → $25M.
Mochilas (ExpendableBackpacks): Cuero 9 espacios $5,000, Cobre 18 espacios $20,000, Hierro 27 espacios $50,000, Oro 36 espacios $100,000, Diamante 45 espacios $175,000.
La tienda ejecuta `backpack give jugador nivel` desde consola: la mochila es un item (clic derecho abre). Pide un espacio libre antes de cobrar.
Tambien se fabrican (cuero+hilo+cofre) y se mejoran rodeandolas con 8 lingotes; Netherite en herreria. `allow-backpack-inception: false`.
Al morir la mochila cae como item (AxGraves la guarda en la tumba); el contenido queda ligado a la mochila.

## Loot aditivo por item y cofre

| Rareza | Probabilidad | Porcentaje |
|---|---:|---:|
| Comun/material | 0.15 | 15% |
| Poco comun | 0.03 | 3% |
| Rara | 0.005 | 0.5% |
| Epica | 0.0004 | 0.04% |
| Legendaria | 3e-06 | 0.0003% |

Catalogo: 154 items; una tirada independiente por item elegible, sin limite que cambie su probabilidad.
Rareza del equipo: ficha.py (T1..T5). Materiales sin rareza reciben tier explicito en MATERIAL_TIERS (tanda5a.py); nucleos/perfectas endgame son T5. Talismanes: tier existente.
La probabilidad es por item, tambien para equipo comun: puede haber varias piezas comunes en un cofre; no hay tirada global ni multiplicador oculto por categoria.
LootGenerateEvent conserva la lista original y agrega items desde astral:item/*. Solo contenedores naturales sin marca de colocacion, primera generacion, survival.
Aldeas/naufragios/tabernas/cabanas/Structory: max T2; templos/minas y desconocidos futuros T3; stronghold/bastion/ancient_city/end_city, D&T catacumbas/magos/mansion y Towers T5.
Tablas con namespace astral se excluyen para evitar recursion. Cofres colocados despues de instalar se marcan y excluyen; cofres previos de jugadores no tienen loot table y no generan evento.

## Verificaciones locales

Suite existente: 227 pruebas OK. Regresion final focalizada: 23 pruebas OK. Compilacion con JDK25 y Paper 26.1.2 build 74.
Ensayo Paper: XP real de baston, espada, arco con cambio de arma, elite y jefe Mythic; una sola recompensa, bonus nativos conservados; claims 6x6 y area acumulativa; filtro de estructuras; loot aditivo de vanilla y los cuatro packs, sin repetir; mochila y persistencia tras reinicio.
Prueba reproducible: `python tools/probar_tanda5a_paper.py --java <java25> --source <Paper-local>` desde la raiz. Logs solo en `.local/tanda5a/`. Nunca instalar ProgressionProbe en remoto.
Jugador NMS simulado: overlays de AuraSkills/PacketEvents apagados solo en el ensayo. No sustituye un cliente real ni valida AxGraves/WorldGuard/Bolt/EconomyShopGUI en remoto.
Comparacion ZIP contra HEAD previo: solo guia.json y la pagina nueva guia/proteccion.json; sin otros cambios de items ni assets.

## Verificacion remota pendiente

- Comparar curva activa con la copia local y comprobar que el preset legacy tenga sorcery.
- Espada, arco (cambiar arma en vuelo), baston directo/area y guadana: una sola recompensa de la skill correcta; matar elite/jefe y mob vanilla escalado.
- Dos cuentas sin OP: proteger 6x6; intentar romper fondo/techo, varias zonas, comprar 25 y comprobar 61; WG y Bolt siguen negando acceso.
- Mochilas: comprar niveles, abrir con clic derecho, desconexion/reinicio; morir con AxGraves, recuperar tumba una vez, revisar que no se duplique contenido.
- Abrir cofres nuevos de cada pack (tambien vagoneta), conservar loot vanilla; reabrir no duplica. Generar chunks en mundo excluido y confirmar que no aparecen estructuras de los packs.
- Revisar consola y medir memoria/TPS con spark. No afirmar estas pruebas remotas como realizadas.
