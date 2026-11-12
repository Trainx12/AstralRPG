"""TAB sidebar layout and reusable progress bars (no extra expansions)."""
from math import ceil

PURPLE = "<#D6B4FF>"
TEXT = "<#F0E6FF>"
MUTED = "<#AA96C5>"
GRADIENT = "<gradient:#5268C7:#D17AFF>"
TITLE = f"{GRADIENT}<bold>✦ ASTRAL RPG ✦</bold></gradient>"
DIVIDER = f"{GRADIENT}{'─' * 16}</gradient>"


SIDEBAR_WIDTH = 160


def text_width(label):
    return sum(4 if c == ' ' or c in 'tI' else 2 if c in "il.,:;!|'" else
               5 if c in 'fk' else 6 for c in label)


def centered_location(label):
    # Approximate the existing rows' width without widening the board with blanks.
    # Trailing spaces count towards Minecraft's sidebar background width.
    gap = max(0, SIDEBAR_WIDTH - text_width(label))
    left = round(gap / 8)
    return " " * left + TEXT + label


def section(label):
    return f"{GRADIENT}<bold>{label}</bold></gradient>"


def condition(name, check, yes, no):
    return (f'  {name}:\n    conditions:\n      - "{check}"\n'
            f'    true: "{yes}"\n    false: "{no}"\n')


def score(objective):
    return f"%objective_score_{{{objective}}}%"


def ref(name):
    return f"%condition:{name}%"


def playtime_conditions():
    # Statistic: days is total; :hours and :minutes are remainders (24/60).
    # Keep zero hours after days and zero minutes, but hide leading zero units.
    minutes = "%statistic_time_played:minutes%m"
    hours = "%statistic_time_played:hours%h " + minutes
    return (condition("playtime", "%statistic_days_played%>=1",
                      "%statistic_days_played%d " + hours, ref("playtime_hours"))
            + condition("playtime_hours", "%statistic_hours_played%>=1", hours, minutes))


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


def world_labels():
    from mobs.mazmorras_data import DEFINITIONS as DUNGEONS, ARENA
    from mobs.mazmorra import MINA
    labels = {d.get('world', d['key']): d['name'] for d in DUNGEONS}
    labels.update({
        'world': 'Supervivencia', 'overworld': 'Supervivencia', 'lobby': 'Refugio Astral',
        'world_nether': 'El Nether', 'the_nether': 'El Nether',
        'world_the_end': 'El End', 'the_end': 'El End',
        'portales_astrales': 'Portales Astrales', ARENA['world']: 'Arena Astral',
        'arenas_tft': 'Arenas PvP', 'parkour_spiral': 'Parkour Espiral', 'parkour_spiral2': 'Parkour Espiral 2',
        'parkour_paradise3': 'Parkour Paradise 3', 'colorescape': 'Color Escape',
        'dropper_facil': 'Dropper', 'dropper_h4rs': 'Dropper H4rs', 'astral_bosque': 'Bosque Astral',
        MINA['world']: 'Minas Olvidadas', 'astral_minas': 'Minas Astrales',
        'bosque': 'Bosque Sombrío', 'tumba': 'Tumba del Rey de Arena',
        'cumbre': 'Cumbre Nevada', 'cumbre_hielo': 'Cumbre Helada',
        'forja': 'Volcán de la Forja', 'forja_volcano': 'Corazón de la Forja',
        'santuario': 'Santuario Celestial', 'santuario_interstellar': 'Santuario Celestial',
        'santuario_azeroth': 'Santuario Celestial',
        'world_minecraft_santuario_azeroth': 'Santuario Celestial',
        'santuario_freemap9': 'Jardines del Santuario',
        'reino': 'Reino de las Mazmorras', 'cavernas': 'Cavernas',
        'exp_desierto': 'Expedición al Desierto', 'exp_hielo': 'Expedición al Hielo',
        'exp_nieve': 'Expedición a la Nieve', 'exp_santuario': 'Expedición al Santuario',
    })
    from infinita import WORLDS as INFINITA
    labels.update({w: 'Mazmorra Infinita' for w in INFINITA})
    # Las 6 copias de cada mazmorra muestran el mismo nombre (instancias.py).
    from instancias import expand_map
    return expand_map(labels)


def location_conditions(centered=False):
    labels = world_labels()
    output = centered_location('Exploración') if centered else 'Exploración'
    prefix = "sidebar_world" if centered else "mundo"
    lines = []
    for i, (world, label) in enumerate(reversed(list(labels.items()))):
        key = prefix if i == len(labels) - 1 else f"{prefix}_{i}"
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
        f"{PURPLE}◷ {MUTED}Tiempo jugado {TEXT}{ref('playtime')}",
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
