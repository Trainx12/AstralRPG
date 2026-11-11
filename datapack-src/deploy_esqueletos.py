"""Entrega aislada de escalas; no modifica packs ni entregas privadas anteriores."""
import math
import re
import yaml
from terceros import ROOT, privado
from mobs.tamanos import rows, bounds, dimensions, scale, VANILLA

NAMES=('astral','mazmorra','tanda3a','tanda3b')


def main():
    dest=privado()/'build/entregas/esqueletos-tamano/mythicmobs/skills'
    dest.mkdir(parents=True,exist_ok=True)
    # Base privada ya preparada: conservar NPC/modelos privados y sus skills.
    source=privado()/'build/entregas/yeti-bastones-guia/mythicmobs/skills/astral.yml'
    data=yaml.safe_load(source.read_text(encoding='utf8'))
    public=yaml.safe_load((ROOT/'build/mythicmobs/skills/astral.yml').read_text(encoding='utf8'))
    for key,value in public.items():
        if not key.startswith('AST_MODEL_') or key not in data:continue
        commands=[v for v in value.get('Skills',[]) if 'minecraft:scale base set' in v or 'minecraft:step_height base set' in v]
        if not commands:continue
        existing=data[key]['Skills']
        existing[:]=[v for v in existing if 'minecraft:scale base set' not in v and 'minecraft:step_height base set' not in v]+commands
    data['AST_MODEL_astral_yeti_cumbre']=public['AST_MODEL_astral_yeti_cumbre']
    # Goblin y abejorro usan geometria privada distinta de la publica.
    from mobs import tamanos
    original=tamanos.ROOT
    try:
        tamanos.ROOT=privado();bounds.cache_clear()
        for mid,entity,s in (('astral_goblin','ZOMBIE',1),('astral_abejorro','VEX',1),('astral_abejorro_elite','VEX',1.35)):
            model=mid.removesuffix('_elite')
            existing=data['AST_MODEL_'+mid]['Skills']
            existing[:]=[v for v in existing if 'minecraft:scale base set' not in v and 'minecraft:step_height base set' not in v]+tamanos.skills(model,s,entity)
    finally:
        tamanos.ROOT=original;bounds.cache_clear()
    (dest/'astral.yml').write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000),encoding='utf8')
    files=[(str((dest/'astral.yml').relative_to(ROOT)).replace('\\','/'),'plugins/MythicMobs/skills/astral.yml')]
    files += [(f'build/mythicmobs/skills/{n}.yml',f'plugins/MythicMobs/skills/{n}.yml') for n in NAMES[1:]]
    lines=['# Correccion de escala de mobs 3D', '',
        'Generado por `datapack-src/deploy_esqueletos.py`. Despliegue remoto pendiente.',
        'Sustituye las escalas y cajas ensanchadas de d51e4de y la indicacion s=20/7 de la entrega anterior. Cumbre usa s=2.0, igual al Ancestral.', '',
        '## Archivos a instalar', '', '| Local | Destino |', '|---|---|']
    lines += [f'| `{a}` | `{b}` |' for a,b in files]
    lines += ['', 'El astral.yml privado conserva las skills de NPC/modelos privados de la entrega anterior; goblin y abejorro usan las medidas de sus modelos privados. Antes de instalar, comparar con la copia vigente del servidor y conservar cualquier cambio posterior ajeno a escalas. Los otros tres YAML son publicos.', '',
        '## Aplicacion', '',
        '1. Confirmar instancia: la documentacion vigente indica Empower; Aternos es una copia antigua. Respaldar los cuatro archivos y esperar a que las salas queden vacias.',
        '2. Reemplazar solo los cuatro YAML. No cambiar mundos, datapack, JAR, modelos ni resource pack. Nunca Worlds > Upload en world.',
        '3. Ejecutar `mm reload` en consola. No requiere apagar ni reiniciar para estos YAML. Si hubo muchas recargas o hay errores de memoria, reiniciar de forma normal.',
        '4. Revisar consola por errores de YAML, skills/modelos ausentes y comandos de atributos. Probar mobs nuevos y descargados/cargados: onSpawn/onLoad reaplica la escala. Una recarga no garantiza corregir entidades ya cargadas: vaciar/resetear las salas por su ciclo normal o descargar/cargar los chunks; no matar controladores ni mascotas globalmente.',
        '5. Comparar arquero, escudero, guardian, nigromante y esqueleto montado sobre arana con jugador. Verificar Cumbre y Ancestral iguales. Probar melee, flecha y baston; los brazos pueden quedar fuera de la caja, como antes de d51e4de.', '',
        '## Escalas minecraft:scale', '',
        'Las columnas historicas reproducen las formulas de `git show d51e4de^:datapack-src/mobs/tamanos.py` y `git show d51e4de:datapack-src/mobs/tamanos.py`. Geometria de modelos sin cambios en esta tarea. Para Cumbre: s historico 4.0, d51e4de 20/7 y nuevo 2.0.', '',
        '| Mob | Antes de d51e4de | En d51e4de | Nueva |', '|---|---:|---:|---:|']
    entries=rows()+[(f'astral_esq_{k}',f'astral_esq_{k}',1,'SKELETON') for k in ('arquero','escudero','guardian','nigromante')]
    for mid,model,s,entity in entries:
        old_s=4 if mid=='astral_yeti_cumbre' else s
        bad_s=20/7 if mid=='astral_yeti_cumbre' else s
        before=round(min(16,dimensions(model,old_s)[1]/VANILLA[entity][1]),6)
        x,y,z=bounds(model)
        bad=math.ceil(max(y[1]*bad_s/VANILLA[entity][1],2*math.hypot(max(map(abs,x)),max(map(abs,z)))*bad_s/VANILLA[entity][0])*1e6)/1e6
        lines.append(f'| {mid} | {before:.6f} | {bad:.6f} | {scale(model,s,entity):.6f} |')
    try:
        tamanos.ROOT=privado();bounds.cache_clear()
        for mid,entity,s in (('astral_goblin','ZOMBIE',1),('astral_abejorro','VEX',1),('astral_abejorro_elite','VEX',1.35)):
            model=mid.removesuffix('_elite');x,y,z=bounds(model)
            before=scale(model,s,entity)
            bad=math.ceil(max(y[1]*s/VANILLA[entity][1],2*math.hypot(max(map(abs,x)),max(map(abs,z)))*s/VANILLA[entity][0])*1e6)/1e6
            lines.append(f'| {mid} (modelo privado instalado) | {before:.6f} | {bad:.6f} | {before:.6f} |')
    finally:
        tamanos.ROOT=original;bounds.cache_clear()
    lines += ['', 'Las filas sin aclaracion usan modelos publicos. Las tres filas privadas corresponden a la entrega instalable. Las variantes por sala y los jinetes reutilizan las mismas skills; montar no agrega un multiplicador aqui.', '',
        '## Cumbre y alcance', '',
        'Mismo modelo astral_yeti, s=2.0, altura geometrica de reposo 7 b y scale=3.181818 en Cumbre y Ancestral. La altura geometrica no certifica el aspecto final de BetterModel con un cliente. Se conservan ataques, radios, dano, fases y posiciones. Las pruebas de terreno verifican la caja en -101.8 30 56.9, en -54.9 30 6.5 y desplazamientos cortos de la sala. No se agregan apoyos.', '',
        'La tabla y las pruebas numericas no sustituyen capturas de cliente. No desplegado ni consola remota verificada.', '',
        '## Verificaciones reproducibles', '',
        'Desde datapack-src: `python mobs/mythic.py`, `python mobs/mazmorra.py`, `python deploy_esqueletos.py`. Pruebas: `python -m unittest discover -p "test_*.py"`.',
        'Smoke local: `python tools/probar_tamanos_paper.py --java <java25.exe> --server .local/tanda4a-paper` desde la raiz. Nunca instalar TamanosProbe en remoto.', '']
    probe=ROOT/'.local/tamanos-probe/paper.log'
    if probe.exists():
        text=probe.read_text(encoding='utf8',errors='replace')
        if 'TAMANOS RESULT tested=10 failures=0' in text and 'TAMANOS FAIL' not in text:
            lines += ['Paper 26.1.2 / BetterModel 3.6.0 / MythicMobs 5.13.0: 10 spawns, 24 comprobaciones aprobadas (escala, displays y montaje). Cuatro esqueletos a pie y montados en arana; Cumbre y Ancestral con scale=3.181818 y altura real de entidad 7 b. Log privado en `.local/tamanos-probe/paper.log`.', '']
    lines += ['Capturas con cliente en `build/previews/`: pendientes, no se dispuso de un cliente grafico conectado. Falta probar golpes/flechas y revisar consola en la instancia remota.', '']
    suite=ROOT/'.local/esqueletos-tracked-tests.txt'
    if suite.exists():
        raw=suite.read_bytes();text=raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf8',errors='replace')
        count=re.search(r'Ran (\d+) tests',text)
        if count and '\nOK' in text:
            lines += [f'Suite versionada mas test_esqueletos_tamano: {count[1]} pruebas aprobadas. Incluye comparacion contra la formula ejecutada desde git show d51e4de^ y terreno/alcance de Cumbre. Descubrimiento completo anterior: 217/218 aprobadas; unico fallo ajeno en test_cosmeticos_nuevos (archivo previo sin versionar), esperaba 20 claves y encontro 21. Ese trabajo se conserva sin editar ni publicar.', '']
    (ROOT/'build/deploy/esqueletos-tamano.md').write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__':main()
