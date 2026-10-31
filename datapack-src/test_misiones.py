"""Regresion del menu vacio: seleccion visible para cada estado del jugador.

Ejecutar: python -m unittest test_misiones
No reemplaza la prueba visual con DeluxeMenus en Minecraft.
"""
import re
import unittest
from unittest.mock import patch

import menus
import misiones
from misiones import DAILIES


def entries(page):
    result = []
    original = menus.item

    def capture(key, material, slot, name, lore=(), amount=1, extra=None, glow=False):
        result.append(dict(key=key, slot=slot, extra=extra or {}, lore=lore))
        return original(key, material, slot, name, lore, amount, extra, glow)

    with patch.object(menus, "item", capture):
        menus.misiones_menu(page)
    return result


def visible(items, scores):
    slots = {}
    for entry in items:
        extra = entry["extra"]
        requirements = re.findall(
            r"input: '%objective_score_\{([^}]+)\}%'\s+output: '([^']+)'",
            extra.get("view_requirement", ""))
        if any(str(scores.get(key, "unavailable")) != value for key, value in requirements):
            continue
        slot = entry["slot"]
        if slot not in slots or extra.get("priority", 1) < slots[slot]["extra"].get("priority", 1):
            slots[slot] = entry
    return slots


class MissionMenus(unittest.TestCase):
    def test_variants_in_same_slot_have_distinct_priorities(self):
        for page in range(5):
            seen = set()
            for entry in entries(page):
                pair = (entry["slot"], entry["extra"].get("priority", 1))
                self.assertNotIn(pair, seen, (page, entry["key"], pair))
                seen.add(pair)

    def test_story_available_active_and_completed(self):
        items = entries(0)
        for state in range(10):
            for accepted in (0, 1):
                with self.subTest(state=state, accepted=accepted):
                    shown = visible(items, {"aq.state": state, "aq.accepted": accepted})
                    active = bool(state and accepted)
                    self.assertEqual(shown[22]['key'], f"historia_{state}_{'active' if active else 'available'}")
                    self.assertEqual(shown[40]['key'], f"cobrar_{state}" if active else f"aceptar_{state}")
                    self.assertEqual(shown[45]['key'], f"pausar_{state}" if active else f"rechazar_{state}")
                    self.check_click_targets(shown, 'viajero' if active else 'gui/accept', active)
        self.assertEqual(visible(items, {"aq.state": 10})[22]['key'], "historia_fin")
        self.assertEqual(visible(items, {"aq.state": 10})[40]['key'], "historia_terminada")

    def test_every_daily_has_details_accept_reject_and_claim(self):
        for did, tier, *_ in DAILIES:
            items = entries(tier + 1)
            for active, done in ((0, 0), (1, 0), (1, 1), (0, 1)):
                with self.subTest(daily=did, active=active, done=done):
                    shown = visible(items, {f"aq.d{tier}": did, f"aq.active{tier}": active, f"aq.done{tier}": done})
                    suffix = f'{did}_{active}_{done}'
                    self.assertEqual(shown[22]['key'], f"diaria_{suffix}")
                    self.assertEqual(shown[40]['key'], f"diaria_fin_{suffix}" if done else f"diaria_cobrar_{suffix}" if active else f"diaria_aceptar_{suffix}")
                    if not done:
                        self.assertEqual(shown[45]['key'], f"diaria_pausar_{suffix}" if active else f"diaria_rechazar_{suffix}")
                        self.check_click_targets(shown, f'gui/daily/claim/{tier}' if active else f'gui/daily/accept/{tier}/{did}', active)
                    else:
                        for slot in list(range(9,36)) + [38,39,40,41,42]:
                            self.assertFalse(shown[slot]['extra'].get('click_commands'))

    def check_click_targets(self, shown, function, active):
        for slot in [38,39,40,41,42] + ([] if active else list(range(9,36))):
            commands = shown[slot]['extra']['click_commands']
            self.assertIn('function astral:quest/' + function, commands[0])
            self.assertIn('[console] dm open misiones', commands[1])
        if active:
            self.assertFalse(shown[22]['extra'].get('click_commands'))
            self.assertIn('shift_left_click_commands', shown[45]['extra'])
            self.assertNotIn('function ', shown[45]['extra']['left_click_commands'][0])

    def test_missing_expansion_never_leaves_blank_screen(self):
        for page in range(4):
            shown = visible(entries(page), {})
            self.assertEqual(shown[22]['key'], "sin_datos")
            self.assertEqual(shown[40]['key'], "sin_accion")
            self.assertEqual(shown[52]['key'], "actualizar")

    def test_navigation_opens_real_menus_and_details_are_readable(self):
        for page in range(5):
            items = entries(page)
            for tab in range(4):
                entry = next(e for e in items if e["key"] == f"tab_{tab}")
                self.assertIn(f"[console] dm open {menus.mission_menu_id(tab)} %player_name%<delay=2>", entry["extra"]["click_commands"])
                self.assertNotIn('/accept', str(entry['extra']))
            for entry in items:
                commands = entry["extra"].get("click_commands", [])
                self.assertNotIn('[close]', commands)
                self.assertNotIn("aq.page", entry["extra"].get("view_requirement", ""))


class AcceptanceTransitions(unittest.TestCase):
    """Ejecuta los guards de aceptacion con scores concretos, sin premios."""
    @classmethod
    def setUpClass(cls):
        cls.files = {f'data/astral/function/{name}.mcfunction': ''
                     for name in ['load','loop/t20'] + [f'drop/elite{t}' for t in range(1,6)]}
        items = {f'{c}_1_{p}': {} for c in ('berserker','mago','arquero')
                 for p in ('helmet','chestplate','leggings','boots')}
        with patch.object(misiones, 'write_bridge'):
            misiones.generate(cls.files, items)

    def run_function(self, name, scores, effects):
        if name == 'sync':
            return
        lines = self.files[f'data/astral/function/quest/{name}.mcfunction'].splitlines()

        def command(line):
            if line.startswith('execute '):
                condition, nested = line[8:].split(' run ',1)
                match = re.fullmatch(r'(if|unless) score (@s|#today) (aq\.[a-z0-9]+) matches ([0-9.]+)', condition)
                self.assertIsNotNone(match, condition)
                mode, who, objective, interval = match.groups()
                value = scores.get((who,objective))
                low, _, high = interval.partition('..')
                valid = value is not None and (value >= int(low) if low else True) and (value <= int(high) if high else '..' in interval or value == int(low))
                return command(nested) if valid == (mode == 'if') else False
            if line.startswith('return run '):
                command(line[11:]); return True
            if line.startswith('return '): return True
            if line.startswith('function astral:quest/'):
                self.run_function(line.split('quest/')[1], scores, effects)
            elif line.startswith('scoreboard players set '):
                _,_,_,who,obj,value=line.split(); scores[who,obj]=int(value)
            elif line.startswith('scoreboard players operation '):
                _,_,_,who,obj,op,other,source=line.split()
                self.assertEqual(op,'='); scores[who,obj]=scores[other,source]
            elif line and not line.startswith('#'): effects.append(line)
            return False
        for line in lines:
            if command(line): break

    def test_accepting_again_preserves_ride_progress_and_does_not_confirm_twice(self):
        scores={('#today','aq.clock'):20000,('@s','aq.d1'):10,('@s','aq.active1'):0,
                ('@s','aq.done1'):0,('@s','aq.horse'):1200,('@s','aq.ride'):800}
        effects=[]
        self.run_function('gui/daily/accept/1/10',scores,effects)
        self.assertEqual(scores['@s','aq.active1'],1)
        self.assertEqual(scores['@s','aq.hbase'],1200)
        scores['@s','aq.horse']=1600
        self.run_function('gui/daily/accept/1/10',scores,effects)
        self.assertEqual(scores['@s','aq.hbase'],1200)
        self.assertEqual(scores['@s','aq.ride'],800)
        self.assertEqual(sum('title @s title ' in e for e in effects),1)

    def test_stale_card_and_already_paid_daily_cannot_accept(self):
        for assigned,done in [(9,0),(10,1)]:
            scores={('#today','aq.clock'):20000,('@s','aq.d1'):assigned,('@s','aq.active1'):0,('@s','aq.done1'):done}
            effects=[]
            self.run_function('gui/daily/accept/1/10',scores,effects)
            self.assertEqual(scores['@s','aq.active1'],0)
            self.assertFalse(any('title @s title ' in e for e in effects))

    def test_story_accepts_once_and_finished_story_does_not_confirm(self):
        for state in (0,4,10):
            scores={('@s','aq.state'):state,('@s','aq.accepted'):0}
            effects=[]
            self.run_function('gui/accept',scores,effects)
            self.run_function('gui/accept',scores,effects)
            self.assertEqual(scores['@s','aq.accepted'],int(state<10))
            self.assertEqual(sum('title @s title ' in e for e in effects),int(state<10))


if __name__ == "__main__":
    unittest.main()
