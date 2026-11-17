"""Genera la entrega de direccion de bastones e interruptores, sin publicar ni desplegar."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ARCHIVOS = {
    'build/runtime/AstralEfectos.jar': 'plugins/AstralEfectos.jar',
    'build/menus/DeluxeMenus/gui_menus/configuraciones.yml': 'plugins/DeluxeMenus/gui_menus/configuraciones.yml',
    'build/AstralRPG-Items.zip': 'world/datapacks/AstralRPG-Items.zip',
}


def generar():
    lines = [
        '# Bastones: direccion e interruptores de efectos — 17/11/2026', '',
        'Preparado para Empower (servidor vigente); despliegue remoto pendiente.',
        'AstralEfectos 1.2.0, Paper 26.1.2, Java 25. Conservar PacketEvents instalado.', '',
        '## Archivos exactos', '',
        '| Local (desde la raiz del repo) | Destino en el servidor | SHA-256 |',
        '|---|---|---|',
    ]
    for src, dest in ARCHIVOS.items():
        digest = hashlib.sha256((ROOT/src).read_bytes()).hexdigest()
        lines.append(f'| `{src}` | `{dest}` | `{digest}` |')
    lines += [
        '', '## Instalacion', '',
        '1. Respaldar los tres archivos actuales del servidor y verificar Java 25. Apagar el servidor.',
        '2. Reemplazar solamente los tres archivos de la tabla. El datapack es la salida completa actual del repositorio; conservar los demas datapacks y archivos del servidor.',
        '3. Iniciar: hace falta reinicio completo por el JAR y el datapack. No usar PlugMan ni recarga global de Bukkit.',
        '4. En consola: `dm reload`. Si Configuraciones ya esta registrado no cambiar config.yml; si falta, agregar `configuraciones: {file: configuraciones.yml}` dentro de `gui_menus`, conservando las otras entradas, y repetir `dm reload`.',
        '5. Revisar consola: AstralEfectos 1.2.0 activo, DeluxeMenus sin errores y funciones `astral:spell/*` cargadas. Comprobar `/configuraciones` y `/efectos` con cliente.',
        '',
        'No hay cambios de MythicMobs: no ejecutar `mm reload`. No cambian texturas ni resource pack: no subir nada a R2 ni cambiar SHA-1.',
        'Nunca sustituir mundos ni usar Worlds > Upload en la fila world. Solo se reemplaza el ZIP del datapack dentro de world/datapacks.',
        'Si se intenta instalar en la copia historica de Aternos, primero confirmar compatibilidad y disponibilidad del JAR por sus vias permitidas; esta entrega no elude sus restricciones.',
        '', '## Comportamiento y limites', '',
        '- El rayo usa raytrace desde los ojos hasta 25 bloques y conserva la salida lateral de 0,36 bloques. ItemDisplay nace con yaw/pitch cero; la transformacion aplica la direccion una sola vez.',
        '- `/efectos armaduras|armas|bastones|mascotas|jefes` alterna; agregar `on` u `off` fija. Sin argumentos lista niveles y cinco estados clickeables. Preferencias individuales persistentes en el scoreboard principal.',
        '- Objetivos: `astral.fx.armadura`, `astral.fx.armas`, `astral.fx.bastones`, `astral.fx.mascotas`, `astral.fx.jefes`. 1=true, 0=false; sin score se inicializa a 1 al entrar o al habilitar el plugin con jugadores conectados. Se releen cada 40 ticks; el comando aplica de inmediato.',
        '- El nivel Bajo/Medio/Alto y cada interruptor se combinan: true no fuerza efectos exclusivos de niveles superiores. Bajo conserva sus particulas vanilla de bastones si Bastones esta en true.',
        '- Bastones controla rayos, fuego e impactos del datapack y `/astralfx rayo`. Jefes controla `/astralfx golpe`, `estallido` y `estela`. Las tareas diferidas conservan su categoria.',
        '- Mascotas controla rastro y llamitas de mascotas evolucionadas de AstralEfectos; armaduras controla auras de set completo, armas controla rastros de armas y arcos.',
        '- MythicMobs emite particulas por su propia via, sin una categoria en los paquetes. No se filtran: permanecen poof/invocacion, end_rod, evolucion y subida de mascotas; particulas, bloques falsos y proyectiles de jefes. No se modifica su YAML.',
        '- Avisos de ataque siempre conservados: los dos `particlering` previos al SLAM (`AST_JEFE_SLAM_*`), proyectil ITEM y rastro nativo, indicadores y zonas de dano de las mazmorras (incluido Trainx). El filtro de PacketEvents sigue limitado a reducir damage_indicator; no cancela avisos.',
        '- Configuraciones usa 45 casillas: niveles 11/13/15, interruptores 29..33 y Volver 40. Fondo generico para evitar reutilizar el panel ilustrado de 27 casillas. Conserva el icono del menu principal.',
        '', '## Verificaciones', '',
        'Regresion: 29 pruebas de `test_efectos_interruptores`, `test_modelos_efectos`, `test_menu_principal`, `test_retiro_ventanas_1611` y `test_ajustes_menu_oleadas`.',
        'Ensayo reproducible con dos jugadores NMS simulados: `python tools/probar_efectos_categorias_paper.py --java <java25.exe> --base .local/testsrv`.',
        'Ejecutado en Paper 26.1.2 / Java 25: 54 comprobaciones aprobadas, `FXCFG RESULT failures=0`, sin errores de carga del datapack.',
        'Comprueba defaults, preferencias individuales, visibilidad de dibujos vivos, ausencia de creacion sin espectadores, toggle/on/argumentos invalidos, Bajo, yaw 90/pitch 30 y raytrace real. No instalar EfectosProbe.jar en remoto.',
        'Pendiente con cliente real: alineacion visual en todas las direcciones y bastones, refresco de iconos sin cerrar el menu, reconexion/reinicio conservando preferencias y particulas recibidas por dos clientes. Revisar tambien los avisos de jefes con Jefes=false.',
        'No se verifico un despliegue remoto ni una sesion de juego visual. Los logs del ensayo quedan solo en .local/.', '',
    ]
    dest = ROOT/'build/deploy/efectos-direccion-interruptores.md'
    dest.write_text('\n'.join(lines), encoding='utf8')
    return dest


if __name__ == '__main__':
    print(generar())
