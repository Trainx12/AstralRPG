# Version de pruebas de Aternos - 30/10/2026

**Estado: instalado en Aternos y arranque verificado.** Los seis mapas, las plataformas, los 13 controladores,
la galeria, los puestos y sus NPC ya estan colocados. No hace falta ejecutar el montaje inicial.
Verificado por consola: 105 mobs cargados, sin errores de funciones/configuracion de AstralRPG,
reloj de diarias activo y menus recargados. La apariencia del HUD y el recorrido de combate necesitan prueba en Minecraft.

El despliegue incluye el HUD actual (resolucion nativa, mas pixelado), historia, diarias, nuevos mapas,
plataformas de combate, arena y ambientacion. Los mapas originales siguen intactos en Downloads.
Se conservo una copia privada del lobby anterior en `.local/backups/lobby-antes-ambientacion.zip`.

## Recorrido

1. Entrar aceptando el resource pack. Si ya estabas dentro, salir y volver a entrar para descargarlo.
2. `/menu` → Misiones e historia. Viajero en `(178,98,190)`, en la union de los cuatro bloques marcados: clic para historia; shift+clic para ir al mundo.
3. Cronista: cerca del Viajero, en `(174.5,100,212.5)`. Muestra/cobra diarias. Reinicio a medianoche argentina.
4. Portal de Expediciones: arco violeta en `(172.5,100,214.5)`. Su guardian lleva a la terraza nueva.
5. Terraza: `(180.5,100,288.5)` en el lobby. Tiene accesos distintos para bosque, tumba, minas, nieve,
   forja, santuario y arena. Hablar con el guardian delante del arco. `/spawn` vuelve a la plaza.
6. Bazar: puesto verde `(178.637,101,152.678)`; Subastas: reubicado por el dueno en `(205.466,100,175.476)`;
   Herrero: reubicado por el dueno en `(198.657,100,181.429)`. Sus funciones anteriores se conservan.

Las mazmorras nuevas tienen plataformas y espacios despejados para probar oleadas; las salas de las Minas
no se reconstruyen. Se teletransporta automaticamente de una sala a la siguiente al limpiar sus enemigos.
La Forja incluye solamente el volcan sur. El Santuario encadena cinco Ancestrales y requiere historia completa.
La arena permite PvP sin perder inventario; no suma progreso de misiones. Las mascotas pueden acompanarte,
pero sus bonus se activan solo en mina, bosque, tumba, cumbre, forja y santuario.
Los efectos ya aplicados terminan por su duracion normal al salir (hasta 3,5 segundos; absorcion del Fenix hasta 20 segundos).

## Pruebas utiles

- HUD: revisar barra de items, seleccion, corazones/medios corazones, comida, armadura, efectos y barra de jefe.
- Historia: hablar con Herrero, forjar tier I y volver al Viajero; comprobar que repetir el dialogo no repite el pago.
- Diarias: entregar materiales solo en el NPC indicado; si faltan, no deberia consumir una parte del pedido.
- Mazmorras: entrar solo y con dos jugadores; abandonar una sala; volver y comprobar que reinicia sus enemigos.
- Cofre: completar otra vez antes de 30 minutos; no debe volver a pagar. La historia si debe contar la victoria.
- Bazar/Subastas: comprobar que abren los mismos menus; Herrero: probar consulta y shift+clic con un arma.
- Arena: probar una muerte con objetos y experiencia; confirmar que los conservas al reaparecer.
- Mascotas: `/mascotas`, invocar y viajar del lobby al mundo y a una mazmorra; comprobar seguimiento y que
  los efectos solo se renuevan dentro de las mazmorras. En arena no deben activarse ni marcar enemigos.

Para probar rapidamente como OP:

```text
/function astral:admin/todo
/skills skill setlevel <jugador> forging 50
/skills skill setlevel <jugador> sorcery 50
/skills skill setlevel <jugador> archery 50
```

Para entrar al Santuario sin recorrer toda la historia, primero anotar el valor que devuelve
`/scoreboard players get @s aq.state`, ponerlo temporalmente en 10 con
`/scoreboard players set @s aq.state 10` y devolverlo al valor anotado al terminar.
Eso sirve solo para revisar el acceso; no concede el titulo ni los premios de historia.

## Construcciones y NPC donde prefieras

Pararse en el centro del frente de una zona libre y usar uno de estos comandos como OP. El modulo
se extiende hacia el sur y mira al norte. Necesita 7x5 bloques libres y 6 de alto; retapiza el suelo
de esa zona. Si esta ocupado, no construye. Conviene probar primero en creativo.

```text
/function astral:ambiente/bosque
/function astral:ambiente/tumba
/function astral:ambiente/mina
/function astral:ambiente/cumbre
/function astral:ambiente/forja
/function astral:ambiente/santuario
/function astral:ambiente/arena
/function astral:ambiente/expediciones
/function astral:ambiente/bazar
/function astral:ambiente/subastas
/function astral:ambiente/herrero
```

Despues, desde el mismo lugar, crear el NPC correspondiente:

```text
/mm mobs spawn astral_npc_bosque
/mm mobs spawn astral_npc_tumba
/mm mobs spawn astral_npc_mina
/mm mobs spawn astral_npc_cumbre
/mm mobs spawn astral_npc_forja
/mm mobs spawn astral_npc_santuario
/mm mobs spawn astral_npc_arena
/mm mobs spawn astral_npc_expediciones
/mm mobs spawn astral_npc_bazar
/mm mobs spawn astral_npc_subastas
/mm mobs spawn astral_npc_herrero
/mm mobs spawn astral_npc_cronista
```

El lobby bloquea apariciones: antes de crear NPC usar `/rg flag -w lobby __global__ mob-spawning allow`
y al terminar `/rg flag -w lobby __global__ mob-spawning deny`. No duplicar al Cronista: uno mantiene
el reloj y atiende los premios para todos. No es necesario volver a crear los NPC ya instalados.

El datapack contiene `astral:ambiente/lobby` para el montaje inicial y `astral:ambiente/prueba/<mundo>`
para las plataformas de prueba. **No repetir las plataformas una vez que haya construcciones propias**:
limpian el espacio de combate de las copias nuevas. No afectan los ZIP originales ni las Minas.
