import bpy, math, random, os, json
from mathutils import Vector
from math import sin, cos, pi
random.seed(19)
OUT='/Volumes/ZHITAI/黑客松/CircusReference3D'
scene=bpy.data.scenes.new('Vintage Circus • Reference Reconstruction')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
groups={}
for name in ['01_Architecture','02_Tent_Canopy','03_Velvet_Drapery','04_Puppet_Theatre','05_Display_Podiums','06_Paper_Rosettes','07_Gilded_Ornaments','08_Pendant_Lanterns','09_Festoon_Lights','10_Lighting_Camera']:
    c=bpy.data.collections.new(name);scene.collection.children.link(c);groups[name[:2]]=c
G='01'
def put(o,name,mat=None):
    o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    groups[G].objects.link(o)
    if mat:o.data.materials.append(mat)
    return o
def material(name,col,metal=0,rough=.65,noise=False,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    n=m.node_tree.nodes;p=next((v for v in n if v.type=='BSDF_PRINCIPLED'),None) or n.new('ShaderNodeBsdfPrincipled');out=next((v for v in n if v.type=='OUTPUT_MATERIAL'),None) or n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if emit:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
    if noise:
        t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=85;t.inputs['Detail'].default_value=3
        b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=.025
        m.node_tree.links.new(t.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
    return m
red=material('Velvet • oxblood',(.36,.025,.037),rough=.87,noise=True)
coral=material('Fabric • faded vermilion',(.57,.13,.105),noise=True)
teal=material('Velvet • deep petrol',(.018,.12,.115),rough=.88,noise=True)
gold=material('Antique gilt',(.65,.36,.12),.68,.31,True)
cream=material('Ivory linen',(.85,.64,.39),noise=True)
wood=material('Painted warm ochre wood',(.40,.19,.075),rough=.55,noise=True)
dark=material('Theatre interior',(.012,.009,.008))
floor=material('Terracotta floor',(.40,.16,.105),noise=True)
rug=material('Faded circular carpet',(.49,.32,.15),noise=True)
bulb=material('Warm fairy light', (1,.52,.18),rough=.22,emit=7)
glass=material('Lantern luminous ivory', (1,.42,.17),rough=.3,emit=2.2)
def mesh(name,vs,fs,mat,smooth=True):
    d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);groups[G].objects.link(o)
    if mat:d.materials.append(mat)
    if smooth:
        for p in d.polygons:p.use_smooth=True
    return o
def cube(name,loc,size,mat,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object,name,mat);o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:m=o.modifiers.new('Soft crafted edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def uv(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=loc);o=put(bpy.context.object,name,mat);o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    return o
def cyl(name,loc,r,depth,mat,verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=put(bpy.context.object,name,mat)
    m=o.modifiers.new('Rounded rim','BEVEL');m.width=.025;m.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def line(name,pts,mat,r=.018,cyclic=False):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=2;d.bevel_depth=r;d.bevel_resolution=3
    s=d.splines.new('POLY');s.points.add(len(pts)-1)
    for p,v in zip(s.points,pts):p.co=(*v,1)
    s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,d);groups[G].objects.link(o);d.materials.append(mat);return o
def ring(name,x,y,z,r,mat,th=.03):return line(name,[(x+r*cos(i*2*pi/96),y+r*sin(i*2*pi/96),z) for i in range(96)],mat,th,True)
def curtain(name,x0,x1,y,bottom,top,mat,folds=16):
    vs=[];fs=[];N=100;M=18
    for j in range(M+1):
        v=j/M
        for i in range(N+1):
            u=i/N;x=x0+(x1-x0)*u
            z=bottom+(top-bottom)*v+.055*cos(u*folds*2*pi)*(1-v)
            vs.append((x,y+.12*cos(u*folds*2*pi)+.025*sin(v*pi*3+u*20),z))
    for j in range(M):
        for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
    o=mesh(name,vs,fs,mat);m=o.modifiers.new('Fabric thickness','SOLIDIFY');m.thickness=.015;return o
def swag(name,a,b,y,top,drop,mat):
    vs=[];fs=[];N=70;M=14
    for j in range(M+1):
        v=j/M
        for i in range(N+1):
            u=i/N;z=top-drop*sin(pi*u)**.7+v*(.20+.48*sin(pi*u))
            vs.append((a+(b-a)*u,y+.065*sin(v*9*pi+u*5)*sin(pi*u),z))
    for j in range(M):
        for i in range(N):k=j*(N+1)+i;fs.append((k,k+1,k+N+2,k+N+1))
    mesh(name,vs,fs,mat)
    line(name+' • lower braid',[(a+(b-a)*i/N,y-.025,top-drop*sin(pi*i/N)**.7) for i in range(N+1)],gold,.025)
    line(name+' • inner braid',[(a+(b-a)*i/N,y-.045,top-drop*sin(pi*i/N)**.7+.085) for i in range(N+1)],gold,.012)
def area(name,loc,target,power,color,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);groups['10'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def point(name,loc,power,color,r=.5):
    d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=r;o=bpy.data.objects.new(name,d);groups['10'].objects.link(o);o.location=loc

OUT='/Volumes/ZHITAI/黑客松/Backstage3D'
scene.name='Circus Backstage Dressing Room'
leather=material('Worn chocolate leather',(.065,.025,.014),rough=.43,noise=True)
black=material('Midnight wool',(.009,.016,.023),noise=True)
blue=material('Jester sapphire',(.012,.15,.32),noise=True)
skin=material('Ivory mannequin',(.57,.38,.23))
hair=material('Auburn curls',(.12,.042,.012),noise=True)
mirror=material('Silver mirror',(.82,.87,.9),1,.07)
for i in range(42):
 for j in range(5):
  cube('Individual worn floorboard',(-8+i*.38,-6+j*3+(i%2)*.6,-.08),(.367,2.985,.16),wood,.008)
curtain('Left crimson velvet wall',-8,3.5,4.5,0,8,red,42)
curtain('Right parted velvet',4.4,8,4.7,0,8,red,18)
# Table and illuminated mirror
cube('Vanity solid wood top',(-.8,3,2),(2.7,1.1,.16),wood)
for x in [-1.92,.32]:
 for y in [2.6,3.4]:
  cyl('Turned table leg',(x,y,.96),.065,1.92,wood)
  for z in [.2,1.45,1.62]:uv('Leg carved bead',(x,y,z),(.09,.09,.1),wood)
cube('Vanity drawer',(-.8,2.65,1.77),(2.5,.4,.3),wood)
uv('Drawer brass pull',(-.8,2.4,1.78),(.06,.03,.04),gold)
cube('Reflective dressing mirror',(-1,3.42,3.48),(1.65,.035,2.55),mirror,.01)
for x in [-1.93,-.07]:cube('Mirror carved upright',(x,3.38,3.48),(.17,.16,2.9),gold)
for z in [2.05,4.91]:cube('Mirror carved crossbar',(-1,3.38,z),(2.03,.16,.17),gold)
for x in [-1.89,-.11]:
 for z in [2.45,3.15,3.85,4.55]:
  uv('Mirror incandescent bulb',(x,3.2,z),(.09,.09,.09),bulb);point('Bulb practical',(x,3.05,z),8,(1,.55,.26),.12)
for x in [-1.55,-1,-.45]:uv('Top mirror bulb',(x,3.2,4.88),(.09,.09,.09),bulb)
for x,y,r in [(-1.6,2.8,.21),(-1,2.7,.12),(-.6,2.85,.14)]:cyl('Cosmetic powder tin',(x,y,2.15),r,.14,coral)
cyl('Brush holder',(-.1,3,2.2),.11,.3,black)
for i in range(7):
 x=-.1+random.uniform(-.09,.09);y=3+random.uniform(-.08,.08);z=2.6+random.uniform(-.08,.1)
 line('Makeup brush handle',[(x,y,2.2),(x,y,z)],wood,.014);uv('Soft makeup brush',(x,y,z),(.045,.045,.08),cream)
cyl('Wig stand base',(.35,3,2.13),.19,.1,cream)
uv('Mannequin head',(.35,3,2.57),(.23,.20,.34),skin)
for i in range(110):
 a=random.uniform(0,2*pi);t=random.uniform(0,1.8)
 uv('Auburn wig curl',(.35+.25*sin(t)*cos(a),3+.22*sin(t)*sin(a),2.64+.28*cos(t)),(.063,.06,.065),hair)
# Costume rail
for x in [-5.6,-3.05]:
 cube('Rack upright',(x,2.6,1.95),(.12,.14,3.9),wood)
 cube('Rack foot',(x,2.6,.17),(.20,1.1,.18),wood)
 for y in [2.2,3]:uv('Rack caster',(x,y,.08),(.07,.07,.08),black)
cube('Rack upper beam',(-4.325,2.6,3.85),(2.7,.16,.17),wood)
cube('Rack shoe shelf',(-4.325,2.6,.32),(2.6,.7,.12),wood)
for k in range(3):
 x=-5.12+k*.77
 line('Wire coat hanger',[(x,2.6,3.85),(x-.1,2.6,3.61),(x-.39,2.6,3.39),(x+.39,2.6,3.39),(x,2.6,3.65)],gold,.018)
 mat=[teal,gold,red][k]
 curtain('Hanging theatrical coat',x-.30,x+.30,2.55,1.1+k*.15,3.4,mat,8)
 for dx in [-.38,.38]:
  o=cube('Coat sleeve',(x+dx,2.55,2.65),(.19,.23,1.25),mat,.08);o.rotation_euler[1]=dx*.3
for x in [-5.1,-4.7,-3.6,-3.25]:
 cyl('Boot tall shaft',(x,2.6,.73),.11,.65,leather)
 uv('Boot toe',(x,2.42,.46),(.14,.27,.13),leather)
 for z in [.6,.7,.8,.9]:line('Boot lace',[(x-.07,2.48,z),(x+.07,2.48,z+.04)],gold,.009)
# Hat stand
cyl('Coat stand pole',(5.45,3.5,2.4),.065,4.8,leather)
for a in [0,2*pi/3,4*pi/3]:
 line('Coat stand foot',[(5.45,3.5,.5),(5.45+.5*cos(a),3.5+.5*sin(a),.08)],leather,.045)
 line('Curved hat hook',[(5.45,3.5,3.8),(5.45+.65*cos(a),3.5+.65*sin(a),4.35),(5.45+.6*cos(a),3.5+.6*sin(a),4.65)],leather,.045)
uv('Coat rack finial',(5.45,3.5,4.9),(.11,.11,.14),leather)
cyl('Top hat brim',(4.95,3.1,3.65),.42,.07,black)
cyl('Top hat crown',(4.95,3.1,3.94),.28,.55,black)
cyl('Top hat satin ribbon',(4.95,3.1,3.74),.285,.12,blue)
uv('Jester cap',(5.8,3.3,4.05),(.3,.23,.22),blue)
for k in [-1,0,1]:
 pts=[(5.8+k*.2+t*k*.45,3.3,4.05+.6*sin(t*pi*.8)-t*.28) for t in [j/24 for j in range(25)]]
 for j in range(24):line('Tapered jester horn',pts[j:j+2],blue if k<1 else gold,.14*(1-j/25))
 uv('Jester bell',pts[-1],(.055,.055,.055),gold)
# Stacked travel trunks
for k in range(4):
 x=5.45+.09*k;y=.7;z=.43+k*.65;w=2.25-k*.15
 cube('Vintage travel trunk',(x,y,z),(w,1.3,.63),leather,.12)
 cube('Trunk lid seam',(x,y,z+.15),(w+.015,1.315,.025),black,.015)
 for dx in [-w/2+.13,w/2-.13]:
  for yy in [y-.56,y+.56]:
   for zz in [z-.23,z+.23]:cube('Brass reinforced corner',(x+dx,yy,zz),(.2,.19,.14),gold,.035)
 for dx in [-.65,.65]:
  cube('Trunk lock plate',(x+dx,y-.67,z+.04),(.14,.035,.19),gold,.02)
 line('Leather suitcase handle',[(x-.22,y-.7,z),(x-.18,y-.79,z-.07),(x+.18,y-.79,z-.07),(x+.22,y-.7,z)],black,.038)
# Warm slit and atmospheric dust
area('Golden light through curtain',(4.1,6,6.5),(0,-3,0),2200,(1,.62,.3),1.2)
area('Soft backstage fill',(-4,-3,5),(0,3,2),180,(.42,.53,1),5)
area('Vanity warm bounce',(-1,2.5,4),(-1,1,1),100,(1,.55,.27),2)
vmat=bpy.data.materials.new('Airborne theatrical haze');vmat.use_nodes=True;n=vmat.node_tree.nodes;n.clear();v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.018;v.inputs['Anisotropy'].default_value=.35;o=n.new('ShaderNodeOutputMaterial');vmat.node_tree.links.new(v.outputs['Volume'],o.inputs['Volume'])
cube('Atmosphere volume',(0,1,4),(16,16,9),vmat,0)
world=bpy.data.worlds.new('Dark backstage');world.use_nodes=True
for n in world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs[0].default_value=(.025,.035,.06,1);n.inputs[1].default_value=.17
scene.world=world
d=bpy.data.cameras.new('Reference camera');cam=bpy.data.objects.new('Reference camera',d);scene.collection.objects.link(cam);cam.location=(8,-14,7);cam.rotation_euler=(Vector((0,2.1,2.6))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=43;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=840;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT+'/preview.png'
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/backstage.blend')
result={'objects':len(scene.objects),'saved':OUT+'/backstage.blend'}
