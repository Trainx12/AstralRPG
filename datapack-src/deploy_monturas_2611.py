"""Parche de monturas sobre la copia verificada 1.24.5; nunca compila AstralDecor/Gomera."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

from terceros import privado
from mobs.mythic import MOBS, mob_block, metaskills

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA256 = 'a735f465310892a53d13d85003fcc503d866ac1e778b3dc98fc269c8122d245d'
# 26/11: el instalado en el server (1.24.5) solo difiere en balance/mercader/mesa.json (datos en vivo)
BASES_OK = {BASE_SHA256, 'e33eec7d50ade429eeb9fd4fd0f4470f44204117a840e860dd6d07b9626acf65'}
MOUNTS = [mid for mid, d in MOBS.items() if d['kind'] == 'montura']


def replace_block(text, name, block):
    pattern = rf'(?m)^{re.escape(name)}:\n.*?(?=^[^\s#]|\Z)'
    result, count = re.subn(pattern, lambda _: block.rstrip()+'\n\n', text, flags=re.S)
    if count != 1:
        raise ValueError(f'Esperaba un bloque {name}, encontre {count}')
    return result


def build(java, server, base, mobs_base=None):
    if hashlib.sha256(base.read_bytes()).hexdigest() not in BASES_OK:
        raise ValueError('La base no es la copia verificada 1.24.5 del 24/11; revisar antes de sustituirla')
    classes = Path(tempfile.mkdtemp(prefix='mount-fix-', dir=ROOT/'.local'))
    deps = [*server.joinpath('libraries').rglob('*.jar'), server/'plugins/mythicmobs.jar', server/'plugins/bettermodel.jar']
    subprocess.run([str(java), '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-encoding', 'UTF-8',
                    '-classpath', os.pathsep.join(map(str, deps)), '-d', str(classes),
                    str(ROOT/'datapack-src/runtime/AstralMounts.java')], check=True)
    dest = ROOT/'build/monturas/AstralDecor.jar'
    dest.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as out:
        for name in old.namelist():
            if name.startswith('astral/AstralMounts') and name.endswith('.class'):
                continue
            data = old.read(name)
            if name == 'plugin.yml':
                data = data.replace(b'version: 1.24.5', b'version: 1.24.7')
            info=zipfile.ZipInfo(name,(2026,11,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            out.writestr(info, data)
        for p in sorted((classes/'astral').glob('AstralMounts*.class')):
            info=zipfile.ZipInfo('astral/'+p.name,(2026,11,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            out.writestr(info, p.read_bytes())
    with zipfile.ZipFile(base) as old, zipfile.ZipFile(dest) as new:
        changed = {n for n in set(old.namelist()) | set(new.namelist())
                   if n not in old.namelist() or n not in new.namelist() or old.read(n) != new.read(n)}
        assert all(n == 'plugin.yml' or n.startswith('astral/AstralMounts') for n in changed), changed
    # Regeneracion publica; la entrega privada aplica solamente los seis bloques de monturas.
    public = ROOT/'build/mythicmobs'
    # Conservar las otras definiciones (el generador general tambien agrega NPC/elites).
    current = (public/'mobs/astral.yml').read_text('utf8')
    for mid in MOUNTS:
        current = replace_block(current, mid, mob_block(mid, MOBS[mid]))
    (public/'mobs/astral.yml').write_text(current, 'utf8')
    (public/'skills/astral.yml').write_text(metaskills(), 'utf8')
    private_dest = privado()/'build/entregas/monturas-26-11'
    for sub in ('mobs', 'skills'):
        source = mobs_base if sub == 'mobs' and mobs_base else privado()/f'build/mythicmobs/{sub}/astral.yml'
        original = source.read_text('utf8')
        generated = (public/sub/'astral.yml').read_text('utf8')
        for mid in MOUNTS:
            name = mid if sub == 'mobs' else 'AST_MOUNT_'+mid
            match = re.search(rf'(?m)^{name}:\n.*?(?=^[^\s#]|\Z)', generated, re.S)
            original = replace_block(original, name, match.group())
        target = private_dest/sub/'astral.yml'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(original, 'utf8')
    print('JAR:', dest, 'SHA-1:', hashlib.sha1(dest.read_bytes()).hexdigest())
    print('YAML privados:', private_dest)
    (ROOT/'build/deploy/monturas-26-11.md').write_text(f'''# Monturas: etiqueta y seguir/quieta (privado) — 26/11/2026

Implementacion preparada; instalacion y consola remota pendientes de Claude. No subir desde APIs privadas.

AstralDecor 1.24.7 se arma sobre la copia 1.24.5 verificada del 24/11. Solo cambian
`astral/AstralMounts*.class` y la version de `plugin.yml`; los demas bytes internos
se comparan automaticamente. No incluye Gomera ni compila AstralDecor 1.25.x.

Antes de instalar, comparar el JAR que actualmente espera en `/plugins/update`:
SHA-256 base `{BASE_SHA256}`, o la entrega anterior 1.24.6
`a9e90fff2fb7b702ffc6646c816376dfb4e3ed7070f937652b2f7a4bbc13ac1b` (ba8f51d).
Ambas son compatibles con este parche acumulado. Si difiere de ambas, **no reemplazarlo**: descargar la base actual
y revisar su delta antes de preparar otro parche. Esta copia local no verifica el estado remoto de hoy.

| Archivo local | Destino remoto | SHA-1 |
|---|---|---|
| `build/monturas/AstralDecor.jar` | `/plugins/update/AstralDecor.jar` | `{hashlib.sha1(dest.read_bytes()).hexdigest()}` |
| `.local/terceros/AstralRPG-privado/build/entregas/monturas-26-11/mobs/astral.yml` | `/plugins/MythicMobs/mobs/astral.yml` | `{hashlib.sha1((private_dest/'mobs/astral.yml').read_bytes()).hexdigest()}` |

El YAML privado conserva todos los bloques de su base y sustituye solo las seis monturas.
Base de YAML local: `{(mobs_base or privado()/'build/mythicmobs/mobs/astral.yml').relative_to(ROOT).as_posix()}`.
SHA-256 base YAML: `{hashlib.sha256((mobs_base or privado()/'build/mythicmobs/mobs/astral.yml').read_bytes()).hexdigest()}`.
Tambien se acepta como base remota el YAML de ba8f51d (SHA-1
`62ebc03914d00fedaf7fd99c505d2f7039ef1509`), sobre el que solo cambia la
condicion del temporizador de IA de las dos voladoras.
Comparar tambien ese archivo con el remoto antes de sustituirlo. Si difiere, descargar
el remoto a `.local/` y regenerar con `--mobs-base <archivo>` para preservar los otros cambios.
`skills/astral.yml` no cambia y no necesita subirse. No instalar el YAML publico encima del privado.

Requiere reinicio completo; `mm reload` solo no activa Java. Dejar el JAR en update para
el reinicio diario de las **05:00** autorizado en el pedido. No activar `reiniciopendiente`
ni apagar antes. Para evitar una mezcla de versiones, instalar el YAML con el servidor
apagado durante esa ventana y arrancar; el inicio carga ambos y no requiere recarga adicional.
No cambia datapack ni resource pack. No sustituir mundos ni usar Worlds > Upload.

Despues del inicio: verificar AstralDecor 1.24.7, MythicMobs sin errores y probar las seis
monturas con cliente real, en survival y creativo: huevo, silla, clic en el modelo, WASD,
espacio, Shift, otro jugador, vuelo y Lagarto sumergido. Revisar asiento y animacion de caminar.
Si se retoca luego solo YAML, comando de consola `mm reload`; evitar recargas repetidas.

Reproduccion desde la raiz (JDK 25 y dependencias Python Pillow/PyYAML):
```
python datapack-src/deploy_monturas_2611.py --java <java25> --server .local/testsrv --base .local/deploy-24-11-recetas-todas/verif-1795554672.jar
python tools/probar_monturas_paper.py --java <java25> --base .local/testsrv
cd datapack-src
python -m unittest test_monturas_1711 -v
```

El ensayo usa eventos Bukkit de clic y el evento de BetterModel con hitboxes reales,
sin depender de ejecutar astralmount por consola. Comprueba conductor nativo, atributos,
migracion, propiedad, antirrobo, sillas, controlador FLY, lobby y vectores de nado.
Es un jugador NMS simulado: no acredita desplazamiento de cliente, asiento ni animacion
visual. Esas verificaciones quedan pendientes en el servidor remoto.

Nuevo en 1.24.7, oculto: solo ByTrainx puede nombrar con etiqueta de yunque y alternar
SEGUIR/QUIETA con **Shift + clic derecho**, sin silla ni etiqueta en la mano.
Clic normal sigue montando. El nombre consume una etiqueta en survival, no en creativo.
Nombre y modo se guardan en PDC; texto separado no persistente se reconstruye al cargar.
Seguimiento cada 10 ticks sobre lista propia; no cruza mundos. Lista positiva:
`world`, `world_nether`, `world_the_end`, `sala_dueno`. Desconectado = quieta.
TP a mas de 20 bloques solo si hay piso y volumen despejado cerca, dentro del borde.
Sin lugar seguro espera. El texto flotante y vuelo necesitan revision visual del dueno.
No abrir al publico ni conceder permisos: esta entrega usa el filtro directo ByTrainx.

Discord para la funcion NUEVA (guardar, publicar solo cuando el dueno la abra):
> Ahora podes ponerle nombre a tu montura con una etiqueta.
> Con Shift + clic podes elegir si te sigue o se queda quieta; te avisa por el chat.

Discord del arreglo PUBLICO anterior, solo cuando quede en vivo:
> Arreglamos las monturas: ahora podes ensillarlas y subirte haciendo clic en su modelo.
> Al poner el huevo ya quedan domadas y a tu nombre. Otros jugadores no pueden usarlas.
> Tambien corregimos el acceso a las monturas voladoras y las terrestres quedan tranquilas al bajarte.
''', 'utf8')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--java', required=True, type=Path)
    p.add_argument('--server', required=True, type=Path)
    p.add_argument('--base', required=True, type=Path)
    p.add_argument('--mobs-base', type=Path, help='Copia privada del YAML remoto actual, para conservar sus otros bloques')
    a = p.parse_args()
    build(a.java.resolve(), a.server.resolve(), a.base.resolve(), a.mobs_base.resolve() if a.mobs_base else None)
