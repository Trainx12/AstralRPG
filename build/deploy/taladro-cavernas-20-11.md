# Taladro en Cavernas y Minas, vetas y aldeanos de minas - 20/11/2026

Pedido del dueno tras probar las Cavernas (7e). Hecho por Claude directo.

## Que se arreglo
- **Vetas que se volvian bloque de musica**: al romper el bloque de arriba o de abajo, el juego recalculaba el
  instrumento del bloque de nota (dejaba de ser "campana" y perdia la textura y el premio). Se apago en
  `config/paper-global.yml`: `block-updates.disable-noteblock-updates: true` (lo mismo usan los plugins de bloques
  propios; tambien protege las menas del Oceano). Pide reinicio.
- **Taladro en las Cavernas** (AstralCavernas 1.1.0): el area la hace el plugin, no el datapack (`tool/broke` sale si
  la dimension es `cavernas_cristal`). Rompe TODO lo del plano (menos roca madre y barreras) como si lo picara el
  jugador: premios, Polvo, comisiones y el campamento protegido igual que a mano. Mirando al piso o al techo rompe un
  cuadrado plano (antes cavaba una columna hacia abajo); en pared crece hacia arriba salvo que el bloque este sobre
  la cabeza. SHIFT = solo un bloque.
- **Oscuridad**: dentro de las Cavernas hay vision nocturna (sin particulas ni icono); se saca al salir.
- **Taladro en las Minas Astrales**: desde la ficha nueva (09/11) la descripcion dice "Area de minado: 3x3" y el
  script buscaba "Rompe en area". `minas.sk` (`am_tool_area`) acepta las dos.
- **Aldeanos de las minas** (en el server, por consola): minas 1-6 un bloque mas arriba (la decoracion subio el piso),
  tier III (14-20) sobre los faros (venta 98,94,63 / viajes 86,95,64 relativo a la mina). `minas.py` lo anota.
  `tp`/`kill` no los mueven (MythicMobs): se borran con `mm mobs kill <id>` y se crean con `mm mobs spawn`.

- **Efecto al picar una veta** (AstralCavernas 1.2.0): la roca es oscura y las grietas casi no se ven. Mientras se pica:
  chispas del color de la gema, sonido de cristal y barra de avance "Picando veta" en la barra de accion; al romperse,
  estallido de color y sonido de cristal.

- **1.3.0**: el avance va en una barra arriba (la barra de accion la pisa la de vida/mana); al romper un bloque, el server
  reenvia las vetas de al lado (el cliente las mostraba un segundo como bloque de musica). Calidad de vetas con menos
  Pulida: comun 88/10/2, honda 72/22/6, con Polvo 76/19/5 y 58/32/10 (Cruda/Pulida/Impecable).

- **Perfecta y Estelar ya salen (muy raras)**, pedido del dueno (antes solo Vacio Estelar). Pesos por mil
  (Cruda/Pulida/Impecable/Perfecta/Estelar): vetas comunes 879/100/20/1/0, hondas 719/220/55/5/1, comunes con Polvo
  758/190/50/2/0, hondas con Polvo 571/320/95/12/2. Guardianes: Perfecta 5 % y Estelar 0,5 % (repartido entre sus
  gemas). Cofres de mazmorra tier 4: 598/350/50/2/0; tier 5 (o tier 4 con nota A/S): 400/450/138/10/2.

- **1.4.0 recoleccion directa**: en las Cavernas lo picado va al inventario (no al piso). La roca y los bloques comunes no
  sueltan nada; los objetos Astral con el inventario lleno caen a los pies con aviso cada 10 s ("anda a vender al barril").

## Notas
- En creativo romper un bloque no suelta nada (vanilla): probar premios en supervivencia.
