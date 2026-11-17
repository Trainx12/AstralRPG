"""Entrega reproducible de gachas, carteles y doble salto; no accede a servidores."""
import hashlib
from pathlib import Path
import re
from lobby import GACHAS

ROOT = Path(__file__).resolve().parents[1]
MARK = '\n## Gachas, carteles y doble salto — tanda del 17/11\n'


def build():
    files = [(ROOT/'build/runtime/AstralDecor.jar', 'plugins/AstralDecor.jar'),
             (ROOT/'build/AstralRPG-Items.zip', 'world/datapacks/AstralRPG-Items.zip'),
             (ROOT/'build/gameplay/astral_gameplay.sk', 'plugins/Skript/scripts/astral_gameplay.sk')]
    files += [(p, 'plugins/CrazyCrates/crates/'+p.name) for p in sorted((ROOT/'build/lobby/CrazyCrates/crates').glob('gacha_*.yml'))]
    files += [(ROOT/f'build/menus/DeluxeMenus/gui_menus/{g}.yml', f'plugins/DeluxeMenus/gui_menus/{g}.yml') for g in GACHAS]
    files += [(ROOT/'.local/crazycrates-server/config-sin-menu.yml', 'plugins/CrazyCrates/config.yml')]
    table = '| Local | Destino | SHA-256 |\n|---|---|---|\n'
    for p, dest in files:
        table += f'| `{p.relative_to(ROOT).as_posix()}` | `{dest}` | `{hashlib.sha256(p.read_bytes()).hexdigest()}` |\n'
    report = '''# Gachas y lobby — 17/11/2026

Preparado localmente, SIN despliegue remoto. Principal documentado: Empower; Aternos es copia.
Paper 26.1.2, Java 25, CrazyCrates 26.1.2-560610d y AstralDecor **1.17.0**.
Conservar todos los pendientes anteriores y el pack FINAL; esta tarea no cambia el resource pack.
Las estatuas tanda3a ya estan instaladas segun el estado recibido (17/11 17:03 del servidor): no recrearlas.

## Archivos exactos

'''+table+'''
El config completo es PRIVADO. Antes de instalar, descargar de nuevo el config vigente y aplicar
`python tools/configurar_crazycrates.py <config-vigente> --output .local/crazycrates-server/config-sin-menu.yml`.
El script modifica solo gui.toggle a false, conservando comentarios y todas las otras claves.
Si el config vigente difiere de la copia del ensayo, su SHA-256 sera distinto: regenerar esta lista.
No instalar la configuracion completa del servidor de prueba ni publicar el JAR de CrazyCrates.

## Instalacion conjunta

1. Esperar a que terminen las ruletas en curso, respaldar los archivos de destino y apagar.
2. Reemplazar JAR, datapack, Skript, los tres menus y las DOCE cajas. Las cajas llevan al final
   la confirmacion interna del premio; no mezclar menus/cajas nuevos con el JAR anterior.
   Conservar config/datos de AstralDecor, variables de Skript y todos los mundos.
3. Aplicar el parche al config vigente de CrazyCrates e instalar esa copia. No borrar examples/.
4. Iniciar: **reinicio completo obligatorio** por el JAR y el datapack. No PlugMan ni reload global.
5. Revisar consola: AstralDecor 1.17.0 y CrazyCrates habilitados, Skript sin errores.
   Ejecutar `crates reload` y `dm reload`. Si posteriormente cambia solo el script:
   `skript:skript reload astral_gameplay`. gui.toggle solo requiere `crates reload`, sin reinicio.
6. Con el lobby cargado, ejecutar TODAS las lineas sin comentarios de
   `build/lobby/carteles-17-11.txt`, en orden. No ejecutar comandos.txt entero.
   Elimina text_display astral_holo del lobby y los recrea; retira el rotulo viejo de Expediciones
   por astral.amb.expediciones y mueve solo el ranking de Minas (astral_rank_minas).
   No borra NPC, rankings de otros sitios ni bloques. Si otros chunks del lobby estan descargados,
   recorrer las posiciones antes de limpiar para evitar que sobreviva un display antiguo.
7. Probar x1/10/25/50, con y sin suerte: una ruleta y luego el resto, progreso premio por premio.
   Verificar rareza alta temprana, garantia al llegar al limite, saldo cobrado una vez y premios exactos.
   Llenar inventario antes de abrir: el lote comprado queda pendiente hasta que haya lugar.
   Comprobar desconexion/reconexion, reinicio, suerte que vence durante el lote y compras consecutivas.
8. Vitrina: sin brujula Menu; conservar flechas para recorrer todos los premios. /crates como jugador
   no debe abrir ejemplos. Carteles: Venta/Bazar/Tienda a Y103.5, nombres pequenos del modelo ocultos;
   Minas sobre el NPC en 174.636 102.6 225.735, ranking separado en 169.636 102.8 226.735;
   Expediciones en 178.699 109.727 225.649. Ajuste visual final pendiente con cliente.
9. Probar doble salto en cada mini juego/dropper/arena: no debe impulsar; en survival sigue disponible.

Nunca sustituir mundos ni usar Worlds > Upload en world. En Aternos usar solo sus vias permitidas;
si no acepta el JAR propio, dejar esa parte pendiente. Claude continua con navegador autorizado.

## Pity y equivalencia

El menu anterior sumaba t antes de elegir la primera caja: podia garantizar la primera tirada
de un lote que recien alcanzaba el limite al final, y despues del reset perdia el progreso.
Ahora AstralDecor conserva una cola en PDC por jugador y la suerte al comprar; suma UNO, decide
la caja, espera la entrega y el reset de CrazyCrates, confirma ese premio y continua.
Primera tirada: forceopen CSGO. Resto: API publica pickPrize/givePrize del mismo CrazyCrates,
que es tambien la seleccion usada por mass-open. No inventa ni recalcula pesos.
El ultimo argumento historico true/false ya no fuerza garantias: el contador decide cada premio.
El progreso en vuelo se guarda para reintentar una animacion interrumpida sin sumarla dos veces.
Las llaves de ranking/directas mantienen su comportamiento anterior, fuera de la compra del menu.

Caso controlado sin epicos naturales (la garantia entrega epico), contador inicial cero:

| Gacha / limite | Lote | Antes: posiciones garantizadas / contador final | Ahora |
|---|---:|---|---|
| Armas / 50 | 50 | 1 / 0 | 50 / 0 |
| Monturas / 40 | 50 | 1 / 0 | 40 / 10 |
| Cosmeticos / 20 | 50 | 1 / 0 | 20 y 40 / 10 |

Antes mostraba una sola garantia al evaluar el total; cualquier progreso restante se perdia
en el reset de la primera ruleta. Con contador n-1 y lote 10: antes final 0, ahora final 9.

## CrazyCrates real: conteos

Se instrumentan solo los comandos de entrega para contar un premio, conservando los doce YAML,
sus pesos, resets y confirmaciones. No es un ensayo de Vault, MythicMobs ni LuckPerms.
Cliente NMS simulado; tick rate acelerado solo en el servidor aislado. CSGO usa su animacion real.
Cada fila tiene 1000 premios, sin pity. Las muestras independientes no tienen que coincidir exactamente.

| Caja | Ruta | Basura | Comun | Poco comun | Raro | Epico | Legendario |
|---|---|---:|---:|---:|---:|---:|---:|
'''
    log = (ROOT/'.local/gacha-1711-probe/paper.log').read_text('utf8', errors='replace')
    if 'GACHA RESULT failures=0' not in log or 'GACHA FAIL' in log:
        raise AssertionError('Falta completar el ensayo real en verde')
    smoke = (ROOT/'.local/gacha-1711-probe/paper-pity.log').read_text('utf8', errors='replace')
    if 'GACHA RESULT failures=0' not in smoke or 'GACHA FAIL' in smoke:
        raise AssertionError('Falta verificar el JAR final, snapshot y recuperacion en Paper')
    samples = re.findall(r'GACHA COUNTS (\S+) (force|mass) n=1000 initial=0 final=0 \{([^}]+)\}', log)
    if len(samples) != 12:
        raise AssertionError(f'Se esperaban 12 muestras, hay {len(samples)}')
    from gacha_balance import RARITY_WEIGHT, FACTOR_SUERTE, RAREZAS_SUERTE
    for crate, mode, raw in samples:
        counts = {r: int(n) for r, n in re.findall(r'(\w+)=(\d+)', raw)}
        assert sum(counts.values()) == 1000
        gid = crate.removesuffix('_suerte')
        weights = dict(GACHAS[gid].get('rarity_weight', RARITY_WEIGHT))
        for rarity in weights:
            if crate.endswith('_suerte') and rarity in RAREZAS_SUERTE:
                weights[rarity] *= FACTOR_SUERTE
        # Filtro conservador de desviaciones graves, no prueba de igualdad estadistica.
        for rarity, weight in weights.items():
            probability = weight/sum(weights.values())
            expected = 1000*probability
            assert abs(counts.get(rarity, 0)-expected) < 5*(1000*probability*(1-probability))**.5, (crate, rarity)
        report += f'| {crate} | {mode} | '+ ' | '.join(str(counts.get(r, 0)) for r in ('trash','common','uncommon','rare','epic','legendary'))+' |\n'
    report += '''
Sin desviaciones mayores a cinco desvios estandar por rareza respecto de la tabla. Los pesos YAML
se conservan sin cambios. Mass-open entrega la misma cantidad; el error corregido estaba en el pity del lote.
54 lotes reales: 10/25/50, contadores 0/n-1/n, las tres gachas, con/sin suerte.
El ensayo compara el score DESPUES DE CADA PREMIO con una secuencia de tiradas simples;
si corresponde garantia comprueba que el resultado sea epico/legendario.
Repeticion con el JAR final: verifica tambien la caja exacta en cada premio, suerte vencida
inmediatamente despues de comprar, vitrinas realmente abiertas y recuperacion simulada desde PDC
con una tirada en vuelo. No sustituye probar desconexion/reinicio con cliente y los plugins remotos.
365 pruebas unitarias aprobadas y auditoria de terceros sin arte privado en archivos versionados/ZIP.
Logs, Paper, cliente simulado, plugin de prueba y configuraciones instrumentadas quedan en .local.
No instalar GachaProbe.jar en remoto.

## Paradise 3: diagnostico remoto pendiente

La largada del datapack original es automatica en la caja X -35..-33, Y95..97, Z805..807;
no se agrega un boton ni se reemplazan bloques sin identificar el lugar real de la captura.
El generador agrega dos funciones propias de diagnostico/recuperacion; no altera largada, checkpoints ni meta.
Archivo privado actualizado: `.local/mapas/subir/parkour_paradise3-datapack.zip`.
Si se instalan estas funciones: apagar, respaldar y reemplazar SOLO el contenido de la carpeta activa
`world/datapacks/parkour_paradise3-datapack/` por el ZIP (data/ y pack.mcmeta en su raiz), sin otra copia
activa del mismo pack, e iniciar. No copiar regiones, entities, level.dat ni mundos.

Consola, con un jugador en Paradise (reemplazar JUGADOR):

```text
datapack list enabled
function pp3_main:astral/diagnostico
scoreboard players get #arranco pp3_astral
execute in minecraft:parkour_paradise3 run forceload query -34 766
execute in minecraft:parkour_paradise3 run data get entity @e[type=marker,name=console,limit=1,distance=0..] Pos
execute as JUGADOR run data get entity @s Pos
execute as JUGADOR run scoreboard players get @s pp3_level
```

Si el mundo existe pero las tareas no corren: `function pp3_main:astral/reiniciar_tareas`.
Esta funcion usa schedule replace del adaptador y no cambia bloques. Volver a comprobar la largada.
Para aislarla: `execute in minecraft:parkour_paradise3 as JUGADOR run function pp3_main:player/tp/to_start`;
teletransporta solo a ese jugador al comienzo original. No es una reparacion del mapa.
Registrar F3 del boton que falta, bloque actual y el correspondiente del original privado antes de repararlo.
Comprobar que #arranco vuelva a 1 tras reinicio, marcador console cargado, avanzar dos checkpoints,
morir/volver y terminar. En la meta real, OP: `/ranking meta parkour_paradise3`.
Sigue pendiente el diagnostico en vivo, la reparacion si falta un bloque y la prueba completa jugando.

## Reproducir

Desde la raiz (Python con Pillow, NumPy y PyYAML; JDK 25 local):

```text
python datapack-src/lobby.py
python datapack-src/menus.py
python datapack-src/rankings.py
python datapack-src/build.py
python datapack-src/minijuegos_datapack.py parkour_paradise3
python datapack-src/build_runtime.py --jdk <JDK25/bin> --server .local/testsrv
python tools/probar_gachas_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv
python -m unittest discover -s datapack-src -p "test*.py"
python tools/verificar_terceros.py
python datapack-src/deploy_gachas_1711.py
```
'''
    dest = ROOT/'build/deploy/gachas-carteles-17-11.md'
    dest.write_text(report, 'utf8')
    pending = ROOT/'build/deploy/pendiente-17-11.md'
    text = pending.read_text('utf8').split(MARK)[0]
    # Actualizar solo hashes de los dos artefactos compartidos, conservar todas las otras entregas.
    for p, _ in files[:2]:
        name = p.relative_to(ROOT).as_posix()
        text = re.sub(r'(\| `'+re.escape(name)+r'` \| `[^`]+` \| `)[a-f0-9]+(` \|)', lambda m: m[1]+hashlib.sha256(p.read_bytes()).hexdigest()+m[2], text)
    pending.write_text(text+MARK+'''
Entrega adicional vigente: [gachas-carteles-17-11.md](gachas-carteles-17-11.md).
AstralDecor **1.17.0** sustituye el 1.16.0 anterior; instalar los siguientes archivos en el mismo apagado.
Conservar todos los otros pendientes y el pack FINAL. Las estatuas tanda3a ya estan instaladas segun el estado recibido.

'''+table+'''
Reinicio completo por JAR/datapack. Luego `crates reload`, `dm reload` y consola sin errores.
Ejecutar las lineas de `build/lobby/carteles-17-11.txt` para limpiar/recrear carteles (solo lobby).
El config privado se prepara sobre una copia NUEVA del vigente con `tools/configurar_crazycrates.py`:
solo `gui.toggle: false`; ese cambio aislado requiere `crates reload` y no requiere reinicio.
Actualizacion opcional del datapack privado de Paradise y comandos de diagnostico en la entrega enlazada.
Paradise sigue pendiente de diagnostico en vivo; no se certifica largada/checkpoints/meta ni boton reparado.
Despliegue, consola remota, cliente visual y reconexion/reinicio con lotes en curso siguen pendientes de Claude.
Nunca sustituir mundos ni usar Worlds > Upload en world.
''', 'utf8')
    print(dest)


if __name__ == '__main__':
    build()
