# AstralRPG: cómo está armado el servidor

Documento de referencia para administrar y cambiar el servidor. Actualizado el 27/10/2026.

> **Contraseñas:** este repositorio es público, así que acá no va ninguna contraseña.
> El usuario y la contraseña de Aternos están en `docs/CREDENCIALES.local.md`. Ese archivo existe solo
> en la PC del dueño y Git lo ignora, así que no se sube a GitHub.
> Como la contraseña de Aternos se compartió por chat, conviene cambiarla y actualizar ese archivo.

## Servidor

| Dato | Valor |
|---|---|
| Dirección | `AstralRPG2.aternos.me` |
| Hosting | Aternos (panel en https://aternos.org/server/) |
| Software | Paper 26.1.2, build 74 (Java 25) |
| Modo | No premium (`online-mode=false`): entran cuentas cracked y originales |
| Login | AuthMe: cada jugador hace `/register <clave> <clave>` la primera vez y `/login <clave>` después |
| Mods | Ninguno. Se entra desde Minecraft vanilla 26.1.2 |
| Repositorio | https://github.com/Trainx12/AstralRPG (público) |

Aternos apaga el servidor cuando no hay nadie. Para prenderlo hay que entrar al panel, apretar **Start** y dejar terminar el anuncio. Si se cierra el anuncio antes de tiempo, a veces el arranque se cancela y hay que apretar Start de nuevo.

**Reglas al cambiar archivos:**
- Aternos no deja reemplazar archivos con el servidor prendido: hay que apagarlo antes de subir el datapack o configs nuevas.
- Cada vez que cambia `AstralRPG-Textures.zip`, hay que actualizar `resource-pack-sha1` en `server.properties` con el sha1 nuevo. Si no se actualiza, los jugadores no bajan la versión nueva o el pack falla al cargar.

## Plugins

| Plugin | Para qué está |
|---|---|
| AuraSkills 2.4.0 | Skills y niveles (Forja, Hechicería, Arquería, Combate, Minería, Tala...). **Tiene cargado el preset `legacy.zip`** (sin él no existen Forging ni Sorcery) |
| LevelledMobs | Sube el nivel de los mobs según la distancia al spawn |
| MythicMobs 5.13.0 | Criaturas custom: fauna, hostiles, monturas, élites y jefes |
| BetterModel 3.6.0 | Modelos 3D de esas criaturas (sin mods) |
| ExcellentEnchants 5.4.3 + NightCore + PacketEvents | Encantamientos extra (el Taladro Infernal usa Tunnel) |
| Bolt | Protege cofres, shulkers y puertas |
| WorldGuard + WorldEdit | Zonas protegidas y edición |
| AuthMe | Login con contraseña (necesario en modo no premium) |
| SkinsRestorer | Skins para cuentas no premium |
| AxGraves | Tumba con tus cosas al morir |
| ClearLag++ | Limpia ítems tirados para que no haya lag |
| TAB | Lista de jugadores |
| nonchat | Filtro y formato de chat |
| RHLeafDecay | Las hojas se caen rápido al talar |
| LuckPerms | Permisos |
| PlaceholderAPI | Variables para otros plugins |

## Datapacks (`world/datapacks`)

- **AstralRPG-Items.zip**: el nuestro. Tiene ítems, recetas, Forja Astral, guía, élites, taladros y motosierras.
- Dungeons and Taverns 5.2.0 y DnT Stronghold Overhaul 2.4.0: estructuras.
- Incendium 5.4.12: Nether.
- Stellarity 5.4.2: End. La 6.0.1 crasheaba en 26.1.2, por eso quedó la 5.4.2.

## Resource pack

- Se sirve desde `https://raw.githubusercontent.com/Trainx12/AstralRPG/main/build/AstralRPG-Textures.zip`.
- Es obligatorio (`require-resource-pack=true`).
- Incluye las texturas originales del dueño (`assets/astral`, `assets/armasrpg`), las armaduras de Mago, Berserker y Arquero, las texturas CC0 (créditos en `datapack-src/pack-source/cc0/CREDITOS.txt`), los taladros y motosierras, y los modelos de BetterModel.
- Después de cambiarlo: commit y push, esperar a que GitHub sirva el archivo nuevo (puede tardar unos minutos) y recién ahí poner el sha1 nuevo en `server.properties`.

## Cómo cambiar cosas

Todo se genera con Python desde `datapack-src/`:

```
cd datapack-src
python gen_textures.py
python build.py
python build_pack.py pack-source
```

`gen_textures.py` solo hace falta si cambiaron texturas generadas (armaduras, recolores, CC0).

| Qué querés cambiar | Archivo |
|---|---|
| Materiales, drops de mobs, armaduras, armas, talismanes, lanzas, élites | `items.py` |
| Taladros y motosierras (niveles, velocidad, área, recetas) | `tools.py` |
| Qué textura usa cada ítem | `textures.py` |
| Lógica: hechizos, arcos, forja, guía, élites, área de taladros | `build.py` |
| Criaturas: modelos | `mobs/creatures.py` → `python mobs/build_models.py` |
| Criaturas: vida, drops, spawn | `mobs/mythic.py` |

Salida:
- `build/AstralRPG-Items.zip` (datapack).
- `build/AstralRPG-Textures.zip` (resource pack).
- `build/models/*.bbmodel` va a `plugins/BetterModel/models/`.
- `build/mythicmobs/{mobs,skills,randomspawns}/astral.yml` va a `plugins/MythicMobs/...`.

**Para subir cambios al servidor:**
1. Apagá el servidor.
2. Reemplazá los archivos.
3. Actualizá el sha1 si cambió el resource pack.
4. Prendé el servidor y mirá la consola por errores.

Si cambia un ítem que los jugadores ya tienen, subí `ITEM_VERSION` en `build.py`: los ítems viejos se actualizan solos al entrar.

## Comandos útiles (como OP o desde la consola, sin `/`)

| Comando | Qué hace |
|---|---|
| `op <jugador>` | Dar OP |
| `skills skill setlevel <jugador> <skill> <nivel>` | Poner nivel de AuraSkills (`mining`, `foraging`, `forging`, `sorcery`, `archery`, `fighting`) |
| `skills preset load legacy.zip` y `skills reload` | Volver a cargar Forging/Sorcery si se resetea AuraSkills |
| `function astral:admin/todo` | Te da todas las cajas de shulker con todos los ítems |
| `function astral:admin/kit_<nombre>` | Una caja: `materiales`, `berserker`, `mago`, `arquero`, `armas`, `especiales`, `herramientas` |
| `function astral:admin/materiales` | Dos de cada material |
| `trigger astral.guia` | Abre la guía (también Esc → Guía AstralRPG) |
| `mm mobs spawn astral_<id>` | Spawnear una criatura (ej. `astral_chocobo`, `astral_yeti`) |
| `mm mobs list` | Lista de criaturas cargadas (tienen que ser 22) |
| `bettermodel reload` | Recargar modelos (tienen que ser 17) |
| `bolt edit add <amigo>` y clic en la caja | Compartir un cofre o shulker protegido |
| `bolt trust` | Confiar todas tus protecciones a un amigo |
| `bolt info` y clic | Ver de quién es una protección |

## Sistemas del juego (resumen)

- **Forja Astral:** abrí la guía al lado de una mesa de herrería (a 3 bloques o menos) y apretá Forjar. Saca los materiales del inventario y, si falta algo, avisa todo lo que falta junto.
- **Clases:** Berserker (Forja), Mago (Hechicería) y Arquero (Arquería). Cada una tiene 5 tiers de armadura y armas, y cada tier se hace con el anterior. Las armaduras tienen skins propias.
- **Arcos:** manteniendo clic derecho disparan solos.
- **Élites:** la dificultad sube con tu equipo y con los días (ver `BALANCE.md`).
- **Criaturas (MythicMobs):**
  - Fauna: mapache y pingüino.
  - Hostiles: espantapájaros, abejorro, araña y cara voladora.
  - Monturas, que nacen sin silla y se ensillan: chocobo, grillo, escarabajo, lagarto, ave y pterodáctilo.
  - Jefes: momia, yeti, gólem de forja, cangrejo y chamán.
  - Hay élites de 5 hostiles, con 2,5 veces la vida.
- **Taladros (Minería 5 → 40):** 9 niveles. Rompen 1x1, 2x1, 2x2, 3x3 y 4x4. Del nivel 3 en adelante son indestructibles.
- **Motosierras (Tala 5 → 32):** 5 niveles. Cortan 1, 2, 3 y 6 troncos, o el árbol entero.
- El área del taladro y la tala solo afectan bloques naturales. Esos bloques extra no dan experiencia de AuraSkills.

## Problemas conocidos y soluciones

- Avisos de MythicMobs sobre `ExampleQuest...`: son de los ejemplos que trae el plugin, no afectan nada.
- Aviso de Paper "4 releases behind": se queda en 26.1.2 a propósito, porque los plugins están probados ahí.
- Errores de GeoIP de AuthMe: no afectan.
- Si alguien no ve texturas: que acepte el resource pack al entrar. Si sigue igual, revisar que el sha1 coincida.
- Si aparece "Unknown skill": cargar el preset legacy de AuraSkills (ver comandos).
- El área de los taladros puede romper bloques dentro de una zona de WorldGuard si picás justo en el borde.

## Servidor de prueba local

Para probar sin tocar Aternos hay una copia del servidor (mismos plugins) en la carpeta temporal de Claude. Se puede rearmar bajando Paper 26.1.2 y los mismos plugins. El mundo de prueba es plano.
