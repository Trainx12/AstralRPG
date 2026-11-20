"""Pasar el terreno del lobby de una propuesta YA PEGADA a otra nueva.

Calcula las dos propuestas sobre el lobby de ANTES del primer pegado y compara con
el lobby descargado HOY. Solo cambia posiciones donde el server sigue igual a lo que
dejo el pegado viejo (si alguien construyo encima, esa posicion se respeta y se
informa). Los cubos se pegan SIN -a: el aire nuevo borra la roca que sobra.

  python datapack-src/lobby_terreno_cambio.py --antes .local/lobby/actual-18-11/region \
     --hoy .local/lobby/actual-19-11/region --original 'C:/Users/Trainx/Downloads/Parrot Spawn.zip' \
     --vieja .local/lobby/config-v4.json --nueva .local/lobby/config-v5.json --out .local/lobby/cambio-v5
"""
import argparse, json, hashlib
from pathlib import Path
import lobby_terreno as lt

NATURAL={'air','cave_air','bamboo','jungle_leaves','grass_block','dirt','moss_block'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for a in ('antes','hoy','original','nueva','out'):
        p.add_argument('--'+a,type=Path,required=True)
    # Varias: si un pegado quedo a medias, el server mezcla versiones.
    p.add_argument('--vieja',type=Path,nargs='+',required=True)
    p.add_argument('--esperados',type=int,help='Cambios de la propuesta vieja (control)')
    args=p.parse_args();out=lt.private(args.out)
    if out.exists():raise ValueError('Usar salida nueva')
    old_cfgs=[json.loads(v.read_text(encoding='utf-8-sig')) for v in args.vieja]
    new_cfg=json.loads(args.nueva.read_text(encoding='utf-8-sig'))
    if any(c['bounds']!=new_cfg['bounds'] for c in old_cfgs):raise ValueError('Bounds distintos')
    bounds=new_cfg['bounds']
    pre=lt.World.load(args.antes,bounds);cur=lt.World.load(args.hoy,bounds)
    original=lt.World.load(args.original,bounds)
    olds=[lt.propose(pre,original,bounds,c)[0] for c in old_cfgs]
    old=olds[0]
    new,report=lt.propose(pre,original,bounds,new_cfg)
    if args.esperados and len(old)!=args.esperados:
        raise ValueError(f'La propuesta vieja no se reproduce: {len(old)} != {args.esperados}')
    delta={};conflicts=[];not_pasted=0
    natural=lambda s:lt.base(s) in NATURAL
    # Terreno = cualquier material que usan las propuestas (roca, piel de abajo,
    # pasto). Restos de pegados a medias se reemplazan; lo construido no.
    terrain={lt.base(s) for o in (*olds,new) for s in set(o.values())}|lt.SOIL|lt.ROCK|NATURAL
    terr=lambda s:lt.base(s) in terrain
    same=lambda a,b:a==b or lt.base(a)==lt.base(b) or (natural(a) and natural(b)) or (terr(a) and terr(b))
    for q in set(new).union(*olds):
        target=new.get(q,pre.get(*q));now=cur.get(*q)
        expecteds=[o.get(q,pre.get(*q)) for o in olds]
        # Solo diferencias reales entre propuestas: no deshacer caminos/pasto posteriores.
        if now==target or all(e==target for e in expecteds):continue
        # Hojas/bambu crecen y cambian estado; pasto<->tierra. Eso no es obra de nadie.
        if not any(same(now,e) for e in expecteds):
            # Cambio a mano posterior (o sector no pegado): no tocar.
            conflicts.append(q);not_pasted+=q in old and now==pre.get(*q)
            continue
        if q in cur.tiles:conflicts.append(q);continue
        delta[q]=target
    out.mkdir(parents=True)
    sectors=lt.export(cur,delta,out)
    # export escribe '//paste -a'; aca el aire es parte del cambio.
    for name in ('pegar.txt',):
        f=out/name;f.write_text(f.read_text(encoding='utf8').replace('//paste -a','//paste'),encoding='utf8')
    removed=sum(lt.base(s) in {'air','cave_air','void_air'} for s in delta.values())
    info={'cambios':len(delta),'a_aire':removed,'sectores':len(sectors),'conflictos':len(conflicts),
          'conflictos_no_pegados':not_pasted,'muestra_conflictos':sorted(conflicts)[:40],
          'vieja':[len(o) for o in olds],'nueva':len(new),'sectors':sectors,'nueva_report':{k:v for k,v in report.items() if k!='rock_by_height'}}
    (out/'manifest.json').write_text(json.dumps(info,indent=1,default=str)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in info.items() if k not in ('sectors','nueva_report')},default=str))


if __name__=='__main__':main()
