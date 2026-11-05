"""TAB sidebar layout and reusable progress bars (no extra expansions)."""
from math import ceil

PURPLE = "<#D6B4FF>"
TEXT = "<#F0E6FF>"
MUTED = "<#AA96C5>"
GRADIENT = "<gradient:#5268C7:#D17AFF>"
TITLE = f"{GRADIENT}<bold>✦ ASTRAL RPG ✦</bold></gradient>"
DIVIDER = f"{GRADIENT}{'─' * 16}</gradient>"


def centered_location(label):
    # Approximate the vanilla font widths. Dynamic stats may widen the sidebar.
    width = sum(2 if c in "il" else 4 if c in " tI" else 6 for c in label)
    return " " * max(0, (134 - width) // 8) + TEXT + label


def section(label):
    return f"{GRADIENT}<bold>{label}</bold></gradient>"


def condition(name, check, yes, no):
    return (f'  {name}:\n    conditions:\n      - "{check}"\n'
            f'    true: "{yes}"\n    false: "{no}"\n')


def score(objective):
    return f"%objective_score_{{{objective}}}%"


def ref(name):
    return f"%condition:{name}%"


def bar(filled):
    full = GRADIENT + "■" * filled + "</gradient>" if filled else ""
    return full + "<#665477>" + "■" * (8 - filled)


def meter(name, value, goal, suffix="", complete=""):
    """Return a condition reference and its YAML, clamping completed counts."""
    states = {0: bar(0) + f" {TEXT}{value}/{goal}{suffix}"}
    for filled in range(1, 8):
        threshold = ceil(goal * filled / 8)
        if threshold < goal:
            states[threshold] = bar(filled) + f" {TEXT}{value}/{goal}{suffix}"
    states[goal] = bar(8) + f" {TEXT}{goal}/{goal}{suffix}{complete}"
    return steps(name, value, list(states.items()))


def steps(name, value, states):
    expression = states[0][1]
    lines = []
    for i, (threshold, result) in enumerate(states[1:], 1):
        key = name if i == len(states) - 1 else f"{name}_{i}"
        lines.append(condition(key, f"{value}>={threshold}", result, expression))
        expression = ref(key)
    return expression, "".join(lines)


def location_conditions(centered=False):
    from mapas_exploracion import DEFINITIONS as EXPEDITIONS
    from mobs.mazmorras_data import DEFINITIONS as DUNGEONS, ARENA
    from mobs.mazmorra import MINA

    labels = {"world": "Survival", "lobby": "Spawn", "world_nether": "Nether",
              "world_the_end": "End", "portales_astrales": "Portales Astrales", ARENA["world"]: "Arena PvP",
              MINA["world"]: "Mazmorra · Minas Olvidadas", "astral_minas": "Minas Astrales"}
    labels.update({d["key"]: f'Mazmorra · {d["name"]}' for d in DUNGEONS})
    labels.update({"bosque": "Mazmorra · Bosque Sombrío", "forja": "Expedición Astral · Forja"})
    labels.update({world: "Expedición Astral · " + name for world, name in {
        "reino": "Reino", "cavernas": "Cavernas", "exp_desierto": "Desierto",
        "exp_hielo": "Cumbre", "exp_santuario": "Santuario",
    }.items() if world in EXPEDITIONS})
    output = "%world%"
    prefix = "sidebar_world" if centered else "mundo"
    lines = []
    for i, (world, label) in enumerate(reversed(list(labels.items()))):
        key = prefix if world == "world" else f"{prefix}_{i}"
        lines.append(condition(key, f"%world%={world}", centered_location(label) if centered else label, output))
        output = ref(key)
    return "".join(lines)


LOCAL_DATE = "%localtime_timezone_America/Argentina/Buenos_Aires,dd/MM/yy%"
SERVER_ROWS = [
    f"{PURPLE}◈ {TEXT}%date% {LOCAL_DATE} {PURPLE}· {TEXT}%time%",
    f"{PURPLE}AstralRPG.aternos.me",
]


def board(name, location, activity, world=None):
    rows = [
        location,
        DIVIDER,
        f"{section('♟ Jugador')} {TEXT}%player%",
        f"{PURPLE}◷ {MUTED}Tiempo jugado {TEXT}%statistic_time_played%",
        f"{section('✦ Stats')} {PURPLE}❤ {TEXT}%player_health_rounded%/%player_max_health_rounded%",
        f"{PURPLE}⛃ {MUTED}Oro {TEXT}%vault_eco_balance_formatted%  {PURPLE}⚡ {MUTED}Poder {TEXT}%auraskills_power%",
        *activity,
        *SERVER_ROWS,
    ]
    assert len(rows) <= 15
    display = f'      display-condition: "%world%={world}"\n' if world else ""
    return (f'    {name}:\n{display}      title: "{TITLE}"\n      lines:\n'
            + "".join(f'        - "{row}"\n' for row in rows))


def weekday_replacements():
    days = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
    return ('placeholder-output-replacements:\n  "%date%":\n'
            + "".join(f'    "{day}": "{day.capitalize()}"\n' for day in days)
            + f'  "{LOCAL_DATE}":\n    "{LOCAL_DATE}": ""\n')
