"""V2 · authored at 30fps. Every subframe remains editable SVG geometry."""
import math
from logo import *
from geometry import *
from rig import Rig,CFG,ROOT,value,settle

SPIRAL_GUIDE='M 808,592 C 813,553 870,548 879,586 C 893,631 825,648 828,602 C 831,579 856,581 853,599'
TIP_L='M 553,124 C 573,80 648,52 706,52 C 715,52 716,93 717,122 C 718,149 689,161 656,163 L 655,153 L 695,149 C 709,146 706,114 705,98'
TIP_R='M 937,199 C 930,176 969,164 1016,157 C 1020,170 1022,189 1021,199 L 1005,202'

PENS={
 'J':['M 326,905 L 326,1062','M 326,1050 C 326,1128 305,1150 263,1150 C 211,1150 209,1128 213,1085 L 218,1061 L 267,1061'],
 'I':['M 468,1176 L 468,900'],
 'A':['M 675,1176 L 776,929 L 871,1176','M 711,1097 L 836,1097'],
 'F':['M 965,1176 L 964,940 L 1120,940','M 970,1034 L 1111,1034'],
 'K':['M 1173,1176 L 1173,900','M 1329,901 C 1302,1001 1278,1036 1174,1049','M 1249,1048 L 1330,1174']
}
LETTER_CENTERS={'J':270,'I':468,'A':773,'F':1015,'K':1240}
LETTER_Y=Track([[0,57],[8,-13],[13,4],[19,0],[40,0]])
LETTER_ROLL=Track([[0,-1.7],[9,.6],[15,-.15],[21,0],[40,0]])

def pen_mask(name,guides,progresses,fn=lambda x,y:(x,y),width=110):
    ink=''
    for d,q in zip(guides,progresses):
        part=trim(d,q)
        if part:
            ink+=path(warp(part,fn),fill='none',stroke='white',stroke_width=width,stroke_linecap='round',stroke_linejoin='round')
    return f'<mask id="{name}" maskUnits="userSpaceOnUse" x="0" y="-76.5" width="1536" height="1536">{ink}</mask>'

def glyph_transform(letter,f,start):
    q=f-start;cx=LETTER_CENTERS[letter]
    def fn(x,y):
        if letter=='J':
            w=smooth((y-1030)/120)*(1-smooth((x-265)/65))
            x,y=rotate(x,y,290,1090,settle(f,start+8,6,12,7)*w)
        x,y=rotate(x,y,cx,1166,LETTER_ROLL(q)*(-1 if letter in ('A','K') else 1))
        return x,y+LETTER_Y(q)
    return fn

def frame(t):
    f=clamp(t*30,0,225);rig=Rig(f)
    outline=warp(OUTLINE,rig.anatomy)
    radius=value('reveal_radius',f)
    muzzle=rig.muzzle(740,730)
    reveal=f'<ellipse cx="{muzzle[0]:.5f}" cy="{muzzle[1]:.5f}" rx="{radius*1.12:.5f}" ry="{radius:.5f}"/>'
    defs=f'<clipPath id="head-boundary">{path(outline)}</clipPath><clipPath id="body-reveal">{reveal}</clipPath>'
    early=''
    if f<100:
        for side,guide,start in [('left',TIP_L,8),('right',TIP_R,12)]:
            ink=trim(guide,bezier_ease((f-start)/20,.25,.3,.3,1))
            if ink:
                early+=group(side+'-ear-growth',path(warp(ink,rig.anatomy),fill='none',stroke='url(#red)',stroke_width=24,stroke_linecap='round',stroke_linejoin='round'))
    positive=''
    defs+=f'<mask id="positive-ear-field" maskUnits="userSpaceOnUse" x="0" y="-76.5" width="1536" height="1536">{positive}{reveal.replace("/>"," fill=\"white\"/>")}</mask>'
    body=group('background','<rect x="0" y="-76.5" width="1536" height="1536" fill="url(#pink)"/>')
    # One restrained illumination pulse, tied to the impact envelope.
    pulse=.06*math.exp(-((f-90)/3.1)**2)
    if pulse>1e-5:
        defs+='<radialGradient id="impact-light"><stop stop-color="#fff8df"/><stop offset="1" stop-color="#fff8df" stop-opacity="0"/></radialGradient>'
        body+=f'<ellipse cx="750" cy="700" rx="800" ry="760" fill="url(#impact-light)" opacity="{pulse:.6f}"/>'
    fox=group('nose-muzzle',path(warp(NOSE,rig.muzzle),fill='url(#red)'),clip_path='url(#body-reveal)')
    fox+=group('ears-born-from-bases',early,clip_path='url(#head-boundary)')
    fox+=group('continuous-face-and-cheek-surface',path(outline,fill='url(#red)'),clip_path='url(#body-reveal)')
    # Ear ornament growth follows its bone three frames later; later curl motion
    # is a nonlinear deformation of control points, never a displaced PNG.
    ornaments=''
    for side,d in [('left',LEFT_ORNAMENT),('right',RIGHT_ORNAMENT)]:
        delayed=Rig(f-3)
        fn=lambda x,y:delayed.anatomy(x,y,True) if f<43 else rig.anatomy(x,y,True)
        if value(side+'_growth',f-3)>.002:
            shape=warp(d,fn)
            ornaments+=group(side+'-curl-negative',path(shape,fill='url(#red)'))
            ornaments+=group(side+'-curl-positive',path(shape,fill='url(#pink)'),mask='url(#positive-ear-field)')
    fox+=group('ear-ribbons',ornaments,clip_path='url(#head-boundary)')
    # Real eye ink is revealed by distance along the central spiral curve.
    for side,d in [('cross',CROSS),('spiral',SPIRAL)]:
        eye=rig.eye(side);gaze,far,width,entry,height=rig.eye_metrics(side)
        if entry<=.0001:continue
        shape=warp(d,eye)
        attributes={}
        if side=='spiral' and f<35:
            progress=bezier_ease((f-7)/22,.36,.08,.32,1)
            defs+=pen_mask('spiral-real-ink',[SPIRAL_GUIDE],[progress],eye,36*entry)
            attributes['mask']='url(#spiral-real-ink)'
        # A curved cheek occluder trims only the distant edge; the symbol remains legible.
        if far>.001:
            cx,cy=(617,585) if side=='cross' else (845,593)
            edge=(70 if side=='cross' else 48)-far*(4 if side=='cross' else 3)
            boundary=f'M {cx-130},{cy-120} H {cx+edge-12} C {cx+edge+5},{cy-45} {cx+edge+5},{cy+45} {cx+edge-12},{cy+120} H {cx-130} Z'
            if side=='cross':
                boundary=f'M {cx+130},{cy-120} H {cx-edge+12} C {cx-edge-5},{cy-45} {cx-edge-5},{cy+45} {cx-edge+12},{cy+120} H {cx+130} Z'
            defs+=f'<clipPath id="{side}-occlusion">{path(warp(boundary,eye))}</clipPath>'
            attributes['clip_path']=f'url(#{side}-occlusion)'
        ink=group(side+'-dark',path(shape,fill='url(#red)'))
        ink+=group(side+'-light',path(shape,fill='#fff8df'),clip_path='url(#body-reveal)')
        fox+=group(side+'-eye-plane',ink,**attributes)
    body+=group('fox-2-5D-rig',fox,transform=rig.global_transform())
    # Individual real glyphs have pen structure, trajectory and overshoot.
    title=''
    for i,(letter,d) in enumerate(LETTERS.items()):
        start=111+i*2
        if f<start:continue
        fn=glyph_transform(letter,f,start)
        qs=[bezier_ease((f-start-j*2)/12,.18,.32,.18,1) for j in range(len(PENS[letter]))]
        defs+=pen_mask('letter-mask-'+letter,PENS[letter],qs,fn,111 if letter in ('J','K') else 104)
        title+=group('letter-'+letter,path(warp(d,fn),fill='url(#red)',fill_rule='evenodd'),mask='url(#letter-mask-'+letter+')' if f<start+22 else 'none')
    body+=group('kinetic-JI-AFK',title)
    subtitle=''
    for i,(c,x,y,w,h) in enumerate(SUBTITLE):
        start=142+abs(i-4)*.65
        q=bezier_ease((f-start)/12,.2,.8,.2,1)
        if q<=1e-5:continue
        tracking=value('tracking',f);cx=x+w/2
        tx=784+(cx-784)*tracking-w/2
        dy=15*(1-q)-1.8*math.sin(math.pi*q)
        glyph=path(GLYPHS[c],fill='url(#red)',fill_rule='evenodd')
        subtitle+=group(f'subtitle-{i}-{c}',glyph,opacity=f'{q:.6f}',transform=f'translate({tx:.6f} {y+dy:.6f}) scale({w/100} {h/100})')
    body+=group('tracking-CINEMATIC',subtitle)
    return svg(body,defs,square=True)

def sample_count(f):
    return CFG['temporal_samples'] if any(a<=f<=b for a,b in [(2,38),(47,66),(77,108),(111,143),(159,168)]) else 1

if __name__=='__main__':
    (ROOT/'assets/ji-afk-cinematic-v2-final.svg').write_text(frame(224/30))
