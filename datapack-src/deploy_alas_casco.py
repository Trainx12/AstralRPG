"""Entrega aislada posterior a Cosmeticos y tanda5a. No despliega ni publica R2."""
import hashlib
import json
import zipfile
from terceros import ROOT, privado
from tanda4b_privado import wing_components
from pack_audit import audit

BASE_SHA = '7c86561ca5edae444bf3fae055eae78a3c31496f'
DELIVERY = 'build/entregas/alas-casco'


def main():
    base = privado()/'build/entregas/cosmeticos-skins/AstralRPG-Textures.zip'
    if hashlib.sha1(base.read_bytes()).hexdigest() != BASE_SHA:
        raise ValueError('La base Cosmeticos no coincide; no combinar con derivados globales')
    with zipfile.ZipFile(base) as z:
        files = {n:z.read(n) for n in z.namelist()}
    original = dict(files)
    for iid, ref in [('asura_alas','asura:asura_wings'),('carnivora_alas','elitecreatures:carnivoret_weapon_set/wing')]:
        ns, name = ref.split(':')
        _, wrapper = wing_components(iid,json.loads(files[f'assets/{ns}/models/{name}.json']),shoulder_tips=True)
        files[f'assets/astral/models/cosmetics/{iid}.json'] = json.dumps(wrapper,indent=2).encode()
    dest = privado()/DELIVERY
    dest.mkdir(parents=True,exist_ok=True)
    target = dest/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            z.writestr(zipfile.ZipInfo(name,(2026,11,11,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    refs = audit(target)
    sha = hashlib.sha1(target.read_bytes()).hexdigest()
    changed = sorted(n for n in files if files[n]!=original.get(n))
    assert changed == [f'assets/astral/models/cosmetics/{iid}.json' for iid in ('asura_alas','carnivora_alas')]
    (dest/'pack.sha1').write_text(sha+'\n')
    (dest/'procedencia.json').write_text(json.dumps(dict(base_sha1=BASE_SHA,final_sha1=sha,
        changed=changed,removed=[],references=refs),indent=2),encoding='utf8')
    manifest(sha,refs)
    print('FINAL',target,'SHA-1',sha,'referencias',refs)


def manifest(sha,refs):
    private = '.local/terceros/AstralRPG-privado/'+DELIVERY
    text = f'''# Alas y casco Carnivora: entrega sin desplegar

Generado por `python datapack-src/deploy_alas_casco.py`. Posterior a `cosmeticos-skins.md` y `tanda5a.md`; conservar esas entregas.
Servidor documentado: Empower, Paper 26.1.2 build 74 / Java 25. Aternos es copia y no admite subir este JAR propio: no eludir esa restriccion.

## Archivos locales y destinos

| Local | Destino |
|---|---|
| `build/runtime/AstralDecor.jar` | `plugins/AstralDecor.jar` (version 1.4.0) |
| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |
| `{private}/AstralRPG-Textures.zip` | R2, objeto `AstralRPG-Textures.zip` |

FINAL privado SHA-1: `{sha}`. Base Cosmeticos `{BASE_SHA}`; solo dos wrappers de alas cambian; todas las otras entradas se conservan byte por byte, sin eliminaciones. {refs} referencias auditadas. No instalar el ZIP publico como FINAL.

## Instalacion pendiente

1. Respaldar los dos archivos de destino y server.properties; esperar sala vacia y apagar.
2. Instalar JAR y datapack de la tabla. Conservar configs, seleccion de cosmeticos y playerdata.
3. Publicar SOLO al realizar el despliegue:

```text
python tools/subir_pack_r2.py {private}/AstralRPG-Textures.zip
```

4. Verificar la descarga publica y SHA-1 antes de fijar `resource-pack-sha1={sha}` en server.properties. Conservar la URL R2 existente.
5. Encender y revisar Done, AstralDecor 1.4.0 y consola sin errores nuevos. Reinicio completo obligatorio; no PlugMan ni /reload. No hacen falta comandos de recarga tras el arranque.
6. No reemplazar mundos, regiones ni mapas; nunca Worlds > Upload sobre world. No subir WingsHelmetProbe.jar, logs, originales ni vistas privadas.

## Diagnostico y cambios

- Casco Carnivora: el modelo privado YA tiene display.head y textura valida, pero equippable.asset_id elegia la armadura plana con cabeza transparente. Solo el casco deja de declarar asset_id, para renderizar el modelo 3D. Pechera, grebas y botas conservan sus capas. Atributos, vida, defensa y material intactos.
- Migracion puntual mediante item modifier: conserva el mismo item, slot, dano, encantamientos y mejoras, incluso v15; no clear/give ni cambio global de version. Se revisa en el chequeo habitual de inventario; cascos guardados en cofres se corrigen al llevarlos. Los kits y recetas nuevos ya salen corregidos.
- Asura solo tiene espada/alas/monedas: no existe casco Asura registrado. Los 20 sombreros de gacha usan HEAD sin asset_id y se ocultan al llevar casco. Otros sets usan capas 2D de equipment, no cascos Java 3D.
- Alas: el runtime previo YA montaba pasajero y usaba getBodyYaw. Se comprobo en CraftPlayer.teleport0 de Paper 26.1.2 que tener pasajeros rechaza teleports Bukkit entre mundos ANTES de PlayerTeleportEvent. Por eso esta entrega se aparta de ese punto del plan: seguimiento de posicion interpolado 2 ticks, sin pasajero real que bloquee /spawn/home/cambio de mundo. Hace falta verificar la suavidad en cliente; no se certifica ausencia visual de tirones con el ensayo NMS.
- Giro corporal limitado a 12 grados/tick por camino angular corto; actualiza transformaciones solo al cambiar, interpoladas 2 ticks. El escaneo de equipo es cada 10 ticks; el bucle cada tick solo visita portadores. No transmite teleports al estar quieto.
- Puntas 0,65 bloques sobre hombros, plano frontal a 0,38 bloques detras; mismo ajuste para ambos pares y seleccion por catalogo extensible. Sigue al jugador tambien sobre montura; agacharse baja el anclaje. Nadando, reptando, durmiendo o planeando se ocultan. Muerte, desconexion, teletransporte y cambio de mundo retiran displays; al recuperar pose/equipo reaparecen. Displays no persistentes y limpieza al desactivar plugin.

La seleccion de modelo de cabeza sigue el comportamiento documentado de [equippable](https://www.minecraft.net/en-us/article/minecraft-java-edition-1-21-2): sin asset de equipo, usa el modelo del item en cabeza. El modelo Carnivora privado conserva su display.head original.

## Verificaciones y limites

Verificado: compilacion Java 25, suite completa de 230 pruebas (incluye 3 nuevas) y 33 regresiones focalizadas, verify.py, auditoria publica sin arte privado y FINAL con 5239 referencias. Ensayo Paper 26.1.2 build 74: 64 comprobaciones de giro limitado/cruce 180, movimiento circular y carrera, agachado, nado/planeo/invisibilidad/espectador, caballo, teletransporte/cambio real de mundo, Carnivora en segunda mano, migracion automatica de casco en cabeza/hotbar/inventario conservando dano/nombre/encantamientos, evento de desconexion, restauracion playerdata y muerte; cero fallos. Los chunks de destino se mantienen cargados solo en el ensayo porque el jugador NMS no crea tickets de una conexion real.
Ensayo automatizado con dos jugadores NMS simulados: no valida imagen, red ni renderizado de un cliente vanilla; no equivale a una reconexion de red real.
No se dispone de dos clientes reales conectados ni capturas en juego antes/despues; no se inventan imagenes ni se publican vistas de arte privado en build/previews.

Antes de dar conformidad visual: dos clientes vanilla 26.1.2 con el FINAL aceptado; casco de frente y desde observador, icono y defensa; ambos pares de alas con pechera y capa, girar cabeza rapido sin mover cuerpo, caminar en circulo/correr, agacharse, montar/desmontar, nadar/planear, morir, reconectar y cambiar de mundo. Confirmar altura/separacion y ausencia de saltos/alas huerfanas; revisar consola. Las capturas de assets licenciados quedan solo en el repositorio privado.

Reproducir: `python build.py` desde datapack-src; `python datapack-src/build_runtime.py --jdk <JDK25/bin> --server <Paper-local>`; `python datapack-src/deploy_alas_casco.py`; `python tools/probar_alas_casco_paper.py --java <java25> --base <Paper-local>`.
'''
    (ROOT/'build/deploy/alas-casco.md').write_text(text,encoding='utf8')


if __name__=='__main__':
    main()
