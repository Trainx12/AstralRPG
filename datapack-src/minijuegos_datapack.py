"""Adapta el datapack de un mapa de terceros para que SOLO actue en su mundo (08/11/2026).

python minijuegos_datapack.py parkour_paradise3   ->  .local/mapas/subir/parkour_paradise3-datapack.zip

Un datapack es de todo el servidor. Este adaptador lo encierra en el mundo del mapa:
- Namespaces propios con prefijo (pp3_main, pp3_time...): dos mapas del mismo autor no chocan.
- Todos los puntajes del mapa llevan prefijo (time -> pp3_time): no pisan los del servidor.
- @a/@e/@p/@r/@n llevan predicate=<pp>_main:astral/en_mapa (estar en ese mundo).
- tick/load y cada `schedule` corren con `execute in minecraft:<mundo>`: sus setblock/fill
  no tocan el mundo principal.
- Se quitan: el filtro que bloqueaba recetas y logros de todo el servidor, `setdisplay`
  (barra lateral y lista de todos) y `team` (equipos globales, chocan con TAB).
- Logros: solo se cumplen dentro del mapa y no se anuncian en el chat.
- Se recrean los puntajes que el mapa traia guardados (scoreboard.dat), con sus valores fijos.
- <pp>_main:astral/salir limpia marcas, puntajes, efectos y modificadores al salir del mapa.

El resultado es de terceros: queda en .local (no se publica).
"""
import gzip
import json
import re
import sys
import zipfile
from pathlib import Path

from mapas import NBT

ROOT = Path(__file__).resolve().parent.parent
DATA_FORMAT = [101, 1]          # Paper 26.1.2 (igual que build.py)
MAPS = {
    # console: marcador que corre los temporizadores; su chunk tiene que estar siempre cargado.
    'parkour_paradise3': dict(source='parkour_paradise3.zip', prefix='pp3', console=(-34, 766)),
    'parkour_spiral2': dict(source='parkour_spiral2.zip', prefix='sp2', console=(0, -96)),
    # Batalla naval de 2 jugadores (TMA): todo en un mundo; sus 202 command blocks son los botones.
    'battleship': dict(source='battleship.zip', prefix='bs'),
    # Tower Defence (MLE_qwq, licencia MIT): usa su mundo normal y su End. Los jugadores de los dos
    # mundos llevan la marca td_m; sus equipos solo dan color al brillo (game.*) y se conservan.
    'towerdefence': dict(source='towerdefence.zip', prefix='td', players_tag=True, keep_teams=True,
                         dims={'overworld': 'towerdefence', 'the_end': 'towerdefence_end'}),
}
UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def text(raw):
    return raw.decode('utf-8-sig', 'replace').replace('\r\n', '\n')


class Adapter:
    def __init__(self, world, source, prefix, console=None, dims=None, players_tag=False, keep_teams=False):
        self.world, self.prefix, self.console = world, prefix, console
        self.dims = dims or {}                  # dimension del mapa -> mundo del servidor
        self.players_tag = players_tag          # mapas de varios mundos: jugadores con marca <pp>_m
        self.keep_teams = keep_teams
        self.mark = f'{prefix}_m'
        self.zip = zipfile.ZipFile(source)
        level = next(n for n in self.zip.namelist() if n.endswith('/level.dat') and n.count('/') == 1)
        self.base = level[:-len('level.dat')]
        self.dp = self.base + 'datapacks/'
        self.files = {}           # ruta dentro del datapack nuevo -> contenido (str)
        self.schedules = {}
        names = [n for n in self.zip.namelist() if n.startswith(self.dp) and not n.endswith('/')
                 and '/._' not in n and not n.endswith('.DS_Store')]   # basura de Mac
        self.sources = {n: self.zip.read(n) for n in names}
        self.moved_tags = sorted({re.sub(r'^.*?/data/minecraft/tags/[a-z_]+/', '', n)[:-5] for n in names
                                  if '/data/minecraft/tags/' in n and '/tags/function/' not in n and n.endswith('.json')})
        self.namespaces = sorted({n.split('/data/')[1].split('/')[0] for n in names if '/data/' in n} - {'minecraft'})
        self.ns = {n: f'{prefix}_{n}' for n in self.namespaces}
        self.main = self.ns.get('main', f'{prefix}_main')
        self.pred = f'{self.main}:astral/en_mapa'
        self.objectives, self.fake_scores, self.triggers = self.read_scoreboard()
        alltext = '\n'.join(text(v) for k, v in self.sources.items() if k.endswith(('.mcfunction', '.json')))
        for name, crit in re.findall(r'objectives add ([\w.+-]+) (\S+)', alltext):
            self.objectives.add(name)
            if crit == 'trigger':
                self.triggers.add(name)
        self.triggers |= set(re.findall(r'players enable \S+ ([\w.+-]+)', alltext))
        self.tags = set(re.findall(r'\btag \S+ (?:add|remove) ([\w.+-]+)', alltext))

    # ------------------------------------------------------------ datos guardados
    def read_scoreboard(self):
        objectives, scores, triggers = set(), [], set()
        try:
            raw = self.zip.read(self.base + 'data/minecraft/scoreboard.dat')
        except KeyError:
            try:
                raw = self.zip.read(self.base + 'data/scoreboard.dat')
            except KeyError:
                return objectives, scores, triggers
        data = NBT(gzip.decompress(raw), typed=True).root()[1]['data'][1]
        for _, o in data.get('Objectives', (9, []))[1]:
            objectives.add(o['Name'][1])
            crit = o.get('CriteriaName', o.get('criteria_name', (8, 'dummy')))[1]
            if crit == 'trigger':
                triggers.add(o['Name'][1])
        for _, s in data.get('PlayerScores', (9, []))[1]:
            owner = s['Name'][1]
            if UUID.match(owner):   # jugadores y entidades del autor: no se copian
                continue
            scores.append((owner, s['Objective'][1], s['Score'][1] if 'Score' in s else 0))
        return objectives, scores, triggers

    # ------------------------------------------------------------ reescritura
    def rename_ns(self, s):
        for old, new in self.ns.items():
            # Rutas que empiezan con numero (random:5_percent) si; numeros SNBT (time:5b) no.
            s = re.sub(rf'(?<![\w.:-]){re.escape(old)}:(?=(?!\d+[bsdflBSDFL]?(?![\w/]))[a-z0-9_])', new + ':', s)
        for tag in self.moved_tags:
            s = re.sub(rf'#minecraft:{re.escape(tag)}(?![\w/])', f'#{self.main}:{tag}', s)
        return s

    def obj(self, name):
        return f'{self.prefix}_{name}' if name in self.objectives else name

    def rename_objectives(self, line):
        # Puntajes: letras, numeros y _ . - + (Tower Defence usa game.data.wave.mob_count).
        o = self.obj
        line = re.sub(r'(scoreboard objectives (?:add|remove|modify) )([\w.+-]+)', lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(scoreboard players (?:set|add|remove|reset|get|enable|test) \S+ )([\w.+-]+)',
                      lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(scoreboard players display \w+ \S+ )([\w.+-]+)', lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(scoreboard players operation \S+ )([\w.+-]+)( \S+ \S+ )([\w.+-]+)',
                      lambda m: m[1] + o(m[2]) + m[3] + o(m[4]), line)
        line = re.sub(r'((?:if|unless) score \S+ )([\w.+-]+)( (?:<|<=|=|>=|>) \S+ )([\w.+-]+)',
                      lambda m: m[1] + o(m[2]) + m[3] + o(m[4]), line)
        line = re.sub(r'((?:if|unless) score \S+ )([\w.+-]+)', lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(store (?:result|success) score \S+ )([\w.+-]+)', lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(objective["\']?\s*:\s*["\'])([\w.+-]+)', lambda m: m[1] + o(m[2]), line)
        line = re.sub(r'(/?trigger )([\w.+-]+)', lambda m: m[1] + o(m[2]), line)

        def scores(m):
            parts = []
            for part in m[1].split(','):
                k, _, v = part.partition('=')
                parts.append(f'{o(k.strip())}={v}' if _ else part)
            return 'scores={' + ','.join(parts) + '}'
        return re.sub(r'scores=\{([^}]*)\}', scores, line)

    def selectors(self, line):
        """Limita cada selector al mundo donde corre el comando (siempre el del mapa).

        `distance=` solo busca en la dimension de ejecucion. Un predicate de dimension no sirve:
        en Paper con mundos de Multiverse da falso aunque el jugador este en el mapa (08/11/2026).
        Si el selector ya trae distance=, ya esta limitado a su mundo y no se toca.
        """
        out, i = [], 0
        while True:
            m = re.compile(r'@([aeprn])(?![\w])').search(line, i)
            if not m:
                out.append(line[i:])
                return ''.join(out)
            out.append(line[i:m.end()])
            i = m.end()
            if i < len(line) and line[i] == '[':
                depth, j, quote = 0, i, None
                while j < len(line):        # fin del [ ... ] respetando {}, [] y comillas
                    c = line[j]
                    if quote:
                        if c == '\\':
                            j += 1
                        elif c == quote:
                            quote = None
                    elif c in '"\'':
                        quote = c
                    elif c in '[{':
                        depth += 1
                    elif c in ']}':
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                args = line[i + 1:j]
                top = re.sub(r'\{[^{}]*\}|\[[^\[\]]*\]', '', args)   # sin nbt/scores anidados
                if self.players_tag and m[1] in 'apr':
                    args = f'tag={self.mark}' + (',' + args if args.strip() else '')
                elif not re.search(r'(^|,)\s*distance\s*=', top):
                    args = 'distance=0..' + (',' + args if args.strip() else '')
                out.append('[' + args + ']')
                i = j + 1
            elif self.players_tag and m[1] in 'apr':
                out.append(f'[tag={self.mark}]')
            else:
                out.append('[distance=0..]')

    def schedule(self, line):
        def wrap(m):
            target = m[1]
            key = re.sub(r'[^a-z0-9_]', '_', target)
            self.schedules[key] = target
            return f'schedule function {self.main}:astral/s/{key} '
        return re.sub(r'schedule function (\S+) ', wrap, line)

    def command(self, line):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            return line
        verb_part = stripped.split(' run ')[-1] if stripped.startswith(('execute', '$execute')) else stripped
        verb = verb_part.lstrip('$/').split(' ')[0]
        if (verb == 'team' and not self.keep_teams) or verb == 'difficulty' \
                or 'scoreboard objectives setdisplay' in stripped:
            return '# (AstralRPG) quitado: ' + stripped
        for old, new in self.dims.items():      # dimensiones del mapa -> mundos del servidor
            line = re.sub(rf'\b(in|dimension)\s+(?:minecraft:)?{old}\b', rf'\1 minecraft:{new}', line)
        line = self.rename_ns(line)
        line = self.rename_objectives(line)
        line = self.selectors(line)
        return self.schedule(line)

    # ------------------------------------------------------------ armado
    def build(self):
        ticks, loads = [], []
        for path, raw in sorted(self.sources.items()):
            rel = path[len(self.dp):]
            pack, _, inner = rel.partition('/')
            if not inner.startswith('data/'):
                continue                       # pack.mcmeta e imagenes de cada pack
            inner = inner[len('data/'):]
            ns, _, rest = inner.partition('/')
            if ns == 'minecraft':
                if rest in ('tags/function/tick.json', 'tags/function/load.json'):
                    values = json.loads(text(raw))['values']
                    (ticks if rest.endswith('tick.json') else loads).extend(self.rename_ns(v) for v in values)
                    continue
                if rest.startswith('tags/') and not rest.startswith('tags/function/'):
                    # Etiquetas del mapa en el espacio de Minecraft: se mudan a su namespace.
                    self.files[f'data/{self.main}/{rest}'] = text(raw)
                    continue
                raise ValueError(f'El datapack sobrescribe algo de Minecraft: {rel}')
            target = f'data/{self.ns[ns]}/{rest}'
            if rest.endswith('.mcfunction'):
                self.files[target] = '\n'.join(self.command(l) for l in text(raw).split('\n'))
            elif rest.endswith('.json'):
                content = self.rename_ns(text(raw))
                for old, new in self.dims.items():
                    content = re.sub(rf'"(?:minecraft:)?{old}"', f'"minecraft:{new}"', content)
                if rest.startswith('advancement/'):
                    content = self.advancement(content)
                else:
                    content = self.selectors(content)
                self.files[target] = content
            else:
                self.files[target] = raw
        m = self.main
        world = f'minecraft:{self.world}'
        self.files[f'data/{m}/predicate/astral/en_mapa.json'] = json.dumps(
            {'condition': 'minecraft:entity_properties', 'entity': 'this',
             'predicate': {'location': {'dimension': world}}}, indent=2)
        flag = f'{self.prefix}_astral'
        self.files[f'data/{m}/function/astral/tick.mcfunction'] = '\n'.join(
            ([f'tag @a[tag={self.mark}] remove {self.mark}']
             + [f'execute in minecraft:{w} run tag @a[distance=0..] add {self.mark}'
                for w in dict.fromkeys([self.world, *self.dims.values()])] if self.players_tag else [])
            + ['# Arranca las tareas repetidas una sola vez, cuando el mundo ya cargo (Multiverse).',
             f'execute unless score #arranco {flag} matches 1 in {world} run function {m}:astral/start']
            + [f'execute in {world} run function {f}' for f in ticks])
        load = [f'# Puntajes que el mapa traia guardados (scoreboard.dat), con prefijo {self.prefix}_.']
        for name in sorted(self.objectives):
            crit = 'trigger' if name in self.triggers else 'dummy'
            load.append(f'scoreboard objectives add {self.obj(name)} {crit}')
        for owner, objective, value in self.fake_scores:
            if ' ' not in owner:
                load.append(f'scoreboard players set {owner} {self.obj(objective)} {value}')
        if 'temp' in self.objectives:
            # Modo servidor del autor: varios jugadores, sin pasar a creativo en el entrenamiento.
            load.append(f'scoreboard players set #is_server {self.obj("temp")} 1')
        load += [f'scoreboard objectives add {flag} dummy', f'scoreboard players set #arranco {flag} 0']
        self.files[f'data/{m}/function/astral/load.mcfunction'] = '\n'.join(load)
        start = [f'scoreboard players set #arranco {flag} 1']
        if self.console:
            start.append(f'forceload add {self.console[0]} {self.console[1]}')
        start += [f'function {f}' for f in loads]
        self.files[f'data/{m}/function/astral/start.mcfunction'] = '\n'.join(start)
        for key, target in self.schedules.items():
            self.files[f'data/{m}/function/astral/s/{key}.mcfunction'] = f'execute in {world} run function {target}'
        salir = [f'tag @s remove {t}' for t in sorted(self.tags)]
        salir += [f'scoreboard players reset @s {self.obj(o)}' for o in sorted(self.objectives)]
        salir += [f'tag @s remove {self.mark}', 'effect clear @s', 'attribute @s minecraft:safe_fall_distance modifier remove spawn',
                  f'clear @s *[minecraft:custom_data~{{"hielkemaps:item":true}}]']
        self.files[f'data/{m}/function/astral/salir.mcfunction'] = '\n'.join(salir)
        self.files['data/minecraft/tags/function/tick.json'] = json.dumps({'values': [f'{m}:astral/tick']})
        self.files['data/minecraft/tags/function/load.json'] = json.dumps({'values': [f'{m}:astral/load']})
        self.files['pack.mcmeta'] = json.dumps({'pack': {
            'description': f'AstralRPG: datapack de {self.world} (solo actua en ese mundo)',
            'min_format': DATA_FORMAT, 'max_format': DATA_FORMAT}}, indent=2)
        return self.files

    def advancement(self, content):
        data = json.loads(content)
        # Sin condicion de mundo (el predicate de dimension no funciona con Multiverse): las
        # funciones de premio ya quedan limitadas por sus selectores con distance=.
        if 'display' in data:
            data['display']['announce_to_chat'] = False
        return json.dumps(data, indent=2)


def generate(world):
    cfg = MAPS[world]
    adapter = Adapter(world, ROOT / '.local/mapas' / cfg['source'], cfg['prefix'], cfg.get('console'),
                      cfg.get('dims'), cfg.get('players_tag', False), cfg.get('keep_teams', False))
    files = adapter.build()
    out = ROOT / '.local/mapas/subir' / f'{world}-datapack.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(files.items()):
            z.writestr(name, content)
    print(f'{world}: {len(files)} archivos, {len(adapter.objectives)} puntajes, '
          f'{len(adapter.schedules)} schedules -> {out}')
    return adapter


if __name__ == '__main__':
    for w in sys.argv[1:] or MAPS:
        generate(w)
