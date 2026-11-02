"""Render de modelos reales con profundidad por pixel, sin dependencias 3D.

Lee los mismos elementos, UV, texturas y giros que exporta Minecraft. El
buffer de profundidad permite revisar relieves largos y piezas entrelazadas
que un pintado por orden de caras puede esconder incorrectamente.
"""
import json
import base64
import math
import uuid
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import varitas3d as v

ROOT=Path(__file__).resolve().parent.parent


def render(w, size=(300,570), yaw=-25, pitch=-9, frame=0):
    texture,n=v.texture(w)
    texture=texture.crop((0,(frame%n)*v.TEX,v.TEX,(frame%n+1)*v.TEX))
    pixels=texture.load()
    width,height=size
    image=Image.new('RGBA',size);target=image.load()
    depth=[float('inf')]*(width*height)
    view=v._mul(v._rx(math.radians(pitch)),v._ry(math.radians(yaw)))
    points=[v._app(view,[p[0]-8,p[1]-8,p[2]-8]) for e in w.els for p in v._corners(e)]
    bounds=[(min(p[i] for p in points),max(p[i] for p in points)) for i in (0,1)]
    scale=min((width-34)/(bounds[0][1]-bounds[0][0]),(height-24)/(bounds[1][1]-bounds[1][0]))
    cx=width/2-(bounds[0][0]+bounds[0][1])/2*scale
    cy=height/2+(bounds[1][0]+bounds[1][1])/2*scale
    for e in w.els:
        m,origin=v._elrot(e)
        slot=w.slots[e['sw']];su,sv=slot%4*v.TS,slot//4*v.TS
        small=max(b-a for a,b in zip(e['from'],e['to']))<1.5
        for normal,corners in v.FACES.values():
            normal=v._app(view,v._app(m,normal) if m else normal)
            if normal[2]>=-1e-6:continue
            pts=[]
            for c in corners:
                p=[(e['from'],e['to'])[c[i]][i] for i in range(3)]
                if m:p=[a+b for a,b in zip(v._app(m,[p[i]-origin[i] for i in range(3)]),origin)]
                x,y,z=v._app(view,[p[0]-8,p[1]-8,p[2]-8])
                pts.append((cx+x*scale,cy-y*scale,z))
            a,b,_,d=pts
            bx,by=b[0]-a[0],b[1]-a[1];dx,dy=d[0]-a[0],d[1]-a[1]
            det=bx*dy-by*dx
            if abs(det)<1e-7:continue
            xa=max(0,math.floor(min(p[0] for p in pts)));xb=min(width-1,math.ceil(max(p[0] for p in pts)))
            ya=max(0,math.floor(min(p[1] for p in pts)));yb=min(height-1,math.ceil(max(p[1] for p in pts)))
            light=max(0,-normal[0]*.30+normal[1]*.65-normal[2]*.69)
            shade=1 if e['glow'] else .67+.36*light
            for y in range(ya,yb+1):
                py=y+.5-a[1]
                for x in range(xa,xb+1):
                    px=x+.5-a[0]
                    u=(px*dy-py*dx)/det;t=(py*bx-px*by)/det
                    if not 0<=u<=1 or not 0<=t<=1:continue
                    z=a[2]+u*(b[2]-a[2])+t*(d[2]-a[2]);index=y*width+x
                    if z>=depth[index]:continue
                    tx=min(7,int(1+u*6) if small else int(u*8))
                    ty=min(7,int(1+t*6) if small else int(t*8))
                    r,g,blue,alpha=pixels[su+tx,sv+ty]
                    if not alpha:continue
                    depth[index]=z
                    target[x,y]=(min(255,int(r*shade)),min(255,int(g*shade)),min(255,int(blue*shade)),255)
    return image


def sheet(items,path,caption,cell=(320,620),yaw=-25):
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
    title_font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',23)
    out=Image.new('RGBA',(cell[0]*len(items),cell[1]+70),'#111923');draw=ImageDraw.Draw(out)
    draw.text((24,15),caption,font=title_font,fill='#f4d69d')
    for i,w in enumerate(items):
        draw.rounded_rectangle((i*cell[0]+7,58,(i+1)*cell[0]-7,cell[1]+40),radius=12,fill='#172231',outline='#354152')
        out.alpha_composite(render(w,(cell[0]-24,cell[1]-55),yaw=yaw),(i*cell[0]+12,65))
        label=w.name
        if draw.textlength(label,font=font)>cell[0]-24:
            label=label.replace('Espada del ','').replace('Guadana del ','').replace('Baston del ','')
        draw.text((i*cell[0]+cell[0]/2,cell[1]+12),label,anchor='mm',font=font,fill='#dce5ef')
    out.convert('RGB').save(path)


def main():
    from armas3d import SWORDS, AXES, BOWS, GAUNTLET
    from guadanas3d import SCYTHES
    groups={'espadas':SWORDS,'bastones':v.WANDS,'guadanas':SCYTHES,
            'hachas':AXES,'arcos':[g[0] for g in BOWS]}
    from lanzas3d import SPEARS
    groups['lanzas']=SPEARS
    output=ROOT/'build/previews';output.mkdir(parents=True,exist_ok=True)
    for key,items in groups.items():
        sheet(items,output/f'{key}-detallados.png',key.upper()+' / MODELOS 3D REFINADOS')
        print(key,[(w.iid,len(w.els)) for w in items],flush=True)
    # Presentacion general con una familia por fila, incluida la evolucion de espadas.
    gallery=Image.new('RGB',(1920,6*365),'#111923')
    draw=ImageDraw.Draw(gallery);font=ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf',20)
    for row,(key,items) in enumerate(groups.items()):
        draw.text((20,row*365+8),key.upper(),font=font,fill='#f4d69d')
        for col,w in enumerate(items):
            image=render(w,(280,310))
            gallery.paste(image,(col*320+20,row*365+40),image)
    gallery.save(output/'arsenal-detallado.png')
    image=render(GAUNTLET[0],(280,310))
    gallery.paste(image,(5*320+20,5*365+40),image)
    draw.text((5*320+20,5*365+8),'PUNO METEORO',font=font,fill='#f4d69d')
    gallery.save(output/'arsenal-detallado.png')
    sheet(GAUNTLET,output/'guantelete-detallado.png','PUNO METEORO',cell=(600,720),yaw=-35)
    # Dos vistas grandes de las espadas de mayor rango; provienen del modelo final.
    sheet([SWORDS[3],SWORDS[4]],output/'espadas-cristal-y-fuego.png','CRISTAL Y FUEGO / DETALLE DE GEOMETRIA',cell=(620,900),yaw=-32)
    sheet([g[-1] for g in BOWS],output/'arcos-tensados.png','ARCOS / MAXIMO TENSADO')
    # Exportacion accesible de modelos, definiciones y atlas usados en el pack.
    exported=v.assets(SWORDS+AXES+GAUNTLET+SCYTHES+v.WANDS+SPEARS)
    from armas3d import assets
    exported.update(assets())
    for path,data in exported.items():
        target=ROOT/'build/armas3d'/path
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Fuentes editables para Blockbench; el pack sigue usando los JSON vanilla.
    for w in SWORDS+AXES+GAUNTLET+SCYTHES+v.WANDS+SPEARS+[g[0] for g in BOWS]:
        save_blockbench(w,ROOT/'build/armas3d/blockbench'/f'{w.iid}.bbmodel')
    viewer(SWORDS+v.WANDS+SCYTHES+AXES+[g[0] for g in BOWS]+SPEARS+GAUNTLET,
           ROOT/'build/armas3d/visor.html')
    readme='''AstralRPG / arsenal refinado

32 armas: 5 espadas, 5 bastones, 6 guadanas, 5 hachas, 5 arcos,
5 lanzas y el guantelete. Los arcos tienen cuatro estados: 47 modelos vanilla.

visor.html: abrir en un navegador con WebGL para girar los modelos originales.
blockbench/: abrir cada .bbmodel en Blockbench para editar geometria y atlas.
assets/: modelos Minecraft, definiciones y texturas originales exportadas.

Las vistas son renders de la geometria final, no imagenes generadas de armas.
Los acabados animados conservan ocho cuadros de tres ticks y los puntos de agarre.
No cambia el dano, las recetas, los costos ni la progresion del equipo.
La comprobacion de escala en mano y aparicion de brillos dentro de Minecraft
se debe hacer al instalar el resource pack.

Regenerar desde datapack-src:
  python weapon_showcase.py
  python build_pack.py pack-source
  python -m unittest test_weapons3d test_adventure_ui test_viajes_mazmorras
'''
    (ROOT/'build/armas3d/LEEME.txt').write_text(readme,encoding='utf-8')
    with zipfile.ZipFile(ROOT/'build/armas3d-editables.zip','w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('LEEME.txt',readme)
        for path in sorted((ROOT/'build/armas3d/blockbench').glob('*.bbmodel')):
            archive.write(path,'blockbench/'+path.name)


def save_blockbench(w,path):
    model=v.model_json(w);texture,n=v.texture(w)
    elements=[];outliner=[]
    for index,(source,element) in enumerate(zip(w.els,model['elements'])):
        uid=str(uuid.uuid5(uuid.NAMESPACE_URL,f'astral:{w.iid}/{index}'))
        rotation=[0,0,0];origin=[8,8,8]
        if source['rot']:
            axis,angle,origin=source['rot'];rotation['xyz'.index(axis)]=angle
        cube={'name':f'{source["sw"]}_{index}','type':'cube','uuid':uid,
              'from':element['from'],'to':element['to'],'origin':origin,'rotation':rotation,
              'box_uv':False,'uv_offset':[0,0],'shade':not bool(source['glow']),
              'faces':{key:{'uv':value['uv'],'texture':0} for key,value in element['faces'].items()}}
        elements.append(cube);outliner.append(uid)
    data={'meta':{'format_version':'4.10','model_format':'java_block','box_uv':False},
          'name':w.name,'model_identifier':w.iid,'resolution':{'width':32,'height':32},
          'elements':elements,'outliner':outliner,'display':model['display'],
          'textures':[{'name':w.iid+'.png','id':'0','uuid':str(uuid.uuid5(uuid.NAMESPACE_URL,w.iid+'/texture')),
                       'source':'data:image/png;base64,'+base64.b64encode(v._png(texture)).decode(),
                       'width':32,'height':32*n,'uv_width':32,'uv_height':32,
                       'frame_time':v.FRAMETIME,'frame_interpolate':True}]}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def viewer(items,path):
    """Visor WebGL autonomo: se abre sin servidor, red ni bibliotecas externas."""
    records=[]
    for w in items:
        model=v.model_json(w);buffer=[]
        bounds=[v._corners(e) for e in w.els]
        points=[p for group in bounds for p in group]
        low=[min(p[i] for p in points) for i in range(3)]
        high=[max(p[i] for p in points) for i in range(3)]
        center=[(a+b)/2 for a,b in zip(low,high)]
        scale=2.1/max(high[i]-low[i] for i in range(3))
        for source,element in zip(w.els,model['elements']):
            rotation,origin=v._elrot(source)
            for name,(normal,corners) in v.FACES.items():
                pts=[]
                for c in corners:
                    p=[(source['from'],source['to'])[c[i]][i] for i in range(3)]
                    if rotation:p=[a+b for a,b in zip(v._app(rotation,[p[i]-origin[i] for i in range(3)]),origin)]
                    pts.append([(p[i]-center[i])*scale for i in range(3)])
                normal=v._app(rotation,normal) if rotation else normal
                u0,t0,u1,t1=[n/16 for n in element['faces'][name]['uv']]
                uv=[(u0,t0),(u1,t0),(u1,t1),(u0,t1)]
                for i in (0,1,2,0,2,3):
                    buffer.extend(round(n,5) for n in (*pts[i],*normal,*uv[i],float(bool(source['glow']))))
        image,n=v.texture(w)
        records.append({'id':w.iid,'name':w.name,'elements':len(w.els),'frames':n,'vertices':buffer,
                        'image':'data:image/png;base64,'+base64.b64encode(v._png(image)).decode()})
    html='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AstralRPG · Taller de armas 3D</title><style>
*{box-sizing:border-box}body{margin:0;background:#0e1420;color:#e4e8ee;font:15px system-ui;display:grid;grid-template-columns:260px 1fr;height:100vh}aside{padding:26px 18px;background:#151d2a;border-right:1px solid #354050;overflow:auto}h1{font-size:21px;letter-spacing:2px;color:#f1d296;margin:8px 0}p{color:#97a6bb;line-height:1.5}.label{font-size:11px;letter-spacing:2px;color:#a6d4dc}button{font:inherit;color:inherit;background:#1c2839;border:1px solid #354356;border-radius:7px;padding:9px 12px;cursor:pointer}aside button{display:block;text-align:left;width:100%;margin:6px 0;font-size:13px}button.active{border-color:#e3c186;background:#344052;color:#ffe5b3}main{position:relative;min-width:0;background:radial-gradient(ellipse at 50% 50%,#28374b,#101724 70%)}canvas{width:100%;height:100%;display:block;touch-action:none;cursor:grab}.top{position:absolute;left:30px;top:24px;pointer-events:none}h2{margin:0 0 6px;font-size:25px}.tools{position:absolute;right:25px;top:25px;display:flex;gap:7px}.hint{position:absolute;bottom:22px;width:100%;text-align:center;color:#9eafc6;font-size:13px;pointer-events:none}@media(max-width:760px){body{grid-template-columns:165px 1fr}aside{padding:12px 8px}.top{left:14px;top:85px}h2{font-size:18px}.tools{right:12px;top:15px}button{padding:8px}.hint{font-size:11px}}
</style><aside><span class="label">ASTRALRPG / ARSENAL</span><h1>TALLER 3D</h1><p>Modelos reales del paquete.<br>Geometría, materiales y brillo animado.</p><div id="list"></div></aside><main><canvas id="canvas"></canvas><div class="top"><h2 id="name"></h2><span id="stats" class="label"></span></div><div class="tools"><button id="spin">Pausar giro</button><button id="reset">Centrar</button></div><div class="hint">Arrastrá para girar · Rueda para acercar · Elegí un arma a la izquierda</div></main><script>
const models=__MODELS__;
const canvas=document.getElementById('canvas'),gl=canvas.getContext('webgl',{alpha:true,antialias:true});
if(!gl)throw new Error('Este navegador no tiene WebGL disponible.');
const vertex=`attribute vec3 p;attribute vec3 n;attribute vec2 uv;attribute float glow;uniform vec2 angle;uniform float aspect,zoom;varying vec2 tex;varying float light;vec3 turn(vec3 v){float c=cos(angle.x),s=sin(angle.x);vec3 a=vec3(v.x*c+v.z*s,v.y,-v.x*s+v.z*c);c=cos(angle.y);s=sin(angle.y);return vec3(a.x,a.y*c-a.z*s,a.y*s+a.z*c);}void main(){vec3 a=turn(p),normal=turn(n);gl_Position=vec4(a.x*zoom/(aspect*1.25),a.y*zoom/1.25,a.z*.15,1.);light=glow>.5?1.:.67+.36*max(0.,dot(normal,normalize(vec3(-.30,.65,-.69))));tex=uv;}`;
const fragment=`precision mediump float;varying vec2 tex;varying float light;uniform sampler2D atlas;uniform float frame,frames;void main(){vec4 c=texture2D(atlas,vec2(tex.x,(tex.y+frame)/frames));if(c.a<.1)discard;gl_FragColor=vec4(c.rgb*light,c.a);}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
gl.enable(gl.DEPTH_TEST);gl.clearColor(0,0,0,0);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);
const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);let offset=0;for(const [key,count] of [['p',3],['n',3],['uv',2],['glow',1]]){const a=gl.getAttribLocation(program,key);gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,count,gl.FLOAT,false,36,offset);offset+=count*4;}
const uniform=Object.fromEntries(['angle','aspect','zoom','frame','frames'].map(k=>[k,gl.getUniformLocation(program,k)]));
let yaw=-.45,pitch=-.10,zoom=1,spinning=true,current,texture,selection=0,ready=false;
function select(i){selection=i;current=models[i];ready=false;document.getElementById('name').textContent=current.name;document.getElementById('stats').textContent=current.elements+' PIEZAS · '+current.frames+' CUADROS DE TEXTURA';document.querySelectorAll('#list button').forEach((b,j)=>b.classList.toggle('active',i===j));gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(current.vertices),gl.STATIC_DRAW);if(texture)gl.deleteTexture(texture);texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);const image=new Image();image.onload=()=>{if(selection!==i)return;gl.bindTexture(gl.TEXTURE_2D,texture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);ready=true;};image.src=current.image;}
models.forEach((m,i)=>{let b=document.createElement('button');b.textContent=m.name;b.onclick=()=>select(i);document.getElementById('list').append(b);});
document.getElementById('spin').onclick=()=>{spinning=!spinning;document.getElementById('spin').textContent=spinning?'Pausar giro':'Girar';};document.getElementById('reset').onclick=()=>{yaw=-.45;pitch=-.10;zoom=1;};
let drag=null;canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};canvas.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-1.4,Math.min(1.4,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];};canvas.onpointerup=canvas.onpointercancel=()=>drag=null;canvas.onwheel=e=>{e.preventDefault();zoom=Math.max(.4,Math.min(2.8,zoom*Math.exp(-e.deltaY*.001)));};
let last=0;function draw(now){const ratio=Math.min(devicePixelRatio||1,2),w=Math.floor(canvas.clientWidth*ratio),h=Math.floor(canvas.clientHeight*ratio);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}if(spinning&&!drag)yaw+=Math.min(now-last,50)*.00018;last=now;gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);if(ready){gl.uniform2f(uniform.angle,yaw,pitch);gl.uniform1f(uniform.aspect,w/h);gl.uniform1f(uniform.zoom,zoom);gl.uniform1f(uniform.frame,Math.floor(now/150)%current.frames);gl.uniform1f(uniform.frames,current.frames);gl.drawArrays(gl.TRIANGLES,0,current.vertices.length/9);}requestAnimationFrame(draw);}select(0);requestAnimationFrame(draw);
</script></html>'''
    path.write_text(html.replace('__MODELS__',json.dumps(records,ensure_ascii=False,separators=(',',':'))),encoding='utf-8')


if __name__=='__main__':main()
