"""Entrega publica: tier T6 y mensajes/tiempo de suerte, sin assets privados."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate():
    artifacts = [('build/AstralRPG-Items.zip', 'world/datapacks/AstralRPG-Items.zip'),
                 ('build/runtime/AstralDecor.jar', 'plugins/AstralDecor.jar')]
    rows = '\n'.join(f'| `{src}` | `{dest}` | `{hashlib.sha256((ROOT/src).read_bytes()).hexdigest()}` |'
                     for src, dest in artifacts)
    content = f'''# Tier T6, XP y Manzana de la Suerte — 17/11/2026

Generado por `datapack-src/deploy_tier6_suerte.py`. Preparado, sin desplegar.
Entrega complementaria de [bastones e interruptores](efectos-direccion-interruptores.md).
Servidor vigente: Empower, Paper 26.1.2 / Java 25. Aternos es copia historica.
Esta entrega reemplaza el datapack de esa guia y agrega AstralDecor 1.14.0.

## Archivos exactos

| Local desde la raiz | Destino | SHA-256 |
|---|---|---|
{rows}

## Instalacion conjunta

1. Respaldar los archivos actuales. Apagar el servidor.
2. Instalar los dos archivos de esta tabla y los otros tres de la guia de bastones:
   AstralEfectos.jar, configuraciones.yml y special_weapons.sk, en sus destinos indicados alli.
   Mantener una sola copia activa de special_weapons.sk y una sola de AstralDecor.jar.
3. Iniciar: requiere reinicio completo por ambos JAR y el datapack. No usar PlugMan.
4. `dm reload` para el menu de Configuraciones. El arranque ya carga datapack y Skript;
   si se necesita recargar solo el script: `skript:skript reload special_weapons`.
5. Revisar consola: AstralDecor 1.14.0 habilitado, 216 recetas exactas, AstralEfectos 1.2.0,
   sin errores de carga de funciones ni scripts. No hace falta `crates reload`: sus YAML son identicos.
6. Con jugador normal: frasco sin chat; con OP y Shift: un solo mensaje por todo el stack.
   Comer dos manzanas y comprobar cerca de 10:00, porcentajes, sonido y particulas.
   Salir/reentrar y reiniciar: conservan vencimiento y maximo de racha. Vencer avisa una vez.
   Ultimos 30 segundos: barra amarilla. Confirmar caracteres y convivencia con mana en cliente real.

No cambia el resource pack: no subir ZIP de texturas, no publicar R2 ni cambiar SHA-1.
Nunca sustituir mundos ni usar Worlds > Upload en la fila world.
Solo se reemplaza el ZIP dentro de world/datapacks. No se realizo instalacion remota.

## Cambios y verificaciones

- Mundo abierto: T1-T5 conserva 4% de tier superior y 10% inferior; desde T6 usa 10%/10%.
  T10 nunca sube de T10; la tirada de subida conserva T10. Mazmorras y tier fijo sin cambios.
- XP: no-OP no recibe chat. OP recibe un total por clic, incluido Shift y mano secundaria.
- Suerte: cada manzana suma 300 segundos al tiempo restante, sin tope de juego.
  PDC astral:suerte_hasta en epoch-ms y astral:suerte_total en ms (maximo restante de la racha).
  Tiempo real sigue al desconectarse; al vencer se limpian ambos y se avisa una sola vez.
- Porcentajes y factor compartidos en gacha_balance.py, reexportados por lobby.py;
  consumibles.json dentro del JAR incluye porcentajes numericos y texto con coma decimal.
  Raro 11% → 15,3%; Epico 3,5% → 4,9%; Legendario 0,5% → 0,7%.
- Action bar Adventure con diez segmentos, verde y tiempo blanco, amarillo al final.
  Mantiene exactamente la cadencia anterior (20 ticks), sin prioridad nueva frente a AuraSkills.
  La convivencia visual y los glifos quedan pendientes de cliente real.
- Compilacion Java 25; 40 pruebas de tier/XP/escala/balance/mesa/interruptores aprobadas.
  Paper local: XPProbe, dos arranques, failures=0 en ambos. Prueba con jugador NMS y
  observacion de llamadas Adventure; no sustituye capturas ni juego remoto.
  Regenerar lobby.py deja las doce tablas CrazyCrates identicas byte a byte.

Reproducir desde raiz: `python datapack-src/build.py`,
`python datapack-src/build_runtime.py --jdk <JDK25/bin> --server <Paper-local>`,
`python datapack-src/lobby.py`, `python datapack-src/deploy_tier6_suerte.py`.
Ensayo: `python tools/probar_tanda_xp_paper.py --java <java25.exe> --base <Paper-local>`.
Desde datapack-src: `python -m unittest test_tier_probabilidad test_tanda_xp test_tanda2c test_tanda3a test_tanda3c test_balance_equipo test_mesa test_efectos_interruptores`.
Auditoria: `python tools/verificar_terceros.py`.
No instalar XPProbe.jar ni publicar .local o sus logs.

## Investigacion de lotes de 50: pendiente por falta del JAR exacto

No hay CrazyCrates en .local/testsrv ni entre los JAR locales inspeccionados.
SERVIDOR.md solo identifica "CrazyCrates (26.1.2)"; no alcanza para confirmar build/hash.
Hace falta el JAR del servidor (o version/build exactos para obtener el mismo binario).
No se afirma que mass-open ignore Weight. No se cambiaron sus pesos ni la logica de lotes/pity
sin el ensayo requerido. XPProbe usa dobles de crates/sudo: verifica routing, no distribucion real.

| Rareza | Peso normal (%) | Con suerte normalizado (%) | Esperados en 1000 normales | Esperados en 1000 con suerte |
|---|---:|---:|---:|---:|
| Comun | 60 | 55,81395 | 600 | 558,14 |
| Poco comun | 25 | 23,25581 | 250 | 232,56 |
| Raro | 11 | 15,34884 | 110 | 153,49 |
| Epico | 3,5 | 4,88372 | 35 | 48,84 |
| Legendario | 0,5 | 0,69767 | 5 | 6,98 |

Estos son valores esperados calculados, NO conteos observados. En 50: 2 Epico+Legendario
normales o 2,79 con suerte, mas lo que corresponda por garantia.
Pendiente: 1000 forceopen y 1000 mass-open con el mismo JAR instalado, sin pity en la comparacion
base, contando premios por comandos; repetir con suerte y probar pity por separado.
Comparar tambien lotes sucesivos con contadores iniciales 0, n-1 y n, para RPG n=50,
Monturas n=40 y Cosmeticos n=20, y registrar reinicios a cero ante cada Epico/Legendario.

Revision estatica del pity: menus.py adelanta el contador en t y decide la garantia de la
primera apertura con ese total; AstralDecor luego abre t-1 de la caja normal/suerte.
Los premios Epico/Legendario reinician el contador a cero en sus comandos.
Esto no equivale a evaluar/resetear el pity despues de cada premio del lote, y puede adelantar
la garantia o perder progreso posterior a un premio alto. No prueba un exceso de premios de mass-open.
Resolver el flujo junto con el ensayo del binario real antes de atribuir una causa o publicar
una correccion de probabilidades. Falta tabla de conteos antes/despues por ese bloqueo.
'''
    (ROOT/'build/deploy/tier6-suerte.md').write_text(content, encoding='utf8')


if __name__ == '__main__':
    generate()
