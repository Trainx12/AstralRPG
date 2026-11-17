"""Entrega de mascotas protegidas, decoraciones y panorama. Nunca conecta al servidor."""
import hashlib
import json
import re
from pathlib import Path
import zipfile
import yaml
from terceros import ROOT, privado
from pack_audit import audit
from panorama import assets as panorama_assets

NAME='mascotas-oceano-panorama-17-11'
BASE_SHA1='96286fbdc33d77b4ebcc11de8b15f7461631bac4'


def generate():
    out=privado()/'build/entregas'/NAME;out.mkdir(parents=True,exist_ok=True)
    base=privado()/'build/entregas/pack-17-11/AstralRPG-Textures.zip'
    if hashlib.sha1(base.read_bytes()).hexdigest()!=BASE_SHA1:raise ValueError('Base instalada incorrecta')
    with zipfile.ZipFile(base) as z:old={n:z.read(n) for n in z.namelist()}
    with zipfile.ZipFile(ROOT/'build/AstralRPG-Textures.zip') as z:
        barrel='assets/astral/items/barril_xp.json';delta={barrel:z.read(barrel)}
        model=json.loads(delta[barrel])['model']
        assert model['type']=='minecraft:model'
        for name in ('assets/astral/models/'+model['model'].split(':')[1]+'.json',):
            delta[name]=z.read(name)
            for texture in json.loads(delta[name]).get('textures',{}).values():
                ns,path=texture.split(':');key=f'assets/{ns}/textures/{path}.png';delta[key]=z.read(key)
    delta.update(panorama_assets())
    final={**old,**delta};target=out/'AstralRPG-Textures.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(final.items()):z.writestr(zipfile.ZipInfo(n,(2026,11,17,0,0,0)),b,compress_type=zipfile.ZIP_DEFLATED)
    assert all(final[n]==blob for n,blob in old.items() if n not in delta)
    report={'base_sha1':BASE_SHA1,'final_sha1':hashlib.sha1(target.read_bytes()).hexdigest(),
            'changed':sorted(n for n,b in delta.items() if old.get(n)!=b),'preserved':len(set(old)-set(delta)),
            'references':audit(target)}
    # Partir del YAML privado real, conservar su modelo/escala/animaciones.
    source=privado()/'build/entregas/monturas-17-11/mythicmobs/skills/mascotas.yml'
    data=yaml.safe_load(source.read_text('utf8'))
    count=0
    for key,skill in data.items():
        if not key.startswith('PET_MODELO_'):continue
        lines=skill['Skills']
        guards=['addtag{tag=astral.pet} @self','command{c="minecraft:data merge entity <caster.uuid> {Invulnerable:1b}"} @self']
        skill['Skills']=guards+[line for line in lines if line not in guards];count+=1
    dest=out/'mythicmobs/skills/mascotas.yml';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=150),'utf8')
    report['private_pet_variants']=count
    report['private_skills_base_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    # Entrega acotada: no alterar los YAML historicos de otras tandas.
    (out/'delta.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    (out/'pack.sha1').write_text(report['final_sha1']+'\n','utf8')
    delivery(report,out)
    print(json.dumps(report,indent=2))
    return report


def delivery(report,out):
    files=[('build/runtime/AstralProgression.jar','plugins/AstralProgression.jar'),
           ('build/runtime/AstralEfectos.jar','plugins/AstralEfectos.jar'),
           ('build/oceano/AstralOceano.jar','plugins/AstralOceano.jar'),
           ('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
           ('build/gameplay/astral_armas_especiales.sk','plugins/Skript/scripts/special_weapons.sk'),
           ((out/'mythicmobs/skills/mascotas.yml').relative_to(ROOT).as_posix(),'plugins/MythicMobs/skills/mascotas.yml')]
    lines=['# Mascotas, oceano y panorama - 17/11/2026','',
           'Preparado localmente. Sin instalacion remota ni publicacion R2. Continuar sobre lo instalado hasta 1ebd0a5; conservar tambien la tanda 054db88 pendiente.','',
           '| Local | Destino | SHA-256 |','|---|---|---|']
    for source,dest in files:
        lines.append(f'| `{source}` | `{dest}` | `{hashlib.sha256((ROOT/source).read_bytes()).hexdigest()}` |')
    lines += ['', 'La configuracion generada `build/tanda5a/AstralProgression/config.yml` incorpora Mapache/Pinguino del catalogo anterior: integrar solo esas entradas de `mythic` si faltan; conservar el resto de la configuracion instalada.',
              '',f'FINAL privado: `{out.relative_to(ROOT).as_posix()}/AstralRPG-Textures.zip`.',
              f"SHA-1: `{report['final_sha1']}`. Base instalada: `{BASE_SHA1}`; {report['preserved']} entradas conservadas fuera del delta.",
              'El delta efectivo es barril_xp.json y seis panoramas. Conserva modelos, fuentes, Crop & Kettle, cosmeticos y pack instalado; no instalar el ZIP publico.',
              '', '## Instalacion por Claude', '',
              '1. Confirmar servidor y versiones en el navegador: Empower es el principal documentado; Aternos es copia. Comparar las entregas pendientes anteriores, incluido 054db88. Respaldar los archivos a reemplazar y `plugins/AstralOceano/decor/`.',
              '2. Apagar e instalar la tabla. Conservar config.yml del oceano (especialmente proxima-regeneracion), mundos, regiones, datos de jugadores y modelos. No instalar ProgressionProbe/Tanda17Probe. Una sola copia activa de cada JAR y special_weapons.sk.',
              f'3. Publicar SOLO el FINAL con `python tools/subir_pack_r2.py "{out.relative_to(ROOT).as_posix()}/AstralRPG-Textures.zip"`. Verificar la descarga publica y fijar resource-pack-sha1 al SHA-1 anterior, conservando la URL fija.',
              '4. Iniciar con Java 25: reinicio completo obligatorio por los tres JAR y el datapack. El arranque carga MythicMobs/Skript; recargas posteriores de solo YAML: `mm reload`; solo script: `skript:skript reload special_weapons`. No usar PlugMan ni /reload global.',
              '5. Revisar consola: AstralProgression 1.1.0, AstralOceano 1.5.0, AstralEfectos 1.3.0, datapack activo, sin errores de YAML, funciones o Skript. Guardar barcos y texto existentes ANTES de la proxima regeneracion siguiendo docs/OCEANO_DECORACIONES.md.',
              '6. Con cliente, probar mascota existente/nueva/nivel 30 con espada, barrido, arco, baston y area: vida intacta, sin XP ni contador. Hostil normal conserva XP. Monturas con dueno siguen vulnerables y no dan XP. Comprobar el barril en mano/GUI/suelo/marco y el panorama al cargar.',
              '', '## Alcance y limites', '',
              f'Catalogo actual: 18 mascotas activas (Fenix + 17), no 23. YAML privado: {report["private_pet_variants"]} variantes de modelo protegidas; evolucion conserva la misma entidad. El runtime reconoce cualquier ID astral_pet_* y tags astral.pet.* para migrar las cinco retiradas y variantes antiguas al cargar/recibir dano.',
              'Vendedores y estatuas conservan Invincible en sus YAML. Los selectores descartan Invulnerable y astral.pet; AstralEfectos tampoco toma esas entidades como fin del rayo. Las seis monturas con dueno no se vuelven invulnerables.',
              'LynExp instalado administra botellas/encantamientos con XP vanilla; no tiene listener de combate. Sin orbes de estas entidades no recibe XP indirecta. No se encontraron otros consumibles con wrapper de display_context que requieran el mismo cambio; los modelos 3D anteriores quedan sin referencia del barril para conservar el pack.',
              'No hay hologramas de oceano generados por el repo: los avisos son menu/titulo/chat. El texto manual debe guardarse con su volumen. Las decoraciones se restauran al regenerar o con poner; no se reaplican en cada arranque normal.',
              '', '## Verificaciones realizadas', '',
              '369 pruebas unitarias aprobadas; contratos finales de panorama/pack repetidos: 4 aprobados. Auditoria publica sin arte privado ni rutas privadas versionadas. Compilados los tres JAR contra Paper 26.1.2 / Java 25.',
              'Paper local: 72 comprobaciones en la fase inicial y 70 tras reiniciar, ambas con failures=0 y sin ERROR. Dano de espada, flecha, magia, explosion, lava, caida y ahogo mediante DamageSource real; vida intacta y cero XP de Combate/Punteria/Hechiceria. Montura propia muere por dano real, sin XP ni MOB_KILLS/KILL_ENTITY; hostil T2 conserva XP real y baja. Las 18 apariciones Mythic y la migracion por tag de las cinco retiradas pasan.',
              'Decoracion de 52 bloques de lado: bloque de diamante, agua y text_display con texto/posicion exactos. Dos reaplicaciones, regeneracion real y reinicio conservan una sola entidad. Cubemap inspeccionado en vista CPU, aristas probadas y polos suavizados; referencias de ambos packs auditadas. Los 52 vendedores/estatuas revisados conservan Invincible.',
              'Paper usa jugador NMS simulado y eventos reales; GP conserva su API pero sus listeners se retiran SOLO en el ensayo para aislar vulnerabilidad/XP. Se omite solo la mecanica visual BetterModel de las skills de prueba. Sin Multiverse local, el ensayo carga explicitamente el oceano al reiniciar. No sustituye cliente visual, seleccion WorldEdit real, WorldGuard/Multiverse ni consola remota.',
              'Reproducir: python tools/verificar_terceros.py; python -m unittest discover -s datapack-src -p "test*.py"; python tools/probar_tanda17_paper.py --java <java25> --base <Paper-local>. Logs solo en .local; nunca instalar el probe en remoto.', '']
    target=ROOT/'build/deploy/mascotas-oceano-panorama-17-11.md';target.write_text('\n'.join(lines),'utf8')
    pending=ROOT/'build/deploy/pendiente-17-11.md';text=pending.read_text('utf8')
    marker='\n## Mascotas, oceano y panorama (tanda actual)\n'
    if marker in text:text=text.split(marker)[0]
    for source,dest in files:
        digest=hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
        text=re.sub(r'(\| `'+re.escape(source)+r'` \| `[^`]+` \| `)[0-9a-f]{64}(` \|)',r'\g<1>'+digest+r'\2',text)
    text+=marker+'\nLista y hashes vigentes: [mascotas-oceano-panorama-17-11](mascotas-oceano-panorama-17-11.md).\n'
    text+='Esta tanda reemplaza los mismos JAR/datapack/script de las tablas anteriores y agrega AstralProgression, AstralOceano y el YAML privado de mascotas. Conservar el resto de 054db88 pendiente.\n'
    text+=f'Unico FINAL para instalar: `{out.relative_to(ROOT).as_posix()}/AstralRPG-Textures.zip`; SHA-1 `{report["final_sha1"]}`, encima de `{BASE_SHA1}`.\n'
    text+='Apagar y reiniciar. R2 e instalacion remota pendientes de Claude con navegador. Nunca reemplazar mundos. Instrucciones del dueno: [decoraciones](../../docs/OCEANO_DECORACIONES.md).\n'
    pending.write_text(text,'utf8')


if __name__=='__main__':generate()
