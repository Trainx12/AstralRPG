import json
import math
from pathlib import Path
import unittest
import zipfile

import bosque_talar as bosque
import minas
from minecraft_commands import validate
from mobs.mythic import NPCS

ROOT = Path(__file__).resolve().parents[1]


class Tanda2c(unittest.TestCase):
    def test_every_generated_function_is_vanilla(self):
        with zipfile.ZipFile(ROOT / 'build/AstralRPG-Items.zip') as pack:
            for name in pack.namelist():
                if name.endswith('.mcfunction'):
                    validate(pack.read(name).decode('utf-8'), name)
        for path in (ROOT / 'build/AstralRPG-Items').rglob('*.mcfunction'):
            validate(path.read_text(encoding='utf-8'), str(path))

    def test_rejects_plugin_commands_even_inside_execute(self):
        for root in 'mm mythicmobs lp rg dm crates tab papi sk skript eco essentials mv'.split():
            for line in (root + ' reload', 'execute as @s run ' + root + ' reload',
                         '$execute as @s run return run ' + root + ' reload'):
                with self.assertRaises(AssertionError):
                    validate(line)

    def test_magma_never_splits_and_keeps_wave_contract(self):
        paths = list((ROOT / 'build/AstralRPG-Items/data/astral/function/tanda2/forja').rglob('spawn*.mcfunction'))
        magma = [p.read_text() for p in paths if 'summon minecraft:magma_cube' in p.read_text()]
        self.assertEqual(len(magma), 4)
        for text in magma:
            for value in ('Size:0', 'minecraft:scale",base:4', 'minecraft:max_health",base:16',
                          'ad.vanilla', '.wave', 'astral:mob/roll', 'fire_resistance'):
                self.assertIn(value, text)

    def test_npcs_on_grass_facing_spawn_and_install_guards(self):
        for name, pos in (('venta', bosque.VENDOR), ('viaje', bosque.TRAVEL)):
            self.assertIn('astral_npc_bosque_' + name, NPCS)
            x, y, z, yaw = pos
            self.assertEqual(y, bosque.GROUND + 1)
            self.assertTrue(-8 <= math.floor(x) <= 119 and -8 <= math.floor(z) <= 119)
            self.assertFalse(-7 <= math.floor(x) <= -3 and 53 <= math.floor(z) <= 59)
            self.assertTrue(2 <= math.hypot(x - bosque.SPAWN[0], z - bosque.SPAWN[2]) <= 3)
            self.assertEqual(yaw, 90 if x > bosque.SPAWN[0] else -90)
        commands = bosque.install()
        self.assertLess(commands.index('mob-spawning allow'), commands.index('mm mobs spawn'))
        self.assertGreater(commands.rindex('mob-spawning deny'), commands.index('mm mobs spawn'))
        self.assertIn('minasmenu', NPCS['astral_npc_bosque_viaje'][2][0])
        self.assertIn('execute console command "spawn %name of player%"', minas.script())

    def test_wood_prices_from_shop_only_and_shared_sale(self):
        catalog = json.loads((ROOT / 'datapack-src/services_catalog.json').read_text())
        prices, missing = bosque.wood_prices()
        self.assertEqual(len(prices) + len(missing), 40)
        for material, price in prices.items():
            self.assertEqual(price, catalog[material.upper()]['min'])
            self.assertNotIn('stem', material)
            self.assertNotIn('hyphae', material)
        for material in missing:
            self.assertIn(material, bosque.install())
        script = minas.script()
        self.assertIn('am_sale_menu(arg-1)', bosque.script())
        self.assertIn('set {_price} to {-ab.price::%type of {_it}%}', script)
        self.assertIn('if lore of {_it} is not set:', script)
        self.assertEqual(bosque.script(), (ROOT / 'build/bosque/astral_bosque.sk').read_text(encoding='utf-8'))

    def test_drops_use_shared_fortune_and_single_transfer(self):
        script = bosque.script()
        for value in ("drops of event-block using player's tool", 'clear drops', 'am_give(player, {_d::*})',
                      'every 2 ticks:', 'scoreboard tags of loop-dropped item contains "ab.saw"', 'delete loop-dropped item',
                      'inventory has enough space', 'teleport loop-dropped item to {_p}'):
            self.assertIn(value, script)
        self.assertNotIn('wait ', script[script.index('every 2 ticks:'):script.index('on place:')])
        # The producer snapshots existing drops before spawning; only fresh loot gets marked.
        text = (ROOT / 'build/AstralRPG-Items/data/astral/function/tool/bosque_loot.mcfunction').read_text()
        self.assertLess(text.index('add ab.older'), text.index('loot spawn'))
        self.assertLess(text.index('loot spawn'), text.index('tag=!ab.older'))
        self.assertIn('ab_saw:1b', text)  # component prevents merging with player drops
        self.assertIn('PickupDelay:32767s', text)
        self.assertLess(script.index('give {_it} to {_p}'), script.index('delete loop-dropped item'))
        self.assertIn('remove ab.saw', script)


if __name__ == '__main__':
    unittest.main()
