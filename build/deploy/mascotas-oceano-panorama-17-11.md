# Mascotas, oceano y panorama - 17/11/2026

Preparado localmente. Sin instalacion remota ni publicacion R2. Continuar sobre lo instalado hasta 1ebd0a5; conservar tambien la tanda 054db88 pendiente.

| Local | Destino | SHA-256 |
|---|---|---|
| `build/runtime/AstralProgression.jar` | `plugins/AstralProgression.jar` | `8dd89a09cb354cade1339752e1a81c342a96a99cb9206f80a1deca8da33027a2` |
| `build/runtime/AstralEfectos.jar` | `plugins/AstralEfectos.jar` | `95a48419a73001a53b5468656f8eaf4d205dc2e345de6c1ccdc50816654b110c` |
| `build/oceano/AstralOceano.jar` | `plugins/AstralOceano.jar` | `35b91ad9b579cc0c1356babec2690d3645bc7ac8b163752e1c13a53cbb7b8142` |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `40bc478d2cb1b35679e14496ae9569abf2887017db6b4419756de19458ab2fc4` |
| `build/gameplay/astral_armas_especiales.sk` | `plugins/Skript/scripts/special_weapons.sk` | `45f2f6bb1292ad1cea5eb4bf655ea678630ffdfda08df6e1d183444f346c1807` |
| `.local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/mythicmobs/skills/mascotas.yml` | `plugins/MythicMobs/skills/mascotas.yml` | `f56962d1413937e87ee17b4c34e602b7129177c25e6554d7ca475ddb3879fc2a` |

La configuracion generada `build/tanda5a/AstralProgression/config.yml` incorpora Mapache/Pinguino del catalogo anterior: integrar solo esas entradas de `mythic` si faltan; conservar el resto de la configuracion instalada.

FINAL privado: `.local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/AstralRPG-Textures.zip`.
SHA-1: `d9ec25c013ccffd028bd384a189e9b3524fdda37`. Base instalada: `96286fbdc33d77b4ebcc11de8b15f7461631bac4`; 17680 entradas conservadas fuera del delta.
El delta efectivo es barril_xp.json y seis panoramas. Conserva modelos, fuentes, Crop & Kettle, cosmeticos y pack instalado; no instalar el ZIP publico.

## Instalacion por Claude

1. Confirmar servidor y versiones en el navegador: Empower es el principal documentado; Aternos es copia. Comparar las entregas pendientes anteriores, incluido 054db88. Respaldar los archivos a reemplazar y `plugins/AstralOceano/decor/`.
2. Apagar e instalar la tabla. Conservar config.yml del oceano (especialmente proxima-regeneracion), mundos, regiones, datos de jugadores y modelos. No instalar ProgressionProbe/Tanda17Probe. Una sola copia activa de cada JAR y special_weapons.sk.
3. Publicar SOLO el FINAL con `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/mascotas-oceano-panorama-17-11/AstralRPG-Textures.zip"`. Verificar la descarga publica y fijar resource-pack-sha1 al SHA-1 anterior, conservando la URL fija.
4. Iniciar con Java 25: reinicio completo obligatorio por los tres JAR y el datapack. El arranque carga MythicMobs/Skript; recargas posteriores de solo YAML: `mm reload`; solo script: `skript:skript reload special_weapons`. No usar PlugMan ni /reload global.
5. Revisar consola: AstralProgression 1.1.0, AstralOceano 1.5.0, AstralEfectos 1.3.0, datapack activo, sin errores de YAML, funciones o Skript. Guardar barcos y texto existentes ANTES de la proxima regeneracion siguiendo docs/OCEANO_DECORACIONES.md.
6. Con cliente, probar mascota existente/nueva/nivel 30 con espada, barrido, arco, baston y area: vida intacta, sin XP ni contador. Hostil normal conserva XP. Monturas con dueno siguen vulnerables y no dan XP. Comprobar el barril en mano/GUI/suelo/marco y el panorama al cargar.

## Alcance y limites

Catalogo actual: 18 mascotas activas (Fenix + 17), no 23. YAML privado: 18 variantes de modelo protegidas; evolucion conserva la misma entidad. El runtime reconoce cualquier ID astral_pet_* y tags astral.pet.* para migrar las cinco retiradas y variantes antiguas al cargar/recibir dano.
Vendedores y estatuas conservan Invincible en sus YAML. Los selectores descartan Invulnerable y astral.pet; AstralEfectos tampoco toma esas entidades como fin del rayo. Las seis monturas con dueno no se vuelven invulnerables.
LynExp instalado administra botellas/encantamientos con XP vanilla; no tiene listener de combate. Sin orbes de estas entidades no recibe XP indirecta. No se encontraron otros consumibles con wrapper de display_context que requieran el mismo cambio; los modelos 3D anteriores quedan sin referencia del barril para conservar el pack.
No hay hologramas de oceano generados por el repo: los avisos son menu/titulo/chat. El texto manual debe guardarse con su volumen. Las decoraciones se restauran al regenerar o con poner; no se reaplican en cada arranque normal.

## Verificaciones realizadas

369 pruebas unitarias aprobadas; contratos finales de panorama/pack repetidos: 4 aprobados. Auditoria publica sin arte privado ni rutas privadas versionadas. Compilados los tres JAR contra Paper 26.1.2 / Java 25.
Paper local: 72 comprobaciones en la fase inicial y 70 tras reiniciar, ambas con failures=0 y sin ERROR. Dano de espada, flecha, magia, explosion, lava, caida y ahogo mediante DamageSource real; vida intacta y cero XP de Combate/Punteria/Hechiceria. Montura propia muere por dano real, sin XP ni MOB_KILLS/KILL_ENTITY; hostil T2 conserva XP real y baja. Las 18 apariciones Mythic y la migracion por tag de las cinco retiradas pasan.
Decoracion de 52 bloques de lado: bloque de diamante, agua y text_display con texto/posicion exactos. Dos reaplicaciones, regeneracion real y reinicio conservan una sola entidad. Cubemap inspeccionado en vista CPU, aristas probadas y polos suavizados; referencias de ambos packs auditadas. Los 52 vendedores/estatuas revisados conservan Invincible.
Paper usa jugador NMS simulado y eventos reales; GP conserva su API pero sus listeners se retiran SOLO en el ensayo para aislar vulnerabilidad/XP. Se omite solo la mecanica visual BetterModel de las skills de prueba. Sin Multiverse local, el ensayo carga explicitamente el oceano al reiniciar. No sustituye cliente visual, seleccion WorldEdit real, WorldGuard/Multiverse ni consola remota.
Reproducir: python tools/verificar_terceros.py; python -m unittest discover -s datapack-src -p "test*.py"; python tools/probar_tanda17_paper.py --java <java25> --base <Paper-local>. Logs solo en .local; nunca instalar el probe en remoto.
