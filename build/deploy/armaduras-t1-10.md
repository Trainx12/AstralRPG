# Armaduras T1-T10 elegidas por el dueno (15/11/2026) - SIN DESPLEGAR

Las 30 armaduras (3 clases x 10 tiers) usan ahora modelos de mods elegidos por el dueno: casco 3D + cuerpo
"horneado" sobre la armadura vanilla (mismo sistema que T6-T10, `datapack-src/armaduras_t6_10.py`).
El arte es de terceros: solo circuito privado (`docs/TERCEROS.md`). Nada commiteado, pusheado ni subido.

| Clase | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| Mago | Mago Errante (Iron's AR) | Fuego netherita (Wizards) | Sanguina violeta (Anarchy, sin casco; saco largo horneado sobre las piernas) | Piromante (Iron's) | Manto Oscuro (Fantasy) |
| Berserker | Berserker (Rogues) | Gladiador (Fantasy) | Alas del Atardecer (Fantasy) | Festin (Fantasy) | Senor Oscuro en rojo (Fantasy) |
| Arquero | Explorador (Archers) | Explorador netherita (Archers) | Ladron (Anarchy) | Ladron de las Sombras (Fantasy) | Caminante de Sombras (Iron's) |

Huecos de T6-T10: Berserker T6 = Chispa del Alba (Fantasy), Arquero T8 = Rastro Olvidado (Fantasy),
Arquero T9 = Cultista (Iron's) sin la mascara de calavera (se ve la cara del jugador).
Mago T9 (Nebulosa): la capucha va pegada a la cabeza (textura plana, sin casco 3D aparte), pedido del dueno.

Los nombres y stats de los sets no cambian; solo como se ven.

## Cambios de codigo (publico, sin arte)
- `armaduras_t6_10.py`: origenes de la carpeta `mods/Revisar` (`ASTRAL_MODS_REVISAR`), capa overlay de
  Fantasy Armor, tinte rojo, `sin_casco`, `casco_sin_mascara`, `casco_plano` (cabeza horneada).
- `armaduras_geo.py`: la raiz de cada hueso es el primer hueso biped de la cadena (el Ladron colgaba todo de `bone`).
- `items_t6_10.py`: `VISUAL` cubre T1-T10; `SIN_CASCO` (Sanguina) y `CASCO_PLANO` (Nebulosa).
- `build.py`: el yelmo pierde el `asset_id` (casco 3D) en todo tier con modelo, salvo sin casco / casco plano.
  `ITEM_VERSION` 19 -> 20 para que los items viejos de los jugadores se actualicen (yelmos T1-T5 y armas T6-T10).
- `deploy_tiers6_10.py`: recorre T1-T10 y maneja sin casco / casco plano.
- `build/runtime/AstralDecor.jar` recompilado: lleva el catalogo de la mesa con las ballestas nuevas.

## Pack FINAL (privado)
Cadena: `entregas/oficios` -> `entregas/tiers6-10` (armaduras, sha1 49b99e7e) -> `entregas/armas-mod`
(armas de la otra sesion). **El que se sube es el de armas-mod**, que ya trae todo:

`<ASTRAL_PRIVADO>/build/entregas/armas-mod/AstralRPG-Textures.zip`
sha1 `3a710f8ba5ee4bc1238996c62d15e40d6e09e122`
(reemplaza al 030b2f4b de `armas-3d.md`, que no tenia estas armaduras).

Vista: `<ASTRAL_PRIVADO>/build/entregas/armaduras-t6-10/previews/armaduras_t1_10.png` y una hoja por set.

## Como regenerar
```
cd datapack-src
python armaduras_t6_10.py
python build.py
python build_pack.py pack-source
python deploy_tiers6_10.py
python armas_mod.py
cd .. && python tools/verificar_terceros.py
```
286 tests OK; auditoria de terceros limpia.

## Para desplegar (cuando el dueno lo apruebe), junto con `armas-3d.md`
1. Commit y push del codigo publico; commit del circuito privado.
2. Subir `build/AstralRPG-Items.zip` a `world/datapacks/` y `build/runtime/AstralDecor.jar` a `plugins/`.
3. `python tools/subir_pack_r2.py <ASTRAL_PRIVADO>/build/entregas/armas-mod/AstralRPG-Textures.zip`,
   verificar la descarga y poner `resource-pack-sha1=3a710f8ba5ee4bc1238996c62d15e40d6e09e122`.
4. Reiniciar.

## Falta probar en juego
- Cascos 3D nuevos en la cabeza y en el inventario (sobre todo los grandes: Alas del Atardecer, Gladiador, Festin).
- Yelmo de Mago T3: no se ve nada en la cabeza (el modelo no trae casco); su icono queda el de antes.
- Que los items viejos se actualicen solos al version 20.
