# Interfaces de servicios

Subastas y los tres gachas: ver [SUBASTAS_Y_GACHAS.md](SUBASTAS_Y_GACHAS.md).

Generadores: `services_ui.py` (arte, modelos y fuentes), `services.py`
(datapack y `build/services/astral_servicios.sk`) y `shop_ui.py`
(apariencia de EconomyShopGUI sobre copias privadas en `.local`).

El herrero y la venta usan Skript 2.17.1, Vault y los plugins existentes.
El objeto depositado se conserva separado de los iconos decorativos. Cerrar,
desconectar o descargar el script devuelve ese objeto; si no hay espacio, cae
al lado del jugador. El herrero conserva las recetas, costos y probabilidades
de `items.MEJORAS`; solo cobra dinero cuando la mejora tiene éxito.

La tienda conserva EconomyShopGUI como autoridad para precios, cantidades,
permisos y transacciones. `services_catalog.json` es una copia de precios para
la **estimación** mostrada por Venta rápida: nunca se utiliza para pagar.
La venta real llama `economyshopgui:sellall hand` sobre el objeto depositado.
No admite equipo RPG, objetos renombrados ni encantados.

Los marcos se aplican mediante títulos de fuente propios. Los modelos grandes
usan `oversized_in_gui` y cada bitmap de fuente mide como máximo 256 px.
No sustituyen el inventario genérico, el HUD ni el Cronista.

## Arte

Marcos originales creados con la herramienta integrada ImageGen. Archivos:
`datapack-src/pack-source/ref/{herrero,bazar,comercio}-frame.png`.
Las referencias del usuario orientan el borde y la composición, no los precios
ni el funcionamiento. Prompts utilizados (resumen de las instrucciones visuales):

- Herrero: marco pixel art medieval frontal, proporción 4:5; nogal tallado,
  abrazaderas de hierro forjado, pequeñas gemas cian, brillos de brasa,
  martillo/yunque pequeños en las esquinas; cartel superior vacío y centro
  carbón grande vacío; sin letras, botones, objetos, perspectiva ni marcas;
  exterior transparente, legible a 200 px.
- Bazar: marco pixel art de mercader, madera castaña, latón y esmeraldas;
  toldo verde y crema, monedas y bolsas de especias en esquinas superiores;
  cartel de madera vacío, borde estrecho, centro marrón vacío; frontal, sin
  texto, botones, casillas, objetos ni marcas; exterior transparente.
- Comercio: marco pixel art de piedra y plata, columnas talladas, hierro
  oscuro, incrustaciones escarlata, estandarte rojo superior y a la derecha,
  rubíes en esquinas; centro carbón vacío, borde arquitectónico estrecho;
  frontal, sin texto, botones, productos, casillas ni marcas; transparente.

Las vistas previas son composiciones estáticas: la validación de interacción
debe hacerse también con Skript cargado y dentro de Minecraft.

## Validación de despliegue

- Skript 2.17.1 compiló y recargó `astral_servicios.sk` sin errores después de
  usar la condición nativa `has the scoreboard tag` y los nombres correctos de
  clic con Shift.
- EconomyShopGUI recargó los 28 archivos de categorías y 28 tiendas sin errores
  de tamaño. Sus seis filas **incluyen** la barra de navegación: hay 45 casillas
  de productos y nueve de navegación. Los diseños de `item-layout` conservan
  seis filas y la barra final no se usa para productos.
- El manejador de clics actúa solo en la interfaz activa del servicio. Al
  cerrarla se devuelve el objeto y se limpia la sesión, sin bloquear Bazar.
- Los destinos del Bazar se abren al tercer tick. DeluxeMenus primero programa
  `ClickActionTask.CLOSE` y después `Menu.closeMenu` programa otro `runTask`
  para `closeInventory`: abrir al primer tick deja el destino expuesto a ese
  cierre pendiente. `test_bazar.py` reproduce esa cola de tareas con todos los
  botones generados. La etiqueta `<delay=3>`
  va pegada al comando: un espacio anterior se conserva en el comando real y
  Minecraft lo rechaza como argumento vacío.
- Comprar y el aldeano Tienda usan `economyshopgui:shop`. El alias `/shop`
  también lo registra QuickShop-Hikari y puede resolver al plugin equivocado
  después de reiniciar; no debe usarse para abrir el catálogo del servidor.
- `verify.py` comprueba también las texturas del atlas de servicios, los
  glifos, su avance horizontal neto cero y la inclusión del backend de mejora.

El Viajero lleva directamente al mundo con clic normal. La historia y sus
entregas se gestionan desde el Cronista. La fabricación desde la guía notifica
los eventos de tier I y V después de entregar el objeto, igual que el altar;
una receta sin materiales no registra progreso. `test_forge_story.py` comprueba
estos enlaces en el datapack generado y la interacción del Viajero.
