"""Items del Modo Historia: solo se consiguen al cobrar capitulos del Cronista.

No tienen receta, no caen de mobs ni salen en gachas: los jugadores que no hacen
la historia los consiguen comerciando (/trade, Subastas). Todos se pueden vender.
La Gomera (capitulo 1) la dispara AstralDecor (runtime/AstralGomera.java): se
estira manteniendo clic derecho y al soltar tira una piedra; los numeros salen de GOMERA.
"""
from escala import DANO, fmt

NS = "astral"
# Dano real de la piedra con la gomera bien estirada (un poco mas que un golpe de espada tier I,
# pero tarda 1 s en estirarse). Con media carga hace la mitad.
GOMERA = dict(dano=round(DANO[1] * 1.2), carga_ticks=20, recarga_ticks=10, velocidad=2.4, minima=0.25)

TRADE = ("Solo Modo Historia - se puede comerciar", "#e0b860")


def _offhand(iid, stats):
    """stats: (atributo, operacion, valor). Solo en la mano secundaria, como los talismanes."""
    return [{"type": f"minecraft:{attr}", "id": f"{NS}:{iid}_{n}", "amount": value, "operation": op, "slot": "offhand"}
            for n, (attr, op, value) in enumerate(stats)]


# capitulo -> lista de (id, cantidad). misiones.complete() los entrega.
REWARDS = {}
# id -> (capitulo, texto corto para la tarjeta del Cronista)
CARD = {}
ITEMS_HISTORIA = {}


def _define(chapter, iid, count, card, **item):
    REWARDS.setdefault(chapter, []).append((iid, count))
    CARD[iid] = (chapter, card)
    ITEMS_HISTORIA[iid] = item


_define(1, "gomera", 1, "Gomera del Refugio",
        name="Gomera del Refugio", color="#c8955a", base="minecraft:stick", model="astral:gomera",
        lore=["Arma a distancia - cualquier clase",
              "Mantene clic derecho para estirarla y solta para tirar una piedra.",
              f"Dano bien estirada: {fmt(GOMERA['dano'])} (menos si la soltas antes).",
              "No gasta municion. No se usa en el lobby."],
        gomera=True)
_define(2, "amuleto_espantapajaros", 1, "Amuleto del Espantapajaros",
        name="Amuleto del Espantapajaros", color="#d9b04a", model="astral:amuleto_espantapajaros",
        lore=["Paja trenzada de los campos. Llevalo en la mano secundaria.",
              "+8% de velocidad", "Subis escalones de 1 bloque sin saltar"],
        mods=[("movement_speed", "add_multiplied_base", 0.08), ("step_height", "add_value", 0.45)])
_define(3, "caparazon_cangrejo", 1, "Caparazon del Cangrejo",
        name="Caparazon del Cangrejo", color="#ff7a5a", model="astral:caparazon_cangrejo",
        lore=["Lo que quedo del Cangrejo de la marea. Mano secundaria.",
              "Aguantas mucho mas sin aire", "Nadas mas rapido",
              "Minas bajo el agua a velocidad normal (ideal Oceano Astral)"],
        mods=[("oxygen_bonus", "add_value", 3.0), ("water_movement_efficiency", "add_value", 0.6),
              ("submerged_mining_speed", "add_value", 0.8)])
_define(4, "brebaje_chaman", 3, "3 Brebajes del Chaman",
        name="Brebaje del Chaman", color="#6fd66f", model="astral:brebaje_chaman", stack=16,
        lore=["La receta que el Chaman usaba en el pantano.",
              "Al tomarlo: Prisa II y Vision nocturna por 8 minutos.",
              "Ideal para las Minas, el Bosque y las Cavernas."],
        drink=[("minecraft:haste", 1), ("minecraft:night_vision", 0)], seconds=480)
_define(6, "venda_momia", 1, "Venda de la Momia",
        name="Venda de la Momia", color="#e8dcb0", model="astral:venda_momia",
        lore=["Vendas viejas de la arena del desierto. Mano secundaria.",
              "Te quemas la mitad de tiempo", "+30% de resistencia al empuje"],
        mods=[("burning_time", "add_multiplied_base", -0.5), ("knockback_resistance", "add_value", 0.3)])
_define(5, "farol_capataz", 1, "Farol del Capataz",
        name="Farol del Capataz", color="#ffd24a", model="astral:farol_capataz",
        lore=["El farol que seguia prendido en las Minas Olvidadas. Mano secundaria.",
              "+25% de velocidad para romper bloques", "+1 bloque de alcance para picar"],
        mods=[("block_break_speed", "add_multiplied_base", 0.25), ("block_interaction_range", "add_value", 1.0)])
_define(7, "colmillo_yeti", 1, "Colmillo del Yeti",
        name="Colmillo del Yeti", color="#bfe8ff", model="astral:colmillo_yeti",
        lore=["Arrancado al Yeti del silencio blanco. Mano secundaria.",
              "+7% de dano", "+5% de velocidad de ataque"],
        mods=[("attack_damage", "add_multiplied_base", 0.07), ("attack_speed", "add_multiplied_base", 0.05)])
_define(8, "martillo_golem", 1, "Martillo del Golem",
        name="Martillo del Golem", color="#ff8a3d", model="astral:martillo_golem",
        lore=["El martillo del Golem de Forja, todavia caliente. Mano secundaria.",
              "+8% de dano", "+8% de vida maxima", "+5% de velocidad de ataque"],
        mods=[("attack_damage", "add_multiplied_base", 0.08), ("max_health", "add_multiplied_base", 0.08),
              ("attack_speed", "add_multiplied_base", 0.05)])
# Defensa: igual que el Talisman de Roca (build.py player/def lee ECO_DEFENSA), sin sumarse a el (misma mano).
ECO_DEFENSA = 0.05
_define(9, "eco_estrella", 1, "Eco de la Estrella",
        name="Eco de la Estrella", color="#fff08a", model="astral:eco_estrella",
        lore=["Un pedacito de la Estrella Astral encendida. Mano secundaria.",
              "+10% de vida maxima", "+5% de dano", "+5% de velocidad", "+5% de velocidad de ataque",
              f"+{int(ECO_DEFENSA * 100)}% de Defensa Astral", "+40% de resistencia al empuje",
              "+0.5 bloques de alcance para pegar"],
        mods=[("max_health", "add_multiplied_base", 0.10), ("attack_damage", "add_multiplied_base", 0.05),
              ("movement_speed", "add_multiplied_base", 0.05), ("attack_speed", "add_multiplied_base", 0.05),
              ("armor", "add_multiplied_base", ECO_DEFENSA), ("knockback_resistance", "add_value", 0.4),
              ("entity_interaction_range", "add_value", 0.5)], glint=True)

def register(add_item, txt):
    for iid, it in ITEMS_HISTORIA.items():
        lore = [txt(it["lore"][0], "gray")] + [txt(line, "green" if "mods" in it else "gray") for line in it["lore"][1:]]
        lore.append(txt(TRADE[0], TRADE[1]))
        extra = {"minecraft:max_stack_size": it.get("stack", 1)}
        data = {"type": "historia"}
        if "mods" in it:
            extra["minecraft:attribute_modifiers"] = _offhand(iid, it["mods"])
            extra["minecraft:tooltip_display"] = {"hidden_components": ["minecraft:attribute_modifiers"]}
        if it.get("gomera"):
            data["gomera"] = 1
            # Animacion de arco al mantener clic derecho; nunca se llega a "consumir" (1 hora).
            extra["minecraft:consumable"] = {"consume_seconds": 3600, "animation": "bow",
                                             "sound": "minecraft:intentionally_empty", "has_consume_particles": False}
            # Grupo propio: la recarga no bloquea los demas palos (bastones, varitas).
            extra["minecraft:use_cooldown"] = {"seconds": GOMERA["recarga_ticks"] / 20, "cooldown_group": f"{NS}:gomera"}
        if "drink" in it:
            extra["minecraft:consumable"] = {"consume_seconds": 1.6, "animation": "drink",
                                             "sound": "minecraft:entity.generic.drink", "has_consume_particles": False,
                                             "on_consume_effects": [{"type": "minecraft:apply_effects", "effects": [
                                                 {"id": e, "amplifier": amp, "duration": it["seconds"] * 20,
                                                  "show_icon": True} for e, amp in it["drink"]]}]}
            extra["minecraft:use_remainder"] = {"id": "minecraft:glass_bottle", "count": 1}
        pdc = {"auraskills:ignore_interact": True} if it.get("gomera") else None
        add_item(iid, it.get("base", "minecraft:paper"), it["name"], it["color"], lore, data,
                 extra=extra, pdc=pdc, model=it["model"], glint=it.get("glint", "mods" in it), kind="item")


def runtime_data():
    """Lo lee AstralGomera (AstralDecor) desde gomera.json."""
    return dict(GOMERA)


def card_lines(chapter):
    """Lineas extra de premio para la tarjeta del capitulo en /misiones."""
    return [f"&6+ {CARD[iid][1]} &8(solo historia)" for iid, _ in REWARDS.get(chapter, [])]
