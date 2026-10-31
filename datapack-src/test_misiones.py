"""Regresion del menu vacio: seleccion visible para cada estado del jugador.

Ejecutar: python -m unittest test_misiones
No reemplaza la prueba visual con DeluxeMenus en Minecraft.
"""
import re
import unittest
from unittest.mock import patch

import menus
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
    return {slot: entry["key"] for slot, entry in slots.items()}


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
                    self.assertEqual(shown[13], f"historia_{state}")
                    if state == 0:
                        self.assertEqual(shown[22], "empezar")
                    else:
                        self.assertEqual(shown[22], f"cobrar_{state}" if accepted else f"aceptar_{state}")
                        self.assertEqual(shown[20], f"pausar_{state}" if accepted else f"rechazar_{state}")
        self.assertEqual(visible(items, {"aq.state": 10})[13], "historia_fin")

    def test_every_daily_has_details_accept_reject_and_claim(self):
        for did, tier, *_ in DAILIES:
            items = entries(tier + 1)
            for active, done in ((0, 0), (1, 0), (1, 1), (0, 1)):
                with self.subTest(daily=did, active=active, done=done):
                    shown = visible(items, {f"aq.d{tier}": did, f"aq.active{tier}": active, f"aq.done{tier}": done})
                    self.assertEqual(shown[13], f"diaria_{did}")
                    self.assertEqual(shown[22], f"diaria_fin_{tier}" if done else f"diaria_cobrar_{tier}" if active else f"diaria_aceptar_{tier}")
                    if not done:
                        self.assertEqual(shown[20], f"diaria_abandonar_{tier}" if active else f"diaria_rechazar_{tier}")

    def test_missing_expansion_never_leaves_blank_screen(self):
        for page in range(4):
            shown = visible(entries(page), {})
            self.assertEqual(shown[13], "sin_datos")
            self.assertEqual(shown[22], "sin_accion")
            self.assertEqual(shown[25], "actualizar")

    def test_navigation_opens_real_menus_and_details_are_readable(self):
        for page in range(5):
            items = entries(page)
            for tab in range(4):
                entry = next(e for e in items if e["key"] == f"tab_{tab}")
                self.assertIn(f"[openguimenu] {menus.mission_menu_id(tab)}", entry["extra"]["click_commands"])
            for entry in items:
                commands = entry["extra"].get("click_commands", [])
                if any("gui/details/" in cmd for cmd in commands):
                    self.assertEqual(commands[0], "[close]")
                self.assertNotIn("aq.page", entry["extra"].get("view_requirement", ""))


if __name__ == "__main__":
    unittest.main()
