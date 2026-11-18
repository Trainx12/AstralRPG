"""Regeneracion acotada de Duelos y vistas representativas, sin alterar el pack."""
from pathlib import Path
import hashlib
import duelos

ROOT = Path(__file__).resolve().parents[1]


def generate():
    import menus
    import minijuegos
    import json
    from menu_ui import decorate
    duelos.generate()
    out = ROOT / 'build/menus/DeluxeMenus/gui_menus'
    (out / 'principal.yml').write_text(menus.principal_menu(), 'utf8')
    (out / 'arenas.yml').write_text(json.dumps(decorate(minijuegos.menu_data('arena')), ensure_ascii=False, indent=2) + '\n', 'utf8')


def previews():
    from PIL import Image, ImageDraw, ImageFont
    import zipfile
    import io
    out = ROOT / 'build/previews'
    with zipfile.ZipFile(ROOT / 'build/AstralRPG-Textures.zip') as pack:
        icons = {key: Image.open(io.BytesIO(pack.read(f'assets/astral/textures/item/menu/icon_{key}.png'))).convert('RGBA').resize((26, 26), Image.Resampling.NEAREST)
                 for key in ('duelos', 'back', 'close')}
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 22)
    screens = {
        'menu': ('Duelos', {20: 'Desafiar', 22: 'Pedidos (2)', 24: 'Estadisticas', 30: 'Ranking', 32: 'Salir / cola'}),
        'jugadores': ('Desafiar · 1', {10: 'Ana · libre', 11: 'Beto · duelo', 12: 'Ceci · libre', 50: 'Siguiente'}),
        'arenas': ('Elegi la arena', {19: 'Astral · libre', 21: 'TFT1 · libre', 23: 'TFT2 · ocupada', 25: 'TFT3 · libre', 31: 'Cualquiera'}),
        'confirmar': ('Confirmar desafio', {22: 'Ana · Astral', 30: 'Enviar pedido', 32: 'Cancelar'}),
        'pedidos': ('Pedidos recibidos', {10: 'Ana · Astral', 11: 'Ceci · TFT3'}),
        'responder': ('Responder desafio', {22: 'Ana · Astral', 30: 'Aceptar', 32: 'Rechazar'}),
        'resultado': ('Resultado', {22: 'Gano Ana', 30: 'Revancha', 32: 'Volver a Arenas'}),
        'estadisticas': ('Mis estadisticas', {22: 'V: 12 / D: 3'}),
        'ranking': ('Ranking semanal', {10: '#1 Ana · 12', 11: '#2 Beto · 8', 49: 'Ver total'}),
    }
    for name, (heading, cells) in screens.items():
        im = Image.new('RGB', (1030, 510), '#18141f'); d = ImageDraw.Draw(im)
        d.text((20, 12), 'ASTRAL | ' + heading, fill='#e7c47d', font=title)
        for i in range(54):
            x, y = 20 + i % 9 * 110, 55 + i // 9 * 63
            border = i < 9 or i >= 45 or i % 9 in (0, 8)
            d.rectangle((x, y, x + 105, y + 58), fill='#26222c' if border else '#49404e', outline='#8c744c')
        for slot, label in (cells | {45: 'Volver', 53: 'Cerrar'}).items():
            x, y = 20 + slot % 9 * 110, 55 + slot // 9 * 63
            icon = 'back' if slot == 45 or label == 'Volver a Arenas' else 'close' if slot == 53 else 'duelos' if label.startswith(('Desafiar', 'Revancha', 'Astral', 'TFT')) else None
            if icon:
                im.paste(icons[icon], (x + 40, y + 3), icons[icon])
            else:
                d.rectangle((x + 42, y + 6, x + 63, y + 27), fill='#bda4dd', outline='#efd58e')
            d.text((x + 3, y + 33), label, fill='#fff0cc', font=font)
        d.text((20, 449), 'Vista representativa del inventario. Iconos existentes; reservas vanilla reemplazables.', fill='#cabbd5', font=font)
        d.text((20, 475), 'Pedidos: [Aceptar] [Rechazar] en chat · 60 s · sin apuestas ni perdida de items.', fill='#cabbd5', font=font)
        im.save(out / f'duelos_{name}.png')


def delivery():
    import re
    files = {
        'build/runtime/AstralDuelos.jar': 'plugins/AstralDuelos.jar',
        'build/duelos/astral_duelos.sk': 'plugins/Skript/scripts/astral_duelos.sk',
        'build/menus/DeluxeMenus/gui_menus/principal.yml': 'plugins/DeluxeMenus/gui_menus/principal.yml',
        'build/menus/DeluxeMenus/gui_menus/arenas.yml': 'plugins/DeluxeMenus/gui_menus/arenas.yml',
    }
    text = '''\n<!-- DUELOS-UI-START -->
## Interfaz propia de Duelos — 17/11/2026

AstralDuelos 1.0.0 + Duels Optimised 8.3. Implementacion local; despliegue pendiente de Claude.
Generadores: `python datapack-src/deploy_duelos.py`; compilar con
`python datapack-src/build_duelos.py --java <java25> --server .local/testsrv`.
No cambia el pack, datapack, AstralDecor, MythicMobs ni mundos. Conservar el ultimo FINAL.
Iconos Astral existentes; libros/tintes/orbe son reservas vanilla reemplazables con arte Gemini.
Las vistas `build/previews/duelos_*.png` son representativas, no capturas de cliente.

| Local | Destino | SHA-256 |
|---|---|---|
'''
    for local, dest in files.items():
        text += f'| `{local}` | `{dest}` | `{hashlib.sha256((ROOT/local).read_bytes()).hexdigest()}` |\n'
    text += '''
### Instalacion exacta (Empower principal; Aternos copia)

1. Esperar que no haya duelos activos; apagar. Respaldar los cuatro destinos y `plugins/Duels/config.yml`.
2. Copiar los cuatro archivos de la tabla. El Skript nuevo retira los comandos viejos;
   verificar que no exista otra copia de ese selector. Mantener `plugins/Duels-Optimised-8.3.jar`.
3. En `plugins/Duels/config.yml`, agregar a `duel.whitelisted-commands`, conservando las entradas:
   `duelos`, `astralduelos:duelos`, `desafiar`, `astralduelos:desafiar`, `duels:duel`.
   Esto permite `/duelos salir` y la rendicion oficial durante el combate.
   Conservar `request.use-own-inventory.drop-inventory-items: false`, apuestas de items/dinero
   desactivadas, `duel.prevent-item-drop: true`, `duel.prevent-item-pickup: true`.
4. Iniciar (reinicio completo requerido por JAR nuevo). No usar PlugMan ni recargar todos los plugins.
   El arranque carga Skript y menus; si luego se ajustan solo menus: `dm reload`.
   Solo retiro del selector viejo en caliente: `skript:skript reload astral_duelos`.
5. Revisar consola: Duels y AstralDuelos habilitados, Skript sin errores. Con dos cuentas survival:
   `/menu` -> Duelos y `/arenas` -> Duelos; desafiar, elegir arena, confirmar; aceptar por chat y por ventana.
   Rechazar, dejar vencer 60 s, desconectar un participante y disputar dos pedidos por una misma arena.
   Probar Cualquiera, cuenta regresiva, muerte/rendicion y regreso al lobby; comparar inventarios completos,
   resultado (tiempo incluye cuenta regresiva), corazones, revancha y rankings.
6. Estadisticas totales y ranking total vienen de Duels (cache hasta 5 min). Racha y semana (lunes,
   Argentina) comienzan con esta instalacion; persisten en `plugins/AstralDuelos/config.yml`.
   Respaldar/conservar ese archivo en futuras actualizaciones. Pedidos y resultados recientes no persisten.
   Aceptar valida disponibilidad otra vez: no reserva arenas durante los 60 s del pedido.
   El inicio usa el comando oficial de consola tras consentimiento; solo survival en world/lobby/arenas,
   respeta pedidos desactivados, cooldown, cola y jugadores ocultos. Dano PvP sigue en astral_gameplay.sk.

No se instalaron archivos remotos ni se verifico consola remota. Claude continua con navegador.
Nunca reemplazar mundos ni usar Worlds > Upload en la fila world. Aternos no permite subir un JAR
propio: si solo se dispone de Aternos, este runtime requiere un host con carga de plugins (Empower).
<!-- DUELOS-UI-END -->
'''
    proof = ROOT / '.local/duelos-ui-probe/paper.log'
    if proof.exists():
        log = proof.read_text('utf8', errors='replace')
        result = re.search(r'DUELOSUI RESULT checks=(\d+) failures=0', log)
        if result and 'DUELOSUI FAIL' not in log and 'generated an exception' not in log:
            test_jar = ROOT / '.local/duelos-ui-probe/paper/plugins/AstralDuelos.jar'
            if test_jar.read_bytes() == (ROOT / 'build/runtime/AstralDuelos.jar').read_bytes():
                checks = f'Verificacion local: {result[1]}/{result[1]} controles Paper 26.1.2 / Java 25 con Duels 8.3 y Skript 2.17.1.\n'
                checks += 'Incluye menus, pedidos, vencimiento, ocupacion, muerte, rendicion, revancha e inventarios.\n'
                checks += 'Tests de generadores: 4 de Duelos y 12 de minijuegos aprobados. Consola/cliente remotos pendientes.\n\n'
                text = text.replace('<!-- DUELOS-UI-END -->', checks + '<!-- DUELOS-UI-END -->')
    path = ROOT / 'build/deploy/pendiente-17-11.md'
    old = path.read_text('utf8')
    if '<!-- DUELOS-UI-START -->' in old:
        old, count = re.subn(r'\n<!-- DUELOS-UI-START -->.*?<!-- DUELOS-UI-END -->\n', lambda _: text, old, flags=re.S)
        if count != 1:
            raise ValueError('Seccion Duelos duplicada o incompleta: no modificar la entrega acumulada')
    else:
        old += text
    path.write_text(old, 'utf8')


if __name__ == '__main__':
    generate()
    previews()
    delivery()
