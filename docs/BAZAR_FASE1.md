# Bazar Astral — 1.3.1 privada, 27/11/2026

La entrega vigente de categorías es [bazar-categorias-27-11.md](../build/deploy/bazar-categorias-27-11.md).
Combate abre por defecto y reúne ambas Netheritas; Bosque (Madera Estelar/Palo Reforzado)
y Océano (Perla Abisal/Coral Astral) reemplazan Minería y Bosque y pesca. Consumibles y
Especiales siguen iguales. Las órdenes guardan ID, no categoría; se conserva SQLite
sin migración destructiva. El cargador admite el catálogo antiguo y categorías desconocidas.

La especificación de operaciones es [bazar-hypixel.md](../build/deploy/bazar-hypixel.md): archivos y destinos,
tabla completa de referencias con cálculos/supuestos, fichas para Gemini y resultado del ensayo.
La entrega histórica de fase 1, citada abajo, describe el flujo anterior.

Inicio reúne categorías en columna y productos paginados. Producto ofrece cuatro acciones:
comprar/vender al instante y crear orden de compra/oferta de venta. La compra entrega al inventario;
la venta paga al saldo de Essentials. Exceso o devolución que no entra queda guardado, nunca al piso.
Vender inventario confirma productos y total, vende solo materiales canónicos con demanda y conserva equipo.
Mis órdenes cobra con clic, cancela/devuelve con clic derecho y tiene Cobrar todo. No hay ventanas separadas
de Retiros ni Retirar plata. Los cobros de 1.1.0 se recuperan con Cobrar todo.

Cantidad instantánea: 1, un stack, llenar inventario, manual. Órdenes: 64, 160, 1024, manual;
en venta también Todo lo que tengo. Precio: igual a la mejor, mejorar $0,10, 5% del margen o manual.
Sin ambas puntas/margen positivo se deshabilita 5%. A mano y Buscar capturan el chat sin publicarlo,
vencen a los 30 segundos y aceptan cancelar. `/bazar entrada <valor>` sigue funcionando.

Referencias: `precios_referencia()` lee drops, recetas y Tienda en memoria. Cada receta suma sus
ingredientes y divide por la producción; vanilla sin precio suma cero. Mínimo ref/10 o piso NPC;
máximo ref×20. El tier adaptable exige supuestos explícitos en la tabla; seis referencias de
Colmillo Carnívoro/monedas Asura siguen pendientes por falta de fuente monetizable.

Migración automática e incremental de SQLite: agrega `claims.order_id` y `order_credit`.
Conserva órdenes, custodia, wallet y journal; las órdenes anteriores siguen ejecutándose aunque
queden fuera de los límites nuevos. No eliminar ni reemplazar la base al instalar.
Conservar juntos SQLite/WAL/SHM, Essentials y archivos de jugador para recuperación.

Inicio, Producto, Cantidad, Precio, Mis órdenes y Vender inventario usan el arte Gemini
del 26/11. Confirmar orden y equipo conservan el diseño previo. La entrega 1.3.1 cambia
solo los botones del inicio sobre el FINAL en vivo; no reemplazarlo por el ZIP público.
F3+H muestra información avanzada del cliente que Paper no permite ocultar selectivamente.

Sigue oculto: `publico: false`, permiso por defecto false y solo ByTrainx autorizado.
Requiere reinicio completo del plugin; despliegue y prueba visual del dueño pendientes.

---

## Referencia histórica de fase 1 (flujo sustituido por 1.2.0)

Esta especificación ajusta el plan histórico de `BAZAR.md` con las reglas nuevas del dueño.
Entrega regenerable, catálogo completo, precios, archivos, hashes y ventanas:
[bazar-fase1.md](../build/deploy/bazar-fase1.md).

Desde `datapack-src/`: `python bazar.py --jdk <bin Java 25> --server ../.local/testsrv`.
Genera únicamente `build/bazar/` y la entrega; lee los registros de ítems de `build.py`
en memoria, sin ejecutar su exportación ni regenerar archivos de otras tareas.
Fuentes de ejecución: `runtime/AstralBazar.java` y `runtime/BazarStore.java`.

El catálogo usa fuentes locales previas aún sin publicar (Clases, Vacío, manzanas,
historia y ajustes de economía/build). Esta tarea no publica esos cambios ajenos.
Para recompilar el JAR desde un checkout limpio usando el catálogo versionado:
`python bazar.py --solo-compilar --jdk <bin Java 25>`. Regenerar los ítems desde
sus generadores requiere sincronizar esas fuentes en su tarea correspondiente.

Solo 88 productos Astrales fungibles. La tabla editable `PRODUCTOS` en `bazar.py`
define ID, categoría y referencia; nombre, material y componentes provienen de los
generadores. Validación estricta de todos los componentes mediante `isSimilar`:
rechaza vanilla, nombre cambiado, encantamientos, gemas/reforja, daño y datos extra.
Los IDs, tipos y materiales se auditan al generar. Las cinco monedas Asura son materiales;
no hay pescados Astrales fungibles registrados. No se agregan productos vanilla ni cultivos
vanilla para llenar categorías vacías.

Cristal de Caverna, Geoda, Fragmento Estelar y Núcleo de Meteorito respetan como mínimo
lo que paga su vendedor, leído de `economia.py`. Las menas de Minas son vanilla y
quedan fuera. Los materiales sin precio NPC usan referencias iniciales editables.

Equipo: únicamente armas y armaduras Astrales de la lista positiva. Incluye libros de
Invocador, guantes y armas especiales. Se vende solo al servidor; nunca se compra ni
se crean órdenes entre jugadores. Pago por pieza = `PLATA_MOB_TIER[tier] * 2`:
3.000 / 6.000 / 12.000 / 24.000 / 50.000 / 100.000 / 200.000 / 400.000 / 800.000 /
1.600.000. No varía por encantamientos, gema, reforja o mejora. La confirmación informa
el total y advierte sobre mejoras; recomienda Subastas. Excluye historia, mochilas,
mascotas, cosméticos, taladros, motosierras y herramientas de oficio.

Todo depósito de equipo queda en custodia SQLite. Cerrar devuelve lo que cabe;
el resto queda en Retiros, nunca en el piso. Los productos adquiridos y el dinero
de ventas también se retiran desde Mis órdenes. Las entradas manuales usan
`/bazar entrada <valor>` después de pulsar A mano o Buscar.

Órdenes: prioridad precio/antigüedad, hasta 14 abiertas por jugador, hasta 71.680
unidades, sin vencimiento, llenado offline y aviso al entrar. Se muestran siete
puntas agregadas por precio en cada lado. Cantidades 1/16/64/160/todo/manual;
precio igual al mejor o mejorado $0,10 (en venta se resta). Impuesto 1,25 % acumulado
por oferta, con redondeo al centavo. Historial ponderado por volumen de 1 h y 24 h.
Compra instantánea cobra la profundidad disponible; venta instantánea devuelve
al retiro lo que no se pudo vender. No hay negociación con órdenes propias.

SQLite usa WAL/FULL y transacciones para custodia, reservas y cruces. Hasta 256
contrapartes por lote; grandes cruces continúan una vez por segundo. Sin tareas
cada tick. Vault/inventarios se operan en el hilo principal. Registro de movimientos
en las tablas audit/trades. Respaldo a las 04:45 Argentina en backups, en tarea aparte.

SQLite, Essentials y los archivos de jugador no tienen una transacción compartida.
Se registra la intención antes del movimiento y se concilia al recuperar: recibo
persistente del jugador para ítems, saldo previo/esperado para Vault. Ante un saldo
ambiguo el plugin se pausa persistentemente para conciliación manual; no repite
pagos. No garantiza recuperación automática de fallos físicos ni de cambios externos
coincidentes de saldo. Conservar juntos SQLite/WAL, datos de Essentials y jugadores.

`publico: false`, permiso `astral.bazar.usar` con default false (también para OP).
Solo darlo a ByTrainx. No se modifica el NPC ni DeluxeMenus. Nada público sin arte,
prueba del dueño en su sala y autorización posterior. JAR nuevo requiere reinicio.

Admin: `/bazar admin pausar|reanudar|ver <jugador>|cancelar <orden>|recargar`.
Recargar toma la config operativa; catálogo y tabla de equipo requieren reinicio.
No quitar IDs de productos con custodia u órdenes existentes.

Verificación: `python tools/probar_bazar_paper.py --java <bin Java 25>` y
`python -m unittest discover -s datapack-src -p test_economia.py` desde la raíz.
El ensayo crea un Paper aislado con dos bots, Vault, Essentials y registros de
encantamientos del datapack. No ejecuta funciones de otras tareas locales.
Incluye caída abrupta de JVM y reapertura del mismo servidor. Consultar números
reales de la última verificación en la entrega; no confundirlos con despliegue remoto.
