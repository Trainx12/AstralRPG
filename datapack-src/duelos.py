"""Interfaz Astral de Duels 8.3: arenas y retiro del selector Skript anterior.
El runtime AstralDuelos.java usa la API publica y el comando oficial duels start.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/duelos'

# Dos puntos enfrentados por arena (mundo Bukkit, x, y, z, yaw). "Astral" conserva su nombre
# para no perder estadisticas. TFT: piso comprobado en Paper local (ArenaScan, 12/11/2026),
# 12 bloques a cada lado de la llegada del menu /arenas.
DUEL_ARENAS = [
    ('Astral', 'arena', (-216.5, 73, -2381.5, -45), (-196.5, 73, -2361.5, 135)),
    ('TFT1', 'arenas_tft', (-274.5, 143, -550.5, 90), (-298.5, 143, -550.5, -90)),
    ('TFT2', 'arenas_tft', (-274.5, 139, -282.5, 90), (-298.5, 139, -282.5, -90)),
    ('TFT3', 'arenas_tft', (-274.5, 139, -14.5, 90), (-298.5, 139, -14.5, -90)),
]
TITLE = '&8Desafiar a un jugador'
# Boton en la ventana ilustrada de /arenas (fila de abajo, entre Lobby 45-47 y Cerrar 51-53).
ARENAS_BUTTON_SLOT = 49


def arenas_json():
    def pos(world, p):
        x, y, z, yaw = p
        return {'world': world, 'x': x, 'y': y, 'z': z, 'pitch': 0, 'yaw': yaw}
    return [{'name': name, 'disabled': False, 'kits': [], 'positions': {'1': pos(world, a), '2': pos(world, b)}}
            for name, world, a, b in DUEL_ARENAS]


def arenas_button():
    return dict(material='DIAMOND_SWORD', slot=ARENAS_BUTTON_SLOT, item_model='astral:menu/icon_duelos',
                display_name='&c&lDuelos',
                lore=['&7Elegi a quien desafiar y despues la arena.', '&7Nadie pierde items en un duelo.',
                      '&7Pedidos, estadisticas y ranking.'],
                click_commands=['[close]', '[player] duelos<delay=3>'])


def script():
    return "# Generado por duelos.py. La interfaz y /desafiar ahora pertenecen a AstralDuelos.jar.\n# Mantener este archivo vacio de comandos evita duplicados al actualizar.\n"


def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'astral_duelos.sk').write_text(script(), encoding='utf8')
    data = json.dumps(arenas_json(), indent=2) + '\n'
    for path in (ROOT/'datapack-src/plugin-presets/Duels--arenas.json', ROOT/'build/plugins-basicos/Duels/arenas.json'):
        path.write_text(data, encoding='utf8')


if __name__ == '__main__':
    generate()
    print(OUT/'astral_duelos.sk')
