"""2.5D surface projection and anatomical vector deformation. No bitmap warps."""
import json,math
from pathlib import Path
from geometry import *

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'src/timeline.json').read_text())
TRACKS={name:Track(keys) for name,keys in CFG['tracks'].items()}
def value(name,f):return TRACKS[name](f)

def spring_table(side):
    # Analytic rig targets integrated at 240Hz, independent of output frame rate.
    step=1/240;omega=2*math.pi*CFG['rig']['spring_hz'];damping=CFG['rig']['spring_damping']
    table=[];x=vel=0.;delay=CFG['rig'][f'ear_{side}_delay_frames']
    for i in range(1802):
        f=i/8-delay
        target=value('yaw',f)*23+(1 if side=='left' else -1)*value('ear_spread',f)
        acc=omega**2*(target-x)-2*damping*omega*vel
        vel+=acc*step;x+=vel*step;table.append(x)
    return table

SPRINGS={s:spring_table(s) for s in ('left','right')}
def spring(side,f):
    f=max(0,min(225,f))*8;i=int(f);u=f-i
    return mix(SPRINGS[side][i],SPRINGS[side][i+1],u)
def settle(f,start,amp,period=15,decay=23):
    if f<start or f>=212:return 0.
    q=f-start
    return amp*math.exp(-q/decay)*math.sin(2*math.pi*q/period)*(1-smooth((f-197)/15))

class Rig:
    def __init__(self,f):
        self.f=f;self.yaw=value('yaw',f)
        self.left_bend=spring('left',f)-self.yaw*23+settle(f,92,3.5,17,26)+settle(f,125,1.1,20,32)
        self.right_bend=spring('right',f)-self.yaw*23+settle(f,95,-3.8,19,29)+settle(f,128,-1.0,22,31)
        tail=1-smooth((f-202)/10)
        self.left_bend*=tail;self.right_bend*=tail
    def project(self,x,y,z,yaw=None):
        a=self.yaw if yaw is None else yaw
        xx=x-740;yy=y-550
        depth=-xx*math.sin(a)+z*math.cos(a)
        # Relative perspective is exactly identity when yaw=0.
        p=CFG['rig']['camera_distance']/(CFG['rig']['camera_distance']-(depth-z))
        return 740+(xx*math.cos(a)+z*math.sin(a))*p,550+yy*p
    def anatomy(self,x,y,ornament=False):
        ox,oy=x,y
        left=1-smooth((ox-735)/80);right=1-left
        influence=smooth((500-oy)/190)
        # Anchored ear extension: bases remain attached; the tips curl as they grow.
        g=value('left_growth',self.f)*left+value('right_growth',self.f)*right
        px=550*left+957*right;py=438*left+469*right
        gx=px+(x-px)*(.28+.72*g);gy=py+(y-py)*g
        x=mix(x,gx,influence);y=mix(y,gy,influence)
        angle=(self.left_bend*left+self.right_bend*right)*influence**1.6
        # An unfurling curve, rather than affine scaling of an entire ear layer.
        angle+=(1-g)*(24*left-20*right)*influence
        x,y=rotate(x,y,px,py,angle)
        # Ribbons and curled tips retain secondary bending after the primary head stops.
        curl=settle(self.f,94 if left>.5 else 97,8 if left>.5 else -7,18,28)
        if ornament:
            w=math.exp(-((ox-(530*left+950*right))/100)**2-((oy-(431*left+487*right))/82)**2)
            x,y=rotate(x,y,530*left+950*right,431*left+487*right,curl*w)
        # Cheek curls flex outward in a delayed wave after the impact.
        cheek=smooth((abs(ox-740)-300)/140)*smooth((oy-590)/90)
        ca=settle(self.f,92,10,18,21)+settle(self.f,122,1.3,22,30)
        x,y=rotate(x,y,405 if ox<740 else 1060,655,ca*cheek*(-1 if ox<740 else 1))
        z=CFG['rig']['face_depth']*math.sqrt(max(0,1-((ox-740)/510)**2))
        z=mix(z,CFG['rig']['ear_depth'],influence)
        return self.project(x,y,z)
    def muzzle(self,x,y):
        # Skin the attachment to the same face surface. Independent depth is
        # introduced only below the attachment, avoiding a pink seam on yaw.
        face_z=CFG['rig']['face_depth']*math.sqrt(max(0,1-((x-740)/510)**2))
        z=mix(face_z,CFG['rig']['muzzle_depth'],smooth((y-755)/80))
        return self.project(x,y,z)
    def eye_metrics(self,side):
        # Leading gaze gets ahead of the head by two frames.
        gaze=value('yaw',min(225,self.f+2))
        far=clamp((gaze if side=='spiral' else -gaze)/.43)
        width=1-(1-CFG['rig']['far_eye_width'])*far
        entry=value('spiral_entry' if side=='spiral' else 'cross_entry',self.f)
        height=value('squint',self.f)*(value('blink',self.f) if side=='cross' else 1)
        return gaze,far,width,entry,height
    def eye(self,side):
        cx,cy=(617,585) if side=='cross' else (845,593)
        gaze,far,width,entry,height=self.eye_metrics(side)
        rotation=value('cross_rotation' if side=='cross' else 'spiral_rotation',self.f)
        rotation+=gaze*(-4 if side=='cross' else 7)
        def fn(x,y):
            x=cx+(x-cx)*width*entry;y=cy+(y-cy)*height*entry
            x,y=rotate(x,y,cx,cy,rotation)
            x,y=self.project(x,y,CFG['rig']['eye_depth'],gaze)
            y-=abs(gaze)*9
            return x,y
        return fn
    def global_transform(self):
        f=self.f;s=value('scale',f)
        return f'translate({740+value("x",f):.5f} {550+value("y",f):.5f}) rotate({value("roll",f):.6f}) scale({s*value("squash_x",f):.7f} {s*value("squash_y",f):.7f}) translate(-740 -550)'
    def metrics(self):
        return {'frame':self.f,'yaw_degrees':math.degrees(self.yaw),'scale':value('scale',self.f),
                'squash_x':value('squash_x',self.f),'squash_y':value('squash_y',self.f),
                'left_ear_bend_degrees':self.left_bend,'right_ear_bend_degrees':self.right_bend,
                'cross_width':self.eye_metrics('cross')[2],'spiral_width':self.eye_metrics('spiral')[2],
                'cross_blink':value('blink',self.f)}
