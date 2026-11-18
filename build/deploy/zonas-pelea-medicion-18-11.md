# Medicion de cercos (18/11/2026)

Lectura local; sin cambios en mapas. Rectangulos en coordenadas de caras de bloque.
Deteccion: columnas de >=4 barreras, busqueda ±100 XZ / -15..+70 Y; interior cerrado con centro y llegada.
Techos y cercos incompletos no definen zonas. Envolvente del interior si ocupacion >=80%.
Copias _2.._6 usan las mismas medidas; verificar igualdad con copia real antes de ejecutar comandos.

| Mundo base | Sala | X | Z | Origen | Radio 3D hasta esquina (+70 Y) |
|---|---|---|---|---|---|
| bosque | Claro de las raices | 1411..1495 | 1512..1603 | cerco | 108 |
| bosque | Altar del Chaman | 1543..1649 | 1356..1425 | cerco | 103 |
| mina | Campamento Minero | -5.5..26.5 | -140.5..-108.5 | sin barreras (radio anterior) | 74 |
| mina | Lago Subterraneo | -2.5..41.5 | -180.5..-136.5 | sin barreras (radio anterior) | 77 |
| mina | Tuneles de Soporte | 27.5..59.5 | -217.5..-185.5 | sin barreras (radio anterior) | 74 |
| mina | Salon del Guardian | 1.5..71.5 | -283.5..-213.5 | sin barreras (radio anterior) | 86 |
| tumba | Patio de los olvidados | -176.5..-120.5 | -126.5..-70.5 | sin barreras (radio anterior) | 81 |
| tumba | Pasaje de los sellos | -211.5..-139.5 | 167.5..239.5 | sin barreras (radio anterior) | 87 |
| tumba | Trono del Rey de Arena | -55.432..56.568 | -55.488..56.512 | sin barreras (radio anterior) | 106 |
| cumbre_hielo | Plaza de la fuente | -59.6..8.4 | -57.4..10.6 | sin barreras (radio anterior) | 85 |
| cumbre_hielo | Trono del Yeti | -229.8..26.2 | -71.1..184.9 | sin barreras (radio anterior) | 195 |
| forja_volcano | Forja - sala 1 | -40.8..87.2 | -223.4..-95.4 | sin barreras (radio anterior) | 115 |
| forja_volcano | Forja - sala 2 | -173.5..-77.5 | -173.7..-77.7 | sin barreras (radio anterior) | 98 |
| forja_volcano | Nucleo de la Forja | -63.9..48.1 | -77.1..34.9 | sin barreras (radio anterior) | 106 |
| santuario_azeroth | Prueba de los cinco ecos | 106.5..406.5 | 106.5..406.5 | sin barreras (radio anterior) | 224 |
| infinita | Infinita | -31.5..32.5 | -31.5..32.5 | sin barreras (radio anterior) | 84 |
| fosa | Fosa | -57..61 | 35..153 | sin barreras (radio anterior) | 109 |


Interior original Claro de las raices: `[1415, 1516, 1491, 1599]`.
- oeste: 39/91 columnas con piso y dos bloques libres a Y 86..106; 0 sin apoyo en ese rango. Ejemplos transitables: [(1410, 91, 1512), (1410, 94, 1521), (1410, 103, 1562), (1410, 103, 1581)].
- este: 75/91 columnas con piso y dos bloques libres a Y 86..106; 0 sin apoyo en ese rango. Ejemplos transitables: [(1495, 106, 1512), (1495, 103, 1536), (1495, 101, 1555), (1495, 97, 1580)].
- norte: 20/84 columnas con piso y dos bloques libres a Y 86..106; 0 sin apoyo en ese rango. Ejemplos transitables: [(1411, 92, 1511), (1438, 94, 1511), (1451, 91, 1511), (1456, 88, 1511)].
- sur: 57/84 columnas con piso y dos bloques libres a Y 86..106; 0 sin apoyo en ese rango. Ejemplos transitables: [(1411, 106, 1603), (1429, 105, 1603), (1454, 102, 1603), (1476, 99, 1603)].


Interior original Altar del Chaman: `[1547, 1360, 1645, 1421]`.
- oeste: 5/69 columnas con piso y dos bloques libres a Y 86..106; 4 sin apoyo en ese rango. Ejemplos transitables: [(1542, 95, 1385), (1542, 95, 1386), (1542, 96, 1387), (1542, 97, 1390)].
- este: 40/69 columnas con piso y dos bloques libres a Y 86..106; 12 sin apoyo en ese rango. Ejemplos transitables: [(1649, 102, 1360), (1649, 103, 1370), (1649, 100, 1385), (1649, 99, 1406)].
- norte: 0/106 columnas con piso y dos bloques libres a Y 86..106; 106 sin apoyo en ese rango. Ejemplos transitables: [].
- sur: 46/106 columnas con piso y dos bloques libres a Y 86..106; 0 sin apoyo en ese rango. Ejemplos transitables: [(1561, 88, 1425), (1582, 101, 1425), (1594, 102, 1425), (1629, 99, 1425)].


**Terreno Bosque:** un piso transitable fuera del +4 permite continuar; un vacio permite caer. Este muestreo de columnas NO certifica un cierre natural ni conectividad caminable. Retirar barreras queda pendiente de revision de Claude/dueno de los lados indicados; el plugin protege el rectangulo solo mientras hay pelea. No modificar otros cercos.

Respaldo exacto comprobado: 35313 bloques originales por mundo, 636 cuboides disjuntos. El inverso usa set barrier exclusivamente sobre esos bloques. No usar replace air barrier.
