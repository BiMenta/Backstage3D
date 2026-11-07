import bpy, math, random
from math import sin,cos,pi
random.seed(27)
s=bpy.context.scene
for name,xa,xb,folds in [('Left crimson velvet wall',-8,3.5,34),('Right parted velvet',4.4,8,12)]:
 o=s.objects.get(name)
 if not o:continue
 verts=[];faces=[];N=360;M=100
 for j in range(M+1):
  v=j/M
  for i in range(N+1):
   u=i/N
   phase=2*pi*(folds*u+.14*sin(u*17)+.10*sin(u*43)+.24*sin(v*3.8+u*9)*(1-v))
   amp=.10+.065*sin(u*19+1)**2+.08*(1-v)
   broad=.15*sin(u*13+v*2.5)*sin(pi*v)
   y=4.5+amp*cos(phase)+.035*cos(2*phase+.4)+broad
   # Gravity gathers broad folds near the floor into a soft fabric pool.
   pool=max(0,1-v/.085)
   y-=.43*pool**2*(.7+.3*sin(u*21)**2)
   z=.035+7.965*v + (.035+.04*sin(u*23)**2)*pool
   x=xa+(xb-xa)*u+.10*sin(v*pi)*sin(u*12)
   if xa<0:x-=u**8*(.55*sin(pi*v)**1.2+.22*(1-v))
   else:x+=(1-u)**8*(.38*sin(pi*v)**1.2+.12*(1-v))
   verts.append((x,y,z))
 for j in range(M):
  for i in range(N):
   k=j*(N+1)+i;faces.append((k,k+1,k+N+2,k+N+1))
 d=bpy.data.meshes.new(name+' natural drape mesh');d.from_pydata(verts,[],faces);d.update()
 for mat in o.data.materials:d.materials.append(mat)
 o.data=d
 for p in d.polygons:p.use_smooth=True
 sub=o.modifiers.get('Soft cloth folds') or o.modifiers.new('Soft cloth folds','SUBSURF');sub.levels=1;sub.render_levels=1
# Dedicated weathered board shader, using real object coordinates and per-board variation.
m=bpy.data.materials.new('Aged stage oak • stains grain and worn patches');m.use_nodes=True
n=m.node_tree.nodes;n.clear();l=m.node_tree.links
out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');l.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Roughness'].default_value=.73
tex=n.new('ShaderNodeTexCoord')
def noise(scale,detail,vec):
 a=n.new('ShaderNodeTexNoise');a.inputs['Scale'].default_value=scale;a.inputs['Detail'].default_value=detail;a.inputs['Roughness'].default_value=.75;l.new(vec,a.inputs['Vector']);return a.outputs['Fac']
def stretch(vec,xyz):
 a=n.new('ShaderNodeVectorMath');a.operation='MULTIPLY';a.inputs[1].default_value=xyz;l.new(vec,a.inputs[0]);return a.outputs[0]
def ramp(inp,stops):
 a=n.new('ShaderNodeValToRGB');r=a.color_ramp
 for e in list(r.elements)[2:]:r.elements.remove(e)
 r.elements[0].position=stops[0][0];r.elements[0].color=(*stops[0][1],1);r.elements[1].position=stops[-1][0];r.elements[1].color=(*stops[-1][1],1)
 for p,c in stops[1:-1]:r.elements.new(p).color=(*c,1)
 l.new(inp,a.inputs[0]);return a.outputs['Color']
grain=noise(3,4,stretch(tex.outputs['Object'],(17,.45,4)))
col=ramp(grain,[(.22,(.035,.017,.010)),(.45,(.12,.064,.030)),(.62,(.24,.145,.075)),(.8,(.34,.23,.135))])
patch=noise(2.6,5,stretch(tex.outputs['Object'],(1.8,.7,1)))
patchcol=ramp(patch,[(.26,(.10,.07,.055)),(.44,(.38,.30,.22)),(.62,(.78,.70,.57)),(.77,(.95,.84,.68))])
mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.72;l.new(col,mix.inputs[1]);l.new(patchcol,mix.inputs[2])
info=n.new('ShaderNodeObjectInfo');vary=ramp(info.outputs['Random'],[(0,(.4,.34,.28)),(1,(1,.92,.78))])
mix2=n.new('ShaderNodeMixRGB');mix2.blend_type='MULTIPLY';mix2.inputs[0].default_value=.5;l.new(mix.outputs[0],mix2.inputs[1]);l.new(vary,mix2.inputs[2]);l.new(mix2.outputs[0],bs.inputs['Base Color'])
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.035;l.new(grain,bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
rough=ramp(patch,[(.2,(.35,.35,.35)),(.8,(.92,.92,.92))]);l.new(rough,bs.inputs['Roughness'])
count=0
for o in s.objects:
 if o.name.startswith('Individual worn floorboard'):
  o.data.materials.clear();o.data.materials.append(m);count+=1
s.render.filepath='/Volumes/ZHITAI/黑客松/Backstage3D/refined_preview.png'
bpy.ops.wm.save_as_mainfile(filepath='/Volumes/ZHITAI/黑客松/Backstage3D/backstage_refined.blend')
result={'curtains':2,'aged_boards':count,'saved':bpy.data.filepath}
