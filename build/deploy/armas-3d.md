# Armas 3D elegidas por el dueno (15/11/2026) - SIN DESPLEGAR

Modelos de las armas T6-T10 de cada familia, guante nuevo y tres ballestas nuevas de Arquero.
El arte es de mods de terceros: vive solo en el circuito privado (`docs/TERCEROS.md`).
Nada de esto esta commiteado, pusheado ni subido al servidor.

## Que se hizo

| Arma | T6 | T7 | T8 | T9 | T10 |
|---|---|---|---|---|---|
| Baston | esculpido | esculpido | esculpido | 3D original | 3D original |
| Espada | esculpida | esculpida (animada) | esculpida | esculpida | esculpida |
| Hacha | esculpida | esculpida | esculpida | esculpida | 3D original |
| Guadana | esculpida | esculpida | esculpida | esculpida | 3D original |
| Arco (4 estados al tensar) | esculpido | esculpido | esculpido | esculpido | esculpido (animado) |
| Lanza | esculpida (animada) | 3D original | 3D original | 3D original | 3D original |

- Guantes de Puno Meteoro: modelo 3D original del guante elegido (mismo item, solo cambia como se ve).
- Ballestas T3, T4 y T5: esculpidas, con sus 6 estados (quieta, tensando x3, con flecha, con cohete).
- "3D original": el mod ya traia el modelo 3D y se conservo pieza por pieza (convertido a Java 26.1).
- "Esculpida": el mod solo traia un dibujo plano. Se armo en 3D parada y derecha como las armas propias:
  mangos redondos, orbes y cristales con volumen, hojas con lomo grueso y filo fino. El dibujo del mod
  queda como textura; lo que brillaba en el mod brilla con luz propia y las animadas siguen animadas.
- En el inventario todas muestran el icono plano del mod.

### Ballestas (items nuevos, clase Arquero)

| Item | Carga | Habilidad | Receta (Forja, hoja Arcos) | Nivel Arqueria |
|---|---|---|---|---|
| `ballesta_3` Ballesta Pesada | 0,9 s | Perforacion I | Arco III + 3 Cristal Refinado + ballesta vanilla | 20 |
| `ballesta_4` Ballesta Rapida | 0,65 s | Multidisparo | Ballesta Pesada + 3 Nucleo Eolico | 25 |
| `ballesta_5` Ballesta Astral | 0,2 s | Multidisparo + Perforacion II, no gasta flechas | Ballesta Rapida + 2 Gema Luminica Perfecta + 1 Nucleo Astral | 30 |

Dano: encantamiento `punteria` del tier (igual que los arcos). Carga: encantamiento nuevo `astral:carga_rapida`
(`minecraft:crossbow_charge_time`). Kit de admin: `/function astral:admin/kit_ballestas`.

### Cambios del 15/11 (segunda pasada)

- Bastones rotados: T8 = aether_wizard_staff (wizards), T9 = staff_of_magic_arrows (BiC), T10 = bonescaller_staff (BiC).
  Stats y progresion iguales.
- Lanzas Varatha confirmadas: T7 Hades, T8 Zagreus, T9 Aquiles, T10 Guan Yu (ya estaban asi).
- Nombres nuevos segun como se ve cada arma (ids, stats, recetas y ficha iguales):

| Tier | Familia | Antes | Ahora | Por que |
|---|---|---|---|---|
| 6 | Baston | Baston del Ocaso | Cetro de Amatista Arcana | Vara dorada con cristal violeta en la punta |
| 7 | Baston | Baston del Eclipse | Baston de Brasa Solar | Orbe de fuego anaranjado sobre vara dorada |
| 8 | Baston | Baston Supernova | Baston del Cristal Celeste | Cristal celeste brillante y adornos dorados |
| 9 | Baston | Baston del Vacio Eterno | Baston de la Calavera Errante | Calavera con tela roja en la punta (dispara flechas magicas) |
| 10 | Baston | Baston del Fin de los Tiempos | Cetro del Llamahuesos | Jaula de huesos con un orbe rojo: el baston del invocador de esqueletos |
| 6 | Espada | Espada del Ocaso | Hoja Siniestra | Hoja negra con vetas rojas |
| 7 | Espada | Espada del Eclipse | Daga del Rito Oscuro | Daga gris oscura con gema roja que late |
| 8 | Espada | Espada Supernova | Espada Espectral Carmesi | Hoja roja translucida, de espiritu |
| 9 | Espada | Espada del Vacio Eterno | Mandoble de Obsidiana | Espadon violeta oscuro, como obsidiana |
| 10 | Espada | Espada del Fin de los Tiempos | Espada Esmeralda Nocturna | Hoja verde esmeralda con guarda oscura |
| 6 | Hacha | Hacha del Ocaso | Hacha Doble de Jade | Dos hojas verde agua oscuro |
| 7 | Hacha | Hacha del Eclipse | Hacha del Torbellino | Hojas plateadas en espiral, de viento |
| 8 | Hacha | Hacha Supernova | Hacha Doble Aurea | Doble hoja plateada con nucleo dorado |
| 9 | Hacha | Hacha del Vacio Eterno | Hacha Marca de Fuego | Hoja anaranjada con forma de llama |
| 10 | Hacha | Hacha del Fin de los Tiempos | Gran Hacha del Verdugo | Hacha enorme de hierro oscuro, de ejecutor |
| 6 | Guadana | Guadana del Ocaso | Guadana del Carcelero | Hoja negra con filo rosado, mango con grilletes |
| 7 | Guadana | Guadana del Eclipse | Guadana Osaria | Hoja de hueso amarillento |
| 8 | Guadana | Guadana Supernova | Guadana de Piedra Antigua | Toda de piedra gris tallada |
| 9 | Guadana | Guadana del Vacio Eterno | Guadana de Escarcha | Hoja de hielo azul con puas |
| 10 | Guadana | Guadana del Fin de los Tiempos | Guadana de la Pesadilla | Hoja negra gigante con detalles rojos |
| 6 | Arco | Arco del Ocaso | Arco de las Almas Perdidas | Madera oscura y hueso, con almas |
| 7 | Arco | Arco del Eclipse | Arco del Vendaval Dorado | Arco dorado con curvas de viento |
| 8 | Arco | Arco Supernova | Arco Enredadera del Eco | Ramas verdes enroscadas |
| 9 | Arco | Arco del Vacio Eterno | Arco de Burbujas Abisales | Burbujas azules entre puntas doradas |
| 10 | Arco | Arco del Fin de los Tiempos | Arco Embrujado | Negro con ojos rojos que se mueven |
| 6 | Lanza | Lanza del Ocaso | Lanza de la Fortuna | Asta negra con punta y anillos dorados |
| 7 | Lanza | Lanza del Eclipse | Tridente del Inframundo | Tridente rosa y violeta de puas |
| 8 | Lanza | Lanza Supernova | Lanza del Principe Errante | Punta verde con chispas, del principe del inframundo |
| 9 | Lanza | Lanza del Vacio Eterno | Lanza del Heroe Dorado | Toda dorada con adornos de heroe griego |
| 10 | Lanza | Lanza del Fin de los Tiempos | Guja del Dragon Verde | Dragon verde enroscado y hoja roja en media luna |
| - | Guante | Guantes de Puno Meteoro | Nudillos de Rubi | Punos de rubi rojo con placas metalicas |
| 3 | Ballesta | Ballesta Pesada | Ballesta Pesada de Zafiro | Cuerpo azul con marco dorado y plateado |
| 4 | Ballesta | Ballesta Rapida | Ballesta Rapida del Nether | Netherita oscura con detalles rojos |
| 5 | Ballesta | Ballesta Astral | Ballesta Celeste Veloz | Azul celeste y oro, la mas rapida |

Los nombres van sin tildes ni enie, como el resto de los items.
El id del guante sigue siendo `guantes_meteoro`.

## Archivos

Publico (codigo, sin arte):
- `datapack-src/armas_mod.py` (generador nuevo; lee los mods y escribe solo en el circuito privado).
- `datapack-src/items_t6_10.py` (`ARMA_MODELO` -> `astral:{familia}_{tier}`, tabla `BALLESTAS`).
- `datapack-src/build.py` (ballestas, encantamiento, guia y kit), `ficha.py` (ficha de ballesta),
  `build_pack.py` (reservas: T6-T10 se ven como el T5 y las ballestas como la vanilla).
- `build/AstralRPG-Items.zip`, `build/AstralRPG-Textures.zip`, `build/runtime/mesa.json` regenerados.

Privado (`ASTRAL_PRIVADO/build/entregas/armas-mod/`):
- `pack/` (302 archivos: modelos, texturas e items).
- `AstralRPG-Textures.zip` = pack FINAL. SHA-1: `030b2f4b68c2ed40e607d1bec9a5552a8ceb2f59`
  (base `entregas/tiers6-10` 53cabb35 + cambios publicos + armas).
- `vista_previa.png`: cada arma sola, en la mano y su icono.

## Como regenerar

```
cd datapack-src
python build.py
python build_pack.py pack-source
python armas_mod.py            # modelos + vista previa + pack FINAL (tarda ~1 min)
cd .. && python tools/verificar_terceros.py
```

## Para desplegar (cuando el dueno lo apruebe)

1. Commit y push del codigo publico (y commit del circuito privado).
2. Subir `build/AstralRPG-Items.zip` al mundo (datapack) y `build/runtime/mesa.json` donde lo lee la mesa.
3. `python tools/subir_pack_r2.py <ASTRAL_PRIVADO>/build/entregas/armas-mod/AstralRPG-Textures.zip`,
   verificar la descarga y poner `resource-pack-sha1=030b2f4b68c2ed40e607d1bec9a5552a8ceb2f59`.
4. Reiniciar.

## Avisos

- **Otra sesion esta haciendo armaduras** sobre la misma base (`tiers6-10`). Si esa entrega sale antes o despues,
  hay que unir los dos packs: lo de armas es una capa aparte (`armas-mod/pack`) que se copia encima de cualquier
  FINAL. No subir uno pisando al otro.
- El datapack y el pack publico se regeneraron con el arbol de trabajo actual, que ya tenia cambios sin
  commitear de otro pedido (`build.py`, `ficha.py`, `oceano_items.py`: fichas de herramientas). Revisar antes del commit.
- Falta probar en juego: agarre en primera persona de cada arma, tamano de las lanzas Varatha y del guante
  (cubre todo el brazo, asi viene en el mod), los estados de arcos y ballestas, y el balance de las ballestas
  (Multidisparo + Punteria pega fuerte). La vista previa es un render propio, no una captura del juego.
- Los bastones T8 y T9 pierden la animacion que tenian en el mod (flotaban piezas): sin mods quedan quietos.
- Las armas esculpidas tienen entre 170 y 520 piezas cada una (las propias tienen 60-150). No deberia notarse,
  pero si alguien con PC floja reporta tirones al tenerlas en mano, se puede bajar el detalle (`CELDA` en `armas_mod.py`).
