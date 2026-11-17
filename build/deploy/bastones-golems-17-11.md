# Bastones perforantes y golemcitos - 17/11/2026

Preparado; R2, instalacion y revision con cliente remoto pendientes de Claude. Principal documentado: Empower; Aternos es copia. Confirmar el panel y estado instalado. Base de esta tarea: 0f0d23a / AstralDecor 1.18.0.

## Implementacion

Todos los bastones atraviesan hasta tres enemigos distintos: 100% / 70% / 70%, incluidos fuego IV/VIII. Constante unica HECHIZO_PERFORA en escala.py; Guia Astral y fichas actualizadas (item v26). AstralSpell selecciona intersecciones vanilla/BetterModel una vez, ordenadas antes de la pared; spell_perfora.py conserva /damage magic por jugador y los eventos normales de XP/contadores. Las marcas se limpian en el mismo disparo. PvP solo en arenas; su normalizacion tambien respeta 70%. Excluye mascotas, monturas con propietario, vendedores, estatuas, NoAI, invulnerables y al mago.
AstralDecor 1.20.0 y AstralEfectos 1.4.0 deben instalarse juntos con el datapack. El rayo/bola usa la longitud real del trazado, con explosion por impacto y los interruptores existentes.
Causa del morado: 39 entradas de los tres golemcitos estaban en bettermodel/... fuera de assets/. Se corrige solo ese prefijo; JSON y PNG se conservan byte por byte. No cambia ningun .bbmodel ni YAML; no requiere subir modelos ni mm reload/bettermodel reload. El cristal conserva sus cristales rosados originales; no es la textura negra/magenta faltante.

## Instalar solo esta tarea con el servidor apagado

Estos archivos son copias cerradas de los artefactos publicados de esta tarea, sin los cambios locales previos de Chaman/hitboxes. Evitan confundir el build compartido, que conserva ese trabajo ajeno. No instalar el ZIP publico de texturas.

| Archivo local desde la raiz | Destino | SHA-256 |
|---|---|---|
| `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/tarea/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` | `a869d45df7717870ed48ea8d99490f49ae8f5e1bbf895f291774cde77b3e588c` |
| `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/tarea/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` | `5ab88fb72c00bb9e1ab7cabcde2fb0c6642f89ddebc6fce40eab99a080537836` |
| `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/tarea/runtime/AstralEfectos.jar` | `plugins/AstralEfectos.jar` | `45c93a28bec6828bbaeb9a97d4ce61063e8eadf8ea51ff35a778ae2080d82554` |
| `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/tarea/gameplay/astral_gameplay.sk` | `plugins/Skript/scripts/astral_gameplay.sk` | `44079619c5ad78988a2a16293d5c897dd34a59746a8c9e21c745e9c59b432b80` |

Si Claude instala tambien la entrega previa Chaman/hitboxes, usar las cuatro rutas equivalentes bajo `acumulado/` en esta misma entrega privada: conservan ambos trabajos locales. No publicar ese acumulado como parte de esta tarea ni instalar luego un datapack/JAR historico encima. Sus hashes se registran en manifest-acumulado.json. Los demas modelos/YAML de aquella tarea se toman de su propia entrega.

Apagar, respaldar solo los archivos a reemplazar, instalar las cuatro rutas, actualizar el pack como sigue y reiniciar. No sustituir mundos/regiones ni usar Worlds > Upload en world. El arranque carga datapack y JAR. Si solo se reinstala el script: `skript:skript reload astral_gameplay`. No usar /reload para sustituir el reinicio de los JAR/datapack.

## FINAL privado y R2

Base mas nueva: `.local\terceros\AstralRPG-privado\build\entregas\cascos-silencio-mercader-17-11\AstralRPG-Textures.zip`, SHA-1 `9d83b49323139271250519fbfd7df7f65857d730`. Se verifico preservacion byte por byte de cada entrada fuera de las 39 rutas movidas y resolucion de las texturas de todos los huesos.
FINAL: `.local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/AstralRPG-Textures.zip`. SHA-1 `5448b7ff24d6da012cc08de16a0d74b11b23a2e0`.
Publicacion pendiente: `python tools/subir_pack_r2.py ".local/terceros/AstralRPG-privado/build/entregas/bastones-golems-17-11/AstralRPG-Textures.zip"`. Verificar la descarga publica y su SHA-1; despues cambiar solo resource-pack-sha1 en server.properties, conservando URL fija. Reiniciar.
Vistas CPU privadas de los tres: `.local/terceros/AstralRPG-privado/build/previews/bastones-golems-17-11.png`. No publicar modelos, PNG, FINAL ni vistas en GitHub.

## Verificaciones y pendientes

Paper local: 139 comprobaciones aprobadas sobre los artefactos de tarea. Incluye 100/70/70, cuarto intacto, disparos consecutivos, fuego IV/VIII, pared, mascotas, montura con dueno, NoAI, invulnerables, extremo visual, estallidos y nivel Bajo/interruptor apagado.
30 pruebas Python relacionadas aprobadas. La suite amplia de 375 pruebas detecto 27 fallos previos del simulador de oleadas (espera cuatro llegadas donde el generador local previo produce una); no se modificaron esos generadores ni sus pruebas para esta tarea. La comprobacion antigua del marcador fx_rayo se actualizo al marcador final fx_perfora y pasa.
Prueba reproducible: `python tools/probar_perforacion_paper.py --java <Java25.exe> --base <Paper-local>`. Para auditar otra copia cerrada usar `--artifacts <raiz-con-build>`. No instalar SpellProbe.jar.
Pendiente remoto: revisar consola de datapack, AstralDecor, AstralEfectos, Skript y BetterModel; probar los tres golems en Bosque/Minas/Cumbre con el FINAL nuevo, bastones en horda y pared, exclusiones, arenas, Hechiceria/XP real con AuraSkills y efectos Bajo/Medio/Alto con cliente. El ensayo local verifica eventos de dano unicos atribuidos al mago; no sustituye esa revision visual ni la XP de la configuracion remota.
