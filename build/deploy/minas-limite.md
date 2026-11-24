# Minas: minerales limitados al mundo (24/11/2026)

Generado por `datapack-src/minas_limite.py`. **Sin desplegar.** Rama de entrega:
`minas-limite`; Claude debe revisar e integrar en main antes de instalar la version elegida.
AstralMinasLimite 1.0.0 + Skript de esta entrega se instalan juntos.

## Archivos exactos

| Archivo local, relativo al worktree AstralRPG-minas-limite | Destino | SHA-256 |
|---|---|---|
| `build/minas/AstralMinasLimite.jar` | `plugins/AstralMinasLimite.jar` | `d02835ae0a1734b94d9e735f9a4a1daf94ec2a6e2f5a596732b87b2f47ab7ef1` |
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` | `a9bd244b44a6ef2a5d51ff4e319a4783f452cc8f7a8b5f4aa6d58f5ad5db31c1` |

No subir fuentes, tests, plugin MinasLimiteProbe, `.local`, logs ni mapas.
No cambia resource pack, datapack, TAB, economia ni las otras minas.
Conservar variables de Skript y todas las configuraciones existentes.

## Instalacion que continua Claude

1. Confirmar servidor y version: CLAUDE.md identifica Empower como principal y
   Aternos como copia. Paper 26.1.2, Java 25, Skript 2.17.1 y Vault/EssentialsX.
2. Apagar el servidor. Guardar copia de los dos archivos reemplazados fuera del repo publico.
3. Subir SOLO los dos archivos de la tabla a sus destinos. No reemplazar mundos
   ni usar Worlds > Upload en world. No ejecutar instalacion.txt, moldes o migracion de mapas.
4. Arrancar (reinicio completo obligatorio por el JAR). No usar /reload ni PlugMan.
5. Consola: `version AstralMinasLimite`, `minaslimite` y `minaslimite privado`.
   Verificar ausencia de errores al cargar AstralMinasLimite y astral_minas.sk.
   El modo queda persistente en plugins/AstralMinasLimite/config.yml; no reemplazarlo
   por una config de prueba. `skript reload astral_minas` solo si se cambia despues el script,
   con el JAR ya cargado; para la primera instalacion basta el reinicio.
6. Dueño con ByTrainx: picar, apilar, vender (comprobar oro), probar Fortuna, taladro,
   ropa de Minero e inventario lleno. Intentar cofre/Ender/shulker/mochila, arrastre,
   shift-clic, tecla numero, trade y ah. Salir por lobby, /home, /tpa y portal;
   comprobar aviso y borrado de barra/inventario/secundaria/armadura/cursor/grilla/Ender.
   Conservar diamantes iguales del Survival. Probar otro jugador en privado:
   sus drops normales deben seguir sin marca, venderse y salir normalmente.
7. Solo despues de la prueba y autorizacion del dueño: `minaslimite publico`.

Aternos no admite subir JAR propios por Files: esta variante requiere el panel
del principal Empower o disponibilidad autorizada del plugin en el catalogo de Aternos.
No usar APIs privadas ni intentar eludir esa restriccion. Despliegue pendiente de Claude.

## Verificacion reproducible

```
python datapack-src/minas.py --script-only
python datapack-src/minas_limite.py --jdk <bin-JDK25> --server <Paper-local>
python tools/probar_minas_limite_paper.py --java <java.exe> --base <Paper-local>
```

Paper aislado en `.local/minas-limite-paper`, puerto 25643, solo 127.0.0.1.
Ensayo con jugadores NMS simulados e inventarios/eventos reales, sin cliente real.
El script de rankings tambien se carga para probar rk_sumar sin reemplazarlo.
La venta conserva los filtros de nombre/lore; no se usa custom_model_data.
La marca PDC se prueba tambien serializada. Prueba visual y compatibilidad con el
conjunto completo de plugins del remoto pendientes. No certificar despliegue sin consola.

Resultado local del 24/11: **32 comprobaciones Paper aprobadas**, 0 fallos;
Skript/rankings cargaron sin errores y sin warnings de estos scripts ni del plugin.
4 pruebas nuevas de contrato aprobadas. El entorno informa avisos de Windows,
modo offline local, actualizadores de Paper/Essentials y HTTP 403 del actualizador
de Skript; no corresponden a errores de carga de la entrega.

Regresiones existentes de economia/oficios/tanda_xp/travel_ui: en el worktree y en
una exportacion limpia de HEAD hay los mismos 4 fallos y 8 errores (37 pruebas
existentes): mapas/previews privados ausentes y salidas/UI desactualizadas en la base.
No se modificaron esos componentes para esta tarea. Tests nuevos: test_minas_limite.

## Alcance y recuperacion

La marca no es retroactiva: minerales viejos sin marca siguen normales. En privado,
solo ByTrainx genera marca y recibe borrado; otros no pueden recoger los drops
marcados del tester. Al volver de publico a privado se conservan las marcas antiguas
y sus barreras de transferencia, pero el borrado vuelve a ByTrainx.
Si se añade otro plugin de comercio, revisar sus comandos/alias y comportamiento
antes de habilitarlo en las minas. Los plugins externos deben respetar cancelaciones
de eventos. No se prueba con el JAR remoto de cada mochila/tumba/comercio.

Para retirar la entrega, apagar y restaurar juntos script y JAR previos, conservando
la config. No eliminar solo el JAR: el script depende del efecto de entrega.
Los materiales ya borrados no se recuperan al retirar el plugin; la regla empieza
privada para permitir al dueño validar antes de hacerla publica.
