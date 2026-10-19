"""Editable SVG Béziers, Hermite timing and real arc-length trimming."""
import re, math
from functools import lru_cache

def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def smooth(x):
    x=clamp(x); return x*x*(3-2*x)
def mix(a,b,u): return a+(b-a)*u

class Track:
    """Keys: [frame, value, incoming derivative/frame, outgoing derivative/frame]."""
    def __init__(self,keys): self.keys=keys
    def __call__(self,f):
        if f<=self.keys[0][0]:return self.keys[0][1]
        if f>=self.keys[-1][0]:return self.keys[-1][1]
        for a,b in zip(self.keys,self.keys[1:]):
            if a[0]<=f<=b[0]:
                d=b[0]-a[0];u=(f-a[0])/d
                va=a[3] if len(a)>3 else (a[2] if len(a)>2 else 0)
                vb=b[2] if len(b)>2 else 0
                return (2*u**3-3*u*u+1)*a[1]+(u**3-2*u*u+u)*va*d+(-2*u**3+3*u*u)*b[1]+(u**3-u*u)*vb*d

def bezier_ease(u,x1=.19,y1=.8,x2=.25,y2=1):
    u=clamp(u);lo=0.;hi=1.
    if u==0 or u==1:return u
    for _ in range(18):
        q=(lo+hi)/2;v=3*(1-q)**2*q*x1+3*(1-q)*q*q*x2+q**3
        if v<u:lo=q
        else:hi=q
    q=(lo+hi)/2
    return 3*(1-q)**2*q*y1+3*(1-q)*q*q*y2+q**3

@lru_cache(None)
def parse(d):
    tokens=re.findall(r'[MLCQHVZmlcqhvz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',d)
    out=[];i=0;x=y=0.;start=(0.,0.)
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd=='Z':out.append(('Z',()));x,y=start;continue
        n={'M':2,'L':2,'C':6,'Q':4,'H':1,'V':1}[cmd]
        a=list(map(float,tokens[i:i+n]));i+=n
        if cmd=='H':cmd='L';a=[a[0],y]
        if cmd=='V':cmd='L';a=[x,a[0]]
        if cmd=='M':start=tuple(a)
        x,y=a[-2:];out.append((cmd,tuple(a)))
    return tuple(out)

def warp(d,fn):
    result=[]
    for cmd,values in parse(d):
        pts=[]
        for i in range(0,len(values),2):
            x,y=fn(values[i],values[i+1]);pts.append(f'{x:.4f},{y:.4f}')
        result.append(cmd+' '.join(pts))
    return ' '.join(result)

def rotate(x,y,cx,cy,degrees):
    a=math.radians(degrees);c=math.cos(a);s=math.sin(a)
    return cx+(x-cx)*c-(y-cy)*s,cy+(x-cx)*s+(y-cy)*c

def cubic(p0,p1,p2,p3,u):
    return tuple((1-u)**3*p0[k]+3*(1-u)**2*u*p1[k]+3*(1-u)*u*u*p2[k]+u**3*p3[k] for k in (0,1))

@lru_cache(None)
def arc_table(d):
    segments=[];p=(0.,0.);total=0.
    for cmd,v in parse(d):
        if cmd=='M':p=tuple(v);continue
        if cmd=='L':
            end=tuple(v);q1=tuple(mix(a,b,1/3) for a,b in zip(p,end));q2=tuple(mix(a,b,2/3) for a,b in zip(p,end))
        elif cmd=='C':q1=tuple(v[:2]);q2=tuple(v[2:4]);end=tuple(v[4:])
        else:raise ValueError('Trim guides require M/L/C')
        controls=(p,q1,q2,end);lengths=[0.];prev=p
        for j in range(1,129):
            pt=cubic(*controls,j/128);lengths.append(lengths[-1]+math.dist(prev,pt));prev=pt
        segments.append((controls,lengths,total));total+=lengths[-1];p=end
    return segments,total

def trim(d,progress):
    """Cut the cubic at physical arc distance; no guessed pathLength/dash length."""
    segs,total=arc_table(d);target=clamp(progress)*total
    if target<=1e-6:return ''
    start=segs[0][0][0];out=[f'M{start[0]},{start[1]}']
    for (p0,p1,p2,p3),lengths,offset in segs:
        remaining=target-offset
        if remaining<=0:break
        if remaining>=lengths[-1]:u=1.
        else:
            k=next(k for k in range(1,129) if lengths[k]>=remaining)
            u=(k-1+(remaining-lengths[k-1])/(lengths[k]-lengths[k-1]))/128
        a=tuple(mix(x,y,u) for x,y in zip(p0,p1));b=tuple(mix(x,y,u) for x,y in zip(p1,p2));c=tuple(mix(x,y,u) for x,y in zip(p2,p3))
        ab=tuple(mix(x,y,u) for x,y in zip(a,b));bc=tuple(mix(x,y,u) for x,y in zip(b,c));end=tuple(mix(x,y,u) for x,y in zip(ab,bc))
        out.append('C'+' '.join(f'{x:.5f},{y:.5f}' for x,y in (a,ab,end)))
        if u<1:break
    return ' '.join(out)
