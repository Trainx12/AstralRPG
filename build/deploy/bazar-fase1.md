# Bazar fase 1 — privado, sin desplegar

No se instaló nada en el servidor. El principal documentado es Empower; Aternos es copia.

## Archivos y destinos

| Local | Destino | SHA-256 |
|---|---|---|
| `build/bazar/AstralBazar.jar` | `plugins/AstralBazar.jar` | `2b6fdbeb6f77183eae0d085d86297b2670969bcf247ff004a9d0cc024ab4d54b` |
| `build/bazar/config.yml` | `plugins/AstralBazar/config.yml` | `4c2a9ddb6d4f5723a140a1804b3382d5f583cd66a6aa327a60f8ab091346a656` |
| `build/bazar/productos.yml` | `plugins/AstralBazar/productos.yml` | `d6a7cd10a398982f6eb93ff5cc39a63646b8d8426c5589d18ba320f13a2c61a8` |

Apagar, respaldar los archivos actuales de AstralBazar si existen, subir los tres archivos y arrancar con Java 25 / Paper 26.1.2, Vault y EssentialsX. El JAR necesita REINICIO completo; no usar reload de JAR ni PlugMan.
Conservar siempre `plugins/AstralBazar/bazar.sqlite`, sus archivos WAL/SHM, `backups/` y datos de Essentials/jugadores. Nunca reemplazar mundos ni usar Worlds > Upload en world.
Si Aternos no permite instalar este JAR propio, queda bloqueado en esa plataforma; usar el panel autorizado de Empower. No usar APIs privadas.

Mantener `publico: false`. Solo para el dueño: `lp user ByTrainx permission set astral.bazar.usar true`.
Verificar consola: `Bazar privado listo`, sin errores del plugin. ByTrainx prueba `/bazar` en `/modo admin` y `/sala`. Otro jugador debe recibir Próximamente. Aldeano y DeluxeMenus siguen iguales.
Después, `/bazar admin pausar`, `/bazar admin reanudar`. Cambios operativos de config: `/bazar admin recargar`; cambios del catálogo requieren reinicio y mantener los IDs de órdenes existentes.

## Verificación

Paper 26.1.2 build 74, Java 25, Vault y EssentialsX: 566 comprobaciones, 0 fallos, dos bots y caída real de JVM con recuperación. test_economia.py: 17 tests, OK. Consola del ensayo final: 0 líneas ERROR; avisos de versión de Paper/Essentials ajenos al Bazar.

El ensayo es aislado con Paper real, Essentials, Vault y los registros reales de encantamientos del datapack; no ejecuta funciones/ticks de otras tareas locales. La prueba de caída usa Runtime.halt y vuelve a abrir el mismo servidor.
El catálogo se generó sobre las fuentes locales vigentes. Clases, Vacio, manzanas e historia y los ajustes recientes de economia/build son trabajo previo que no se publica en esta tarea. Hasta que se publique por separado, un checkout limpio puede recompilar este JAR y catálogo versionado con `python bazar.py --solo-compilar --jdk <bin Java 25>`; regenerar el catálogo desde todos los generadores requiere esas fuentes locales.
La prueba del dueño, el conjunto completo de plugins remotos y su consola siguen pendientes. No se certifica despliegue.

## Catálogo final

Todos usan custom_data Astral, material y componentes canónicos completos. Versiones antiguas deben pasar por la migración del datapack. Nombre cambiado, encantamientos, daño o componentes adicionales se rechazan como producto.

| Categoría | ID | Nombre | Referencia | Mínimo | Máximo | Piso servidor |
|---|---|---|---:|---:|---:|---:|
| Bosque y pesca | `coral_astral` | Coral Astral | 10000 | 1000 | 100000 | 0 |
| Bosque y pesca | `madera_estelar` | Madera Estelar | 5000 | 500 | 50000 | 0 |
| Bosque y pesca | `palo_reforzado` | Palo Reforzado | 10000 | 1000 | 100000 | 0 |
| Bosque y pesca | `perla_abisal` | Perla Abisal | 15000 | 1500 | 150000 | 0 |
| Combate | `alma_corrupta` | Alma Corrupta | 15000 | 1500 | 150000 | 0 |
| Combate | `asura_moneda_card` | Moneda Asura Carta | 30000 | 3000 | 300000 | 0 |
| Combate | `asura_moneda_circle` | Moneda Asura Circulo | 30000 | 3000 | 300000 | 0 |
| Combate | `asura_moneda_emerald` | Moneda Asura Esmeralda | 30000 | 3000 | 300000 | 0 |
| Combate | `asura_moneda_square` | Moneda Asura Cuadrado | 30000 | 3000 | 300000 | 0 |
| Combate | `asura_moneda_triangle` | Moneda Asura Triangulo | 30000 | 3000 | 300000 | 0 |
| Combate | `chispa_astral` | Chispa Astral | 15000 | 1500 | 150000 | 0 |
| Combate | `colmillo_carnivoro` | Colmillo Carnivoro | 30000 | 3000 | 300000 | 0 |
| Combate | `corazon_fin` | Corazon del Fin | 15000 | 1500 | 150000 | 0 |
| Combate | `corazon_shulker` | Corazon de Shulker | 15000 | 1500 | 150000 | 0 |
| Combate | `cristal_arcano` | Cristal Arcano | 15000 | 1500 | 150000 | 0 |
| Combate | `cristal_refinado` | Cristal Arcano Refinado | 15000 | 1500 | 150000 | 0 |
| Combate | `cuero_tratado` | Cuero Tratado | 15000 | 1500 | 150000 | 0 |
| Combate | `esencia_elite` | Esencia de Elite | 15000 | 1500 | 150000 | 0 |
| Combate | `esencia_nether` | Esencia del Nether | 15000 | 1500 | 150000 | 0 |
| Combate | `esencia_vacio` | Esencia del Vacio | 15000 | 1500 | 150000 | 0 |
| Combate | `esquirla_eclipse` | Esquirla de Eclipse | 15000 | 1500 | 150000 | 0 |
| Combate | `fragmento_astral` | Fragmento Astral | 15000 | 1500 | 150000 | 0 |
| Combate | `fragmento_cristal` | Fragmento de Cristal Arcano | 15000 | 1500 | 150000 | 0 |
| Combate | `fragmento_ocaso` | Fragmento de Ocaso | 15000 | 1500 | 150000 | 0 |
| Combate | `fragmento_umbrio` | Fragmento Umbrio | 15000 | 1500 | 150000 | 0 |
| Combate | `gema_luminica` | Gema Luminica | 15000 | 1500 | 150000 | 0 |
| Combate | `gema_luminica_perfecta` | Gema Luminica Perfecta | 15000 | 1500 | 150000 | 0 |
| Combate | `gema_umbria` | Gema Umbria | 15000 | 1500 | 150000 | 0 |
| Combate | `gema_umbria_fragmentada` | Gema Umbria Fragmentada | 15000 | 1500 | 150000 | 0 |
| Combate | `gema_umbria_perfecta` | Gema Umbria Perfecta | 15000 | 1500 | 150000 | 0 |
| Combate | `nucleo_astral` | Nucleo Astral | 15000 | 1500 | 150000 | 0 |
| Combate | `nucleo_eolico` | Nucleo Eolico | 15000 | 1500 | 150000 | 0 |
| Combate | `nucleo_furia` | Nucleo de Furia | 15000 | 1500 | 150000 | 0 |
| Combate | `nucleo_furia_pura` | Nucleo de Furia Pura | 15000 | 1500 | 150000 | 0 |
| Combate | `nucleo_supernova` | Nucleo de Supernova | 15000 | 1500 | 150000 | 0 |
| Combate | `polvo_astral` | Polvo Astral | 15000 | 1500 | 150000 | 0 |
| Combate | `shadowsteel` | Acero Sombrio | 15000 | 1500 | 150000 | 0 |
| Consumibles | `manzana_t10` | Manzana del Fin | 3.2e+06 | 320000 | 3.2e+07 | 0 |
| Consumibles | `manzana_t2` | Manzana Mineral | 12000 | 1200 | 120000 | 0 |
| Consumibles | `manzana_t3` | Manzana Ancestral | 24000 | 2400 | 240000 | 0 |
| Consumibles | `manzana_t4` | Manzana Glacial | 48000 | 4800 | 480000 | 0 |
| Consumibles | `manzana_t5` | Manzana Ignea | 100000 | 10000 | 1e+06 | 0 |
| Consumibles | `manzana_t6` | Manzana del Ocaso | 200000 | 20000 | 2e+06 | 0 |
| Consumibles | `manzana_t7` | Manzana del Eclipse | 400000 | 40000 | 4e+06 | 0 |
| Consumibles | `manzana_t8` | Manzana Supernova | 800000 | 80000 | 8e+06 | 0 |
| Consumibles | `manzana_t9` | Manzana del Vacio | 1.6e+06 | 160000 | 1.6e+07 | 0 |
| Especiales | `cristal_caverna` | Cristal Astral en bruto | 17000 | 8500 | 170000 | 8500 |
| Especiales | `fragmento_estelar` | Fragmento Estelar | 36000 | 18000 | 360000 | 18000 |
| Especiales | `gema_amatista_1` | Amatista Cruda | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_amatista_2` | Amatista Pulida | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_amatista_3` | Amatista Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_amatista_4` | Amatista Perfecta | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_amatista_5` | Amatista Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_jade_1` | Jade Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_jade_2` | Jade Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_jade_3` | Jade Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_jade_4` | Jade Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_jade_5` | Jade Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_onix_1` | Ónix Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_onix_2` | Ónix Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_onix_3` | Ónix Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_onix_4` | Ónix Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_onix_5` | Ónix Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_opalo_1` | Ópalo Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_opalo_2` | Ópalo Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_opalo_3` | Ópalo Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_opalo_4` | Ópalo Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_opalo_5` | Ópalo Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_rubi_1` | Rubí Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_rubi_2` | Rubí Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_rubi_3` | Rubí Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_rubi_4` | Rubí Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_rubi_5` | Rubí Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_topacio_1` | Topacio Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_topacio_2` | Topacio Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_topacio_3` | Topacio Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_topacio_4` | Topacio Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_topacio_5` | Topacio Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `gema_zafiro_1` | Zafiro Crudo | 10000 | 1000 | 100000 | 0 |
| Especiales | `gema_zafiro_2` | Zafiro Pulido | 40000 | 4000 | 400000 | 0 |
| Especiales | `gema_zafiro_3` | Zafiro Impecable | 160000 | 16000 | 1.6e+06 | 0 |
| Especiales | `gema_zafiro_4` | Zafiro Perfecto | 640000 | 64000 | 6.4e+06 | 0 |
| Especiales | `gema_zafiro_5` | Zafiro Estelar | 2.56e+06 | 256000 | 2.56e+07 | 0 |
| Especiales | `geoda_estelar` | Geoda Estelar | 152000 | 76000 | 1.52e+06 | 76000 |
| Especiales | `nucleo_meteorito` | Nucleo de Meteorito | 1e+06 | 500000 | 1e+07 | 500000 |
| Especiales | `polvo_cristal` | Polvo de Cristal | 100000 | 10000 | 1e+06 | 0 |
| Mineria | `netherita_fundida` | Netherita Fundida | 10000 | 1000 | 100000 | 0 |
| Mineria | `netherita_reforzada` | Netherita Reforzada | 20000 | 2000 | 200000 | 0 |

Minas vende minerales vanilla: quedan fuera del catálogo. Los cuatro pisos propios vienen de `economia.CAVERNAS_PRECIO` y `VACIO_PRECIO`. Comprar en el Bazar cuesta al menos el precio de venta al servidor, sin ganancia de arbitraje. No existen pescados Astrales fungibles registrados actualmente: no se inventan IDs. Las monedas Asura sí son materiales registrados.

Referencias de materiales sin venta NPC: valores iniciales editables, requieren revisión de balance del dueño. No se compra ni vende equipo entre jugadores en este bazar.

## Equipo al servidor

| Tier | Pago por pieza |
|---|---:|
| 1 | $3,000 |
| 2 | $6,000 |
| 3 | $12,000 |
| 4 | $24,000 |
| 5 | $50,000 |
| 6 | $100,000 |
| 7 | $200,000 |
| 8 | $400,000 |
| 9 | $800,000 |
| 10 | $1,600,000 |

Fórmula: `economia.PLATA_MOB_TIER[tier] * 2`. Sin impuesto para esta liquidación al servidor. Mismo valor con mejoras. Toda venta pide confirmación y la mejorada advierte que en Subastas vale más. El pago queda en saldo para retirar a Vault.
Lista positiva de armas/armaduras; incluye bastones, guadañas, lanzas, cuchillos, ballestas, guantes y libros de clase. Excluye historia, mochilas, mascotas, cosméticos, taladros, motosierras y oficios.

## Persistencia y operación

SQLite FULL/WAL guarda órdenes, custodia, saldo, trades y audit en transacciones. El registro de movimientos es la tabla `audit` (y `trades`), dentro del archivo SQLite, no un log público. Impuesto 125 puntos base, acumulado por oferta y redondeado al centavo; no se evita fraccionando ventas.
Cada cruce procesa hasta 256 contrapartes; la cola restante continúa una vez por segundo, también para desconectados. Ninguna tarea corre cada tick. Acceso a inventarios y Vault solo en hilo principal; respaldo diario a las 04:45 Argentina mediante SQLite VACUUM INTO en tarea asíncrona.
Vault y el archivo del jugador no comparten transacción con SQLite. El journal escribe intención antes de tocar recursos. Inventario y recibo se guardan juntos con saveData; al entrar se concilia una vez. Vault se concilia por saldo previo/esperado. Si no coincide, pausa persistente y revisión manual con Essentials; no se repite el pago a ciegas. No editar/borrar journal ni restaurar solo una de las bases durante conciliación.
No se promete atomicidad distribuida absoluta: cambios externos coincidentes de saldo o fallos de disco requieren conciliación. Para producción pública hace falta la prueba del dueño y revisión de recuperación con los respaldos operativos.

## Ventanas para diseño (fase 3)

Slots desde 0. Títulos fijos; sin glifos ni arte en esta fase. Slots no listados vacíos. Entradas manuales por `/bazar entrada <valor>`: no hay una ventana adicional de chat/yunque.

| Título exacto | Filas | Casilleros y botones |
|---|---:|---|
| Bazar - Categorias | 4 | 10–14 categorías; 20 buscar; 22 Mis órdenes; 24 vender equipo; 35 cerrar. |
| Bazar - Productos | 6 | 0–44 productos de categoría/búsqueda; 45 volver; 48 anterior; 50 siguiente; 53 cerrar. |
| Bazar - Producto | 6 | 4 producto, rango e historial; 10–16 siete compras; 19–25 siete ventas; 28 comprar instante; 30 vender instante; 32 orden compra; 34 oferta venta; 40 Mis órdenes; 45 volver; 53 cerrar. |
| Bazar - Cantidad | 3 | 10/11/12/13 = 1/16/64/160; 15 todo; 16 a mano; 18 volver; 26 cerrar. |
| Bazar - Precio | 3 | 11 igual al mejor; 13 mejorar $0,10 (compra suma, venta resta); 15 a mano; 18 volver; 26 cerrar. |
| Bazar - Confirmar orden | 3 | 11 confirmar; 13 resumen cantidad, límite e impuesto; 15 volver. El resto vacío. |
| Bazar - Mis ordenes | 6 | 0–35 órdenes (activas primero); 39 retiros de objetos; 41 retirar saldo; 45 volver; 48 anterior; 50 siguiente; 53 cerrar. |
| Bazar - Orden | 3 | 11 cancelar y devolver restante; 13 avance, plata e impuesto; 18 volver; 26 cerrar. |
| Bazar - Retiros | 6 | 0–44 lotes para retirar; 45 volver; 48 anterior; 50 siguiente; 53 cerrar. |
| Bazar - Vender equipo | 6 | 0–44 vista del lote en custodia; clic simple en inventario inferior deposita pieza; 45 volver; 49 total/confirmar; 53 cerrar. Cerrar devuelve, exceso queda para retirar. |
| Bazar - Confirmar equipo | 3 | 11 vender definitivamente; 13 advertencia de mejoras/valor; 15 cancelar y devolver. El resto vacío. |
