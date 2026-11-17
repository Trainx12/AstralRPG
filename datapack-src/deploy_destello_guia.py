"""Entrega acumulada del 17/11: calcula hashes de archivos existentes, sin red."""
import hashlib
from pathlib import Path
from terceros import ROOT, privado


def build():
    files = [
        (ROOT/'build/runtime/AstralEfectos.jar', 'plugins/AstralEfectos.jar'),
        (ROOT/'build/runtime/AstralDecor.jar', 'plugins/AstralDecor.jar'),
        (ROOT/'build/AstralRPG-Items.zip', 'world/datapacks/AstralRPG-Items.zip'),
        (privado()/'build/entregas/crop-kettle/CropAndKettle-Astral.zip', 'world/datapacks/CropAndKettle-Astral.zip'),
        (ROOT/'build/gameplay/astral_armas_especiales.sk', 'plugins/Skript/scripts/special_weapons.sk'),
        (ROOT/'build/menus/DeluxeMenus/gui_menus/configuraciones.yml', 'plugins/DeluxeMenus/gui_menus/configuraciones.yml'),
    ]
    lines = ['# Pendiente conjunto — 17/11/2026', '',
        'Generado por `datapack-src/deploy_destello_guia.py`. Preparado localmente; sin despliegue remoto.',
        'Empower es el principal documentado; Aternos es copia. Paper 26.1.2 / Java 25.',
        'Esta tabla reemplaza los hashes/listas del 17/11 en [bastones e interruptores](efectos-direccion-interruptores.md) '
        'y [tier T6, XP y suerte](tier6-suerte.md). Conservar sus instrucciones funcionales y pendientes.',
        'Incluye las tres tandas: direccion/interruptores, T6/XP/suerte y Destello/pausa. '
        'No sustituye otras entregas anteriores que todavia no se hayan instalado.', '',
        '## Archivos actuales (SHA-256)', '', '| Local desde la raiz | Destino | SHA-256 |', '|---|---|---|']
    for path, dest in files:
        local = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
        lines.append(f'| `{local}` | `{dest}` | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |')
    lines += ['',
        'CNK permanece privado: no subir su ZIP al GitHub publico. El cambio de pausa no modifica recursos, '
        'la base FINAL ni texturas: no subir a R2 ni cambiar resource-pack-sha1.', '',
        '## Orden de instalacion y consola', '',
        '1. Cotejar esta tabla con los archivos actuales. Respaldar solo los archivos que se reemplazan y apagar el servidor.',
        '2. Reemplazar los seis archivos en los destinos indicados. Si CNK conserva el nombre original '
        '`CropAndKettle-v1.3.12-Data-Pack.zip`, reemplazar esa unica copia activa por la adaptada: '
        'no dejar ambos ZIP activos. Conservar los demas datapacks y configs.',
        '3. Mantener una sola copia activa de AstralDecor y special_weapons.sk. Conservar desactivada '
        'la copia duplicada astral_armas_especiales.sk registrada el 16/11. Nunca reemplazar mundos ni usar Worlds > Upload en world.',
        '4. Antes de iniciar, auditar las copias de TODOS los datapacks habilitados con '
        '`python tools/verificar_menu_pausa.py <Astral.zip> <CNK.zip> <otros-ZIP-o-carpetas-habilitados>`. '
        'La union en pausa y acciones rapidas debe ser solo astral:guia. '
        'Revisar tambien datapacks adicionales que no figuren en la documentacion.',
        '5. Iniciar: reinicio completo obligatorio por JAR y datapacks. No usar PlugMan ni recarga global. '
        'El arranque carga Skript; si solo se cambia despues: `skript:skript reload special_weapons` (cero errores).',
        '6. Ejecutar `dm reload`; si falta registrar Configuraciones, integrar '
        '`configuraciones: {file: configuraciones.yml}` en gui_menus sin pisar otras entradas. '
        'No hace falta mm reload ni crates reload: no cambian sus YAML.',
        '7. Consola: `datapack list enabled`; AstralDecor 1.15.0 y AstralEfectos 1.2.0 activos, '
        '216 recetas exactas, Skript sin errores. Mantener PacketEvents y el preset legacy de AuraSkills.',
        '8. Con cliente: probar Destello en lobby y survival, sin cartel de carga ni giro de camara, '
        'mana 50 por uso, bloqueo/protecciones con devolucion, estela, sonidos y velocidad. '
        'Abrir pausa: debe decir Guia Astral; no debe haber acceso nuevo a CNK/Smithed. '
        'Comprobar cocina y los interruptores, XP, suerte y requisitos segun las dos guias anteriores.', '',
        'Aternos: si se eligiera esa copia, instalar solo por sus vias permitidas y confirmar que acepta el JAR. '
        'Esta entrega no uso navegador ni APIs remotas; Claude continua la instalacion con acceso al panel.', '',
        '## Implementacion y evidencia', '',
        '- AstralDecor 1.15.0 agrega astraldecor:astralblink UUID dx dy dz, exclusivo de consola, '
        'con destino calculado desde el mundo actual y limites finitos/radio 13. Usa TeleportCause.PLUGIN '
        'y flags vigentes de velocidad/rotacion, RETAIN_PASSENGERS. Conserva la cancelacion de listeners. '
        'El listener de cosmeticos ignora viajes dentro del mismo mundo.',
        '- Skript mantiene trayectoria, costo, devolucion, estela, sonidos, velocidad y caida. '
        'Danza del Ender ya usa la API mediante Skript, sin minecraft:tp; no se cambio su giro intencional hacia el enemigo. '
        'El unico minecraft:tp de armas cortas era Destello.',
        '- CNK/Smithed se retiran de los tags de pausa y acciones rapidas despues de resolver overlays. '
        'No se agrega boton a Guia Astral ni replace:true. Cocina y archivos de dialogos originales siguen disponibles internamente.',
        '- 38 pruebas unitarias aprobadas (armas, CNK, mesa, XP, requisitos, interruptores y loops). '
        'Auditoria final de Astral+CNK+Dungeons and Taverns 5.2.0: ambos tags contienen solo astral:guia.',
        '- Paper 26.1.2 local, Skript 2.17.1: 28 comprobaciones aprobadas y BLINK RESULT failures=0. '
        'Jugador NMS simulado y captura directa en ServerGamePacketListenerImpl: en world y minecraft:lobby '
        'avanza 12 bloques, conserva mundo/rotacion/velocidad, emite posicion sin RESPAWN; '
        'cancelar devuelve mana una vez; rechaza NaN, desplazamiento excesivo y comando como jugador. '
        'Mana usa un doble de consola para contar debitos/devoluciones; no acredita el saldo real de AuraSkills. '
        'Arranque y scripts sin errores. No instalar BlinkProbe.jar en remoto.', '',
        '## Limites y pendientes concretos', '',
        '- El comando vanilla anterior TAMPOCO emitio RESPAWN en el ensayo local, en ninguno de los dos mundos. '
        'La causa del cartel remoto no esta reproducida ni confirmada. No se afirma solucion visual verificada.',
        '- No se encontro el JAR de Multiverse en las dependencias locales. Lobby se creo por WorldCreator '
        'con clave minecraft:lobby, dimension separada. Falta ensayar el conjunto remoto de plugins '
        '(Multiverse, WorldGuard, BetterModel, mascotas y demas listeners) y cliente real.',
        '- La API de Paper recibe destino absoluto; sus flags relativos conservan velocidad y rotacion. '
        'Los alias X/Y/Z/YAW/PITCH estan obsoletos y no garantizan coordenadas relativas del paquete. '
        'Confirmar ausencia de tiron de camara con cliente en survival y lobby antes de cerrar el incidente.',
        '- No hay copias locales identificadas de DnT Stronghold Overhaul 2.4.0, Incendium 5.4.12 '
        'ni Stellarity 5.4.2. Falta auditar los ZIP realmente habilitados del servidor y su orden; '
        'no se certifica la union remota solo con las copias disponibles.',
        '- Siguen pendientes los ensayos mass-open/pity y sus conteos del JAR exacto de CrazyCrates, '
        'detallados en tier6-suerte.md. No se alteraron probabilidades ni lotes en esta tarea.',
        '- Despliegue, consola remota y validacion visual pendientes de Claude con navegador.', '',
        '## Reproducir', '', 'Desde la raiz, con Python/dependencias locales:', '', '```text',
        'python datapack-src/special_weapons.py',
        'python datapack-src/crop_kettle.py --datapack-only',
        'python datapack-src/build_runtime.py --jdk <JDK25/bin> --server .local/testsrv',
        'python tools/probar_destello_paper.py --java <JDK25/bin/java.exe> --base .local/testsrv',
        'python datapack-src/deploy_destello_guia.py',
        'python tools/verificar_terceros.py', '```', '',
        '`--datapack-only` no selecciona ni reescribe el FINAL privado: usa los originales CNK conservados. '
        'Logs y plugins de ensayo permanecen exclusivamente en .local/.', '']
    target=ROOT/'build/deploy/pendiente-17-11.md'
    target.write_text('\n'.join(lines),encoding='utf8')
    print(target)


if __name__=='__main__': build()
