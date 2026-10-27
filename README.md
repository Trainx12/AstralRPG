# AstralRPG

Servidor de Minecraft 26.1.2 (Paper) con progresión RPG, sin mods: se puede entrar desde vanilla.

- `build/AstralRPG-Items.zip`: datapack (va en `world/datapacks`).
- `build/AstralRPG-Textures.zip`: resource pack que el servidor manda al entrar.
- `datapack-src/`: generadores. Para cambiar stats, recetas o drops se edita `items.py` (o `textures.py` para las texturas) y se corre:

```
python build.py
python build_pack.py pack-source
```

## Cómo se juega

- **Forja Astral**: poné una mesa de herrería, tirá encima los materiales de una receta (tecla Q) y agachate al lado.
- Al entrar por primera vez recibís la guía con todas las recetas. Si la perdés: `/trigger astral.guia`.
- Las armas y armaduras piden nivel de AuraSkills para usarse.
