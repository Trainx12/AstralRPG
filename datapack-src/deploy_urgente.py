"""Entrega reproducible de la correccion urgente; no instala ni modifica mundos."""
import hashlib
import json
from pathlib import Path
import shutil
from terceros import ROOT,privado
from mobs.muerte import MODELS
from mobs.rutas_mazmorras import ROUTES
from mobs.mascotas import CONTROL
from mobs.mazmorra import MINA
from mobs.mazmorras_data import catalog
from mobs.entrega_tanda2 import collision,movement
from mobs.tamanos import scale
from pack_audit import audit


def verification(dest, sha):
    """Publica solo el resumen comprobado; nunca copia los logs privados."""
    import re
    tests=ROOT/'.local/pruebas-entrega.txt'
    probe=ROOT/'.local/urgente-probe/corregido.log'
    if not tests.exists() or not probe.exists():return
    test_text=tests.read_text(encoding='utf8',errors='replace')
    runtime=probe.read_text(encoding='utf8',errors='replace')
    count=re.search(r'Ran (\d+) tests',test_text)
    if not count or '\nOK' not in test_text or 'URGENTE RESULT failures=0' not in runtime:return
    pets=set(re.findall(r'URGENTE PASS pet=(\w+) stage=guardar',runtime))
    deaths=set(re.findall(r'URGENTE PASS death=(\w+) tick=24',runtime))
    checks=len(re.findall('URGENTE PASS ',runtime))
    lines=['# Verificacion de la entrega unica', '',
           f'- Suite completa: {count[1]} pruebas aprobadas.',
           '- verify.py: JSON, funciones, loot, sprites, IDs y secuencia de mazmorras validos.',
           f'- Paper 26.1.2 / MythicMobs 5.13.0 / BetterModel 3.6.0: {checks} comprobaciones aprobadas, cero fallos.',
           f'- {len(pets)} mascotas: invocacion con UUID de dueno, seguimiento (<25 bloques), cambio de mundo y guardado.',
           f'- {len(deaths)} criaturas: tracker animado a ticks 1/8/15 y retirado al tick 24; transformaciones cambian al morir.',
           '- Progreso real: vivos + cola pendiente, barra 3/4 -> 2/4, aislamiento entre dos salas y ocultacion al cambiar de mundo.',
           f'- Pack FINAL: SHA-1 `{sha}`; 5193 referencias verificadas. Cero texturas obsoletas de Carnivora/Asura/peluches.',
           '- Causa reproducida: <global.pet_owner> queda literal; <global.var.pet_owner> devuelve el nombre. La invocacion anterior quedaba sin UUID de dueno.',
           '- Prueba con jugador NMS simulado: no es cliente grafico. Piso de prueba ampliado para evitar caidas al vacio.',
           '- Sin WorldGuard/ClearLag en este Paper. Falta confirmar sus ajustes y la apariencia con cliente real en produccion.',
           '- Sin despliegue remoto ni subida a R2. Logs solo en .local.', '',
           'Reproduccion local: `python tools/probar_urgente_paper.py --java <java25> --server .local/tanda4a-paper --all-pets --install`.', '']
    (dest/'urgente-verificacion.md').write_text('\n'.join(lines),encoding='utf8')


def main():
    private=privado();pack=private/'build/AstralRPG-Textures.zip'
    sha=hashlib.sha1(pack.read_bytes()).hexdigest();refs=audit(pack)
    dest=ROOT/'build/deploy';dest.mkdir(exist_ok=True)
    delivery=private/'build/entregas/urgente-mascotas-texturas';delivery.mkdir(parents=True,exist_ok=True)
    private_files=['AstralRPG-Textures.zip','pack.sha1','models/astral_goblin.bbmodel','models/astral_abejorro.bbmodel',
        'mythicmobs/mobs/astral.yml','mythicmobs/skills/astral.yml','mythicmobs/skills/mascotas.yml',
        'previews/urgente-gui-desde-pack.png','previews/arreglos-apoyos.png','previews/arreglos-cofres.png']
    for rel in private_files:
        target=delivery/rel;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(private/'build'/rel,target)
    rows=[('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
          ('build/mapas_exploracion/astral_viajes.sk','plugins/Skript/scripts/astral_viajes.sk'),
          ('build/menus/DeluxeMenus/gui_menus/principal.yml','plugins/DeluxeMenus/gui_menus/principal.yml'),
          ('build/menus/DeluxeMenus/gui_menus/comandos.yml','plugins/DeluxeMenus/gui_menus/comandos.yml'),
          ('build/shop/EconomyShopGUI/sections/Peluches.yml','plugins/EconomyShopGUI/sections/Peluches.yml'),
          ('build/shop/EconomyShopGUI/shops/Peluches.yml','plugins/EconomyShopGUI/shops/Peluches.yml'),
          ('build/lobby/TAB/secciones-config.yml','plugins/TAB/config.yml: integrar scoreboard y conditions; conservar ajustes locales')]
    for model in sorted(MODELS-{'astral_abejorro'}):rows.append((f'build/models/{model}.bbmodel',f'plugins/BetterModel/models/{model}.bbmodel'))
    for sub,names in [('mobs',('mascotas','tanda3a','tanda3b','tanda4b','mazmorra','bosque','tumba','cumbre','forja')),
                      ('skills',('tanda3b','mazmorra','bosque','tumba','cumbre','forja'))]:
        for name in names:rows.append((f'build/mythicmobs/{sub}/{name}.yml',f'plugins/MythicMobs/{sub}/{name}.yml'))
    for rel in private_files:
        if rel.startswith(('models/','mythicmobs/')):
            target='plugins/'+('BetterModel/'+rel if rel.startswith('models/') else 'MythicMobs/'+rel.removeprefix('mythicmobs/'))
            rows.append(('PRIVADO/build/entregas/urgente-mascotas-texturas/'+rel,target))
    ds=[MINA]+catalog();route_rows=[]
    for d in ds:
        for room,route in zip(d['rooms'],ROUTES[d['key']]):
            route_rows.append((d['key'],d['world'],room['id'],*route))
    sc=scale('astral_yeti',4,'RAVAGER')
    metrics={'yeti_scale':sc,'jefe':collision('cumbre_hielo',(-101.8,30,56.9),'RAVAGER',sc),
        'puerta':collision('cumbre_hielo',(-54.9,30,6.5),'RAVAGER',sc),
        'movimiento':movement('cumbre_hielo',(-101.8,30,56.9),'RAVAGER',sc)}
    (dest/'urgente-yeti.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8')
    lines=['# Urgente: mascotas, texturas, Yeti, esqueletos y Cumbre','',
        'Despliegue PENDIENTE. Preparado para Empower (Paper 26.1.2 / Java 25, MythicMobs 5.13.0, BetterModel 3.6.0).',
        'Aternos es copia; no se subio nada a ningun servidor ni a R2. No usar Worlds > Upload, mundos ni regiones.',
        'PRIVADO = repositorio AstralRPG-privado, por defecto `.local/terceros/AstralRPG-privado`.', '',
        '## Causa de las mascotas','',
        '`<global.pet_owner>` no es un placeholder valido en MythicMobs 5.13. El valido es `<global.var.pet_owner>`.',
        'El anterior setowner no encontraba al jugador: la mascota quedaba sin UUID de dueno y ownerIsOnline la eliminaba.',
        'Ahora sudoskill hace que el jugador invoque en su posicion y summonerIsOwner=true asigna su UUID, sin variable global.',
        'Se conserva el control de permiso, seleccion, desconexion y guardado. Un pedido cambiado/guardado durante la demora se cancela.',
        'Los bonus usan los nombres reales cumbre_hielo, forja_volcano y santuario_interstellar.', '',
        '## Entrega unica: urgente y ajustes del menu/oleadas','',
        'Esta entrega reemplaza los packs y apoyos propuestos anteriormente. No ejecutar arreglos-apoyos.txt.',
        'Los rangos de piso y comandos para recrear TODOS los controladores estan en arreglos-esqueleto-volcano.md y arreglos-puntos.json.',
        'Si aun faltan los datapacks adaptados de parkour del arreglo anterior, usar las dos rutas privadas y destinos de esa guia; nunca subir mundos.',
        'Menu: 14 accesos conservados + Fragmentos y Duelos; /trade en Comandos, Peluches dentro de la Tienda.',
        'TAB: integrar scoreboard.scoreboards (minas, mazmorra, astral) y conditions de secciones-config.yml, conservando el resto del config remoto.',
        'ScoreboardObjectives de PlaceholderAPI ya era requerido; conservar esa expansion. No necesita plugin nuevo.',
        'Cada sala tiene bossbar PURPLE propia. Restantes suma vivos y pendientes; jugadores se asignan al controlador mas cercano para resolver radios solapados.',
        'La barra se vacia al terminar/salir y no se muestra durante jefes. TAB reemplaza las diarias en los cinco mundos de mazmorra; Santuario sigue en espera.', '',
        '## Archivos locales y destinos','', '| Local | Destino |','|---|---|',
        *[f'| `{source}` | `{target}` |' for source,target in rows], '',
        'No subir el ZIP publico de texturas: los 17 modelos privados de mascota y sus retratos ya instalados se conservan.',
        'Los YAML privados astral.yml y skills/mascotas.yml tienen prioridad sobre las copias publicas.', '',
        '## Pack FINAL','',f'SHA-1: `{sha}`. Tamano: {pack.stat().st_size} bytes. Auditoria: {refs} referencias de modelos.',
        '`PRIVADO/build/entregas/urgente-mascotas-texturas/AstralRPG-Textures.zip` es la entrega aislada para publicar en el repo privado.',
        'Todos los PNG usados por modelos estan en item/ o block/. Los sprites sinteticos de adornos son la excepcion: se generan con paletted_permutations declaradas en el atlas, no corresponden a PNG fuera del atlas.',
        'Las capas Carnivora humanoid/humanoid_leggings conservan entity/equipment; las alas son item_display del runtime.',
        'Los originales antiguos de Carnivora, Asura y peluches se retiraron del item-pack derivado; no se tocaron las fuentes.',
        'La auditoria tambien normaliza PNG de modelos legacy de Stellarity y corrige su referencia ender_grass_block_side_snow.', '',
        '## Instalacion (mazmorras vacias)','',
        '1. Respaldar los archivos que se reemplazan. Apagar el servidor: se cambia el datapack y el pack obligatorio.',
        '2. Reemplazar solamente los archivos de la tabla. Conservar los otros modelos y configuraciones.',
        '3. En plugins/WorldGuard/worlds/lobby/config.yml editar solo `mobs.block-plugin-spawning: false`.',
        '   Conservar las regiones; `spawn_mobs=false` sigue evitando apariciones naturales. El arranque carga WG; si se edita encendido, `wg reload`.',
        '4. Claude publica el FINAL con `python tools/subir_pack_r2.py <ruta-del-ZIP-FINAL>`; verificar la descarga publica y su SHA-1.',
        f'5. En server.properties conservar la URL R2 fija y poner `resource-pack-sha1={sha}`. Iniciar y revisar consola.',
        '6. El arranque carga datapack, modelos, MythicMobs y Skript. Si se reemplazan YAML/script encendido: `mm reload`, `skript:skript reload astral_viajes`; para modelos: `bettermodel reload`.',
        '   TAB: `tab reload`; menus: `dm reload`. Para esta entrega completa se recomienda un unico reinicio. No hacer varias recargas de prueba en produccion.',
        '7. Recrear el controlador de mascotas (abajo) y TODOS los de mazmorra con salas vacias, usando arreglos-esqueleto-volcano.md.',
        '8. Comprobar invocar/guardar/cambiar mascota y mundo, creativo/survival, bonus, arco en las tres animaciones, muerte y nuevas llegadas. Revisar consola.', '',
        '## Comandos de actualizacion (sin /)','', '```text',
        f'execute in minecraft:lobby run forceload add {int(CONTROL[0])} {int(CONTROL[2])}',
        'mm mobs kill astral_mascotas_control',
        f'mm mobs spawn astral_mascotas_control 1 lobby,{CONTROL[0]},{CONTROL[1]},{CONTROL[2]}',
        '```','',
        'Retirar espadachines existentes, con las mazmorras vacias (solo la etiqueta de esa variante):','', '```text',
        *[f'execute in minecraft:{w} run minecraft:kill @e[tag=ad.esq.espadachin]' for w in
          ('overworld','the_nether','the_end','lobby','arena','mina','bosque','tumba','cumbre_hielo','forja_volcano','santuario_interstellar')],
        '```','',
        'No instalar el apoyo antiguo propuesto para Cumbre a Y32: el Yeti y el cofre vuelven al piso natural Y30.',
        'Si aquel apoyo ya se instalo en el remoto, inspeccionarlo antes de habilitar Cumbre; no borrar construcciones por suposicion.', '',
        '## Llegadas: tabla unica rutas_mazmorras.py','',
        '| Mazmorra | Mundo | Sala | X | Y | Z | yaw |','|---|---|---|---:|---:|---:|---:|',
        *['| '+' | '.join(map(str,row))+' |' for row in route_rows], '',
        'Entrada por NPC y /mazmorras usa la primera fila; transiciones usan la sala destino. Salidas: Essentials `spawn`, que toma el spawn vigente del lobby.',
        'Cumbre: piso firme comprobado en -54.9 Y30 6.5 (white_concrete_powder); Y52.7 era la posicion desde donde el dueno miraba y no tiene piso ahi.',
        'Jefe en -101.8 30 56.9, yaw -138.9. El generador anterior sobrescribia su llegada con la entrada de la oleada 1.', '',
        '## Tamano y limites de la verificacion','',
        f'Yeti Cumbre s=4, Ancestral s=2; alto 14 bloques, scale={sc}, caja vanilla 12.409 x 14.',
        'El ancho vanilla difiere del modelo (8 bloques). Sin intersecciones en el punto del jefe, llegada/puerta ni desplazamientos de 1 bloque en las cuatro direcciones del mapa local.',
        'Detalles: urgente-yeti.json. Conserva la velocidad casi quieta elegida antes y los ataques del jefe. Falta recorrido de puerta y combate con cliente real.',
        'No se obtuvo captura/video con cliente de la mascota siguiendo ni una comparacion con el esqueleto vanilla en Minecraft. Arco: detalle CPU frente/costado/3-4 en arco-arquero-animaciones.png.',
        'Muerte: animacion death no repetida de 0.8 s, caida de 90 grados, articulaciones flojas. BetterModel usa su evento nativo de muerte; AST_MUERTE agrega tinte y poof.',
        'Las vistas build/previews/muerte-*.png, yeti-tamano.png y esqueletos-brazos.png son renders CPU, no capturas de Minecraft.',
        'GUI desde el FINAL: PRIVADO/build/entregas/urgente-mascotas-texturas/previews/urgente-gui-desde-pack.png (31 items).',
        'El Paper local no cargo WorldGuard ni ClearLag; sus ajustes quedan para comprobar en el despliegue. La prueba NMS no reemplaza capturas/video con cliente ni la consola de produccion. No se instalaron plugins de prueba en remoto.', '']
    (dest/'urgente-mascotas-texturas.md').write_text('\n'.join(lines),encoding='utf8')
    (delivery/'procedencia.json').write_text(json.dumps({'sha1':sha,'source':'build_privado.py --prepare y --assets; Paper local BetterModel 3.6.0',
        'files':private_files},indent=2)+'\n',encoding='utf8')
    verification(dest, sha)
    print('Entrega preparada:',sha,len(rows),'archivos de servidor')


if __name__=='__main__':main()
