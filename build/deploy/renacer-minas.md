# Renacer de Minas — 25/11/2026

Preparado; NO desplegado. Arranca privado (solo ByTrainx); no abrir al publico
hasta prueba del dueno en su sala.

| Local | Destino |
|---|---|
| build/minas/Skript/scripts/astral_minas.sk | plugins/Skript/scripts/astral_minas.sk |
| build/gameplay/astral_cosmeticos.sk | plugins/Skript/scripts/astral_cosmeticos.sk |
| build/menus/DeluxeMenus/gui_menus/cosmeticos_titulos.yml | plugins/DeluxeMenus/gui_menus/cosmeticos_titulos.yml |

Recargar en consola: `skript reload astral_minas`, `skript reload astral_cosmeticos`,
`dm reload`, `minasrenacer privado`. Revisar consola: cero errores.
Estos tres archivos no requieren apagar/reiniciar. No ejecutar instalacion.txt,
minasmoldes ni modificar/reemplazar mundos.

FINAL privado local (raiz del proyecto):
`.local/terceros/AstralRPG-privado/build/entregas/renacer-minas-25-11/AstralRPG-Textures.zip`

Base: FINAL cazador-bugs-24-11 e765df5c. Solo agrega tres recursos de minero_renacido.
SHA-1: `30e8b93f235804251f9709ca68dfe79454c6aca0`.
Subir ese ZIP FINAL a R2 justo antes del reinicio usando `tools/subir_pack_r2.py`
(con el ZIP como argumento), verificar descarga y actualizar resource-pack-sha1
en server.properties. Reiniciar para cargarlo. Nunca subir el ZIP publico encima.
El titulo funciona por prefijo de LuckPerms aun sin insignia instalada.

Prueba remota pendiente: ByTrainx rango 20, confirmar, verificar rango 1,
bloques/minutos 0, renac 1 y permiso; venta Carbon I x1,10. Otro jugador en
privado no debe ver el boton ni recibir bonus. Probar cancelar, doble clic y tope 10.
No se realizaron cambios en Aternos/Empower ni R2.

## Verificaciones locales

`minas.py` y `cosmeticos.py` ejecutados con Python del entorno local tanda17-venv
(sin Python global). FINAL generado y base SHA-1 validada; auditoria
`tools/verificar_terceros.py` aprobada. `git diff --check` aprobado.
Renacimiento general revisado: solo elimina am.rank, no am.renac.
Paper 26.1.2 + Skript 2.17.1: ensayo aislado con Essentials/Vault,
ExcellentEnchants y AstralMinasLimite; ranking externo sustituido por stub sin
operaciones. No equivale a una prueba con jugadores. Logs solo en .local.
Prueba de interfaz/venta/permisos con jugadores: pendiente.

## Publicacion

Incluye, con autorizacion expresa, cambios previos ya en vivo de recorte de
minas y titulo Dueño en los generadores compartidos y salidas de esta tarea.
No incluye economia.py ni /pay, ni otros cambios previos. docs/MINAS.md se
publica por contenido separado, conservando sus cambios previos solo locales.

Resultado Paper: All scripts loaded without errors (3 scripts; cero errores de Skript). ExcellentEnchants aviso que falta el proveedor de tooltips en el ensayo; no impidio la carga.
