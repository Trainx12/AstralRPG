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
    for a in ('antes','hoy','original','vieja','nueva','out'):
        p.add_argument('--'+a,type=Path,required=True)
    p.add_argument('--esperados',type=int,help='Cambios de la propuesta vieja (control)')
    args=p.parse_args();out=lt.private(args.out)
    if out.exists():raise ValueError('Usar salida nueva')
    old_cfg=json.loads(args.vieja.read_text(encoding='utf-8-sig'))
    new_cfg=json.loads(args.nueva.read_text(encoding='utf-8-sig'))
    if old_cfg['bounds']!=new_cfg['bounds']:raise ValueError('Bounds distintos')
    bounds=old_cfg['bounds']
    pre=lt.World.load(args.antes,bounds);cur=lt.World.load(args.hoy,bounds)
    original=lt.World.load(args.original,bounds)
    old,_=lt.propose(pre,original,bounds,old_cfg)
    new,report=lt.propose(pre,original,bounds,new_cfg)
    if args.esperados and len(old)!=args.esperados:
        raise ValueError(f'La propuesta vieja no se reproduce: {len(old)} != {args.esperados}')
    delta={};conflicts=[];not_pasted=0
    for q in set(old)|set(new):
        expected=old.get(q,pre.get(*q));target=new.get(q,pre.get(*q));now=cur.get(*q)
        if now==target:continue
        # Hojas/bambu crecen y cambian estado; pasto<->tierra. Eso no es obra de nadie.
        natural=lambda s:lt.base(s) in NATURAL
        if now!=expected and not (lt.base(now)==lt.base(expected) or (natural(now) and natural(expected))):
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
          'vieja':len(old),'nueva':len(new),'sectors':sectors,'nueva_report':{k:v for k,v in report.items() if k!='rock_by_height'}}
    (out/'manifest.json').write_text(json.dumps(info,indent=1,default=str)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in info.items() if k not in ('sectors','nueva_report')},default=str))


if __name__=='__main__':main()
