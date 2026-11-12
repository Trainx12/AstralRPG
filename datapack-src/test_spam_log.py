"""El mantenimiento de salas usa el scheduler vanilla y conserva el contexto."""
import json
import unittest
import yaml
from mobs.mazmorra import MINA, mob_yml
from mobs.mazmorras_data import catalog
from mobs.tanda2 import generate, path


class SpamLogTests(unittest.TestCase):
    def test_all_rooms_move_to_datapack_once_and_keep_other_skills(self):
        files={'data/astral/function/load.mcfunction':''}
        generate(files)
        root='data/astral/function/'
        self.assertEqual(files[root+'loop/t20.mcfunction'].count('function astral:tanda2/tick\n'),1)
        lines=files[root+'tanda2/tick.mcfunction'].splitlines()
        expected=[]
        for d in [MINA]+[d for d in catalog() if d['key']!='santuario']:
            mobs=yaml.safe_load(mob_yml(d))
            for r in d['rooms']:
                skills=mobs[f'astral_{d["key"]}_control_{r["id"]}']['Skills']
                self.assertFalse(any('/tick' in s for s in skills))
                for suffix in ('_INICIO}', '_RESET}', '_LIMPIA}'):
                    self.assertTrue(any(suffix in s and '~onTimer:' in s for s in skills))
                selector=f'@e[type=armor_stand,name={json.dumps("Control "+r["name"],ensure_ascii=False)},tag={d["key"]}.on]'
                from instancias import copias
                expected += [f'execute in minecraft:{w} as {selector} at @s run function astral:{path(d,r)}/tick' for w in copias(d['world'])]
        self.assertEqual(lines,expected)
        self.assertEqual(len(lines),len(set(lines)))


if __name__=='__main__':unittest.main()
