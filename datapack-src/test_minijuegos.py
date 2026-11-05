"""Contratos de destinos, proteccion y preparacion privada de mapas."""
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import yaml
import minijuegos as m
import gameplay
from menus import principal_menu, comandos_menu
from mapas import NBT
from minijuegos_mapas import prepare, encode, clean_region


class MinijuegosTests(unittest.TestCase):
    def test_generated_files_match_sources_and_registry(self):
        build = m.ROOT / 'build'
        self.assertEqual((build / 'minijuegos/astral_minijuegos.sk').read_text('utf-8'), m.script())
        self.assertEqual((build / 'gameplay/astral_gameplay.sk').read_text('utf-8'), gameplay.script())
        self.assertEqual((build / 'minijuegos/despliegue.txt').read_text('utf-8'), m.deployment())
        registry = yaml.safe_load((build / 'menus/DeluxeMenus/config-gui_menus.yml').read_text('utf-8'))['gui_menus']
        for kind, name in [('parkour', 'parkour'), ('arena', 'arenas')]:
            path = build / f'menus/DeluxeMenus/gui_menus/{name}.yml'
            self.assertEqual(yaml.safe_load(path.read_text('utf-8')), m.menu_data(kind))
            self.assertEqual(registry[name]['file'], name + '.yml')
        for filename, npc in [('minijuegos.yml', 'astral_npc_parkour'), ('arena.yml', 'astral_npc_arena')]:
            self.assertIn(npc, yaml.safe_load((build / 'mythicmobs/mobs' / filename).read_text('utf-8')))

    def test_menus_have_unique_slots_and_every_destination(self):
        for kind, maps, command in [('parkour', m.PARKOURS, 'parkour'), ('arena', m.ARENAS, 'arenas')]:
            data = yaml.safe_load(json.dumps(m.menu_data(kind)))
            slots = [i['slot'] for i in data['items'].values()]
            self.assertEqual(len(slots), len(set(slots)))
            self.assertTrue(all(0 <= s < data['size'] for s in slots))
            for d in maps:
                self.assertEqual(data['items'][d['id']]['click_commands'],
                                 ['[close]', f'[player] {command} {d["id"]}<delay=3>'])
                self.assertIn(f'if {{_id}} is "{kind}.{d["id"]}":', m.script())
                self.assertIn(f'execute in minecraft:{d["world"]} run minecraft:tp', m.script())

    def test_no_free_player_text_in_console_commands(self):
        for line in m.script().splitlines():
            if 'execute console command' in line:
                for forbidden in ('arg-', '%{_id}%', '%{_w}%', '%{_l}%'):
                    self.assertNotIn(forbidden, line)
        self.assertIn('if player is not op:', m.script())
        for kind, d in m.definitions():
            self.assertIn(f'set {{astral.punto::{kind}.{d["id"]}}} to location of player', m.script())
            self.assertIn(f'if name of world of player is not "{d["world"]}"', m.script())

    def test_future_worlds_in_pvp_and_grapple_guards(self):
        m.ARENAS.append(dict(m.ARENAS[0], id='test', world='arena_futura'))
        m.PARKOURS.append(dict(m.PARKOURS[0], id='test', world='parkour_futuro'))
        try:
            self.assertIn('"arena_futura"', gameplay.pvp())
            guard = gameplay.script().split('function astral_dungeon', 1)[1].split('function astral_builder', 1)[0]
            self.assertIn('"parkour_futuro"', guard)
            self.assertNotIn('"arena_futura"', guard)
        finally:
            m.ARENAS.pop()
            m.PARKOURS.pop()

    def test_classic_random_arrivals(self):
        from mobs.mazmorras_data import ARENA
        self.assertEqual([p[:3] for p in m.ARENAS[0]['spawn_points']], ARENA['spawn_points'])
        self.assertIn('random integer between 1 and 25', m.script())

    def test_tft_verified_arrivals_and_optional_override(self):
        script = m.script()
        travel = script.split('function astral_minijuego_ir', 1)[1].split('command /parkour', 1)[0]
        expected = {'tft1': (-286.5, 143, -550.5, 0, 0),
                    'tft2': (-286.5, 139, -282.5, 0, 0),
                    'tft3': (-286.5, 139, -14.5, 0, 0)}
        tft = {d['id']: d for d in m.ARENAS if d['id'].startswith('tft')}
        self.assertEqual(set(tft), set(expected))
        for key, arrival in expected.items():
            d = tft[key]
            self.assertFalse(d.get('needs_point', False))
            self.assertEqual(d['arrival'], arrival)
            self.assertEqual(d['rescue_y'], 120)
            branch = travel.split(f'if {{_id}} is "arena.{key}":', 1)[1].split('    if {_id}', 1)[0]
            fallback = ', '.join(map(str, arrival[:3])) + ', world "arenas_tft", 0, 0'
            self.assertIn(f'set {{_l}} to {{astral.punto::arena.{key}}}\n'
                          '        if {_l} is not set:\n'
                          f'            set {{_l}} to location({fallback})', branch)
            self.assertIn('execute in minecraft:arenas_tft run minecraft:tp', branch)
            self.assertNotIn('Requiere una llegada', str(m.menu_data('arena')['items'][key]))
        self.assertNotIn('Esta arena necesita que un OP revise', script)
        rescue = script.split('every 10 ticks:', 1)[1]
        for key in expected:
            self.assertIn(f'if {{_id}} is "arena.{key}":\n'
                          '                if y-coordinate of loop-player is less than 120:\n'
                          '                    if gamemode of loop-player is survival or adventure:\n'
                          '                        astral_minijuego_ir(loop-player, {_id})', rescue)

    def test_principal_commands_and_npc(self):
        principal = yaml.safe_load(principal_menu())['items']
        commands = yaml.safe_load(comandos_menu())['items']
        for key in ('parkour', 'arenas'):
            self.assertIn('[openguimenu] ' + key, principal[key]['click_commands'])
            self.assertIn('cmd_' + key, commands)
        self.assertEqual(len({i['slot'] for i in commands.values()}), len(commands))
        self.assertIn('dm open parkour', str(yaml.safe_load(m.npc('parkour'))))

    def test_mode_rescue_and_death_protection(self):
        script = m.script()
        self.assertIn('set gamemode of {_p} to adventure', script)
        self.assertIn('set gamemode of {_p} to {astral.minijuegos.mode::%{_u}%}', script)
        self.assertIn('if gamemode of {_p} is creative:', script)
        for kind, d in m.definitions():
            self.assertIn(f'less than {d["rescue_y"]}', script)
            death_guard = gameplay.script().split('on death of player:', 1)[1].split('on jump:', 1)[0]
            self.assertIn('"' + d['world'] + '"', death_guard)

    def test_private_zip_whitelist_and_old_blocks_sanitized(self):
        blocks = bytearray(4096)
        blocks[:5] = bytes([137, 210, 211, 52, 1])
        tree = (10, {'Level': (10, {'Sections': (9, [(10, {'Y': (1, 0), 'Blocks': (7, bytes(blocks))})]),
                                    'Entities': (9, [(10, {'id': (8, 'commandblock_minecart')})])})})
        import zlib, struct
        payload = zlib.compress(encode(tree))
        record = struct.pack('>I', len(payload) + 1) + b'\x02' + payload
        raw = b'\x00\x00\x02\x01' + bytes(8192 - 4) + record.ljust(4096, b'\0')
        cleaned = clean_region(raw)
        length = int.from_bytes(cleaned[8192:8196], 'big')
        chunk = NBT(zlib.decompress(cleaned[8197:8196 + length])).root()['Level']
        self.assertEqual(chunk['Sections'][0]['Blocks'][:5], bytes([98, 98, 98, 98, 1]))
        self.assertNotIn('Entities', chunk)
        with tempfile.TemporaryDirectory(dir=m.ROOT / '.local') as tmp:
            folder = Path(tmp)
            source, dest = folder / 'source.zip', folder / 'clean.zip'
            level = (10, {'Data': (10, {'Player': (10, {}), 'LevelName': (8, 'original')})})
            with zipfile.ZipFile(source, 'w') as z:
                z.writestr('Original/level.dat', gzip.compress(encode(level)))
                z.writestr('Original/region/r.0.0.mca', raw)
                for path in ('../evil.html', 'Original/playerdata/private.dat', 'Original/datapacks/code.zip', 'a.schematic'):
                    z.writestr(path, b'ignored')
            prepare(source, dest, 'nuevo')
            with zipfile.ZipFile(dest) as z:
                self.assertEqual(set(z.namelist()), {'nuevo/level.dat', 'nuevo/region/r.0.0.mca'})
                data = NBT(gzip.decompress(z.read('nuevo/level.dat'))).root()['Data']
                self.assertNotIn('Player', data)
                self.assertEqual(data['LevelName'], 'nuevo')


if __name__ == '__main__':
    unittest.main()
