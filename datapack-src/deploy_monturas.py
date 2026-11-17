"""Entrega aislada de monturas/hostiles y Basura, sin cambiar el pack ni los mundos."""
import hashlib
from pathlib import Path
from collections import defaultdict
from terceros import privado
from lobby import GACHAS, mount_rewards

ROOT=Path(__file__).resolve().parents[1]

def main():
    import deploy_modelos_efectos as configs
    configs.OUT=privado()/'build/entregas/monturas-17-11'
    private=configs.configs_privadas()
    rows=[(ROOT/'build/runtime/AstralDecor.jar','plugins/AstralDecor.jar')]
    rows += [(private/sub/'astral.yml',f'plugins/MythicMobs/{sub}/astral.yml') for sub in ('mobs','skills')]
    rows += [(ROOT/f'build/lobby/CrazyCrates/crates/gacha_monturas{suffix}.yml',
              f'plugins/CrazyCrates/crates/gacha_monturas{suffix}.yml') for suffix in ('','_suerte','_garantia')]
    rows += [(ROOT/'build/menus/DeluxeMenus/gui_menus/gacha_monturas.yml','plugins/DeluxeMenus/gui_menus/gacha_monturas.yml')]
    rows += [(ROOT/'build/mythicmobs/mobs/tanda3a.yml','plugins/MythicMobs/mobs/tanda3a.yml')]
    sums=defaultdict(float);animals=defaultdict(float)
    for rarity,weight,name,cmds in mount_rewards():
        sums[rarity]+=weight
        if cmds[0].startswith('mm egg give') or 'astral.mascota.' in cmds[0]:animals[rarity]+=weight
    probability=sum(pct*animals[r]/sums[r] for r,pct in GACHAS['gacha_monturas']['rarity_weight'].items())
    text='''# Monturas, criaturas hostiles y Basura — 17/11/2026

Preparado localmente. Instalacion y consola remota pendientes de Claude con navegador.
Servidor principal documentado: Empower (Paper 26.1.2 / Java 25); Aternos es copia.
No usar APIs privadas ni reemplazar mundos. Esta entrega conserva el pack FINAL vigente y su SHA-1.
Se integra al apagado/reinicio de pendiente-17-11.md; AstralDecor 1.16.0 sustituye 1.15.0.

## Archivos exactos

| Local | Destino | SHA-256 |
|---|---|---|
'''
    for local,dest in rows:
        text+=f'| `{local.relative_to(ROOT).as_posix()}` | `{dest}` | `{hashlib.sha256(local.read_bytes()).hexdigest()}` |\n'
    text+='''
Los dos YAML de MythicMobs son las copias de la entrega privada: conservan modelos de vendedores,
Goblin y Grub. No instalar encima las skills publicas de reserva. Randomspawns, modelos, texturas,
datapack y scripts no cambian por esta tarea. El datapack y gameplay vigentes deben estar activos
para mob/roll y dano por tier; sus actualizaciones previas siguen en la entrega acumulada.

## Instalacion

1. Guardar copias de los ocho archivos de destino. Apagar el servidor.
2. Reemplazar solo esos archivos. Conservar configuracion y datos de AstralDecor y los mundos.
3. Iniciar: reinicio completo obligatorio por AstralDecor.jar. No PlugMan.
4. El arranque carga los YAML; comprobar AstralDecor 1.16.0, MythicMobs, BetterModel y Skript sin errores.
   Para recargas posteriores solo de configuraciones: `mm reload`, `crates reload`, `dm reload`.
   Ninguna recarga de YAML reemplaza el reinicio del JAR.
5. Con cliente en survival: huevo, silla y WASD/salto de Grillo, Chocobo, Escarabajo y Lagarto;
   probar tambien creativo y otro jugador (no roba la propiedad). Verificar silla y posicion del jinete.
   Las naturales nacen domadas sin dueno; el primer usuario las reclama. Las creadas con huevo
   reciben UUID del usuario del evento, tambien en creativo; no se usa NearestPlayer.
6. Lagarto: agua profunda, W y mirada arriba/abajo, espacio para ascender, Shift para bajar del animal;
   respiracion mientras esta sumergido. Comparar distancia con nado a pie, comprobar corriente/paredes.
7. Mapache y Pinguino: huevos en survival, persecucion y golpes con tier; Pinguino aplica Lentitud
   durante 2,5 s, copos y frio visual 1 s sin dano adicional por congelacion. Los mobs antiguos ya
   cargados mantienen su tipo anterior: comprobar con huevos nuevos; no borrar indiscriminadamente entidades.
8. Verificar Gran Ave/Pterodactilo, vitrina (Basura al final), iconos, bota gastada y compras normales,
   con suerte y con garantia. Falta el ensayo de mass-open del JAR remoto de CrazyCrates.

## Estatuas del Santuario

El octavo archivo (`mobs/tanda3a.yml`) tambien se puede instalar solo, sin apagar:
subirlo, `mm reload` y `mm mobs kill astral_estatua_cangrejo`. Comandos individuales
de spawn en [pendiente-17-11.md](pendiente-17-11.md#estatuas-del-santuario-instalable-por-separado-sin-reinicio).
Conservar la Forja existente. Todas usan IRON_GOLEM y modelo a s=2.0.
Alturas geometricas locales: Coloso 5,76; Chaman 5,38; Momia 4,10; Yeti 7,00; Forja 6,90 bloques.
El Coloso conserva su escala de jefe y entra en el rango de las otras estatuas.
La comparacion visual en pedestales y persistencia al descargar chunks quedan para el cliente remoto.

## Balance

| Rareza | Normal | Con suerte | Garantia |
|---|---:|---:|---:|
| Basura | 55% | 51,16279% | 0% |
| Comun | 20% | 18,60465% | 0% |
| Poco comun | 10% | 9,30233% | 0% |
| Raro | 11% | 15,34884% | 0% |
| Epico | 3,5% | 4,88372% | 87,5% |
| Legendario | 0,5% | 0,69767% | 12,5% |

Basura tiene diez premios equiprobables (5,5% cada uno). No reinicia el pity; la garantia
sigue cada 40 tiradas y excluye Basura. Armas y Cosmeticos conservan sus archivos y tablas.
'''
    text+=f'\nAnimales/mascotas reales: **{probability:.8f}%** por tirada normal, **{probability/2:.8f} en 50**\n'
    text+='''(sin aplicar las tiradas de garantia). Cuenta: 20×70/92 + 10×20/34 + 11×60/60 +
3,5×34/37 + 0,5×22/22. La estimacion ~30% del plan no coincide con su tabla explicita;
se conservaron los pesos pedidos. Sin Basura, el catalogo actual daba 75,07427%.

## Verificacion y limites

Pruebas reproducibles: `python -m unittest discover -s datapack-src -p test_monturas_1711.py`,
regresiones de gacha/mascotas/gameplay, `python tools/verificar_terceros.py`.
Ensayo Paper: `python tools/probar_monturas_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv`.
No instalar MountProbe.jar ni publicar sus logs/mundo. Evidencia y limites finales se registran en el resultado.
Verificado el 17/11: 42 pruebas relevantes aprobadas; suite completa 360/361.
El unico fallo preexistente es `test_special_weapons.test_every_weapon_has_a_resolved_animated_model`
por `varita_curacion`: sus fuentes y test son identicos a HEAD y quedan fuera de esta tarea.
Paper 26.1.2, MythicMobs 5.13.0, BetterModel 3.6.0 y Skript 2.17.1: 51 comprobaciones
aprobadas, incluyendo dueños de huevos, control nativo, una sola silla al morir, direcciones A/D,
vector de nado, respiracion, persecucion por tier, hielo y cinco estatuas persistentes en Pacifico.
Las seis cajas de Armas/Cosmeticos son identicas byte a byte al checkout de HEAD; su generador coincide.
Java 25 compila con dos avisos de deprecacion anteriores; auditoria de terceros aprobada.
El jugador NMS simulado no envia movimiento de vehiculo: el desplazamiento observado fue cero.
Por eso 0,65 bloques/tick es velocidad solicitada; no hay medicion real de nado sin cliente.
El ensayo sin cliente no certifica la posicion visual ni las restricciones del conjunto remoto de
WorldGuard/ClearLag/AstralProgression. Mantener CUSTOM y clearlag_exclude, y la prohibicion de montar
en mazmorras del gameplay. El modelo rosa no se identifica con certeza: la captura original no fue
adjuntada a esta invocacion; no alcanza su descripcion para asignarle una especie.
'''
    (ROOT/'build/deploy/monturas-17-11.md').write_text(text,encoding='utf8')
    pending=ROOT/'build/deploy/pendiente-17-11.md'
    s=pending.read_text('utf8');marker='\n## Monturas, criaturas y Basura (17/11)\n'
    section=marker+'''
Entrega adicional: [monturas-17-11.md](monturas-17-11.md), con ocho archivos exactos y hashes.
Instalar AstralDecor **1.16.0** (sustituye el 1.15.0 indicado arriba) en el mismo apagado/reinicio.
Incluye las copias privadas de mobs/astral.yml y skills/astral.yml, las tres cajas de Monturas
y su menu. Mantener todos los otros pendientes. No cambia el pack FINAL ni su SHA-1.
Tras arrancar: consola limpia; para ajustes posteriores `mm reload`, `crates reload`, `dm reload`.
Despliegue y validacion con cliente siguen pendientes; no se reemplazan mundos.

### Estatuas del Santuario (instalable por separado, sin reinicio)

Subir `build/mythicmobs/mobs/tanda3a.yml` a `plugins/MythicMobs/mobs/tanda3a.yml`.
Conservar skills/tanda3a.yml: no cambia. Ejecutar en consola:
```
mm reload
mm mobs kill astral_estatua_cangrejo
```
Las cinco estatuas ahora usan IRON_GOLEM; el modelo sigue a escala 2.0.
Conservar la Forja existente. El dueno, parado en cada pedestal correspondiente:
```
/mm mobs spawn astral_estatua_coloso_musgoso
/mm mobs spawn astral_estatua_chaman
/mm mobs spawn astral_estatua_momia
/mm mobs spawn astral_estatua_yeti
```
Si falta tambien la Forja: `/mm mobs spawn astral_estatua_golem_forja`.
Comprobar `mm mobs listactive`, persistencia tras cargar chunks y consola sin errores.
No recrear una estatua que ya exista: verificar primero para evitar duplicados.
La escala visual relativa necesita validacion con cliente en los pedestales.
'''
    if marker in s:
        start=s.index(marker);end=s.find('\n## ',start+len(marker))
        s=s[:start]+section+(s[end:] if end!=-1 else '')
    else:s+=section
    pending.write_text(s,encoding='utf8')
    print('build/deploy/monturas-17-11.md')

if __name__=='__main__':main()
