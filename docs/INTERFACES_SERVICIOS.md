# Interfaces de servicios

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
