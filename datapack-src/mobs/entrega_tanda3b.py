"""Manifiesto reproducible, sin subir archivos ni modificar el servidor."""
from pathlib import Path
import hashlib
from mobs.tanda3b import WEIGHTS
from mobs.tamanos import dimensions, scale

ROOT=Path(__file__).resolve().parents[2]


def main():
    pack=ROOT/'build/AstralRPG-Textures.zip'
    digest=hashlib.sha1(pack.read_bytes()).hexdigest()
    names=['astral_esq_'+k for k in WEIGHTS]+['astral_creeper_fantasma']
    rows=['# Tanda 3b: entrega sin desplegar','',
        'Servidor vigente: Empower (Aternos es copia). No desplegado. Requiere las tandas 2 y 3a compatibles.','',
        '## Archivos exactos','', '| Archivo local | Destino |','|---|---|']
    for name in names:
        rows.append(f'| `build/models/{name}.bbmodel` | `plugins/BetterModel/models/{name}.bbmodel` |')
    for name in ('mazmorra','bosque','tumba','cumbre'):
        rows.append(f'| `build/mythicmobs/mobs/{name}.yml` | `plugins/MythicMobs/mobs/{name}.yml` |')
    for sub in ('mobs','skills'):
        rows.append(f'| `build/mythicmobs/{sub}/tanda3b.yml` | `plugins/MythicMobs/{sub}/tanda3b.yml` |')
    rows += ['| `build/gameplay/astral_tanda3b.sk` | `plugins/Skript/scripts/astral_tanda3b.sk` |',
        '| `build/AstralRPG-Items.zip` | `world/datapacks/AstralRPG-Items.zip` |',
        '| `build/AstralRPG-Textures.zip` | R2: objeto `AstralRPG-Textures.zip` |','',
        f'Pack: {pack.stat().st_size} bytes. SHA-1: **`{digest}`**.','',
        '## Actualizacion v2 sobre 3b ya instalada','',
        'De la tabla anterior, reemplazar solamente los seis `.bbmodel`, los dos `tanda3b.yml`, '
        '`astral_tanda3b.sk` y el resource pack. Actualizar `resource-pack-sha1` y reiniciar. '
        'No requiere cambiar datapack, archivos de mazmorras ni recrear controladores. '
        'La lista completa y los controladores siguientes aplican si 3b aun no fue instalada.','',
        '## Instalacion por el responsable del navegador','',
        '1. Revisar `docs/TANDA3B.md` y vistas previas. Salas de Bosque/Minas/Tumba/Cumbre vacias y sin combate.',
        '2. Respaldar los archivos de la tabla. Apagar para reemplazar el datapack. No reemplazar mundos ni usar Worlds > Upload.',
        '3. Subir los archivos de la tabla. Conservar el resto de modelos, YAML y Skripts.',
        '4. Subir el pack con `python tools/subir_pack_r2.py build/AstralRPG-Textures.zip`; verificar la descarga publica y su SHA-1. '
        'En `server.properties`, conservar la URL fija R2 y poner el SHA-1 de esta entrega en `resource-pack-sha1`.',
        '5. Iniciar. El reinicio carga el datapack, modelos y MythicMobs. Comprobar consola. '
        'Si se ajusta durante una prueba: `bettermodel reload`, `mm reload`, `skript:skript reload astral_tanda3b`. '
        'El cambio de propiedades/pack y esta instalacion requieren reinicio.',
        '6. Recrear los controladores siguientes con las salas vacias. Evita retener skills antiguas. '
        'Los comandos borran entidades etiquetadas de esas salas, incluida una instancia de jefe: nunca ejecutarlos durante una partida.',
        '7. Reconectar un jugador, aceptar pack y probar cada clase, oleadas completas, spawn natural y creeper. '
        'Comprobar protecciones de explosion existentes de Tanda 2; potencia 6 y multiplicador de dano x2.','',
        '## Controladores (solo salas vacias)','', '```text']
    from mobs.mazmorra import MINA
    from mobs.mazmorras_data import catalog
    for d in [MINA]+[d for d in catalog() if d['key'] not in ('santuario','forja')]:
        key=d['key']; world=d['world']
        for r in d['rooms']:
            room=r['id']; x,y,z=r['centro']
            rows += [f'mm mobs kill astral_{key}_control_{room}',
                f'execute in minecraft:{world} run kill @e[tag=ad.{key}.{room}]',
                f'data remove storage astral:tanda2/{key}/{room} queue',
                f'mm mobs spawn astral_{key}_control_{room} 1 {world},{x},{y},{z}']
    rows += ['```','', 'No recrear controladores de Santuario ni Forja. No subir configs de prueba completas.','',
        '## Modelos y caja vanilla','', '| Modelo | s | Modelo ancho x alto x fondo (b) | scale entidad |','|---|---:|---|---:|']
    for name in names:
        rows.append(f'| `{name}` | 1 | '+ ' x '.join(f'{v:.3f}' for v in dimensions(name,1))+
            f' | {scale(name,1,"SKELETON") if "esq_" in name else 1} |')
    rows += ['', '## Reproduccion y pendientes','',
        'Desde `datapack-src`: `python mobs/build_models.py`, `python mobs/mythic.py`, `python mobs/mazmorra.py`, '
        '`python build.py`, `python mobs/preview_tanda3b.py`. Convertir los seis modelos con BetterModel 3.6.0 local '
        '(docs/GUIA.md seccion 4), copiar los assets de estos seis modelos de `plugins/BetterModel/build/assets` a '
        '`pack-source/bettermodel/assets`, conservando los demas. '
        '`python build_pack.py pack-source`; `python -m mobs.entrega_tanda3b`.', '',
        'Validacion: `python -m unittest discover -p "test_*.py"` y `python verify.py`. '
        'Las pruebas reales y sus limites, el detalle por modelo, paleta y diferencias finales estan en `docs/TANDA3B.md`.', '',
        'Pendientes: revision visual del dueno; prueba visual en cliente Minecraft 26.1.2 de transparencia/animaciones y combate; '
        'subida R2, instalacion y consola de produccion. No se afirma despliegue. '
        'Se conserva el fantasma: Minecraft 26.1 soporta translucidez en modelos de item y BetterModel usa item_display '
        '(fuentes en docs/TANDA3B.md). Alfa 115-153 en el hielo, destellos blancos opacos, brillo 15/15 y polvo celeste. '
        'Esto confirma la viabilidad tecnica; no reemplaza la comprobacion visual en cliente. '
        'No se regenero el datapack ni cambiaron controladores en v2: los de la tabla corresponden a la instalacion '
        'completa sobre tandas 2/3a. Si ya esta instalada 3b, actualizar solo seis modelos, mobs/skills tanda3b.yml, '
        'astral_tanda3b.sk, pack y SHA-1; no recrear controladores.']
    out=ROOT/'build/deploy/tanda3b.md'; out.write_text('\n'.join(rows)+'\n',encoding='utf8')
    print(out,digest)


if __name__=='__main__': main()
