# Recetas Astral en mesa: entrega sin desplegar

Generado por `python datapack-src/deploy_recetas_mesa.py`. Posterior a alas-casco; anterior al tren del lobby.
Servidor documentado: Empower, Paper 26.1.2 build 74 / Java 25. Aternos conserva una copia y no admite instalar este JAR propio; no eludir esa restriccion.

## Archivos locales y destinos exactos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` (1.5.0) |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |

`build/runtime/mesa.json` ya esta empacado dentro del JAR: no subirlo por separado.
No cambia el resource pack ni server.properties. Conservar el FINAL privado y SHA-1 de `alas-casco.md`;
no reemplazarlo por el ZIP publico ni volver a subir a R2 por esta tarea.

| Archivo | SHA-256 |
|---|---|
| `build/runtime/AstralDecor.jar` | `852dc84963ba503fb99464ecc90134985047e5c583415dc80668767ee4094f5f` |
| `build/AstralRPG-Items.zip` | `192c43d235c1d14299030d35b4a73b2412ebd8beccb39dc1da232c639f0cc88d` |

## Instalacion pendiente

1. Respaldar ambos archivos de destino. Esperar sala vacia y **apagar el servidor**.
2. Reemplazar solo los dos archivos indicados; conservar configs de AstralDecor, AuraSkills y todos los mundos/playerdata.
3. Encender. **Reinicio completo obligatorio** por el JAR; no PlugMan ni `/reload`. No hacen falta comandos de recarga despues.
4. Verificar `Done`, AstralDecor 1.5.0, `Mesa Astral: 130 recetas exactas registradas` y ausencia de errores nuevos en consola.
5. Hacer la revision con cliente indicada abajo. No sustituir mundos ni usar Worlds > Upload en la fila world.

No instalar TableProbe.jar, carpetas del ensayo, logs, originales ni mapas privados.
No se accedio al panel ni se desplego esta tarea. Claude continua la instalacion con navegador autorizado.

## Comportamiento y decisiones

- 130 recetas de mesa sin forma fija: cada unidad ocupa una casilla. Ingredientes y cantidades vienen de `RECIPES` de build.py,
  exactamente los mismos que usa la Forja. Las 28 que superan nueve unidades quedan solo en Forja, sin abaratar ni comprimir materiales.
- ExactChoice para cada ingrediente, incluidos los vanilla y la botella de agua; resultado construido desde las loot tables del datapack,
  con nombre, lore, componentes, requisitos y encantamientos reales. Se necesita el datapack y los plugins de encantamientos habituales.
- La mesa exige los requisitos AuraSkills del resultado al preparar y al retirar. Si AuraSkills falta o no puede consultar el jugador, bloquea
  recetas con requisitos. Muestra el nivel necesario, limitado a un aviso cada dos segundos.
  La Forja existente no verificaba niveles al fabricar (solo al usar equipo): se conserva ese comportamiento por el pedido de mantenerla igual.
- Desbloqueo por material: cada segundo revisa el inventario, tambien despues de entrar/reiniciar. Un ingrediente exacto basta; no desbloquea todo al entrar.
  La lista descubierta es la nativa de Minecraft. Categoria MISC; grupo `astral_<resultado>` para no esconder distintas recetas detras de una tarjeta.
- El libro admite el autollenado normal de Paper. Consumo, shift-clic, inventario lleno y sobrantes quedan en el motor nativo, sin descontar ni dar items a mano.
  Las misiones de forja I/V se notifican despues de verificar consumo real.
- Bloquea items Astral en recetas comunes de 2x2/3x3 (incluida reparacion), herreria vanilla, fundicion/coccion, combustible y pociones.
  El horno sigue haciendo Netherita Fundida desde un lingote vanilla.
- ExactChoice distingue tambien dano, nombre, mejoras y encantamientos: equipo modificado se sigue usando como ingrediente en la Forja existente.
  No se pierden mejoras intentando encajarlo a la fuerza en la mesa.
- Los items canonicos previos reciben solo el lore nuevo al llevarlos en inventario, conservando cantidad y demas componentes. Si tienen otras modificaciones,
  no se normalizan. Sin cambio global de ITEM_VERSION ni clear/give para esta migracion.
- Guia: cada receta indica mesa o solo Forja. En Como se juega explica el libro y `Opciones -> Controles -> Acciones rapidas`.
  El tag `minecraft:quick_actions` ya estaba registrado y sigue abriendo la guia. Lore explica usos y lugar de fabricacion.

## Solo Forja por superar 3x3

| Resultado | Unidades totales |
|---|---:|
| `espada_sombras` | 16 |
| `hacha_terremoto` | 14 |
| `varita_estallido` | 12 |
| `taladro_mitril` | 13 |
| `taladro_amatista` | 16 |
| `taladro_rubi` | 13 |
| `motosierra_basica` | 10 |
| `motosierra_infernal` | 10 |
| `motosierra_astral` | 14 |
| `carnivora_espada` | 13 |
| `carnivora_hacha` | 13 |
| `carnivora_guadana` | 13 |
| `carnivora_baston` | 13 |
| `carnivora_arco` | 13 |
| `carnivora_lanza` | 13 |
| `carnivora_martillo` | 13 |
| `carnivora_helmet` | 13 |
| `carnivora_chestplate` | 17 |
| `carnivora_leggings` | 13 |
| `carnivora_boots` | 13 |
| `carnivora_pico` | 13 |
| `carnivora_pala` | 13 |
| `carnivora_azada` | 13 |
| `carnivora_cana` | 13 |
| `carnivora_escudo` | 13 |
| `carnivora_alas` | 13 |
| `asura_espada` | 45 |
| `asura_alas` | 45 |

## Verificaciones y limites

Verificado localmente el 11/11/2026: compilacion Java 25; 234 pruebas del datapack y 7 de herramientas aprobadas;
`verify.py` aprobado; auditoria publica sin arte privado. Paper 26.1.2 build 74:
50 comprobaciones aprobadas (25 en cada arranque), cero fallos y cero errores nuevos de consola.
Incluye clic normal e inventario lleno, ademas de shift-clic y paquete de autollenado del libro.

Reproduccion desde raiz (Python con Pillow, PyYAML y NumPy instalados):

```text
python datapack-src/build.py
python datapack-src/build_runtime.py --jdk <JDK25/bin> --server <Paper-local>
python -m unittest discover -s datapack-src -p "test_*.py"
python datapack-src/verify.py
python tools/probar_recetas_paper.py --java <JDK25/bin/java.exe> --base <Paper-local>
python datapack-src/deploy_recetas_mesa.py
python tools/verificar_terceros.py
```

El ensayo corre dos arranques completos de un Paper aislado. Verifica cuatro recetas con materiales exactos y sustitutos vanilla,
bloqueo/restauracion por nivel, receta vanilla sin Astral, shift-clic, desbloqueo por ingrediente, paquete de clic de libro con autollenado,
migracion conservadora de lore y fabricacion desde la Forja. No conecta un cliente real ni valida sus pixeles.
Los logs del ensayo quedan exclusivamente en `.local/recetas-probe/`; no se publican.

Pendiente con cliente vanilla 26.1.2 y el FINAL aceptado: ver las tarjetas/iconos y texto completo del aviso por nivel,
abrir la guia con la tecla asignada, comprobar las mismas interacciones con raton real, receta con cubo de lava y su sobrante,
probar altar con materiales arrojados y confirmar persistencia del libro al reconectar. Revisar consola remota despues del reinicio.
