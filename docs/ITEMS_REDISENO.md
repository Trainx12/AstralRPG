# Rediseño de ítems — 02/11/2026

Arte original creado con la herramienta integrada ImageGen. Se conserva cada
PNG original en `datapack-src/pack-source/art/items/`, junto con su prompt.
`item_redesign.py` exporta los talismanes como sprites RGBA nativos de 16×16
píxeles y el resto a 32×32, sin suavizado y con alfa binario. El constructor aplica esta capa al final para
que las generaciones antiguas de texturas no la sobrescriban.

- Cinco motosierras: se conservan los diseños actuales y solo se retocan los
  brillos, las sombras y los detalles de superficie. Los rediseños iniciales
  fueron descartados por pedido del usuario.
- Doce talismanes: corazón de vida, llama de furia, pluma/viento y escudo de
  piedra. Engarce sencillo de bronce, plata y oro según nivel. Reimaginados
  específicamente sobre una cuadrícula de 16×16, con un máximo de ocho colores,
  símbolo grande, sin cadenas ni adornos diminutos. No son las joyas detalladas
  de la primera versión reducidas de tamaño.
- Gancho: se conserva el diseño curvo actual con retoques de metal y agarre.
- Chispa Astral como estrella de energía, Alma Corrupta como espectro,
  Madera Estelar como tronco con vetas luminosas y Palo Reforzado con abrazaderas.
- Fragmentos de cristal arcano, umbrío, astral, marea, pantano, arena, hielo y
  fuego; también la Gema Umbría Fragmentada. Cada material tiene fractura y
  motivo propios; los recuerdos de historia ahora usan modelos personalizados.

El Taladro Infernal fue retirado del catálogo, receta, guía y kits. Los nueve
taladros de la progresión siguen disponibles. Las copias antiguas que ya estén
en inventarios no se borran automáticamente; la retirada impide obtener nuevas
copias mediante el datapack.

La versión de ítems sube a 5 para actualizar los modelos de los recuerdos que
ya existían. Los bloques colocados de madera conservan sus texturas anteriores;
el nuevo dibujo corresponde al ítem de material.

Para reconstruir desde `datapack-src`:

```text
python build.py
python item_redesign.py
python build_pack.py pack-source
python -m unittest test_gameplay
python verify.py
```

La lámina `build/Items-redesign-preview.png` muestra los sprites normalizados.
`build/Talismans-16px-preview.png` muestra los doce talismanes ampliados x8 y
también a tamaño nativo. Los doce PNG finales de 16×16 se exportan a
`build/talismans-16px/`; sus originales de ImageGen y prompts se conservan en
`datapack-src/pack-source/art/items/`.
También se empaquetan los doce PNG nativos en `build/talismans-16px.zip`.
Esta revisión de talismanes modifica solo el resource pack; conserva los mismos
IDs y modelos de ítem y no requiere otra migración del datapack.
Los ZIP están publicados en `c3b32bd` e instalados en Aternos. El servidor arrancó
y confirmó `file/AstralRPG-Items.zip (world)` entre los ocho datapacks habilitados.
Falta la revisión visual del jugador dentro de Minecraft.

Los originales, referencias ampliadas y retoques de motosierras/gancho quedan
en `datapack-src/pack-source/art/chainsaws/`. Sus prompts piden explícitamente
mantener silueta, colores y proporciones. Esos seis sprites conservan el encuadre
original al reducirse; no se recentran como los ítems imaginados de cero. La
exportación limita el cambio generado a luz interior (máximo 20 sobre 255) y
conserva exactamente el canal alfa del original. La motosierra astral conserva
sus cuatro cuadros y su tiempo de animación. `verify.py` comprueba esos límites.

Validación local: ocho pruebas de `test_gameplay` aprobadas y `verify.py` aprobado
(JSON, funciones, loot, 31 sprites, nueve taladros y comprobaciones de mazmorras).
La lámina completa fue inspeccionada visualmente. Los prompts exactos están en
los archivos `.prompt.txt` junto al arte; se usó ImageGen integrado.

Revisión de talismanes: comprobados los doce PNG nativos de 16×16, máximo ocho
colores opacos, transparencia binaria, modelos y referencias del ZIP; lámina
ampliada y a tamaño nativo inspeccionada. Se usó ImageGen integrado, con los
prompts exactos en `pack-source/art/items/talisman_*.prompt.txt`.

SHA1 del resource pack local: `e68693c160e3742288ea39b15c00ef1aafc8b0df`.

URL instalada y verificada por descarga pública:
`https://raw.githubusercontent.com/Trainx12/AstralRPG/c3b32bd7270f25d54a3052c2109e979398285a08/build/AstralRPG-Textures.zip`.
URL y SHA1 releídos después de recargar `server.properties`. Copias de los ZIP
publicados anteriores y valores anteriores en `.local/backups/items-redesign/`.
