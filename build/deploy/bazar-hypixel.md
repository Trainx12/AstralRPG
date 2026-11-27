# AstralBazar 1.3.1 — flujo tipo Hypixel (privado)

Entrega local. No se desplegó en Empower ni Aternos. Pack y categorías: ver bazar-categorias-27-11.md.

## Archivos y destinos

| Local | Destino | SHA-256 |
|---|---|---|
| `build/bazar/AstralBazar.jar` | `plugins/AstralBazar.jar` | `e885c627d0780a3c15db8a7ede43ac751afb7313e150dd26609f12532dbe85dc` |
| `build/bazar/config.yml` | `plugins/AstralBazar/config.yml` | `4c2a9ddb6d4f5723a140a1804b3382d5f583cd66a6aa327a60f8ab091346a656` |
| `build/bazar/productos.yml` | `plugins/AstralBazar/productos.yml` | `077451559f4a15557fa3fa13e0fdcca9e3812e036a89242cd5e47cbaef004187` |

`ventanas.yml` va embebido en el JAR; no subir al pack ni reemplazar el existente.

1. `/bazar admin pausar`. Respaldar juntos SQLite/WAL/SHM, carpeta AstralBazar, Essentials y jugadores.
2. Subir el JAR a `plugins/update/AstralBazar.jar` (si el panel admite update), y productos.yml a su destino. Conservar la config operativa actual: `publico: false`; el config.yml generado es plantilla privada, no sobreescribir permisos/pausa del servidor.
3. Requiere un reinicio completo; no PlugMan ni reload de JAR. Esperar el reinicio diario; no activar reiniciopendiente ni reiniciar por cuenta propia. Alternativa: apagar, reemplazar `plugins/AstralBazar.jar` y arrancar con Java 25.
4. Consola: `Bazar privado listo: 88 productos. publico=false`, versión 1.3.1 sin errores. `/bazar admin reanudar`; probar con ByTrainx en `/modo admin` y `/sala`. Otro jugador sin permiso debe ver Próximamente.
5. Config operativa: `/bazar admin recargar`. Catálogo/JAR requieren reinicio. No borrar IDs existentes ni reemplazar bazar.sqlite; la migración agrega `claims.order_id` y `order_credit` sin eliminar tablas/órdenes.
Aternos puede impedir instalar JAR propios: no eludir restricciones ni usar APIs privadas. No subir mundos ni usar Worlds > Upload en world.

## Verificación

Paper final: 653 comprobaciones, 0 fallos, dos bots, reapertura real JVM; categorias antiguas y desconocidas, saldos y ordenes conservados. Auditoria de terceros aprobada.

SQLite/Vault/inventarios conservan el journal y los recibos durables. Los nuevos cobros tienen relación con su orden. Los cobros 1.1.0 no tienen esa relación: se recuperan con Cobrar todo (también devuelve equipo antiguo). Nunca al piso.

## Referencias de precio

No son cotizaciones del mercado: son referencias de reposición para límites. Mínimo=max(ref/10, piso NPC, $0,01); máximo=ref×20. Recetas se calculan recursivamente y se dividen por la cantidad producida. Ingredientes vanilla sin precio=0.
El survival adapta su tier al jugador: se asume T5 para Nether/End y T3 para vindicator. Para bloques/cofres sin pago se usa una unidad de esfuerzo explícita, no una medición de tiempo real. Las seis referencias sin fuente monetizable quedan marcadas PENDIENTE; requieren revisión del dueño.

| ID | Nombre | Cálculo | Referencia | Mínimo | Máximo |
|---|---|---|---:|---:|---:|
| `netherita_fundida` | Netherita Fundida | Horno: 1 lingote netherita; precio venta NPC/Tienda (combustible sin precio = 0) | 1.666,67 | 166,67 | 33.333,40 |
| `netherita_reforzada` | Netherita Reforzada | Receta: (1 × netherita_fundida + 4 × minecraft:blaze_powder ($66 NPC/Tienda)) / 1; vanilla sin precio = 0 | 1.930,67 | 193,07 | 38.613,40 |
| `shadowsteel` | Acero Sombrio | Receta: (1 × minecraft:iron_ingot ($138 NPC/Tienda) + 1 × esencia_nether) / 1; vanilla sin precio = 0 | 11.204,67 | 1.120,47 | 224.093,40 |
| `esencia_nether` | Esencia del Nether | items.MOB_DROPS/wither_skeleton: kill vanilla T5 $8,300 / 3 drops / 0.25 | 11.066,67 | 1.106,67 | 221.333,40 |
| `madera_estelar` | Madera Estelar | build.py chorus End, probabilidad 0.35; $830 por bloque/cofre | 2.371,43 | 237,14 | 47.428,60 |
| `palo_reforzado` | Palo Reforzado | Receta: (2 × shadowsteel + 1 × minecraft:stick ($15 NPC/Tienda)) / 1; vanilla sin precio = 0 | 22.424,34 | 2.242,43 | 448.486,80 |
| `cuero_tratado` | Cuero Tratado | Receta: (8 × minecraft:leather ($840 NPC/Tienda) + 1 × water_bottle ($0 NPC/Tienda)) / 2; vanilla sin precio = 0 | 3.360,00 | 336,00 | 67.200,00 |
| `cristal_arcano` | Cristal Arcano | Receta: (2 × fragmento_cristal) / 1; vanilla sin precio = 0 | 41.500,00 | 4.150,00 | 830.000,00 |
| `fragmento_cristal` | Fragmento de Cristal Arcano | build.py end stone, probabilidad 0.04; $830 por bloque/cofre | 20.750,00 | 2.075,00 | 415.000,00 |
| `cristal_refinado` | Cristal Arcano Refinado | Receta: (4 × cristal_arcano) / 1; vanilla sin precio = 0 | 166.000,00 | 16.600,00 | 3.320.000,00 |
| `fragmento_umbrio` | Fragmento Umbrio | items.MOB_DROPS/wither_skeleton: kill vanilla T5 $8,300 / 3 drops / 0.15 | 18.444,44 | 1.844,44 | 368.888,80 |
| `gema_umbria_fragmentada` | Gema Umbria Fragmentada | Receta: (8 × fragmento_umbrio + 1 × minecraft:coal ($132 NPC/Tienda)) / 1; vanilla sin precio = 0 | 147.687,52 | 14.768,75 | 2.953.750,40 |
| `gema_umbria` | Gema Umbria | Receta: (8 × fragmento_umbrio + 1 × gema_umbria_fragmentada) / 1; vanilla sin precio = 0 | 295.243,04 | 29.524,30 | 5.904.860,80 |
| `gema_umbria_perfecta` | Gema Umbria Perfecta | Receta: (8 × gema_umbria + 1 × nucleo_furia_pura) / 1; vanilla sin precio = 0 | 2.547.112,76 | 254.711,28 | 50.942.255,20 |
| `gema_luminica` | Gema Luminica | build.py cofre Overworld, probabilidad 0.25; $16,600 por bloque/cofre | 66.400,00 | 6.640,00 | 1.328.000,00 |
| `gema_luminica_perfecta` | Gema Luminica Perfecta | Receta: (8 × gema_luminica + 1 × nucleo_astral) / 1; vanilla sin precio = 0 | 1.983.700,00 | 198.370,00 | 39.674.000,00 |
| `fragmento_astral` | Fragmento Astral | items.MOB_DROPS/enderman: kill vanilla T5 $16,600 / 2 drops / 0.2 | 41.500,00 | 4.150,00 | 830.000,00 |
| `polvo_astral` | Polvo Astral | Receta: (8 × fragmento_astral) / 2; vanilla sin precio = 0 | 166.000,00 | 16.600,00 | 3.320.000,00 |
| `nucleo_astral` | Nucleo Astral | Receta: (4 × polvo_astral + 4 × cristal_refinado + 1 × corazon_shulker) / 1; vanilla sin precio = 0 | 1.452.500,00 | 145.250,00 | 29.050.000,00 |
| `nucleo_furia` | Nucleo de Furia | items.MOB_DROPS/wither_skeleton: kill vanilla T5 $8,300 / 3 drops / 0.06 | 46.111,11 | 4.611,11 | 922.222,20 |
| `nucleo_furia_pura` | Nucleo de Furia Pura | Receta: (4 × nucleo_furia + 4 × minecraft:blaze_powder ($66 NPC/Tienda) + 1 × minecraft:lava_bucket ($460 NPC/Tienda)) / 1; vanilla sin precio = 0 | 185.168,44 | 18.516,84 | 3.703.368,80 |
| `corazon_shulker` | Corazon de Shulker | items.MOB_DROPS/shulker: kill vanilla T5 $12,450 / 1 drops / 0.1 | 124.500,00 | 12.450,00 | 2.490.000,00 |
| `nucleo_eolico` | Nucleo Eolico | items.MOB_DROPS/vindicator: kill vanilla T3 $2,400 / 1 drops / 0.1 | 24.000,00 | 2.400,00 | 480.000,00 |
| `esencia_elite` | Esencia de Elite | Elites: amenaza 4, mob T1 $1,500 / 0.2912 por kill | 5.151,10 | 515,11 | 103.022,00 |
| `alma_corrupta` | Alma Corrupta | Elites: amenaza 6, mob T3 $6,000 / 0.1080 por kill | 55.555,56 | 5.555,56 | 1.111.111,20 |
| `chispa_astral` | Chispa Astral | Elites: amenaza 8, mob T5 $25,000 / 0.0307 por kill | 815.217,39 | 81.521,74 | 16.304.347,80 |
| `fragmento_ocaso` | Fragmento de Ocaso | items_t6_10: T6 / (0.012 comun + 46% elites x 0.12) | 810.635,54 | 81.063,55 | 16.212.710,80 |
| `esquirla_eclipse` | Esquirla de Eclipse | items_t6_10: T7 / (0.012 comun + 46% elites x 0.12) | 1.621.271,08 | 162.127,11 | 32.425.421,60 |
| `nucleo_supernova` | Nucleo de Supernova | items_t6_10: T8 / (0.012 comun + 46% elites x 0.12) | 3.242.542,15 | 324.254,21 | 64.850.843,00 |
| `esencia_vacio` | Esencia del Vacio | items_t6_10: T9 / (0.012 comun + 46% elites x 0.12) | 6.485.084,31 | 648.508,43 | 129.701.686,20 |
| `corazon_fin` | Corazon del Fin | items_t6_10: T10 / (0.012 comun + 46% elites x 0.12) | 12.970.168,61 | 1.297.016,86 | 259.403.372,20 |
| `manzana_t2` | Manzana Mineral | manzanas.PROB común: T2 / 0.03 | 100.000,00 | 10.000,00 | 2.000.000,00 |
| `manzana_t3` | Manzana Ancestral | manzanas.PROB común: T3 / 0.03 | 200.000,00 | 20.000,00 | 4.000.000,00 |
| `manzana_t4` | Manzana Glacial | manzanas.PROB común: T4 / 0.03 | 400.000,00 | 40.000,00 | 8.000.000,00 |
| `manzana_t5` | Manzana Ignea | manzanas.PROB común: T5 / 0.03 | 833.333,33 | 83.333,33 | 16.666.666,60 |
| `manzana_t6` | Manzana del Ocaso | manzanas.PROB común: T6 / 0.03 | 1.666.666,67 | 166.666,67 | 33.333.333,40 |
| `manzana_t7` | Manzana del Eclipse | manzanas.PROB común: T7 / 0.03 | 3.333.333,33 | 333.333,33 | 66.666.666,60 |
| `manzana_t8` | Manzana Supernova | manzanas.PROB común: T8 / 0.03 | 6.666.666,67 | 666.666,67 | 133.333.333,40 |
| `manzana_t9` | Manzana del Vacio | manzanas.PROB común: T9 / 0.03 | 13.333.333,33 | 1.333.333,33 | 266.666.666,60 |
| `manzana_t10` | Manzana del Fin | manzanas.PROB común: T10 / 0.03 | 26.666.666,67 | 2.666.666,67 | 533.333.333,40 |
| `gema_rubi_1` | Rubí Crudo | Veta honda de rubi: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_rubi_2` | Rubí Pulido | Veta honda de rubi: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_rubi_3` | Rubí Impecable | Veta honda de rubi: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_rubi_4` | Rubí Perfecto | Veta honda de rubi: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_rubi_5` | Rubí Estelar | Veta honda de rubi: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_zafiro_1` | Zafiro Crudo | Veta honda de zafiro: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_zafiro_2` | Zafiro Pulido | Veta honda de zafiro: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_zafiro_3` | Zafiro Impecable | Veta honda de zafiro: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_zafiro_4` | Zafiro Perfecto | Veta honda de zafiro: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_zafiro_5` | Zafiro Estelar | Veta honda de zafiro: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_jade_1` | Jade Crudo | Veta honda de jade: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_jade_2` | Jade Pulido | Veta honda de jade: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_jade_3` | Jade Impecable | Veta honda de jade: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_jade_4` | Jade Perfecto | Veta honda de jade: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_jade_5` | Jade Estelar | Veta honda de jade: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_topacio_1` | Topacio Crudo | Veta honda de topacio: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_topacio_2` | Topacio Pulido | Veta honda de topacio: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_topacio_3` | Topacio Impecable | Veta honda de topacio: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_topacio_4` | Topacio Perfecto | Veta honda de topacio: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_topacio_5` | Topacio Estelar | Veta honda de topacio: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_amatista_1` | Amatista Cruda | Veta honda de amatista: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_amatista_2` | Amatista Pulida | Veta honda de amatista: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_amatista_3` | Amatista Impecable | Veta honda de amatista: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_amatista_4` | Amatista Perfecta | Veta honda de amatista: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_amatista_5` | Amatista Estelar | Veta honda de amatista: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_opalo_1` | Ópalo Crudo | Veta honda de opalo: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_opalo_2` | Ópalo Pulido | Veta honda de opalo: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_opalo_3` | Ópalo Impecable | Veta honda de opalo: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_opalo_4` | Ópalo Perfecto | Veta honda de opalo: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_opalo_5` | Ópalo Estelar | Veta honda de opalo: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `gema_onix_1` | Ónix Crudo | Veta honda de onix: CALIDAD 719/1000; una veta = un Cristal ($8,500), sin polvo | 11.821,97 | 1.182,20 | 236.439,40 |
| `gema_onix_2` | Ónix Pulido | Veta honda de onix: CALIDAD 220/1000; una veta = un Cristal ($8,500), sin polvo | 38.636,36 | 3.863,64 | 772.727,20 |
| `gema_onix_3` | Ónix Impecable | Veta honda de onix: CALIDAD 55/1000; una veta = un Cristal ($8,500), sin polvo | 154.545,45 | 15.454,55 | 3.090.909,00 |
| `gema_onix_4` | Ónix Perfecto | Veta honda de onix: CALIDAD 5/1000; una veta = un Cristal ($8,500), sin polvo | 1.700.000,00 | 170.000,00 | 34.000.000,00 |
| `gema_onix_5` | Ónix Estelar | Veta honda de onix: CALIDAD 1/1000; una veta = un Cristal ($8,500), sin polvo | 8.500.000,00 | 850.000,00 | 170.000.000,00 |
| `cristal_caverna` | Cristal Astral en bruto | Precio de venta NPC en economia.CAVERNAS_PRECIO/VACIO_PRECIO (piso y referencia) | 8.500,00 | 8.500,00 | 170.000,00 |
| `geoda_estelar` | Geoda Estelar | Precio de venta NPC en economia.CAVERNAS_PRECIO/VACIO_PRECIO (piso y referencia) | 76.000,00 | 76.000,00 | 1.520.000,00 |
| `polvo_cristal` | Polvo de Cristal | cavernas.py mob exterior T4 / drop 0.02 | 600.000,00 | 60.000,00 | 12.000.000,00 |
| `fragmento_estelar` | Fragmento Estelar | Precio de venta NPC en economia.CAVERNAS_PRECIO/VACIO_PRECIO (piso y referencia) | 18.000,00 | 18.000,00 | 360.000,00 |
| `nucleo_meteorito` | Nucleo de Meteorito | Precio de venta NPC en economia.CAVERNAS_PRECIO/VACIO_PRECIO (piso y referencia) | 500.000,00 | 500.000,00 | 10.000.000,00 |
| `colmillo_carnivoro` | Colmillo Carnivoro | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `asura_moneda_emerald` | Moneda Asura Esmeralda | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `asura_moneda_card` | Moneda Asura Carta | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `asura_moneda_circle` | Moneda Asura Circulo | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `asura_moneda_square` | Moneda Asura Cuadrado | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `asura_moneda_triangle` | Moneda Asura Triangulo | PENDIENTE: referencia previa conservada; sin drop/receta monetizable en generadores | 30.000,00 | 3.000,00 | 600.000,00 |
| `perla_abisal` | Perla Abisal | Veta Océano (escala.TIER_FIJO=2), 1 unidad; supuesto esfuerzo de un mob T2 por veta | 3.000,00 | 300,00 | 60.000,00 |
| `coral_astral` | Coral Astral | Veta Océano (escala.TIER_FIJO=2), 1 unidad; supuesto esfuerzo de un mob T2 por veta | 3.000,00 | 300,00 | 60.000,00 |

## Fichas para Gemini

Casilleros desde 0, izquierda a derecha. No dibujar nombres/precios/cantidades variables; van en el tooltip. Los espacios no listados quedan libres. Arte y casilleros vigentes del diseño Gemini 1.3.0: ver bazar-ventanas-26-11.md; esta tabla conserva la referencia del modo simple.

| Ventana | Filas | Casilleros / texto |
|---|---:|---|
| Inicio | 6 | Columna categorías 0 Combate, 9 Bosque, 18 Océano, 27 Consumibles, 36 Especiales. Productos: columnas 2–8 de filas 0–4 (35 por página). 45 Buscar, 46 Mis órdenes, 47 Vender inventario, 48 Vender equipo al server, 49 Anterior, 50 Página, 51 Siguiente, 53 Cerrar. |
| Producto | 6 | Comprar al instante 10/11/19/20; Vender al instante 14/15/23/24; Crear orden de compra 28/29/37/38; Crear oferta de venta 32/33/41/42; 45 Volver; 49 Mis órdenes. Lore: mejor precio, hasta siete puntas, inventario y clic. |
| Cantidad | 5 | Instantánea: 10 Una unidad, 12 Un stack, 15 Llenar inventario. Órdenes: 10 64, 12 160, 14 1024; venta: 15 Todo lo que tengo. Siempre: 16 A mano, 36 Volver, 44 Cerrar. |
| Precio | 5 | 10 Igual a la mejor, 12 Mejor +/-$0,10, 14 5% del margen, 16 A mano. 36 Volver, 44 Cerrar. Sin margen positivo el botón 14 queda deshabilitado y lo explica. |
| Mis órdenes | 6 | 0–44 órdenes; clic cobra, derecho cancela/devuelve. 45 Cobrar todo, 48 Anterior, 49 Página, 50 Siguiente, 51 Volver, 53 Cerrar. No Retiros ni Retirar plata. |
| Vender inventario | 6 | 0–44 productos/cantidad/estimado neto; 45 Volver, 49 Confirmar con total neto, 53 Cerrar. Lo que exceda las 45 tarjetas sigue incluido en el total. No equipo. |

Confirmar orden y las dos ventanas de equipo mantienen sus botones del diseño 1.1.0. Orden/Retiros ya no se abren. Si `diseno: false`, todas son simples.

El tooltip oculta atributos/encantamientos en las copias de UI, sin modificar los ítems comerciables. Las líneas avanzadas del cliente (`minecraft:paper`, número de componentes, F3+H) no pueden ocultarse selectivamente desde Paper sin esconder también nombre/lore; desactivar F3+H en el cliente.

El catálogo depende de generadores locales previos no publicados (economía, Clases, Vacío, historia, manzanas); la tarea no autoriza publicar esas fuentes. Recompilar el catálogo versionado con `--solo-compilar` evita ejecutarlas. La base del Bazar 1.3.0 se incluye por autorización expresa en la tarea de categorías 1.3.1.
