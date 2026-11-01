"""Regresion de la carrera entre CLOSE de DeluxeMenus y el nuevo inventario."""
import heapq
import itertools
import re
import unittest
from pathlib import Path
from unittest.mock import patch
import menus


def run_deluxemenus_actions(commands):
    """Modela sus dos runTask: ClickActionTask y Menu.closeMenu.

    Fuente oficial: HelpChat/DeluxeMenus, DeluxeMenusConfig.onClick,
    ClickActionTask.CLOSE y Menu.closeMenu (runTask de closeInventory).
    """
    queue=[]
    sequence=itertools.count()
    view='bazar'
    def enqueue(tick,action):heapq.heappush(queue,(tick,next(sequence),action))
    for command in commands:
        delay=re.search(r'<delay=(\d+)>$',command)
        enqueue(int(delay[1]) if delay else 1,re.sub(r'<delay=\d+>$','',command))
    while queue:
        tick,_,action=heapq.heappop(queue)
        if action=='[close]':enqueue(tick+1,'closeInventory')
        elif action=='closeInventory':view=None
        elif action.startswith('[player] '):view=action[len('[player] '):]
    return view


class BazarNavigation(unittest.TestCase):
    def test_shop_npc_uses_the_same_explicit_plugin_as_bazaar(self):
        mobs=(Path(__file__).resolve().parent.parent/'build/mythicmobs/mobs/astral.yml').read_text(encoding='utf-8')
        shop=re.search(r'^astral_npc_tienda:.*?(?=^astral_npc_|\Z)',mobs,re.M|re.S)[0]
        self.assertIn('sudo <trigger.name> economyshopgui:shop',shop)
        self.assertNotIn('sudo <trigger.name> shop"',shop)

    def test_old_one_tick_open_is_closed_by_pending_close(self):
        self.assertIsNone(run_deluxemenus_actions(['[close]','[player] shop<delay=1>']))

    def test_every_card_tile_leaves_its_destination_open(self):
        entries=[]
        def capture(key,material,slot,name,lore=(),amount=1,extra=None,glow=False):
            entries.append((key,extra or {}))
            return []
        expected={'comprar':'economyshopgui:shop','vender':'astralventa','subastas':'astralmenu_subastas','ordenes':'orders'}
        seen=set()
        with patch.object(menus,'item',capture):menus.bazar_menu()
        for key,extra in entries:
            card=key.rsplit('_',1)[0]
            if card not in expected:continue
            with self.subTest(tile=key):
                self.assertEqual(run_deluxemenus_actions(extra['click_commands']),expected[card])
                seen.add(card)
        self.assertEqual(seen,set(expected))


if __name__=='__main__':unittest.main()
