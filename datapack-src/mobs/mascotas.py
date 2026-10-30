# -*- coding: utf-8 -*-
"""
Mascotas de AstralRPG (MythicMobs + modelos de BetterModel en creatures.py, MASCOTAS).

Como funciona:
  - Tener una mascota = tener el permiso astral.mascota.<id> (LuckPerms). Se gana matando ciertos mobs, en la mazmorra
    o en la Gacha de Monturas (PET_GANAR_<ID>).
  - /mascotas (alias en commands.yml) hace '/trigger mascota set 99'. Un controlador invisible en el lobby
    (astral_mascotas_control, en un chunk siempre cargado) mira a todos los jugadores cada 1/4 de segundo:
      99 = mostrar el menu (botones Invocar / Guardar), 1..6 = invocar esa mascota, 98 = guardar.
  - La mascota sigue a su dueno (goToOwner, tambien entre mundos) y cada 2 segundos le da sus efectos.
    Si el dueno guarda, cambia de mascota o se desconecta, la mascota desaparece.
  - Nivel: suben con los mobs que mata el dueno mientras la mascota esta afuera (1 nivel cada 25, hasta 30).
    Nivel 10 y 20: efecto extra. Nivel 30: se ve mas grande y con particulas.
  - En el lobby no aparecen (ahi no hay mobs).

Salida: ../../build/mythicmobs/{mobs,skills}/mascotas.yml y ../../build/mascotas/comandos.txt
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "build")
KILLS_POR_NIVEL = 25
NIVEL_MAX = 30

# id: numero del boton, nombre, color, como se consigue, efectos por nivel (desde 1, desde 10, desde 20)
#   efecto = (efecto de pocion, nivel 0 = I)
MASCOTAS = {
    "lobo": dict(n=1, nombre="Lobo del Bosque", color="#9AA0A8", fuente="Espantapajaros y Abejorros (raro)",
                 efectos=[[("strength", 0)], [("speed", 0)], [("resistance", 0)]],
                 texto=["Fuerza I", "+ Velocidad I", "+ Resistencia I"]),
    "cuervo": dict(n=2, nombre="Cuervo Arcano", color="#B07CFF", fuente="Gacha de Monturas",
                   efectos=[[("night_vision", 0)], [("luck", 0)], [("speed", 0)]], brillo=True,
                   texto=["Vision nocturna y marca a los mobs cercanos", "+ Suerte", "+ Velocidad I"]),
    "golem": dict(n=3, nombre="Golem de Piedra", color="#8A8A8A", fuente="Mazmorra Minas Olvidadas (raro)",
                  efectos=[[("resistance", 0)], [("regeneration", 0)], [("absorption", 0)]],
                  texto=["Resistencia I", "+ Regeneracion I", "+ 2 corazones de absorcion"]),
    "zorro": dict(n=4, nombre="Zorro Espectral", color="#BFE8FF", fuente="Yeti de las Cumbres y Caras Voladoras (raro)",
                  efectos=[[("speed", 0)], [("jump_boost", 0)], [("speed", 1)]],
                  texto=["Velocidad I", "+ Salto I", "Velocidad II"]),
    "dragon": dict(n=5, nombre="Dragoncito de Fuego", color="#E04A3A", fuente="Gacha de Monturas (epico)",
                   efectos=[[("fire_resistance", 0)], [("strength", 0)], [("haste", 0)]],
                   texto=["Resistencia al fuego", "+ Fuerza I", "+ Prisa I"]),
    "fenix": dict(n=6, nombre="Fenix", color="#FF7A2A", fuente="Gacha de Monturas (legendario)",
                  efectos=[[], [], []], rescate=[600, 420, 300],
                  texto=["Te salva con poca vida (cada 10 min)", "cada 7 min", "cada 5 min"]),
}
CONTROL = (180.5, 92, 190.5)        # debajo de la plaza del lobby (chunk siempre cargado con forceload)


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def sk(s):
    return "  - " + q(s)


def mob_yml():
    L = ["# Mascotas (generado por datapack-src/mobs/mascotas.py)", ""]
    for pid, d in MASCOTAS.items():
        n = d["n"]
        skills = [f"skill{{s=PET_MODELO_{pid}}} @self ~onSpawn", f"skill{{s=PET_MODELO_{pid}}} @self ~onLoad",
                  "setowner @NearestPlayer{r=4} ~onSpawn",
                  "remove @self ~onTimer:40 ?!hasowner", "remove @self ~onTimer:20 ?!ownerIsOnline",
                  f"skill{{s=PET_{pid}_CHEQUEO}} @owner ~onTimer:20",
                  f"skill{{s=PET_{pid}_BONUS1}} @owner ~onTimer:40",
                  f"skill{{s=PET_{pid}_BONUS2}} @owner ~onTimer:40",
                  f"skill{{s=PET_{pid}_BONUS3}} @owner ~onTimer:40",
                  f"skill{{s=PET_{pid}_EVOLUCION}} @owner ~onTimer:100",
                  "teleport @owner ~onTimer:40 ?!playerwithin{d=20}"]
        if d.get("brillo"):
            skills.append(f"skill{{s=PET_{pid}_MARCA}} @owner ~onTimer:40")
        if d.get("rescate"):
            for t in range(3):
                skills.append(f"skill{{s=PET_{pid}_RESCATE{t + 1}}} @owner ~onTimer:10 ?!hastag{{tag=pet.rescate}}")
        L += [f"astral_pet_{pid}:", "  Type: PIG", f"  Display: {q('&f' + d['nombre'])}", "  Health: 40", "  Options:",
              "    Invincible: true", "    Silent: true", "    Collidable: false", "    Despawn: false", "    Persistent: false",
              "    PreventOtherDrops: true", "    PreventItemPickup: true", "    MovementSpeed: 0.32", "    FollowRange: 48",
              "  AIGoalSelectors:", "  - clear", "  - float",
              "  - goToOwner{followrange=4;minrange=2;speed=1.5;teleporttoworld=true}", "  - lookatplayers",
              "  AITargetSelectors:", "  - clear", "  Skills:"] + [sk(x) for x in skills] + [""]
    x, y, z = CONTROL
    tim = [f"skill{{s=MASC_MENU}} @PlayersOnServer ~onTimer:5", "skill{s=MASC_GUARDAR} @PlayersOnServer ~onTimer:5",
           "skill{s=MASC_LOBBY} @PlayersOnServer ~onTimer:5", "skill{s=MASC_ARENA} @PlayersOnServer ~onTimer:5",
           "skill{s=MASC_NIVELES} @self ~onTimer:20"]
    for pid in MASCOTAS:
        tim += [f"skill{{s=MASC_INVOCAR_{pid}}} @PlayersOnServer ~onTimer:5", f"skill{{s=MASC_NOTIENE_{pid}}} @PlayersOnServer ~onTimer:5"]
    L += ["astral_mascotas_control:", "  Type: ARMOR_STAND", "  Display: 'Control de mascotas'", "  Health: 100", "  Options:",
          "    Invisible: true", "    Marker: true", "    Invincible: true", "    Silent: true", "    NoGravity: true",
          "    Despawn: false", "    Persistent: true", "    Collidable: false", "  Skills:"] + [sk(t) for t in tim] + [""]
    return "\n".join(L) + "\n"


def skill_yml():
    L = ["# Mascotas (generado por datapack-src/mobs/mascotas.py)", ""]
    p = "<target.name>"
    for pid, d in MASCOTAS.items():
        n = d["n"]
        lv = f"plv_{pid}"
        L += [f"PET_MODELO_{pid}:", "  Skills:", "  - addtag{tag=astral.seen} @self", f"  - model{{m=astral_pet_{pid}}} @self", ""]
        # chequeo: si el dueno ya no la tiene elegida, la mascota se va
        L += [f"PET_{pid}_CHEQUEO:", "  TargetConditions:", f"  - score{{o=petsel;v={n}}} false", "  Skills:",
              sk("particles{p=poof;amount=12;hS=0.4;vS=0.4} @self"), sk("remove @self"), ""]
        # efectos por nivel (duran 3 s y se renuevan cada 2 s: si la mascota se va, se terminan solos)
        for t, (efs, desde) in enumerate(zip(d["efectos"], (1, 10, 20))):
            cond = ["  TargetConditions:", f"  - score{{o={lv};v={desde}to{NIVEL_MAX}}} true"] if desde > 1 else []
            lines = [sk(f"potion{{type={e};duration=70;level={a};hasParticles=false}}") for e, a in efs]
            if not lines:
                lines = [sk("delay 1")]
            L += [f"PET_{pid}_BONUS{t + 1}:"] + cond + ["  Skills:"] + lines + [""]
        # nivel 30: mas grande y con particulas
        L += [f"PET_{pid}_EVOLUCION:", "  TargetConditions:", f"  - score{{o={lv};v={NIVEL_MAX}to{NIVEL_MAX}}} true", "  Skills:",
              sk(f"model{{m=astral_pet_{pid};s=1.35}} @self"),
              sk("particles{p=end_rod;amount=6;hS=0.4;vS=0.6;speed=0.01} @self"), ""]
        if d.get("brillo"):
            L += [f"PET_{pid}_MARCA:", "  Skills:", sk(f"skill{{s=PET_{pid}_MARCA_UNO}} @LivingInRadius{{r=14}}"), "",
                  f"PET_{pid}_MARCA_UNO:", "  TargetConditions:", "  - isplayer false", "  Skills:",
                  sk("potion{type=GLOWING;duration=60;level=0;hasParticles=false}"), ""]
        if d.get("rescate"):
            for t, cd in enumerate(d["rescate"]):
                desde, hasta = (1, 9) if t == 0 else ((10, 19) if t == 1 else (20, NIVEL_MAX))
                L += [f"PET_{pid}_RESCATE{t + 1}:", "  TargetConditions:", "  - healthpercent{p=<0.3} true",
                      f"  - score{{o={lv};v={desde}to{hasta}}} true", "  Skills:",
                      sk("addtag{tag=pet.rescate} @self"),
                      sk("potion{type=REGENERATION;duration=100;level=2}"), sk("potion{type=ABSORPTION;duration=400;level=1}"),
                      sk("potion{type=RESISTANCE;duration=60;level=2}"),
                      sk("particles{p=totem_of_undying;amount=60;hS=0.6;vS=1;speed=0.4}"), sk("sound{s=item.totem.use;v=0.8}"),
                      sk(f'message{{m="&6&lEl Fenix te salvo! &7(otra vez en {cd // 60} minutos)"}}'),
                      sk(f"delay {cd * 20}"), sk("removetag{tag=pet.rescate} @self"), ""]
        # controlador: invocar / no la tenes
        L += [f"MASC_INVOCAR_{pid}:", "  TargetConditions:", f"  - score{{o=mascota;v={n}}} true",
              f"  - haspermission{{p=astral.mascota.{pid}}} true", "  - world{w=lobby} false", "  - world{w=arena} false", "  Skills:",
              sk(f'command{{c="scoreboard players set {p} mascota 0"}}'),
              sk(f'command{{c="scoreboard players set {p} petsel {n}"}}'),
              sk("delay 25"),                                  # que la anterior alcance a irse
              sk(f"summon{{type=astral_pet_{pid};amount=1}}"),
              sk("particles{p=happy_villager;amount=20;hS=0.6;vS=0.6}"),
              sk(f'message{{m="&7Invocaste a tu &f{d["nombre"]}&7. &8(/mascotas para guardarla)"}}'), ""]
        L += [f"MASC_NOTIENE_{pid}:", "  TargetConditions:", f"  - score{{o=mascota;v={n}}} true",
              f"  - haspermission{{p=astral.mascota.{pid}}} false", "  Skills:",
              sk(f'command{{c="scoreboard players set {p} mascota 0"}}'),
              sk(f'message{{m="&cTodavia no tenes al {d["nombre"]}. &7Se consigue en: {d["fuente"]}."}}'), ""]
        # ganarla
        L += [f"PET_GANAR_{pid.upper()}:", "  TargetConditions:", "  - isplayer true",
              f"  - haspermission{{p=astral.mascota.{pid}}} false", "  Skills:",
              sk(f'command{{c="lp user {p} permission set astral.mascota.{pid} true"}}'),
              sk("sound{s=ui.toast.challenge_complete}"),
              sk(f"command{{c=\"tellraw @a ['',{{text:'(!) ',color:'gold',bold:true}},{{text:'{p}',color:'yellow'}},"
                 f"{{text:' consiguio la mascota ',color:'gray'}},{{text:'{d['nombre']}',color:'{d['color']}',bold:true}}]\"}}"),
              sk('message{m="&7Escribi &f/mascotas &7para invocarla."}'), ""]
    # menu
    L += ["MASC_MENU:", "  TargetConditions:", "  - score{o=mascota;v=99} true", "  Skills:",
          sk(f'command{{c="scoreboard players set {p} mascota 0"}}'),
          sk(f"command{{c=\"tellraw {p} ['',{{text:'✦ Mascotas ✦ ',color:'#FFB347',bold:true}},"
             f"{{text:'(una a la vez - suben de nivel con los mobs que matas)',color:'gray'}}]\"}}"),
          sk("skill{s=MASC_MENU_NINGUNA}")] + [sk(f"skill{{s=MASC_MENU_{pid}}}") for pid in MASCOTAS] + [
          sk(f"command{{c=\"tellraw {p} {{text:'[Guardar mascota]',color:'gray',click_event:{{action:'run_command',command:'/trigger mascota set 98'}}}}\"}}"),
          ""]
    L += ["MASC_MENU_NINGUNA:", "  TargetConditions:"] + [f"  - haspermission{{p=astral.mascota.{pid}}} false" for pid in MASCOTAS] + [
          "  Skills:", sk('message{m="&7Todavia no tenes mascotas. &8Algunas caen de mobs raros, otras de la mazmorra o la Gacha de Monturas."}'), ""]
    for pid, d in MASCOTAS.items():
        n = d["n"]
        L += [f"MASC_MENU_{pid}:", "  TargetConditions:", f"  - haspermission{{p=astral.mascota.{pid}}} true", "  Skills:",
              sk(f"command{{c=\"tellraw {p} ['',{{text:' {d['nombre']} ',color:'{d['color']}',bold:true}},"
                 f"{{text:'nivel ',color:'gray'}},{{score:{{name:'{p}',objective:'plv_{pid}'}},color:'yellow'}},{{text:'  ',color:'gray'}},"
                 f"{{text:'[Invocar]',color:'green',click_event:{{action:'run_command',command:'/trigger mascota set {n}'}},"
                 f"hover_event:{{action:'show_text',value:'{' / '.join(d['texto'])} (nivel 1 / 10 / 20)'}}}}]\"}}"), ""]
    L += ["MASC_GUARDAR:", "  TargetConditions:", "  - score{o=mascota;v=98} true", "  Skills:",
          sk(f'command{{c="scoreboard players set {p} mascota 0"}}'), sk(f'command{{c="scoreboard players set {p} petsel 0"}}'),
          sk('message{m="&7Guardaste tu mascota."}'), "",
          "MASC_LOBBY:", "  TargetConditions:", "  - score{o=mascota;v=1to6} true", "  - world{w=lobby} true", "  Skills:",
          sk(f'command{{c="scoreboard players set {p} mascota 0"}}'),
          sk('message{m="&cEn el lobby no pueden salir mascotas. &7Invocala en el mundo."}'), ""]
    # niveles: mobs que mato el dueno con la mascota afuera -> experiencia -> nivel
    L += ["MASC_ARENA:", "  TargetConditions:", "  - world{w=arena} true", "  Skills:",
          sk(f'command{{c="execute as {p} if score @s petsel matches 1.. run scoreboard players set @s petsel 0"}}'),
          sk(f'command{{c="execute as {p} if score @s mascota matches 1..6 run scoreboard players set @s mascota 0"}}'), ""]
    niv = []
    for pid, d in MASCOTAS.items():
        n = d["n"]
        niv += [f'command{{c="execute as @a[scores={{petsel={n},petkills=1..}}] run scoreboard players operation @s pxp_{pid} += @s petkills"}} @self',
                f'command{{c="execute as @a[scores={{petsel={n}}}] run scoreboard players operation @s plv_{pid} = @s pxp_{pid}"}} @self',
                f'command{{c="execute as @a[scores={{petsel={n}}}] run scoreboard players operation @s plv_{pid} /= #nivel petkills"}} @self',
                f'command{{c="execute as @a[scores={{petsel={n}}}] run scoreboard players add @s plv_{pid} 1"}} @self',
                f'command{{c="execute as @a[scores={{plv_{pid}={NIVEL_MAX + 1}..}}] run scoreboard players set @s plv_{pid} {NIVEL_MAX}"}} @self']
    # 'execute if entity @a' evita el aviso 'No entity was found' en la consola cuando no hay nadie conectado
    # solo se resetea a quien mato algo, y con 'execute as' (si no, a los OP les llega "Se ha cambiado la puntuacion" cada vez)
    niv += ['command{c="execute as @a[scores={petkills=1..}] run scoreboard players set @s petkills 0"} @self',
            'command{c="execute if entity @a run scoreboard players enable @a mascota"} @self']
    L += ["MASC_NIVELES:", "  Skills:"] + [sk(x) for x in niv] + [""]
    return "\n".join(L) + "\n"


def commands():
    x, y, z = CONTROL
    C = ["# Mascotas: comandos de consola (sin /). Generado por datapack-src/mobs/mascotas.py",
         "scoreboard objectives add mascota trigger",
         "scoreboard objectives add petsel dummy",
         "scoreboard objectives add petkills minecraft.custom:minecraft.mob_kills",
         f"scoreboard players set #nivel petkills {KILLS_POR_NIVEL}"]
    for pid in MASCOTAS:
        C += [f"scoreboard objectives add pxp_{pid} dummy", f"scoreboard objectives add plv_{pid} dummy"]
    C += ["# controlador (en un chunk del lobby que queda siempre cargado)",
          f"execute in minecraft:lobby run forceload add {int(x)} {int(z)}",
          "rg flag -w lobby __global__ mob-spawning allow",
          f"mm mobs spawn astral_mascotas_control 1 lobby,{x},{y},{z}",
          "rg flag -w lobby __global__ mob-spawning deny",
          "# /mascotas: agregar en commands.yml (raiz de Files), dentro de 'aliases:'",
          "#   mascotas:",
          "#   - minecraft:trigger mascota set 99",
          "# despues: reiniciar (los alias se cargan al arrancar)",
          "# para dar una mascota a mano: lp user <jugador> permission set astral.mascota.<lobo|cuervo|golem|zorro|dragon|fenix> true"]
    return "\n".join(C) + "\n"


def main():
    for sub in ("mobs", "skills"):
        os.makedirs(os.path.join(OUT, "mythicmobs", sub), exist_ok=True)
    os.makedirs(os.path.join(OUT, "mascotas"), exist_ok=True)
    open(os.path.join(OUT, "mythicmobs", "mobs", "mascotas.yml"), "w", encoding="utf-8").write(mob_yml())
    open(os.path.join(OUT, "mythicmobs", "skills", "mascotas.yml"), "w", encoding="utf-8").write(skill_yml())
    open(os.path.join(OUT, "mascotas", "comandos.txt"), "w", encoding="utf-8").write(commands())
    print(f"mascotas: {len(MASCOTAS)}")


if __name__ == "__main__":
    main()
