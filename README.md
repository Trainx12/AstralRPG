# AstralRPG

**Cambios locales pendientes de probar y publicar:** [docs/AVANCE_CODEX.md](docs/AVANCE_CODEX.md).

Servidor de Minecraft 26.1.2 (Paper) con progresión RPG, sin mods: se puede entrar desde vanilla.

**Administración del servidor (plugins, lobby, comandos, problemas conocidos): [docs/SERVIDOR.md](docs/SERVIDOR.md).**

**Dónde está cada cosa y cómo agregar cosas nuevas: [docs/GUIA.md](docs/GUIA.md).**

- `build/AstralRPG-Items.zip`: datapack (va en `world/datapacks`).
- `build/AstralRPG-Textures.zip`: resource pack que el servidor manda al entrar.
- `datapack-src/`: generadores. Para cambiar stats, recetas o drops se edita `items.py` (o `textures.py` para las texturas) y se corre:

```
python build.py
python build_pack.py pack-source
```

## Cómo se juega

- **Forja Astral**: poné una mesa de herrería, abrí la guía al lado (Esc → "Guía AstralRPG" o `/trigger astral.guia`) y apretá **Forjar**. Los materiales se sacan de tu inventario.
- La guía es un menú con todas las recetas, ítems y dónde conseguir cada material.
- Las armas y armaduras piden nivel de AuraSkills para usarse.
- **Lobby**: aparecés en la isla del lobby. Hay tienda, venta rápida, 3 gachas con ruleta y el Viajero que te lleva al mundo. `/spawn` vuelve al lobby, `/balance` muestra tu plata y `/sb` oculta o muestra el panel de stats.
- **Monturas** (Ave Corredora, Grillo, Escarabajo, Lagarto, Gran Ave, Pterodáctilo): clic derecho con una montura en la mano para ensillarla (se ve la silla puesta). Después, clic derecho para subirte: se maneja con WASD, espacio salta (o sube, en las voladoras) y shift para bajarte. Si muere, suelta la montura.
