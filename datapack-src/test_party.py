"""Contrato de generacion Party; el comportamiento en Paper se prueba por separado."""
import unittest
import yaml
import zipfile
from pathlib import Path
import party


class PartyGeneration(unittest.TestCase):
    def test_bridge(self):
        import mazmorras_copias
        text=mazmorras_copias.script()
        self.assertNotIn('command /party ',text)
        self.assertIn('function party_miembros',text)
        self.assertIn('return {_p}',text)
        self.assertIn('executable by: console',text.split('command /astralpartysync',1)[1].split('on load:')[0])
        self.assertEqual(text.count('astralpartyinternal victory'),1)

    def test_all_boards(self):
        import lobby
        data=yaml.safe_load(lobby.TAB_SECTIONS)
        for name,board in data['scoreboard']['scoreboards'].items():
            with self.subTest(board=name):
                self.assertLessEqual(len(board['lines']),15)
                self.assertTrue(any('%astral_party_titulo%' in x for x in board['lines']))
                self.assertTrue(any('%astral_party_fila3%' in x for x in board['lines']))
        footer=data['header-footer']['designs']['default']['footer']
        self.assertIn('%astral_party_tab3%',footer)

    def test_menu(self):
        import menus,menu_ui
        data=yaml.safe_load(menus.principal_menu())
        self.assertEqual(data['items']['party']['slot'],33)
        self.assertIn('[player] party<delay=3>',data['items']['party']['click_commands'])
        self.assertEqual(len(menu_ui.SLOTS),len(set(menu_ui.SLOTS)))
        self.assertNotIn(menu_ui.EFFECTS_SLOT,menu_ui.SLOTS)
        self.assertEqual(menu_ui.icon('party').size,(18,18))

    def test_real_death_infinita_guard(self):
        import infinita
        text=infinita.script()
        self.assertIn('on death of player:\n    if scoreboard tags of victim contains "astral.party.fallen":\n        stop',text)

    def test_plugin_metadata(self):
        with zipfile.ZipFile(party.ROOT/'build/runtime/AstralParty.jar') as z:
            data=yaml.safe_load(z.read('plugin.yml'))
            self.assertEqual(data['depend'],['Skript','PlaceholderAPI'])
            self.assertIn('waves=30',z.read('party.properties').decode())
            self.assertIn('boss=15',z.read('party.properties').decode())
            self.assertIn('wipe=3',z.read('party.properties').decode())
            self.assertNotIn(b'.local',z.read('party.properties'))

    def test_pack_delta(self):
        import json
        from terceros import privado
        folder=privado()/'build/entregas/party-17-11'
        report=json.loads((folder/'delta.json').read_text('utf8'))
        with zipfile.ZipFile(party.ROOT/report['base']) as base,zipfile.ZipFile(folder/'AstralRPG-Textures.zip') as target:
            for n in base.namelist():
                if n not in report['assets']:self.assertEqual(base.read(n),target.read(n),n)
            self.assertEqual(set(target.namelist())-set(base.namelist()),{n for n in report['assets'] if 'icon_party' in n})


if __name__=='__main__':unittest.main()
