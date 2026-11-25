# Minas: cobre oxidado — 25/11/2026

Arreglo de error habilitado para todos. Las ocho variantes de cobre compacto se
tratan como `copper_block`: permiso de rotura, conteo, drops, XP de los bloques
extra, taladro, Minero de Vetas y Venta rápida (precios actuales y anteriores).
Se mantienen mundo, límites del pozo y rango abierto. Los objetos con nombre o
lore conservan la protección de venta. No se incluyen variantes cortadas.

Los moldes nuevos usan `waxed_copper_block` (mismo aspecto que el cobre nuevo),
sin modificar porcentajes, precios, recorte, límite ni renacimiento.

## Archivo para instalar

| Archivo local | Destino en el servidor |
|---|---|
| `build/minas/Skript/scripts/astral_minas.sk` | `plugins/Skript/scripts/astral_minas.sk` |

Para instalar **solo este arreglo**, usar el contenido de ese archivo en el commit
de esta tarea. La copia del workspace también conserva cambios previos de la
ventana de renacer: no subirla como parte de esta corrección aislada.
Copia aislada lista para que Claude la suba:
`C:\Users\Trainx\Desktop\AstralRPG\.local\cobre-oxidado\entrega\astral_minas.sk`.
SHA-256: `87c3a67eb889ff049aeb797d3c538a0fbecdbfcdefa9e9313ff48bd3fe167c24`.

Conservar las variables de Skript y el archivo actual como respaldo. Reemplazar
solo el script y ejecutar desde consola:

```text
skript reload astral_minas
```

También sirve `skript:skript reload astral_minas`. Verificar consola sin errores.
No requiere apagar ni reiniciar. No hay JAR, datapack, resource pack, TAB ni mapas
que instalar. No reemplazar mundos ni usar Worlds > Upload en la fila `world`.

## Moldes existentes

El arreglo permite picar inmediatamente el cobre oxidado existente, incluso si
los moldes viejos vuelven a copiarlo. Para impedir oxidación futura conviene
rehacer únicamente los dos moldes de las minas de cobre compacto, una mina por
vez, esperando el mensaje final de cada comando:

```text
minasmoldes 8
minasmoldes 15
```

8 = II · Cobre; 15 = III · Cobre. Cobre I (2) contiene mena, no cobre compacto,
y no necesita cambios. No ejecutar `/minasmoldes` sin número.
Después de preparar ambos moldes de cada mina, esperar la regeneración habitual
o ejecutar `minasreset 8` y `minasreset 15` (suben a la plataforma a los jugadores
que están dentro del pozo). No hace falta reiniciar el servidor.

## Verificación y estado

- Generación: `python minas.py` desde `datapack-src/`, sin errores (Python 3.13
  local con las dependencias existentes en `.local/task-deps`).
- Paper 26.1.2-74, Java 25, Skript 2.17.1, sin skript-reflect: carga y recarga
  correctas; 44 comprobaciones aprobadas con jugador NMS simulado en un pozo
  con mina abierta, también usando la versión pública aislada.
- Ocho variantes: permiso de rotura, drop canónico y `am_xp = 5.3`; rechazo de
  mina cerrada, fuera del pozo y cobre cortado; venta de originales con ambos
  esquemas de precios; protección de objetos con nombre; taladro y vetas con
  variantes distintas y conteo; rotura real de cobre oxidado y conteo.
- El bloque principal se normaliza antes del listener MONITOR de AuraSkills
  (prioridad confirmada inspeccionando el JAR local). Su XP queda a cargo de
  AuraSkills como para `copper_block`; no se agregó una segunda recompensa.
  El ensayo funcional no cargó AuraSkills ni midió su saldo real de XP.
- Auditoría `python tools/verificar_terceros.py`: sin arte privado en versionados
  ni ZIP; `git diff --check` correcto.

Fuentes: `datapack-src/minas.py` y `datapack-src/minas.sk`; salida regenerada:
`build/minas/Skript/scripts/astral_minas.sk`. Publicación limitada al parche del
cobre y esta entrega; los cambios previos de renacer se conservan fuera del commit.

Despliegue remoto pendiente de Claude con acceso al navegador. No se efectuó
ninguna subida ni recarga en Aternos/Empower desde esta implementación.
