"""Entrega aislada de Tienda y decoracion sobre el pack instalado. No despliega."""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
import subprocess
import zipfile
import yaml
from terceros import ROOT, privado
from tanda4b_privado import wing_components
from pack_audit import audit
from lobby import NPC_POS

BASE_COMMIT='756d2ec'
BASE_DIR='build/entregas/urgente-mascotas-texturas/'
BASE_SHA='9c181ed2a097ea27021f761346714ca04416e24f'


def baseline(relative):
    return subprocess.check_output(['git','-C',str(privado()),'show',f'{BASE_COMMIT}:{BASE_DIR}{relative}'])


def main(assets):
    blob=baseline('AstralRPG-Textures.zip')
    if hashlib.sha1(blob).hexdigest()!=BASE_SHA:raise ValueError('La base no coincide con el pack instalado')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:files={n:z.read(n) for n in z.namelist()}
    original=dict(files)
    own=[]
    for p in sorted(assets.rglob('*')):
        if p.is_file() and p.stem.startswith('astral_npc_comerciante'):
            relative=p.relative_to(assets).as_posix()
            if not relative.startswith('bettermodel/'):raise ValueError(relative)
            content=p.read_bytes();files['assets/'+relative]=content;own.append('assets/'+relative)
            dest=ROOT/'datapack-src/pack-source/bettermodel/assets'/relative
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
    if not own or not any('/textures/' in n for n in own):raise ValueError('BetterModel no exporto la Tienda')
    for iid,ref in [('asura_alas','asura:asura_wings'),('carnivora_alas','elitecreatures:carnivoret_weapon_set/wing')]:
        ns,name=ref.split(':')
        tree,wrapper=wing_components(iid,json.loads(files[f'assets/{ns}/models/{name}.json']))
        files[f'assets/astral/items/{iid}.json']=json.dumps({'model':tree},indent=2).encode()
        files[f'assets/astral/models/cosmetics/{iid}.json']=json.dumps(wrapper,indent=2).encode()
    delivery=privado()/'build/entregas/tienda-modelo';delivery.mkdir(parents=True,exist_ok=True)
    target=delivery/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):z.writestr(zipfile.ZipInfo(name,(2026,11,11,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
    refs=audit(target);sha=hashlib.sha1(target.read_bytes()).hexdigest()
    (delivery/'pack.sha1').write_text(sha+'\n')
    changed=sorted(n for n,data in files.items() if original.get(n)!=data)
    (delivery/'procedencia.json').write_text(json.dumps({'base_commit':BASE_COMMIT,'base_sha1':BASE_SHA,'final_sha1':sha,
        'changed':changed,'removed':sorted(set(original)-set(files)),'references':refs},indent=2),encoding='utf8')
    # No tocar los derivados previos sin publicar del repositorio privado.
    mobs=yaml.safe_load(baseline('mythicmobs/mobs/astral.yml'))
    public=yaml.safe_load((ROOT/'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf8'))
    mobs['astral_npc_tienda']=public['astral_npc_tienda']
    skills=yaml.safe_load(baseline('mythicmobs/skills/astral.yml'))
    skills['AST_VENDEDOR_PRIVADO']={'Skills':['model{m=astral_vendedor} @self']}
    for relative,data in [('mobs/astral.yml',mobs),('skills/astral.yml',skills)]:
        p=delivery/'mythicmobs'/relative;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True,width=150),encoding='utf8')
    manifest(sha,refs,len(changed))
    print('FINAL',target,'SHA-1',sha,'archivos cambiados',len(changed))


def manifest(sha,refs,count):
    private='.local/terceros/AstralRPG-privado/build/entregas/tienda-modelo'
    rows=[('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
          ('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
          ('build/models/astral_npc_comerciante.bbmodel','plugins/BetterModel/models/astral_npc_comerciante.bbmodel'),
          ('build/mythicmobs/skills/tanda3c.yml','plugins/MythicMobs/skills/tanda3c.yml'),
          (private+'/mythicmobs/mobs/astral.yml','plugins/MythicMobs/mobs/astral.yml'),
          (private+'/mythicmobs/skills/astral.yml','plugins/MythicMobs/skills/astral.yml')]
    lines=['# Tienda, nombres de NPC, alas y peluches', '',
           'Generado por `datapack-src/deploy_tienda.py`. Preparado; no desplegado. El servidor activo figura como Empower en docs/SERVIDOR.md.', '',
           '## Archivos exactos', '', '| Local | Destino |','|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in rows]
    lines += ['',f'Pack FINAL: `{private}/AstralRPG-Textures.zip` -> R2 con `python tools/subir_pack_r2.py {private}/AstralRPG-Textures.zip`.',
              f'Actualizar `resource-pack-sha1={sha}` solo despues de verificar la descarga publica.',
              f'Base instalada `{BASE_SHA}`; {count} entradas cambiadas, ninguna eliminada; {refs} referencias verificadas.', '',
              'El ZIP publico no contiene el arte privado. No instalarlo como FINAL. No subir DecorProbe.jar ni configuraciones del Paper local.', '',
              '## Instalacion y reinicio', '',
              '1. Avisar y esperar sin jugadores; respaldo de los seis archivos/properties que se reemplazan. Apagar el servidor.',
              '2. Subir los archivos de la tabla. Conservar las configuraciones locales de plugins. AstralDecor genera su config nueva; si ya existe, integrar los mapas del config.yml incluido en el JAR.',
              '3. Subir el FINAL a R2, verificar su descarga y actualizar server.properties. No cambiar mundos, regiones ni mapas.',
              '4. Encender, esperar Done y BetterModel listo; revisar consola de MythicMobs, BetterModel y AstralDecor. No requiere recargas adicionales despues del arranque.',
              '5. Comprobar el nombre visible sin apuntar, el clic en Tienda y los guardianes ocultos. Si se recargan YAML con el servidor encendido: `mm reload`; modelos: `bettermodel reload`. El JAR requiere reinicio, no /reload.', '',
              '## Rehacer solo la Tienda si hace falta', '',
              'La recuperacion de modelos no requiere volver a spawnear. Estas lineas son opcionales, solo si falta o debe rehacerse el NPC:', '', '```text',
              'rg flag -w lobby __global__ mob-spawning allow',
              'mm mobs kill astral_npc_tienda',
              'mm mobs spawn astral_npc_tienda 1 lobby,182.5,101,152.678,0,0',
              'rg flag -w lobby __global__ mob-spawning deny','```', '',
              'Si queda una entidad vanilla sin registrar, inspeccionar su UUID y usar `minecraft:kill <UUID>` solo sobre esa entidad. No matar todos los aldeanos ni borrar copias de Portales de otros mundos.', '',
              '## Coordenadas elegidas el 11/11', '', '| NPC | x y z | yaw |','|---|---|---|']
    for mid in ('expediciones','minas','cronista','arena','portales','venta','bazar','herrero','subastas','viajero','tienda'):
        x,y,z,yaw=NPC_POS['astral_npc_'+mid];lines.append(f'| {mid} | {x} {y} {z} | {yaw} |')
    lines += ['', 'Los listados de lobby y tanda3c reflejan estas posiciones; no ejecutar todo comandos.txt para esta actualizacion.', '',
              '## Alas y peluches', '',
              '- Alas en segunda mano (F o inventario), con cualquier pechera. Sacarlas de esa mano las oculta. Sin proteccion ni vuelo; caen o se conservan segun las reglas de muerte/tumbas del servidor. El runtime nunca consume ni entrega copias. Los items viejos se actualizan a v15 al entrar.',
              '- Display pasajero, offset local detras de hombros, rotacion del cuerpo e interpolacion de 2 ticks; baja al agacharse. El objeto no se dibuja en la mano; GUI y suelo conservan su vista.',
              '- Peluches sobre superficies con colision (incluye losas y alfombras). Espacio libre de 0,9 bloques; mensajes al faltar apoyo, permiso, espacio o ante interaccion bloqueada. Conserva cancelaciones ajenas.',
              '- Para decorar lobby: OP con bypass WorldGuard activo o `lp user <jugador> permission set worldguard.region.bypass.lobby true`. Revocar el permiso al terminar. No abrir build para todos. El runtime consulta el bypass oficial tambien al recoger.',
              '- WorldGuard y WorldEdit usados en la prueba local; Bolt, Essentials y AxGraves no estan cargados alli. Si otro plugin bloquea, revisar su permiso en remoto; no desactivar protecciones globalmente.', '',
              '## Calidad y limites', '',
              '- Cuatro vueltas renderizadas, con comparacion frontal, ambos tres cuartos, costado y espalda. Evidencia privada en `.local/tienda-review/vuelta1.png` a `vuelta4.png`.',
              '- Vuelta 1: lentes muy altos, guantes como barra larga; se bajaron lentes, se achicaron y juntaron manos.',
              '- Vuelta 2: bigote recto y nariz escondida, abrigo corto; se inclinaron mechones, se adelanto nariz y alargaron solapas/faldones.',
              '- Vuelta 3: faltaban hebilla ancha, bajo del chaleco, cuello y detalle posterior; se agregaron.',
              '- Vuelta 4: comprobados calva, patillas, lentes turquesa, bigote mas ancho que cabeza, abrigo rojizo con oro, chaleco verde, guantes juntos, botas oscuras e idle. Escala y pixelado usan el rig de los otros nueve NPC.',
              '- Diferencias finales: antiparras simetricas, detalles del abrigo y bigote simplificados en bloques, hebilla octogonal; las manos se juntan segun el pedido. La referencia usa perspectiva y sombreado pintado diferentes; no es una copia pixel a pixel.',
              '- `build/previews/npc-tienda-comparacion.png` contiene referencia y queda local. `npc-todos.png` solo incluye modelos propios.',
              f'- Render de alas Asura y Carnivora con pechera, frente/espalda/costado: `{private}/previews/alas-pechera.png` (solo privado).',
              '- Paper con jugador NMS simulado verifica estado, protecciones y reinicio; no certifica suavidad visual de caminar/correr/saltar ni el clic del menu con cliente real. Revisar esas acciones y las tumbas al desplegar. No hay captura de cliente ni despliegue remoto.', '',
              'Reproduccion: generar datapack/lobby/MythicMobs y `python mobs/preview_tanda3c.py npc`; compilar build_runtime.py; ejecutar `tools/probar_decor_paper.py` con Java25/Paper local; `python datapack-src/deploy_tienda.py --assets <Paper>/plugins/BetterModel/build/assets`; luego `python build_pack.py pack-source` desde datapack-src.', '']
    tests=ROOT/'.local/tienda-tests.txt'
    probes=[ROOT/'.local/decor-probe'/n for n in ('primero.log','reinicio.log')]
    if tests.exists() and all(p.exists() for p in probes):
        blob=tests.read_bytes();suite=blob.decode('utf-16' if blob.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf8',errors='replace')
        runtime='\n'.join(p.read_text(encoding='utf8',errors='replace') for p in probes)
        count=re.search(r'Ran (\d+) tests',suite)
        if count and '\nOK' in suite and runtime.count('DECOR RESULT failures=0')==2 and 'DECOR FAIL' not in runtime:
            lines += ['## Verificacion local comprobada', '',f'- Suite completa: {count[1]} pruebas aprobadas.',
                      f'- Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0 / WorldGuard 7.0.18: {runtime.count("DECOR PASS")} comprobaciones, cero fallos, incluido reinicio.',
                      '- Recuperacion sin duplicados: Tienda, maquinas, Venta rapida, NPC de Expediciones, guardian oculto y guia de salida. Nombre/tracker acompanan /tp.',
                      '- Alas: pasajero unico, pechera simultanea, altura real 1,45 b, giro corporal y altura agachado 1,2 b.',
                      '- Peluches: clic nativo Paper, proteccion WG y bypass OP; piedra, losa y alfombra en supervivencia/creativo; una sola devolucion.',
                      '- Logs completos y referencias conservados solo en .local. Falta la revision visual con cliente real y el despliegue remoto.', '']
    (ROOT/'build/deploy/tienda-modelo.md').write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assets',type=Path,required=True)
    main(p.parse_args().assets.resolve())
