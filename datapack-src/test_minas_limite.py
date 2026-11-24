"""Contrato de generacion y limites de alcance; el comportamiento se ensaya en Paper."""
from pathlib import Path
import unittest
import zipfile
import minas

ROOT = Path(__file__).resolve().parents[1]


class MinasLimite(unittest.TestCase):
    def test_generated_script_is_current(self):
        self.assertEqual(minas.script(), (ROOT / 'build/minas/Skript/scripts/astral_minas.sk').read_text('utf8'))

    def test_all_mining_paths_use_provenance_delivery(self):
        script = minas.script()
        give = script.split('function am_give(', 1)[1].split('function am_drill(', 1)[0]
        self.assertIn('astral mine give loop-value to {_p}', give)
        self.assertIn('am_give({_p}, {_d::*})', script)
        self.assertIn('am_give(player, {_d::*})', script)
        self.assertIn('astral.ofi_minero', script)
        self.assertIn('if name of {_it} is not set:', script)
        self.assertIn('if lore of {_it} is not set:', script)

    def test_private_default_and_cleanup_contract(self):
        java = (ROOT / 'datapack-src/runtime/AstralMinasLimite.java').read_text('utf8')
        for text in ('addDefault("publico", false)', 'equalsIgnoreCase("ByTrainx")', 'saveConfig()',
                     'clear(p.getEnderChest())', 'p.setItemOnCursor(null)', 'clear(p.getInventory())',
                     'InventoryType.CRAFTING', 'PlayerChangedWorldEvent', 'PlayerJoinEvent',
                     'EntityPickupItemEvent', 'InventoryMoveItemEvent', 'InventoryPickupItemEvent',
                     'minas_origen', 'PersistentDataType.BYTE', 'Ningún mineral de las Minas Astrales',
                     '"astral.minas.admin"'):
            self.assertIn(text, java)
        self.assertNotIn('setCustomModelData', java)
        self.assertNotIn('setDisplayName', java)
        self.assertNotIn('setLore', java)

    def test_distribution_has_only_plugin_code(self):
        with zipfile.ZipFile(ROOT / 'build/minas/AstralMinasLimite.jar') as jar:
            self.assertTrue(all(n == 'plugin.yml' or n.startswith('astral/AstralMinasLimite') and n.endswith('.class') for n in jar.namelist()))
            self.assertIn('depend: [Skript]', jar.read('plugin.yml').decode())


if __name__ == '__main__':
    unittest.main()
