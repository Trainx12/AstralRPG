"""Entrega incremental sobre cascos-silencio-mercader-17-11; nunca publica arte privado."""
from pathlib import Path
import hashlib
import json
import shutil
import yaml
from terceros import ROOT, privado
from mobs.hitboxes import BOSSES, attach

OUT=privado()/'build/entregas/chaman-hitboxes-17-11'


def prepare():
    base=privado()/'build/entregas/cascos-silencio-mercader-17-11/mythicmobs/mobs'
    rows=[]
    def deliver(source,relative,destination):
        target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        rows.append((target.relative_to(ROOT).as_posix(),destination,hashlib.sha256(target.read_bytes()).hexdigest()))
    for name in ('bosque','tumba','cumbre','forja','mazmorra','santuario'):
        # Verificar que no se reemplacen ajustes privados anteriores.
        before=yaml.safe_load((base/f'{name}.yml').read_text('utf8'))
        import subprocess
        old=yaml.safe_load(subprocess.check_output(['git','show',f'0f0d23a:build/mythicmobs/mobs/{name}.yml'],cwd=ROOT).decode('utf8'))
        assert before==old, f'Base privada distinta: {name}; revisar antes de reemplazar'
        deliver(ROOT/f'build/mythicmobs/mobs/{name}.yml',f'mythicmobs/mobs/{name}.yml',f'plugins/MythicMobs/mobs/{name}.yml')
    data=yaml.safe_load((base/'astral.yml').read_text('utf8'))
    for mid,mob in data.items():
        if mid in ('astral_chaman','astral_chaman_ancestral','astral_chaman_elite'):
            skill='command{c="execute at <caster.uuid> run function astral:boss/chaman_ice"} @self ~onTimer:5'
            if skill not in mob['Skills']:mob['Skills'].append(skill)
    target=OUT/'astral.yml';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False,width=10000),encoding='utf8')
    deliver(target,'mythicmobs/mobs/astral.yml','plugins/MythicMobs/mobs/astral.yml')
    for name in ('bosque','tumba','cumbre','forja','mazmorra'):
        deliver(ROOT/f'build/mythicmobs/skills/{name}.yml',f'mythicmobs/skills/{name}.yml',f'plugins/MythicMobs/skills/{name}.yml')
    for mid in sorted(BOSSES):
        source=(privado()/'build/models' if mid=='astral_trainx' else ROOT/'build/models')/f'{mid}.bbmodel'
        model=json.loads(source.read_text('utf8'));attach(model)
        target=OUT/f'models/{mid}.bbmodel';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(model),encoding='utf8')
        rows.append((target.relative_to(ROOT).as_posix(),f'plugins/BetterModel/models/{mid}.bbmodel',hashlib.sha256(target.read_bytes()).hexdigest()))
    for source,dest in [('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
                        ('build/mazmorras/astral_mazmorras_copias.sk','plugins/Skript/scripts/astral_mazmorras_copias.sk')]:
        p=ROOT/source;rows.append((source,dest,hashlib.sha256(p.read_bytes()).hexdigest()))
    text='# Chaman, hitboxes y expediciones — 17/11/2026\n\nPreparado sobre `0f0d23a`; despliegue pendiente. Conservar FINAL `9d83b49323139271250519fbfd7df7f65857d730`.\n\n'
    text+='| Local desde la raiz | Destino | SHA-256 |\n|---|---|---|\n'
    text+=''.join(f'| `{a}` | `{b}` | `{c}` |\n' for a,b,c in rows)
    text+='''
Apagar el servidor, respaldar solo los archivos de la tabla, instalar y reiniciar.
No sustituir mundos, regiones, configuraciones completas ni instalar el probe.
No ejecutar el setup completo ni los comandos historicos de mazmorras.
El arranque carga datapack, Skript, AstralDecor 1.19.0, BetterModel y MythicMobs.
Si se comprueban YAML por separado: `mm reload`; modelos: `bettermodel reload`.
Esas recargas solas no instalan el JAR ni el datapack: esta entrega requiere reinicio.
Las cajas `b_` no tienen textura ni geometria visible nueva; no cambiar el FINAL/R2.
Conservar los demas YAML privados y sus skills, incluyendo mascotas y monturas.

Revisar consola sin errores de funciones, Skript, MythicMobs o BetterModel.
Entrar con party, abandonar y volver a la misma copia: sala 1/oleada 1;
sumarse a una party ya dentro no debe reiniciarla. Recorrer cada copia real:
la auditoria local usa las regiones disponibles y no certifica mapas remotos.
Probar al Chaman cruzando el rio y la reversion del hielo temporal; no hay
teletransporte por agua. Las correas por distancia se conservan.
Probar flechas, tridentes, bastones y melee en cabeza, cuerpo y extremos.
Las cajas son conservadoras en pose de reposo, no siguen toda deformacion animada.
Mini jefes vanilla conservan la caja nativa de su modelo vanilla ampliado.
''' 
    (ROOT/'build/deploy/chaman-hitboxes-17-11.md').write_text(text,encoding='utf8')
    return rows


if __name__=='__main__':
    print(f'{len(prepare())} archivos listados; entrega privada {OUT}')
