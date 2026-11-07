import bpy,math,random
from math import sin,cos,pi
random.seed(42)
s=bpy.context.scene
coll=bpy.data.collections.new('Reference tailored costumes');s.collection.children.link(coll)
def mat(name,col,metal=0,rough=.65):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
stripe=mat('Grey ivory pinstripe wool',(.22,.23,.20))
n=stripe.node_tree.nodes;l=stripe.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED');tc=n.new('ShaderNodeTexCoord');w=n.new('ShaderNodeTexWave');w.wave_type='BANDS';w.bands_direction='X';w.inputs['Scale'].default_value=24;w.inputs['Distortion'].default_value=.3;l.new(tc.outputs['Object'],w.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.55;r.color_ramp.elements[0].color=(.035,.043,.041,1);r.color_ramp.elements[1].position=.7;r.color_ramp.elements[1].color=(.36,.35,.29,1);l.new(w.outputs['Color'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
gold=mat('Gold sequin fabric',(.48,.29,.09),.8,.27);black=mat('Black costume lining',(.008,.009,.011));burgundy=mat('Harlequin burgundy',(.21,.018,.024));green=mat('Harlequin dark sage',(.06,.10,.07));ivory=mat('Harlequin old ivory',(.49,.39,.23));brass=mat('Small antique buttons',(.45,.27,.08),.75,.3)
def mesh(name,v,f,m,sub=1):
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(m)
 for p in d.polygons:p.use_smooth=True
 if sub:a=o.modifiers.new('Tailored smooth cloth','SUBSURF');a.levels=sub
 a=o.modifiers.new('Cloth thickness','SOLIDIFY');a.thickness=.008
 return o
def curve(name,pts,m,r=.015):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,d);coll.objects.link(o);d.materials.append(m)
def sphere(name,loc,scale,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o)
 return o
# Replace only prior placeholder garments and hangers.
for o in list(s.objects):
 if o.name.startswith(('Hanging theatrical coat','Coat sleeve','Wire coat hanger')):bpy.data.objects.remove(o,do_unlink=True)
# Curtain silhouette: narrow diagonal opening, long heavy unbroken folds, minimal pooling.
for name,xa,xb,nfold in [('Left crimson velvet wall',-10,3.92,40),('Right parted velvet',4.42,9,16)]:
 o=s.objects[name];v=[];f=[];N=400;M=100
 for j in range(M+1):
  t=j/M
  for i in range(N+1):
   u=i/N;phase=2*pi*(nfold*u+.12*sin(u*19)+.09*sin(t*4+u*12))
   x=xa+(xb-xa)*u
   if xa<0:x+=u**12*(.45*t-.47*(1-t)**1.4)
   else:x+=(1-u)**12*(.10*(1-t))
   y=4.5+(.13+.055*sin(u*31)**2)*cos(phase)+.09*sin(t*pi)*sin(u*17)-.12*math.exp(-t*32)
   z=.018+8*t+.028*(1-t)**15*(1+sin(phase))
   v.append((x,y,z))
 for j in range(M):
  for i in range(N):k=j*(N+1)+i;f.append((k,k+1,k+N+2,k+N+1))
 d=bpy.data.meshes.new(name+' reference silhouette');d.from_pydata(v,[],f);d.update()
 for m in o.data.materials:d.materials.append(m)
 o.data=d
 for p in d.polygons:p.use_smooth=True
# Each coat is a shaped open tubular torso, separate sleeves, and folded lapels.
def garment(name,x,y,length,m,sleeves=True,width=.29):
 top=3.39;N=40;M=35;v=[];f=[]
 for j in range(M+1):
  t=j/M;z=top-length*t
  # narrow neck, broad shoulders, tapered waist, flared tails
  ww=width*(.50+.50*min(t/.13,1))*(1-.20*sin(pi*t)+.1*t*t)
  for i in range(N+1):
   a=.23+(2*pi-.46)*i/N
   xx=x+ww*sin(a);yy=y-.15*cos(a)+.022*sin(a*9+t*4)*sin(pi*t)
   zz=z-.11*cos(a)**2*(1-t)**12+.035*cos(a*3)*t**9
   v.append((xx,yy,zz))
 for j in range(M):
  for i in range(N):k=j*(N+1)+i;f.append((k,k+1,k+N+2,k+N+1))
 body=mesh(name+' tailored body',v,f,m)
 if sleeves:
  for side in [-1,1]:
   vs=[];fs=[]
   for j in range(25):
    t=j/24;cx=x+side*(width*.86+.15*t);cz=top-.14-length*.73*t
    for i in range(17):
     a=2*pi*i/16;rr=.115*(1-.29*t);vs.append((cx+rr*cos(a),y+.015+rr*sin(a)+.025*sin(t*8),cz+.025*cos(a)))
   for j in range(24):
    for i in range(16):k=j*17+i;fs.append((k,k+1,k+18,k+17))
   mesh(name+' hanging sleeve',vs,fs,m)
   for q in range(3):sphere(name+' cuff button',(x+side*(width*.86+.14),y-.09,top-.14-length*.73+.05+q*.045),(.016,.012,.016),brass)
 for side in [-1,1]:
  mesh(name+' folded lapel',[(x+side*.07,y-.16,top-.04),(x+side*.22,y-.18,top-.19),(x+side*.12,y-.21,top-.52),(x+side*.06,y-.18,top-.35)],[(0,1,2,3)],m,0)
 curve(name+' wooden hanger',[(x,2.6,3.85),(x-.035,2.6,3.64),(x-width,2.6,3.37),(x+width,2.6,3.37),(x,2.6,3.64)],brass,.018)
 return body
coat=garment('01 long striped frock coat',-5.11,2.52,2.12,stripe,True,.30)
g=garment('02 gold sequined open jacket',-4.19,2.43,1.55,gold,True,.27)
garment('03 black inner waistcoat',-3.83,2.69,1.35,black,False,.23)
h=garment('04 harlequin sleeveless vest',-3.43,2.52,1.33,burgundy,False,.26)
# UV-based diamond patchwork follows the torso rather than flat stripes.
h.data.materials.append(green);h.data.materials.append(ivory)
for p in h.data.polygons:
 row=p.index//40;col=p.index%40
 a=math.floor((col/40*8+row/35*6));b=math.floor((col/40*8-row/35*6));p.material_index=(a+b)%3
# Thousands of small reflective discs over gold fabric front and sleeve surfaces.
vs=[];fs=[]
for i in range(2300):
 t=random.uniform(.08,.98);a=random.uniform(.25,2*pi-.25);ww=.27*(.5+.5*min(t/.13,1))*(1-.20*sin(pi*t)+.1*t*t)
 x=-4.19+ww*sin(a);y=2.43-.153*cos(a)+.022*sin(a*9+t*4)*sin(pi*t);z=3.39-1.55*t
 rr=random.uniform(.006,.012);k=len(vs)
 for q in range(6):ang=q*pi/3;vs.append((x+rr*cos(ang),y-.004,z+rr*sin(ang)))
 fs.append(tuple(range(k,k+6)))
mesh('Gold jacket individual sequin glints',vs,fs,gold,0)
s.render.filepath='/Volumes/ZHITAI/黑客松/Backstage3D/tailored_preview'
bpy.ops.wm.save_as_mainfile(filepath='/Volumes/ZHITAI/黑客松/Backstage3D/backstage_tailored.blend')
result={'saved':bpy.data.filepath,'garment_styles':4}
