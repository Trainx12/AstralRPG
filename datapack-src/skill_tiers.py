"""Requisitos de XP derivados del mismo equipo que usa la Forja."""
from pathlib import Path
import re
from items import SWORDS, STAFFS, BOWS

START = '    // BEGIN GENERATED SKILL TIERS'
END = '    // END GENERATED SKILL TIERS'


def requirements():
    return {skill: [item['lvl'] for item in family] for skill, family in
            [('fighting', SWORDS), ('sorcery', STAFFS), ('archery', BOWS)]}


def java_block():
    lines = [START, '    // Generado por skill_tiers.py desde items.py/items_t6_10.py.',
             '    private static final Map<String,int[]> SKILL_TIER_LEVELS = Map.of(']
    rows = [f'        "{skill}", new int[]{{{", ".join(map(str, levels))}}}'
            for skill, levels in requirements().items()]
    return '\n'.join(lines) + '\n' + ',\n'.join(rows) + '\n    );\n' + END


def generate():
    path = Path(__file__).with_name('runtime') / 'AstralProgression.java'
    source = path.read_text(encoding='utf8')
    updated, count = re.subn(re.escape(START) + r'.*?' + re.escape(END),
                             lambda _: java_block(), source, flags=re.S)
    if count != 1:
        raise ValueError('Se esperaba un unico bloque de requisitos de skills')
    if source != updated:
        path.write_text(updated, encoding='utf8')


if __name__ == '__main__':
    generate()
