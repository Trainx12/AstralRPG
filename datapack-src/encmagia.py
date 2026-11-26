"""Encantamientos mágicos privados. Datos compartidos por datapack, mesa y entrega."""
import json
from pathlib import Path

# id: nombre, máximo, destinos, descripción. La mesa filtra custom_data, no el material.
MAGIA = {
    'poder_arcano': ('Poder Arcano', 5, 'baston', '+4% de daño de hechizo por nivel.'),
    'fluidez': ('Fluidez', 4, 'baston', '-5% de recarga de hechizo por nivel.'),
    'sifon_mana': ('Sifón de Maná', 3, 'ofensivo', 'Recupera 1/2/3% del maná máximo al acertar, una vez por lanzamiento.'),
    'marca_arcana': ('Marca Arcana', 3, 'baston', 'El enemigo recibe +5/8/12% de daño de hechizos durante 4 segundos. Renueva, no acumula.'),
    'bendicion': ('Bendición', 3, 'cura', '+10% de curación por nivel. También cura a tu party hasta 2 bloques más lejos.'),
    'sabio_arcano': ('Sabio Arcano', 5, 'todos', '-4% de maná por nivel en habilidades que cobran maná (máximo -20%). Definitivo.'),
    'eco_arcano': ('Eco Arcano', 3, 'baston', '5/10/15% de repetir el hechizo gratis a los 4 ticks con la mitad del daño. Sin Sifón ni otro eco. Definitivo.'),
    'escudo_mana': ('Escudo de Maná', 3, 'todos', 'Paga con maná el 10/20/30% del daño recibido: 1 maná por 1 punto de vida. Definitivo.'),
}
DEFINITIVOS = ('sabio_arcano', 'eco_arcano', 'escudo_mana')


def generate(files):
    def fn(path, text):
        files[f'data/astral/function/{path}.mcfunction'] = text
    files['data/astral/tags/item/magia.json'] = json.dumps({'values': ['minecraft:carrot_on_a_stick', 'minecraft:stick']})
    files['data/astral/tags/enchantment/magia_definitivos.json'] = json.dumps({'values': ['astral:' + k for k in DEFINITIVOS]})
    for key, (name, maximum, _, _) in MAGIA.items():
        data = dict(description=dict(text=name, color='gold' if key in DEFINITIVOS else 'aqua'),
                    supported_items='#astral:magia', weight=1, max_level=maximum,
                    min_cost=dict(base=999, per_level_above_first=0), max_cost=dict(base=999, per_level_above_first=0),
                    anvil_cost=8, slots=['mainhand'], effects={})
        if key in DEFINITIVOS:
            data['exclusive_set'] = '#astral:magia_definitivos'
        files[f'data/astral/enchantment/{key}.json'] = json.dumps(data, ensure_ascii=False)
    path = 'data/astral/function/spell/cast.mcfunction'
    cast = files[path]
    bonus = []
    for key, maximum, score, step in [('poder_arcano', 5, '#pct', 400), ('fluidez', 4, '#cdr', 5)]:
        for level in range(1, maximum + 1):
            bonus.append(f'execute if entity @s[tag=astral.encmagia] if items entity @s weapon.mainhand *[minecraft:enchantments~[{{enchantments:"astral:{key}",levels:{level}}}]] run scoreboard players add {score} astral.tmp {step * level}')
    anchor = 'scoreboard players set #mej astral.tmp 100'
    assert anchor in cast
    cast = cast.replace(anchor, '\n'.join(bonus) + '\n' + anchor)
    cast = cast.replace('tag @s add astral.caster', 'tag @s add astral.caster\nfunction astral:encmagia/inicio')
    cast = cast.replace('tag @s remove astral.caster', 'function astral:encmagia/fin\ntag @s remove astral.caster')
    files[path] = cast
    for sub in ('inicio', 'fin'):
        # El marcador síncrono identifica al caster sin interpolar nombres en macros.
        fn(f'encmagia/{sub}', f'summon marker ~ ~ ~ {{Tags:["astral.encmagia.{sub}"]}}\nkill @e[type=marker,tag=astral.encmagia.{sub},distance=0..]\n')


def delivery():
    import hashlib
    root=Path(__file__).resolve().parents[1]
    rows=[('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
          ('build/gameplay/astral_armas_especiales.sk','plugins/Skript/scripts/special_weapons.sk'),
          ('build/mesa/AstralMesa.jar','plugins/update/AstralMesa.jar'),
          ('build/mesa/config.yml','plugins/AstralMesa/config.yml (integrar las entradas mágicas)')]
    text='''# Encantamientos mágicos — privados, entrega para Claude

Implementados para bastones I–X y Varitas de Curación/Estallido. No agregan requisitos de skill para encantar.
La Guía pública no cambia. Sin resource pack nuevo ni cambios de mundos.

## Instalación pendiente (no se realizó despliegue remoto)

El servidor principal documentado es Empower; Aternos es una copia histórica. Confirmar el destino en el panel.
Instalar juntos en el reinicio diario de las **05:00**, según la instrucción vigente del dueño.
No ejecutar `reiniciopendiente`, no adelantar el reinicio ni reemplazar mundos.
El datapack y el JAR requieren un arranque completo: no alcanza `/reload` ni un cargador de plugins.
Preparar los archivos y dejar que el reinicio diario los tome. Si el panel exige apagar para reemplazar
el datapack, hacer esa sustitución durante la parada programada, antes del arranque.

| Archivo local | Destino | SHA-256 local |
|---|---|---|
'''
    for source,target in rows:
        digest=hashlib.sha256((root/source).read_bytes()).hexdigest()
        text+=f'| `{source}` | `{target}` | `{digest}` |\n'
    text+='''
Conservar una sola copia de `special_weapons.sk` (no subirlo con el nombre local `astral_armas_especiales.sk`).
Conservar el nombre del JAR instalado al ponerlo en `plugins/update/`; si tiene otro nombre/version,
usar ese nombre de archivo para reemplazarlo, sin dejar dos AstralMesa.
La versión interna del JAR es **1.5.0** (el árbol local ya indicaba 1.5.0 al iniciar esta tarea;
el plan informa que en el servidor está 1.4.1). Verificar consola al arrancar.
Integrar del config generado `encmagia.publico: false` y las ocho claves `astral:` nuevas dentro de
`nombres`, `descripciones` y los tres definitivos dentro de `costos`. Conservar todo otro ajuste remoto.
El JAR requiere AuraSkills; la extensión de radio consulta `AstralParty.members(Player)` si está instalado.

Tras el arranque: revisar carga de AstralMesa 1.5.0, datapack habilitado y ausencia de errores nuevos de Skript.
Una corrección posterior SOLO del script puede recargarse con `skript:skript reload special_weapons`;
una corrección SOLO del config con `astralmesa reload`. No reemplazan el reinicio de esta instalación.

## Privacidad y funcionamiento

`/encmagia publico` abre todo; `/encmagia privado` cierra todo. Solo administradores (`astral.mesa.admin`, OP)
pueden cambiarlo. El estado se guarda en `plugins/AstralMesa/config.yml`, clave `encmagia.publico`;
la ausencia de esa clave significa privado. No hay permiso OP implícito para probar: en privado solo ByTrainx.
El plugin pone/quita el tag `astral.encmagia` al entrar, en cada tick y al cambiar el estado.
Skript sincroniza antes de cobrar. La mesa revalida al comprar, además de filtrar la lista.
Los objetos prestados a otros jugadores no otorgan ventajas mágicas mientras esté privado.
La marca se retira al cerrar si su autor deja de estar habilitado; mientras está privado tampoco mejora
los hechizos de otro jugador. Al abrir, beneficia los hechizos de cualquiera.

Escudo: **1 maná = 1 punto de vida real = medio corazón vanilla**. No se usa el multiplicador de daño
de armas/mobs de `escala.py`: el jugador tiene su propia vida real. Absorbe 10/20/30% del daño final
tras defensa/armadura, limitado al saldo. El coste se aplica en MONITOR y un golpe cancelado no cobra.
Sifón devuelve 1/2/3% del máximo real de AuraSkills solo al acertar daño positivo, una vez por lanzamiento;
Estallido usa un contexto por explosión completa. El eco no da Sifón ni genera otro eco.
Eco conserva daño/tier/elemento calculados, lanza a los 4 ticks y usa la mirada actual. Se cancela si
el jugador sale, muere, cambia de mundo, cambia el objeto de la mano o deja de estar habilitado.
El eco abre y restaura la inmunidad temporal durante su trazado síncrono para que el golpe menor
no sea descartado por la inmunidad de la primera descarga; conserva las cancelaciones de eventos.
Bendición mantiene una sola curación activa por receptor; volver a usar la varita renueva, no acumula.
La extensión de 2 bloques solo alcanza a la party del lanzador y solo si tiene Bendición.

## Prueba del dueño, antes de abrir

En `/modo admin` y `/sala`, luego `/encmagia privado`:

```text
/loot give ByTrainx loot astral:item/baston_1
/enchant ByTrainx astral:poder_arcano 5
/enchant ByTrainx astral:fluidez 4
/enchant ByTrainx astral:sifon_mana 3
/enchant ByTrainx astral:marca_arcana 3
/enchant ByTrainx astral:sabio_arcano 5
```

Usar un bastón nuevo por cada definitivo (no pueden combinarse):

```text
/loot give ByTrainx loot astral:item/baston_1
/enchant ByTrainx astral:eco_arcano 3
/loot give ByTrainx loot astral:item/baston_1
/enchant ByTrainx astral:escudo_mana 3
/loot give ByTrainx loot astral:item/varita_curacion
/enchant ByTrainx astral:bendicion 3
/loot give ByTrainx loot astral:item/varita_estallido
/enchant ByTrainx astral:sifon_mana 3
```

Seleccionar en la mano el objeto recién entregado ANTES de cada `/enchant` (loot no selecciona ranura).
Comparar daño y recarga con/sin encantamiento. Revisar maná bajo/insuficiente, varios blancos por disparo,
marca renovada a los 4 s, eco sin cobro, varita a radio normal y party a radio+2.
Probar con un segundo jugador, incluso OP: sin ofertas mágicas ni efectos al prestar el objeto en privado.
Abrir y volver a cerrar en la prueba para verificar ambos cambios y comprobar persistencia tras el arranque.
La apertura definitiva al público requiere el OK del dueño, por separado. No anunciar lo privado en Discord.

## Texto listo para la Guía, todavía sin publicar

'''
    for key,(name,maximum,_,desc) in MAGIA.items():
        text+=f'- **{name}** (I–{maximum}): {desc}\n'
    text+='''
## Reproducción y publicación

Desde la raíz, con Python y dependencias Pillow/PyYAML disponibles:

```text
python datapack-src/build.py
python datapack-src/mesa_encantamientos.py --jdk <carpeta-bin-java25> --server <Paper-local> --packetevents <packetevents.jar>
python datapack-src/encmagia.py
python -m unittest discover -s datapack-src -p test_encmagia.py
python tools/probar_encmagia_paper.py --java <java25.exe>
```

Los ZIP/JAR y `build/gameplay/astral_armas_especiales.sk`, `build/mesa/config.yml` ya contenían cambios
locales ajenos al inicio. Se regeneraron para la entrega local, pero **no se publican completos** en el
commit de esta tarea. Las fuentes compartidas se separan por cambios de esta tarea; el resto permanece local.
Los hashes de arriba identifican la entrega local acumulada, no un paquete puro reproducido desde GitHub.
Antes de instalarla, Claude debe revisar los pendientes acumulados que ya existían. No usar un artefacto
antiguo de GitHub en lugar de los archivos locales verificados.

## Verificaciones y límites

Tests de Python de esta tarea y regresiones de bastones/fichas/armas especiales: 15 pruebas aprobadas.
El probe local comprueba filtros por jugador y custom_data, definitivos, cobro real de Skript,
Poder/Fluidez en un cast real, Sifón por lanzamiento, Marca, apertura/cierre, Escudo con saldo parcial,
Bendición/radio de party y eco real a los 4 ticks sin otro eco ni Sifón.
No sustituye la prueba visual del dueño ni una revisión de la consola remota después de instalar.

Se ejecutó también `test_mesa.py`: 2 pruebas pasan y 2 fallan **también en las salidas iniciales guardadas
antes de esta tarea**. Espera el diálogo antiguo `data/astral/dialog/receta/1.json` (ya no está en el ZIP)
y AstralDecor 1.20.0 (el JAR inicial es 1.25.1). No se cambió ese test ni la mesa de crafteo en esta tarea.
'''
    target=root/'build/deploy/encantamientos-magicos.md'
    target.write_text(text,encoding='utf8')
    print(target)


if __name__=='__main__':
    delivery()
