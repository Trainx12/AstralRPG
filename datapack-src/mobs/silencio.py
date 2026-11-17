"""Auditoria de modelo directo o alcanzable por metaskills, sin alterar sonidos propios."""
import re


def modeled_skills(skills):
    modeled = {key for key, data in skills.items() if re.search(r'\bmodel\s*\{', str(data), re.I)}
    def references(data):
        for body in re.findall(r'\b(?:skill|randomskill)\s*\{([^}]+)\}', str(data), re.I):
            match = re.search(r'(?:^|;)\s*(?:s|skill|skills)\s*=\s*([^;]+)', body, re.I)
            if match:
                yield from (name.strip().split()[0] for name in match[1].split(','))
    while True:
        more = {key for key, data in skills.items() if set(references(data)) & modeled}
        if more <= modeled:
            break
        modeled |= more
    return modeled, references


def modeled_mobs(mobs, skills):
    modeled, references = modeled_skills(skills)
    return {key for key, data in mobs.items() if
            re.search(r'\bmodel\s*\{', str(data.get('Skills', [])), re.I) or
            set(references(data.get('Skills', []))) & modeled}


def silence(mobs, skills):
    keys = modeled_mobs(mobs, skills)
    for key in keys:
        mobs[key].setdefault('Options', {})['Silent'] = True
    return keys
