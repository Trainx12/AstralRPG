# AstralBazar 1.2.0 — flujo tipo Hypixel (privado)

Entrega local. No se desplegó en Empower ni Aternos. No cambia el resource pack.

## Archivos y destinos

| Local | Destino | SHA-256 |
|---|---|---|
| `build/bazar/AstralBazar.jar` | `plugins/AstralBazar.jar` | `c214b872e0b8d8cdb88222422d7b4ebf1355935261a331ba768cd65927d53b63` |
| `build/bazar/config.yml` | `plugins/AstralBazar/config.yml` | `4c2a9ddb6d4f5723a140a1804b3382d5f583cd66a6aa327a60f8ab091346a656` |
| `build/bazar/productos.yml` | `plugins/AstralBazar/productos.yml` | `f2d08e4806bd22aca15ddbd17f55051c986990fe81d6d9f41d732e0232d3388d` |

`ventanas.yml` va embebido en el JAR; no subir al pack ni reemplazar el existente.

1. `/bazar admin pausar`. Respaldar juntos SQLite/WAL/SHM, carpeta AstralBazar, Essentials y jugadores.
2. Subir el JAR a `plugins/update/AstralBazar.jar` (si el panel admite update), y productos.yml a su destino. Conservar la config operativa actual: `publico: false`; el config.yml generado es plantilla privada, no sobreescribir permisos/pausa del servidor.
3. Requiere un reinicio completo; no PlugMan ni reload de JAR. En Empower, cuando todo esté subido: `reiniciopendiente Bazar 1.2.0`. Alternativa: apagar, reemplazar `plugins/AstralBazar.jar` y arrancar con Java 25.
4. Consola: `Bazar privado listo: 88 productos. publico=false`, versión 1.2.0 sin errores. `/bazar admin reanudar`; probar con ByTrainx en `/modo admin` y `/sala`. Otro jugador sin permiso debe ver Próximamente.
5. Config operativa: `/bazar admin recargar`. Catálogo/JAR requieren reinicio. No borrar IDs existentes ni reemplazar bazar.sqlite; la migración agrega `claims.order_id` y `order_credit` sin eliminar tablas/órdenes.
Aternos puede impedir instalar JAR propios: no eludir restricciones ni usar APIs privadas. No subir mundos ni usar Worlds > Upload en world.

## Verificación

Paper 26.1.2 / Java 25 / Vault / Essentials: 634 comprobaciones, 0 fallos, dos bots, caída/reapertura real de JVM. Incluye chat capturado, vencimiento real de 30 s, las 8 combinaciones compra/venta de precios, cobro/cancelación y migración 1.1.0 con custodia/saldo/oferta fuera del mínimo nuevo. Economía: 17 tests OK. py_compile y git diff --check OK.

Publicación bloqueada: el JAR probado incorpora trabajo previo 1.1.0 sin commit. No se creó commit ni se hizo push. Integrar/publicar esa base por separado antes de publicar 1.2.0; no incluirla sin autorización.

SQLite/Vault/inventarios conservan el journal y los recibos durables. Los nuevos cobros tienen relación con su orden. Los cobros 1.1.0 no tienen esa relación: se recuperan con Cobrar todo (también devuelve equipo antiguo). Nunca al piso.

## Referencias de precio

No son cotizaciones del mercado: son referencias de reposición para límites. Mínimo=max(ref/10, piso NPC, $0,01); máximo=ref×20. Recetas se calculan recursivamente y se dividen por la cantidad producida. Ingredientes vanilla sin precio=0.
El survival adapta su tier al jugador: se asume T5 para Nether/End y T3 para vindicator. Para bloques/cofres sin pago se usa una unidad de esfuerzo explícita, no una medición de tiempo real. Las seis referencias sin fuente monetizable quedan marcadas PENDIENTE; requieren revisión del dueño.

| ID | Nombre | Cálculo | Referencia | Mínimo | Máximo |
|---|---|---|---:|---:|---:|
| `netherita_fundida` | Netherita Fundida | Horno: 1 lingote netherita; precio venta NPC/Tienda (combustible sin precio = 0) | 1.666,67 | 166,67 | 33.333,40 |
| `netherita_reforzada` | Netherita Reforzada | Receta: (1 × netherita_fundida + 4 × minecraft:blaze_powder ($66 NPC/Tienda)) / 1; vanilla sin precio = 0 | 1.930,67 | 193,07 | 38.613,40 |
| `shadowsteel` | Acero Sombrio | Receta: (1 × minecraft:iron_ingot ($138 NPC/Tienda) + 1 × esencia_nether) / 1; vanilla sin precio = 0 | 100.138,00 | 10.013,80 | 2.002.760,00 |
| `esencia_nether` | Esencia del Nether | items.MOB_DROPS/wither_skeleton: PLATA_MOB_TIER[5] / 0.25; tier supuesto (survival adaptable) | 100.000,00 | 10.000,00 | 2.000.000,00 |
| `madera_estelar` | Madera Estelar | build.py chorus End, probabilidad 0.35; supuesto unidad de esfuerzo T5 por bloque/cofre | 71.428,57 | 7.142,86 | 1.428.571,40 |
| `palo_reforzado` | Palo Reforzado | Receta: (2 × shadowsteel + 1 × minecraft:stick ($15 NPC/Tienda)) / 1; vanilla sin precio = 0 | 200.291,00 | 20.029,10 | 4.005.820,00 |
| `cuero_tratado` | Cuero Tratado | Receta: (8 × minecraft:leather ($840 NPC/Tienda) + 1 × water_bottle ($0 NPC/Tienda)) / 2; vanilla sin precio = 0 | 3.360,00 | 336,00 | 67.200,00 |
| `cristal_arcano` | Cristal Arcano | Receta: (2 × fragmento_cristal) / 1; vanilla sin precio = 0 | 1.250.000,00 | 125.000,00 | 25.000.000,00 |
| `fragmento_cristal` | Fragmento de Cristal Arcano | build.py end stone, probabilidad 0.04; supuesto unidad de esfuerzo T5 por bloque/cofre | 625.000,00 | 62.500,00 | 12.500.000,00 |
| `cristal_refinado` | Cristal Arcano Refinado | Receta: (4 × cristal_arcano) / 1; vanilla sin precio = 0 | 5.000.000,00 | 500.000,00 | 100.000.000,00 |
| `fragmento_umbrio` | Fragmento Umbrio | items.MOB_DROPS/piglin_brute: PLATA_MOB_TIER[5] / 0.15; tier supuesto (survival adaptable) | 166.666,67 | 16.666,67 | 3.333.333,40 |
| `gema_umbria_fragmentada` | Gema Umbria Fragmentada | Receta: (8 × fragmento_umbrio + 1 × minecraft:coal ($132 NPC/Tienda)) / 1; vanilla sin precio = 0 | 1.333.465,36 | 133.346,54 | 26.669.307,20 |
| `gema_umbria` | Gema Umbria | Receta: (8 × fragmento_umbrio + 1 × gema_umbria_fragmentada) / 1; vanilla sin precio = 0 | 2.666.798,72 | 266.679,87 | 53.335.974,40 |
| `gema_umbria_perfecta` | Gema Umbria Perfecta | Receta: (8 × gema_umbria + 1 × nucleo_furia_pura) / 1; vanilla sin precio = 0 | 23.001.780,44 | 2.300.178,04 | 460.035.608,80 |
| `gema_luminica` | Gema Luminica | build.py cofre Overworld, probabilidad 0.25; supuesto unidad de esfuerzo T5 por bloque/cofre | 100.000,00 | 10.000,00 | 2.000.000,00 |
| `gema_luminica_perfecta` | Gema Luminica Perfecta | Receta: (8 × gema_luminica + 1 × nucleo_astral) / 1; vanilla sin precio = 0 | 23.050.000,00 | 2.305.000,00 | 461.000.000,00 |
| `fragmento_astral` | Fragmento Astral | items.MOB_DROPS/enderman: PLATA_MOB_TIER[5] / 0.2; tier supuesto (survival adaptable) | 125.000,00 | 12.500,00 | 2.500.000,00 |
| `polvo_astral` | Polvo Astral | Receta: (8 × fragmento_astral) / 2; vanilla sin precio = 0 | 500.000,00 | 50.000,00 | 10.000.000,00 |
| `nucleo_astral` | Nucleo Astral | Receta: (4 × polvo_astral + 4 × cristal_refinado + 1 × corazon_shulker) / 1; vanilla sin precio = 0 | 22.250.000,00 | 2.225.000,00 | 445.000.000,00 |
| `nucleo_furia` | Nucleo de Furia | items.MOB_DROPS/piglin_brute: PLATA_MOB_TIER[5] / 0.06; tier supuesto (survival adaptable) | 416.666,67 | 41.666,67 | 8.333.333,40 |
| `nucleo_furia_pura` | Nucleo de Furia Pura | Receta: (4 × nucleo_furia + 4 × minecraft:blaze_powder ($66 NPC/Tienda) + 1 × minecraft:lava_bucket ($460 NPC/Tienda)) / 1; vanilla sin precio = 0 | 1.667.390,68 | 166.739,07 | 33.347.813,60 |
| `corazon_shulker` | Corazon de Shulker | items.MOB_DROPS/shulker: PLATA_MOB_TIER[5] / 0.1; tier supuesto (survival adaptable) | 250.000,00 | 25.000,00 | 5.000.000,00 |
| `nucleo_eolico` | Nucleo Eolico | Receta: (4 × minecraft:feather ($150 NPC/Tienda) + 4 × madera_estelar + 1 × gema_luminica) / 1; vanilla sin precio = 0 | 386.314,28 | 38.631,43 | 7.726.285,60 |
| `esencia_elite` | Esencia de Elite | items.ELITE_DROPS T1: PLATA_MOB_TIER / (0.5 × 1) | 3.000,00 | 300,00 | 60.000,00 |
| `alma_corrupta` | Alma Corrupta | items.ELITE_DROPS T3: PLATA_MOB_TIER / (0.35 × 1) | 17.142,86 | 1.714,29 | 342.857,20 |
| `chispa_astral` | Chispa Astral | items.ELITE_DROPS T5: PLATA_MOB_TIER / (0.6 × 1) | 41.666,67 | 4.166,67 | 833.333,40 |
| `fragmento_ocaso` | Fragmento de Ocaso | items_t6_10: T6 / probabilidad común 0.012 | 4.166.666,67 | 416.666,67 | 83.333.333,40 |
| `esquirla_eclipse` | Esquirla de Eclipse | items_t6_10: T7 / probabilidad común 0.012 | 8.333.333,33 | 833.333,33 | 166.666.666,60 |
| `nucleo_supernova` | Nucleo de Supernova | items_t6_10: T8 / probabilidad común 0.012 | 16.666.666,67 | 1.666.666,67 | 333.333.333,40 |
| `esencia_vacio` | Esencia del Vacio | items_t6_10: T9 / probabilidad común 0.012 | 33.333.333,33 | 3.333.333,33 | 666.666.666,60 |
| `corazon_fin` | Corazon del Fin | items_t6_10: T10 / probabilidad común 0.012 | 66.666.666,67 | 6.666.666,67 | 1.333.333.333,40 |
| `manzana_t2` | Manzana Mineral | manzanas.PROB común: T2 / 0.03 | 100.000,00 | 10.000,00 | 2.000.000,00 |
| `manzana_t3` | Manzana Ancestral | manzanas.PROB común: T3 / 0.03 | 200.000,00 | 20.000,00 | 4.000.000,00 |
| `manzana_t4` | Manzana Glacial | manzanas.PROB común: T4 / 0.03 | 400.000,00 | 40.000,00 | 8.000.000,00 |
| `manzana_t5` | Manzana Ignea | manzanas.PROB común: T5 / 0.03 | 833.333,33 | 83.333,33 | 16.666.666,60 |
| `manzana_t6` | Manzana del Ocaso | manzanas.PROB común: T6 / 0.03 | 1.666.666,67 | 166.666,67 | 33.333.333,40 |
| `manzana_t7` | Manzana del Eclipse | manzanas.PROB común: T7 / 0.03 | 3.333.333,33 | 333.333,33 | 66.666.666,60 |
| `manzana_t8` | Manzana Supernova | manzanas.PROB común: T8 / 0.03 | 6.666.666,67 | 666.666,67 | 133.333.333,40 |
| `manzana_t9` | Manzana del Vacio | manzanas.PROB común: T9 / 0.03 | 13.333.333,33 | 1.333.333,33 | 266.666.666,60 |
| `manzana_t10` | Manzana del Fin | manzanas.PROB común: T10 / 0.03 | 26.666.666,67 | 2.666.666,67 | 533.333.333,40 |
| `gema_rubi_1` | Rubí Crudo | Veta honda de rubi: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_rubi_2` | Rubí Pulido | Veta honda de rubi: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_rubi_3` | Rubí Impecable | Veta honda de rubi: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_rubi_4` | Rubí Perfecto | Veta honda de rubi: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_rubi_5` | Rubí Estelar | Veta honda de rubi: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_zafiro_1` | Zafiro Crudo | Veta honda de zafiro: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_zafiro_2` | Zafiro Pulido | Veta honda de zafiro: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_zafiro_3` | Zafiro Impecable | Veta honda de zafiro: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_zafiro_4` | Zafiro Perfecto | Veta honda de zafiro: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_zafiro_5` | Zafiro Estelar | Veta honda de zafiro: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_jade_1` | Jade Crudo | Veta honda de jade: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_jade_2` | Jade Pulido | Veta honda de jade: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_jade_3` | Jade Impecable | Veta honda de jade: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_jade_4` | Jade Perfecto | Veta honda de jade: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_jade_5` | Jade Estelar | Veta honda de jade: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_topacio_1` | Topacio Crudo | Veta honda de topacio: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_topacio_2` | Topacio Pulido | Veta honda de topacio: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_topacio_3` | Topacio Impecable | Veta honda de topacio: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_topacio_4` | Topacio Perfecto | Veta honda de topacio: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_topacio_5` | Topacio Estelar | Veta honda de topacio: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_amatista_1` | Amatista Cruda | Veta honda de amatista: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_amatista_2` | Amatista Pulida | Veta honda de amatista: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_amatista_3` | Amatista Impecable | Veta honda de amatista: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_amatista_4` | Amatista Perfecta | Veta honda de amatista: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_amatista_5` | Amatista Estelar | Veta honda de amatista: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_opalo_1` | Ópalo Crudo | Veta honda de opalo: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_opalo_2` | Ópalo Pulido | Veta honda de opalo: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_opalo_3` | Ópalo Impecable | Veta honda de opalo: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_opalo_4` | Ópalo Perfecto | Veta honda de opalo: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_opalo_5` | Ópalo Estelar | Veta honda de opalo: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
| `gema_onix_1` | Ónix Crudo | Veta honda de onix: CALIDAD 719/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 16.689,85 | 1.668,98 | 333.797,00 |
| `gema_onix_2` | Ónix Pulido | Veta honda de onix: CALIDAD 220/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 54.545,45 | 5.454,55 | 1.090.909,00 |
| `gema_onix_3` | Ónix Impecable | Veta honda de onix: CALIDAD 55/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 218.181,82 | 21.818,18 | 4.363.636,40 |
| `gema_onix_4` | Ónix Perfecto | Veta honda de onix: CALIDAD 5/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 2.400.000,00 | 240.000,00 | 48.000.000,00 |
| `gema_onix_5` | Ónix Estelar | Veta honda de onix: CALIDAD 1/1000; supuesto esfuerzo de un mob T4 por veta, sin polvo | 12.000.000,00 | 1.200.000,00 | 240.000.000,00 |
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

Casilleros desde 0, izquierda a derecha. No dibujar nombres/precios/cantidades variables; van en el tooltip. Los espacios no listados quedan libres. Inicio, Producto, Cantidad, Precio, Mis órdenes y Vender inventario usan título simple hasta aprobar arte nuevo.

| Ventana | Filas | Casilleros / texto |
|---|---:|---|
| Inicio | 6 | Columna categorías 0 Minería, 9 Combate, 18 Bosque y pesca, 27 Consumibles, 36 Especiales. Productos: columnas 2–8 de filas 0–4 (35 por página). 45 Buscar, 46 Mis órdenes, 47 Vender inventario, 48 Vender equipo al server, 49 Anterior, 50 Siguiente, 51 Página, 53 Cerrar. |
| Producto | 6 | Comprar al instante 10/11/19/20; Vender al instante 14/15/23/24; Crear orden de compra 28/29/37/38; Crear oferta de venta 32/33/41/42; 45 Volver; 49 Mis órdenes. Lore: mejor precio, hasta siete puntas, inventario y clic. |
| Cantidad | 5 | Instantánea: 10 Una unidad, 12 Un stack, 15 Llenar inventario. Órdenes: 10 64, 12 160, 14 1024; venta: 15 Todo lo que tengo. Siempre: 16 A mano, 36 Volver, 44 Cerrar. |
| Precio | 5 | 10 Igual a la mejor, 12 Mejor +/-$0,10, 14 5% del margen, 16 A mano. 36 Volver, 44 Cerrar. Sin margen positivo el botón 14 queda deshabilitado y lo explica. |
| Mis órdenes | 6 | 0–44 órdenes; clic cobra, derecho cancela/devuelve. 45 Cobrar todo, 48 Anterior, 49 Página, 50 Siguiente, 51 Volver, 53 Cerrar. No Retiros ni Retirar plata. |
| Vender inventario | 6 | 0–44 productos/cantidad/estimado neto; 45 Volver, 49 Confirmar con total neto, 53 Cerrar. Lo que exceda las 45 tarjetas sigue incluido en el total. No equipo. |

Confirmar orden y las dos ventanas de equipo mantienen sus botones del diseño 1.1.0. Orden/Retiros ya no se abren. Si `diseno: false`, todas son simples.

El tooltip oculta atributos/encantamientos en las copias de UI, sin modificar los ítems comerciables. Las líneas avanzadas del cliente (`minecraft:paper`, número de componentes, F3+H) no pueden ocultarse selectivamente desde Paper sin esconder también nombre/lore; desactivar F3+H en el cliente.

El catálogo depende de generadores locales previos no publicados (economía, Clases, Vacío, historia, manzanas); la tarea no autoriza publicar esas fuentes. Recompilar el catálogo versionado con `--solo-compilar` evita ejecutarlas. Arte previo del Bazar también existe sin publicar y debe separarse antes de publicar esta tarea.
