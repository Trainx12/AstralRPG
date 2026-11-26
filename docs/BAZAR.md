# Bazar estilo Hypixel — plan

Pedido del dueño (23/11/2026): el "Bazar" de hoy es solo un menú que lleva a Tienda, Venta rápida,
Subastas e Intercambio. Tiene que ser un bazar de verdad, como el de Hypixel: los jugadores compran y
venden materiales entre ellos con órdenes y al instante.

**Orden de trabajo:** primero que funcione igual que en Hypixel (con ventanas simples, sin arte), después
los diseños. Nada llega al público sin diseño y sin que el dueño lo pruebe en su sala de admin
(ver "Regla de publicación" al final).

## Qué tiene que hacer (igual que Hypixel)

Por cada producto (ej. Hierro, Madera de roble, Hueso, Fragmento Astral):

| Acción | Cómo funciona |
|---|---|
| **Comprar al instante** | Compra al precio de la oferta de venta más barata. Si no alcanza esa, sigue con la próxima. |
| **Vender al instante** | Vende a la orden de compra que paga más. Si no alcanza, sigue con la próxima. |
| **Crear orden de compra** | "Compro 640 de Hierro a $5 c/u". La plata se descuenta al crearla y queda guardada. Cuando alguien vende, el hierro queda esperando para retirar. |
| **Crear oferta de venta** | "Vendo 640 de Hierro a $6 c/u". Los ítems salen del inventario al crearla. Cuando alguien compra, la plata queda esperando para retirar. |
| **Mis órdenes** | Ver todas las órdenes propias, cuánto se llenó, **retirar** lo conseguido y **cancelar** (devuelve plata o ítems que falten). |

Detalles copiados de Hypixel:
- Cantidades: 1, 16, 64, 160 (2,5 stacks), "todo lo que tengo" (vender) / "todo lo que alcanza" (comprar) y número a mano.
- Precio al crear orden: "igual al mejor", "mejor +0,1" (para quedar primero) o número a mano.
- En cada producto se ven las 7 mejores órdenes de compra y las 7 mejores ofertas de venta, con cantidad y cantidad de órdenes.
- Las órdenes **no vencen** y se llenan aunque el jugador esté desconectado; al entrar le avisa "Tenés cosas para retirar en el Bazar".
- Prioridad: gana el mejor precio; a igual precio, la orden más vieja.
- **Impuesto** a cada venta (Hypixel cobra 1,25 %). Saca plata de la economía.
- Tope de órdenes abiertas por jugador (Hypixel: 14 al empezar).
- Buscador por nombre y categorías.

Categorías propuestas (como las 5 de Hypixel, con lo nuestro):
1. **Minería** — carbón, hierro, oro, diamante, esmeralda, lapis, redstone, cuarzo, netherita, minerales Astrales.
2. **Bosque y pesca** — maderas, pescados, cosas del Océano Astral.
3. **Cultivos** — trigo, papa, zanahoria, calabaza, sandía, caña, etc.
4. **Combate** — drops de mobs (hueso, pólvora, perla de Ender, cuero...) y materiales de jefes que se puedan vender.
5. **Especiales** — gemas en bruto, cristales de las Cavernas, fragmentos.

Qué **no** entra: armas, armaduras, herramientas, ítems con nivel/encantamiento/reforja, ítems de historia,
cosméticos y mascotas. Eso sigue yendo a **Subastas** (cada uno es distinto). El bazar es solo para cosas
que son todas iguales entre sí.

## Cómo se arma

- **Plugin propio `AstralBazar`** (Java, como AstralCavernas o AstralGemas), generado por
  `datapack-src/bazar.py` con `runtime/AstralBazar.java`. No en Skript: tiene muchas órdenes y cuentas, y
  en Skript sería lento y frágil. Cuida la RAM: todo liviano, sin tareas que corran cada tick.
- **Plata:** la misma de siempre (EssentialsX por Vault). Nada de moneda nueva.
- **Ítems:** cada producto se reconoce por su id exacto. Un ítem con nombre cambiado, encantado o dañado no
  se acepta (para que no se cuele algo raro). La lista de productos y sus precios de referencia salen de
  `economia.py`, así no se contradice con la tienda.
- **Guardado:** base de datos SQLite dentro de `plugins/AstralBazar/`. Cada compra/venta se guarda entera
  o no se guarda (no puede quedar a medias si se cae el server). Respaldo automático diario antes del
  reinicio de las 05:00.
- **Registro:** archivo con cada movimiento (quién, qué, cuánto, precio) para revisar si alguien encuentra
  un truco.
- **Protecciones anti-trucos:**
  - Precio mínimo y máximo por producto (ej. entre 10 % y 10 veces el precio de referencia) para que nadie
    se equivoque con un cero de más.
  - Inventario lleno: retira solo lo que entra, el resto queda guardado.
  - Doble clic rápido / dos jugadores a la vez sobre la misma orden: se procesa de a uno.
  - Interruptor de emergencia: `/bazar admin pausar` congela todo sin perder nada.
- **Comandos:** `/bazar` (o el aldeano). Admin: `/bazar admin pausar|reanudar|ver <jugador>|cancelar <orden>|recargar`.
- **Historial de precios:** precio promedio de compra y venta de la última hora y del último día en cada producto.
- **Relación con la tienda del server (EconomyShopGUI):** la tienda sigue. Su precio de compra hace de techo
  y su precio de venta de piso, como el vendedor NPC de Hypixel. Hay que revisar que no se pueda ganar
  plata comprando en un lado y vendiendo en el otro.

## Fases

1. **Funciona (sin diseño).** Plugin con ventanas de cofre simples (ítems normales, textos claros). Pruebas
   automáticas: órdenes que se cruzan, llenado parcial, cancelar, retirar, inventario lleno, plata
   insuficiente, reinicio en medio, dos jugadores a la vez. Prueba en un Paper local con bots
   (como `tools/probar_vacio_paper.py`).
2. **Prueba del dueño en su sala.** Se sube al server **solo para el dueño**: el permiso
   `astral.bazar.usar` lo tiene únicamente ByTrainx (en modo admin, en `/sala`). Los jugadores siguen viendo
   el menú de hoy. El dueño prueba y pide cambios.
3. **Diseños.** Ventanas con arte (Gemini + glifos del pack, como Subastas y Banco): pantalla de
   categorías, producto, crear orden y Mis órdenes. Pack nuevo encima del último FINAL.
4. **Prueba del dueño con el diseño**, de nuevo solo en su sala.
5. **Abrir al público** solo con el OK del dueño: dar el permiso a todos y hacer que el aldeano Bazar abra
   el bazar nuevo. El menú de hoy (Tienda / Venta / Subastas / Intercambio) pasa a llamarse
   **Mercado** o queda como botón dentro del bazar (lo decide el dueño).

## Decisiones del dueño (con propuesta)

| Tema | Propuesta |
|---|---|
| Impuesto por venta | 1,25 % como Hypixel |
| Órdenes abiertas por jugador | 14 |
| Lista de productos | la de arriba; el dueño saca o agrega |
| Menú de hoy | pasa a llamarse "Mercado" y se entra desde un botón del bazar |
| Máximo por orden | 71.680 (como Hypixel) |

## Regla de publicación (desde el 23/11/2026)

Nada nuevo se sube al server para el público si no está:
1. **con su diseño terminado**, y
2. **probado por el dueño en su sala de admin.**

Lo que se sube antes de eso va oculto: solo con permiso del dueño, solo en `/sala` o apagado. Abrirlo a
todos es un paso aparte y solo con el OK del dueño.


## Bazar Astral privado (fase 1, 25/11/2026)

Desde `datapack-src/`: `python bazar.py --jdk <bin Java 25>` genera exclusivamente
`build/bazar/AstralBazar.jar`, `config.yml`, `productos.yml` y la entrega
`build/deploy/bazar-fase1.md`. Especificación vigente: [BAZAR_FASE1.md](BAZAR_FASE1.md).
Solo productos Astrales; equipo únicamente se liquida al servidor. `publico: false`
y permiso default false. No cambia el NPC ni DeluxeMenus. Requiere reinicio;
despliegue pendiente, solo ByTrainx hasta prueba y diseño. Ensayo local:
`python tools/probar_bazar_paper.py --java <bin Java 25>` desde la raíz.
