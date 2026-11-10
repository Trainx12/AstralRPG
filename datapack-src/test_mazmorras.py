"""Verifica el YAML que ejecutara MythicMobs, incluidas las llamadas de refuerzos."""
from collections import Counter
import math
import re
import unittest

import yaml
from mobs.mazmorras_data import catalog
from mobs.mazmorra import commands, mob_yml, skill_yml


class TumbaBossVictoryTests(unittest.TestCase):
    def test_absence_or_despawn_cannot_complete_boss_room(self):
        dungeon = next(d for d in catalog() if d['key'] == 'tumba')
        skills = yaml.safe_load(skill_yml(dungeon))
        mobs = yaml.safe_load(mob_yml(dungeon))
        victory = skills['TUMBA_SALA3_LIMPIA']['Conditions']
        self.assertIn('hastag{tag=tumba.jefe.derrotado} true', victory)
        self.assertIn('hastag{tag=tumba.fin} false', victory)
        timer = next(s for s in mobs['astral_tumba_control_sala3']['Skills'] if 'LIMPIA' in s)
        self.assertIn('?hastag{tag=tumba.jefe.derrotado}', timer)
        # Los husks que invoca el jefe (o los del desierto) no pueden trabar el final.
        self.assertNotIn('mobsinradius', timer)
        aviso = next(s for s in mobs['astral_tumba_momia']['Skills'] if 'tumba.jefe.derrotado' in s)
        self.assertTrue(aviso.startswith('command{') and aviso.endswith('~onDeath'))
        # El comando busca al control por su nombre visible: tienen que coincidir.
        self.assertIn("name='" + mobs['astral_tumba_control_sala3']['Display'] + "'", aviso)
        self.assertIn('?!hastag{tag=tumba.sala3.busy}', timer)
        for state in ('INICIO', 'RESET'):
            self.assertIn('removetag{tag=tumba.jefe.derrotado} @self', skills['TUMBA_SALA3_' + state]['Skills'])
        # Al ganar no se teletransporta: aparecen el cofre y el guia de Expediciones.
        fin = skills['TUMBA_SALA3_LIMPIA']['Skills']
        self.assertFalse(any('spawn <target.name>' in s for s in fin))
        self.assertTrue(any(s.startswith('summon{type=astral_tumba_cofre') for s in fin))
        self.assertTrue(any(s.startswith('summon{type=astral_tumba_guia') for s in fin))
        cofre = mobs['astral_tumba_cofre']['Skills']
        self.assertIn('command{c="dm open cofre_tumba <trigger.name>"} @self ~onInteract', cofre)
        self.assertIn('command{c="dm open expediciones <trigger.name>"} @self ~onInteract', mobs['astral_tumba_guia']['Skills'])
        self.assertTrue(any('astral_tumba_cofre' in s for s in skills['TUMBA_SALA3_RESET']['Skills']))
        start = skills['TUMBA_SALA3_INICIO']['Skills']
        self.assertLess(start.index('addtag{tag=tumba.espera} @self'), next(i for i,s in enumerate(start) if s.startswith('summon{')))
        self.assertIn('delay 10', start)



class EsperaCofreTests(unittest.TestCase):
    """Sin el false explicito, el cofre le dice 'ya cobraste' a los OP."""

    def test_every_dungeon_sets_cooldown_false_for_default_group(self):
        for dungeon in [None] + catalog():
            key = dungeon["key"] if dungeon else "mina"
            self.assertIn(f"lp group default permission set astral.{key}.cd false", commands(dungeon))


class CofreMenuTests(unittest.TestCase):
    """El cofre abre su ventana; el fragmento se guarda solo la primera vez."""

    def test_every_dungeon_spawns_a_chest_that_opens_its_window(self):
        for dungeon in [None] + catalog():
            key = dungeon["key"] if dungeon else "mina"
            mobs = yaml.safe_load(mob_yml(dungeon))
            skills = yaml.safe_load(skill_yml(dungeon))
            P = key.upper()
            self.assertIn(f'command{{c="dm open cofre_{key} <trigger.name>"}} @self ~onInteract',
                          mobs[f"astral_{key}_cofre"]["Skills"])
            final = [k for k in skills if k.endswith("_LIMPIA")][-1]
            fin = skills[final]["Skills"]
            self.assertTrue(any(s.startswith(f"summon{{type=astral_{key}_cofre") for s in fin))
            self.assertFalse(any("spawn <target.name>" in s for s in fin))
            self.assertFalse(any(f"{P}_PREMIO}}" in s for s in fin))

    def test_window_gives_fragment_only_first_time(self):
        from cofre_mazmorra import cofre_menu, PREMIOS, permiso, espera
        for dungeon in [None] + catalog():
            from mobs.mazmorra import MINA
            dungeon = dungeon or MINA
            key = dungeon["key"]
            frag = PREMIOS[key][0]
            items = cofre_menu(dungeon)["items"]
            primera, despues = items["reclamar_0"], items["reclamar_ya_0"]
            set_frag = f"[console] lp user %player_name% permission set {permiso(frag)} true"
            self.assertIn(set_frag, primera["click_commands"])
            self.assertNotIn(set_frag, despues["click_commands"])
            self.assertEqual(primera["view_requirement"]["requirements"]["r"]["type"], "!has permission")
            self.assertLess(primera["priority"], despues["priority"])
            for boton in (primera, despues):
                self.assertEqual(boton["click_commands"][0], "[close]")
                self.assertEqual(boton["click_requirement"]["requirements"]["libre"]["permission"], espera(key))
                self.assertTrue(any(f"settemp {espera(key)} true 30m" in c for c in boton["click_commands"]))
            self.assertIn("&7Solo se puede reclamar la primera vez.", items["fragmento_apagado"]["lore"])

    def test_collection_permissions_default_to_false(self):
        from cofre_mazmorra import FRAGMENTOS
        texto = commands()
        for frag, *_ in FRAGMENTOS:
            self.assertIn(f"lp group default permission set astral.fragmento.{frag} false", texto)


if __name__ == "__main__":
    unittest.main()
