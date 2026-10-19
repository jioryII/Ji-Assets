"""Deterministic 60fps vector choreography. Time values are seconds.

Every frame is assembled as an SVG: Béziers, clipping geometry, affine layers,
eye parallax, delayed ears, and independent stroke masks for each real glyph.
"""
import json, math
from pathlib import Path
from logo import *

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'src/timeline.json').read_text())

def clamp(v): return max(0,min(1,v))
def smooth(v):
    v=clamp(v)
    return v*v*v*(10+v*(-15+6*v))
def phase(t,a,b): return smooth((t-a)/(b-a))
def mix(a,b,u): return a+(b-a)*u
def color(a,b,u):
    aa=[int(a[i:i+2],16) for i in (1,3,5)]
    bb=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(mix(x,y,u)):02x}' for x,y in zip(aa,bb))
def head(t):
    keys=CFG['head_keys']
    for a,b in zip(keys,keys[1:]):
        if a[0]<=t<=b[0]:
            u=smooth((t-a[0])/(b[0]-a[0]))
            return [mix(x,y,u) for x,y in zip(a[1:],b[1:])]
    return keys[-1][1:]
def transform(v,cx=740,cy=550):
    x,y,r,sx,sy=v
    return f'translate({cx+x:.5f} {cy+y:.5f}) rotate({r:.5f}) scale({sx:.7f} {sy:.7f}) translate({-cx} {-cy})'
def ear_transform(t,left=True):
    # Small reactive rotations, delayed from the leading head pose.
    now=head(t)[2]; lag=head(max(0,t-(.13 if left else .19)))[2]
    extra=(lag-now)*(.48 if left else .62)
    extra+=math.sin((t-3.3)*20)*math.exp(-max(0,t-3.3)*8)*(.7 if left else -.5) if 3.3<t<3.96 else 0
    px,py=(582,413) if left else (953,425)
    return f'rotate({extra:.5f} {px} {py})'

def stroke_mask(name, paths, t, start, duration, width):
    # Each segment is a separate pen pass. Rounded caps disappear once complete.
    body=''
    for i,(d,length) in enumerate(paths):
        u=phase(t,start+i*.13,start+i*.13+duration)
        if u>0:
            body+=path(d,fill='none',stroke='white',stroke_width=width,
                       stroke_linecap='round',stroke_linejoin='round',
                       stroke_dasharray=f'{length} {length}',stroke_dashoffset=length*(1-u))
    return f'<mask id="{name}" maskUnits="userSpaceOnUse" x="0" y="0" width="1536" height="1383">{body}</mask>'

PENS={
 'J': [('M 326,905 L 326,1062 C 326,1128 305,1150 263,1150 C 211,1150 209,1128 213,1085 L 218,1061 L 267,1061',450)],
 'I': [('M 468,1176 L 468,900',276)],
 'A': [('M 675,1176 L 776,929 L 871,1176',550),('M 711,1097 L 836,1097',125)],
 'F': [('M 965,1176 L 964,940 L 1120,940',410),('M 970,1034 L 1111,1034',141)],
 'K': [('M 1173,1176 L 1173,900',276),('M 1329,901 C 1302,1001 1278,1036 1174,1049',220),('M 1249,1048 L 1330,1174',150)]
}

def frame(t):
    t=max(0,min(CFG['duration'],t))
    v=head(t)
    reveal=phase(t,3.08,3.76)
    # The primary reveal is a growing lens, never a global opacity fade.
    rr=1000*reveal
    defs=f'<clipPath id="reveal"><ellipse cx="737" cy="572" rx="{rr*1.12:.5f}" ry="{rr:.5f}"/></clipPath>'
    body=group('background','<rect x="0" y="-76.5" width="1536" height="1536" fill="url(#pink)"/>')
    fox=group('nose',path(NOSE,fill='url(#red)'),clip_path='url(#reveal)')
    # Clipped fragments retain the exact canonical contour at rest.
    silhouette=group('silhouette',path(OUTLINE,fill='url(#red)'),clip_path='url(#head-clip)')
    silhouette+=group('left-ear',group('left-ear-contour',path(OUTLINE,fill='url(#red)'),clip_path='url(#left-ear-clip)'),transform=ear_transform(t,True))
    silhouette+=group('right-ear',group('right-ear-contour',path(OUTLINE,fill='url(#red)'),clip_path='url(#right-ear-clip)'),transform=ear_transform(t,False))
    silhouette+=group('lateral-details',''.join(group(side+'-lateral',path(OUTLINE,fill='url(#red)'),clip_path=f'url(#{side}-lateral-clip)') for side in ('left','right')))
    fox+=group('silhouette-reveal',silhouette,clip_path='url(#reveal)')
    # Original ear curls appear as burgundy islands in negative space.
    # Their color joins the pink openings as the red silhouette reaches them.
    for side,d,cx,cy in [('left',LEFT_ORNAMENT,522,320),('right',RIGHT_ORNAMENT,945,390)]:
        start=.18 if side=='left' else .36
        q=phase(t,start,start+.68)
        earcolor=color('#a80720','#f5a3aa',phase(t,3.19,3.54))
        fill='url(#pink)' if t>=3.54 else earcolor
        defs+=f'<clipPath id="{side}-ornament-build"><ellipse cx="{cx}" cy="{cy}" rx="{220*q:.5f}" ry="{280*q:.5f}"/></clipPath>'
        fox+=group(side+'-ear-ornament',path(d,fill=fill),clip_path=f'url(#{side}-ornament-build)',transform=ear_transform(t,side=='left'))
    # Minimal curved tips contextualize the isolated ornaments. They retract
    # into the geometric reveal rather than floating away as decoration.
    hints=[('left-tip','M 543,116 C 561,76 632,44 706,43 C 717,42 721,48 722,63',205),
           ('right-tip','M 930,182 C 927,168 968,156 1015,151 C 1022,150 1025,157 1025,175',117)]
    for i,(name,d,length) in enumerate(hints):
        u=phase(t,.32+i*.18,.98+i*.18)
        out=1-phase(t,3.10,3.48)
        if out>0 and u>0:
            fox+=group(name,path(d,fill='none',stroke='#a80720',stroke_width=6.5*out,stroke_linecap='round',stroke_dasharray=f'{length} {length}',stroke_dashoffset=length*(1-u)),transform=ear_transform(t,i==0))
    # Independent cross and spiral builds; the spiral is always the official shape.
    eye_color=color('#a80720','#fff8df',phase(t,3.10,3.28))
    px=-v[2]*2.2
    py=abs(v[2])*.32
    eyes=''
    eye_q=phase(t,.04,.60)
    defs+=f'<clipPath id="cross-build"><rect x="{617-85*eye_q:.5f}" y="{585-85*eye_q:.5f}" width="{170*eye_q:.5f}" height="{170*eye_q:.5f}"/></clipPath>'
    eyes+=group('cross-eye',path(CROSS,fill=eye_color),clip_path='url(#cross-build)')
    # Wedge reveal around the real spiral, using a vector stroke mask.
    spiral_guide='M 808,592 C 813,553 870,548 879,586 C 893,631 825,648 828,602 C 831,579 856,581 853,599'
    defs+=stroke_mask('spiral-build',[(spiral_guide,265)],t,.18,.64,34)
    eyes+=group('spiral-eye',path(SPIRAL,fill=eye_color),mask='url(#spiral-build)' if t<1.05 else 'none')
    fox+=group('eye-parallax',eyes,transform=f'translate({px:.5f} {py:.5f})')
    body+=group('fox-rig',fox,transform=transform(v))
    title=''
    for i,(letter,d) in enumerate(LETTERS.items()):
        start=3.92+i*.115
        name='build-'+letter
        defs+=stroke_mask(name,PENS[letter],t,start,.61,100 if letter not in ('J','K') else 111)
        # Mask is removed after the last pass, ensuring exact final contours.
        end=start+.61+.13*(len(PENS[letter])-1)
        title+=group('letter-'+letter,path(d,fill='url(#red)',fill_rule='evenodd'),mask=f'url(#{name})' if t<end+.05 else 'none')
    body+=group('JI-AFK',title)
    sub=''
    for i,(c,x,y,w,h) in enumerate(SUBTITLE):
        start=5.12+i*.035
        q=phase(t,start,start+.35)
        defs+=f'<clipPath id="sub-{i}"><rect x="{x-2}" y="{y+h*(1-q):.6f}" width="{w+4}" height="{h*q+1 if q else 0:.6f}"/></clipPath>'
        glyph=path(GLYPHS[c],fill='url(#red)',fill_rule='evenodd',transform=f'translate({x} {y}) scale({w/100} {h/100})')
        sub+=group(f'subtitle-{i}-{c}',glyph,clip_path=f'url(#sub-{i})')
    body+=group('CINEMATIC',sub)
    return svg(body,defs,square=True)
