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
        self.assertEqual(menu_ui.icon('party').size,(72,72))   # 21/11: emblema a 4x

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

    def test_fight_rooms_cover_all_copies(self):
        import instancias, infinita, oceano_fosa
        from viajes_mazmorras import destinations
        rows = [line.split(',') for line in party.fight_rooms()]
        worlds = {r[0] for r in rows}
        expected = {instancias.bukkit(w) for d in destinations() if d.get('enabled')
                    for w in instancias.copias(instancias.DUNGEON_WORLDS[d['key']])}
        self.assertEqual(worlds, expected | set(infinita.WORLDS) | set(oceano_fosa.WORLDS))
        for d in destinations():
            if not d.get('enabled'): continue
            for w in instancias.copias(instancias.DUNGEON_WORLDS[d['key']]):
                self.assertEqual(len([r for r in rows if r[0]==instancias.bukkit(w)]),len(d['rooms']))
        self.assertEqual(len(rows),len({tuple(r) for r in rows}))
        self.assertTrue(all(len(r)==12 for r in rows))
        # Piso de pelea: debajo de la llegada y del centro, nunca dentro de la sala.
        for r in rows:
            if r[11]: self.assertLessEqual(float(r[11]),float(r[2])-8)
        self.assertEqual({r[11] for r in rows if r[0]=='bosque'},{'92'})
        with zipfile.ZipFile(party.ROOT/'build/runtime/AstralParty.jar') as z:
            self.assertEqual(z.read('fight-rooms.csv').decode().splitlines(),party.fight_rooms())

    def test_bosque_expands_real_rooms_preserving_safe_spawns(self):
        from mobs.mazmorras_data import catalog
        from mobs.salas_seguras import safe
        from mobs.mazmorra import mob_yml, skill_yml
        d=next(d for d in catalog() if d['key']=='bosque')
        self.assertEqual([r['r'] for r in d['rooms']],[108,103])
        for r in d['rooms']:
            self.assertTrue(all(safe('bosque',p) for p in r['spawn_points']))
            self.assertLessEqual(abs(r['llegada'][0]-r['centro'][0]),44)
            self.assertLessEqual(abs(r['llegada'][2]-r['centro'][2]),44)
        self.assertIn('playerwithin{d=44}',mob_yml(d))
        self.assertNotIn('playerwithin{d=108}',mob_yml(d))
        self.assertIn('PlayersInRadius{r=116}',skill_yml(d))

    def test_bosque_patch_is_only_three_wave_functions(self):
        import bosque_bordes
        import hashlib
        base=party.ROOT/'build/AstralRPG-Items.zip'
        before=hashlib.sha256(base.read_bytes()).digest()
        data=bosque_bordes.contents()
        self.assertEqual(hashlib.sha256(base.read_bytes()).digest(),before)
        self.assertEqual(len(data),4)
        for name,text in data.items():
            if name=='pack.mcmeta':continue
            self.assertTrue(name.startswith('data/astral/function/tanda2/bosque/sala1/wave'))
            self.assertIn('@a[distance=..108,gamemode=!spectator]',text)

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
