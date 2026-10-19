#!/usr/bin/env python3
"""Decode both deliverables, compare exact times and audit geometry/rig/encoding."""
import csv,hashlib,json,subprocess,struct,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from animate import *
from render import render_frame
from raster import render_svg

VIDEO=ROOT.parent/'deliverables/ji-afk-cinematic-logo-animation-v2.mp4'
V1=ROOT.parent/'deliverables/ji-afk-cinematic-logo-animation.mp4'
QA=ROOT/'qa'
TIMES=[.4,1.2,1.8,2.5,2.9,3,3.1,4.2,5,5.4,6.5,7.3]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(video,v1=False):
    vf=('select=not(mod(n\\,2)),' if v1 else '')+'scale=270:270:flags=lanczos'
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',vf,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
    return np.frombuffer(raw,np.uint8).reshape(-1,270,270,3)
def png_at(video,f,dest):
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(dest)],check=True)
def atoms(p):
    result=[]
    with p.open('rb') as f:
        while True:
            offset=f.tell();head=f.read(8)
            if len(head)<8:break
            size,kind=struct.unpack('>I4s',head)
            if size==1:size=struct.unpack('>Q',f.read(8))[0]
            result.append({'kind':kind.decode(),'offset':offset,'bytes':size})
            if not size:break
            f.seek(offset+size)
    return result

def main():
    QA.mkdir(exist_ok=True);(QA/'frames').mkdir(exist_ok=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)]))
    s=probe['streams'][0]
    assert (s['width'],s['height'],s['avg_frame_rate'],s['r_frame_rate'],s['pix_fmt'],s['codec_name'],int(s['nb_read_frames']))==(1080,1080,'30/1','30/1','yuv420p','h264',225)
    assert len(probe['streams'])==1 and float(probe['format']['duration'])==7.5
    pts=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(VIDEO)]))
    timestamps=np.array([float(x['best_effort_timestamp_time']) for x in pts['frames']])
    assert len(timestamps)==225 and np.max(np.abs(timestamps-np.arange(225)/30))<1e-6
    boxes=atoms(VIDEO);kinds=[x['kind'] for x in boxes];assert kinds.index('moov')<kinds.index('mdat')
    subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-'],check=True)
    v2=decode(VIDEO);assert len(v2)==225
    v1=decode(V1,True) if V1.exists() else None
    font=ImageFont.truetype(FONT,21)
    if v1 is not None:
        for block in range(3):
            sheet=Image.new('RGB',(1080,4*576),'#25131b');draw=ImageDraw.Draw(sheet)
            for row,t in enumerate(TIMES[block*4:(block+1)*4]):
                f=round(t*30)
                for col,seq in enumerate([v1,v2]):
                    im=Image.fromarray(seq[f]).resize((540,540),Image.Resampling.LANCZOS)
                    sheet.paste(im,(col*540,row*576+36));draw.text((col*540+16,row*576+7),f'V{col+1}  |  {t:.2f} s  |  frame {round(t*(60 if col==0 else 30))}',font=font,fill='white')
            sheet.save(QA/f'comparison-v1-v2-{block+1:02d}.jpg',quality=95)
    for t in TIMES:png_at(VIDEO,round(t*30),QA/'frames'/f'v2-{t:04.1f}s.png')
    png_at(VIDEO,224,QA/'poster-v2.png')
    impact=Image.new('RGB',(7*270,4*298),'#25131b');draw=ImageDraw.Draw(impact)
    for i,f in enumerate(range(78,106)):
        x=i%7*270;y=i//7*298;impact.paste(Image.fromarray(v2[f]),(x,y+28))
        draw.text((x+8,y+3),f'{f:03d} | {f/30:.3f}s',font=font,fill='white')
    impact.save(QA/'impact-frames-078-105.jpg',quality=95)
    # Compare every actual decoded frame, separating character and type areas.
    def deltas(seq):
        diff=np.abs(np.diff(seq.astype(np.float32),axis=0))
        return {'whole':diff.mean(axis=(1,2,3)),'character':diff[:,:170].mean(axis=(1,2,3)),'type':diff[:,170:].mean(axis=(1,2,3))}
    d2=deltas(v2);d1=deltas(v1[:225]) if v1 is not None else None
    stages=[(0,30,'entry'),(30,66,'yaw'),(66,87,'anticipation'),(87,111,'impact'),(111,153,'typography'),(153,177,'blink/residual'),(177,212,'settle'),(212,225,'hero hold')]
    density=[]
    for a,b,label in stages:
        row={'stage':label,'start_frame':a,'end_exclusive':b}
        for version,d in [('v2',d2),('v1',d1)]:
            if d is None:continue
            q=d['character'][a:b-1]
            row[version+'_character_mean_abs_delta']=float(q.mean())
            row[version+'_character_transitions_over_0_005']=int(np.count_nonzero(q>.005))
        density.append(row)
    with (QA/'motion-density.csv').open('w') as out:
        w=csv.DictWriter(out,fieldnames=density[0].keys());w.writeheader();w.writerows(density)
    fig,axes=plt.subplots(3,1,figsize=(12,8),layout='constrained')
    seconds=np.arange(1,225)/30
    for name,ax in zip(['whole','character','type'],axes):
        if d1 is not None:ax.plot(seconds,d1[name],label='V1 (sampled for comparison only)',color='#999',lw=1)
        ax.plot(seconds,d2[name],label='V2 native 30 fps',color='#aa0926',lw=1.4)
        ax.axvline(3,color='#df9562',ls='--');ax.axvspan(212/30,7.5,color='#e5e2e3');ax.set(xlabel='Seconds',ylabel='Mean RGB delta (0–255 levels)',title=name)
        ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(QA/'motion-density.png',dpi=140);plt.close(fig)
    metrics=[Rig(f).metrics() for f in range(225)]
    with (QA/'rig-curves.csv').open('w') as out:
        w=csv.DictWriter(out,fieldnames=metrics[0].keys());w.writeheader();w.writerows(metrics)
    fig,axes=plt.subplots(3,1,figsize=(12,8),layout='constrained')
    for names,ax in zip([['yaw_degrees','left_ear_bend_degrees','right_ear_bend_degrees'],['scale','squash_x','squash_y'],['cross_width','spiral_width','cross_blink']],axes):
        for name in names:ax.plot(np.arange(225)/30,[m[name] for m in metrics],label=name,lw=1.2)
        ax.axvline(3,color='#aa0926',ls='--');ax.legend(fontsize=8);ax.grid(alpha=.2);ax.set_xlabel('Seconds')
    fig.savefig(QA/'rig-curves.png',dpi=140);plt.close(fig)
    # Meaningful source checks: no embedded bitmaps or font dependencies, masks
    # cover the entire final glyph, stable hold and deterministic regeneration.
    final=frame(224/30);tree=ET.fromstring(final)
    tags=[el.tag.split('}')[-1] for el in tree.iter()]
    assert 'image' not in tags and 'text' not in tags
    assert all(frame(f/30)==final for f in range(212,225))
    for f in range(88,112):
        rig=Rig(f)
        for x,y in [(662,735),(701,691),(778,692),(822,730)]:
            assert math.dist(rig.muzzle(x,y),rig.anatomy(x,y))<1e-9
    bg=svg('<rect x="0" y="-76.5" width="1536" height="1536" fill="url(#pink)"/>',square=True)
    assert render_svg(frame(0),540).tobytes()==render_svg(bg,540).tobytes(), 'Opening contains premature dots'
    coverage={}
    for k,d in {**LETTERS,'spiral':SPIRAL}.items():
        guides=[SPIRAL_GUIDE] if k=='spiral' else PENS[k]
        width=36 if k=='spiral' else (111 if k in ('J','K') else 104)
        defs=pen_mask('coverage',guides,[1]*len(guides),width=width)
        shape=path(d,fill='white',fill_rule='evenodd')
        black='<rect x="0" y="-76.5" width="1536" height="1536" fill="black"/>'
        reference=np.asarray(render_svg(svg(black+shape,square=True),1080))[:,:,0]
        masked=np.asarray(render_svg(svg(black+'<g mask="url(#coverage)">'+shape+'</g>',defs,square=True),1080))[:,:,0]
        coverage[k]=int(np.count_nonzero((reference>250)&(masked<250)))
    assert max(coverage.values())==0
    master_xml=master().replace('viewBox="0 0 1536 1383"','viewBox="0 -76.5 1536 1536"')
    # librsvg render function normalizes target to square; replace explicit height too.
    master_xml=master_xml.replace('height="972.421875"','height="1080"')
    final_im=np.asarray(render_svg(final,1080)).astype(np.float32)
    master_im=np.asarray(render_svg(master_xml,1080)).astype(np.float32)
    diff=np.abs(final_im-master_im)
    reproducible={}
    for f in [36,90,162,224]:
        a=render_frame((f,1080,2,True));b=render_frame((f,1080,2,True))
        assert a==b;reproducible[str(f)]=hashlib.sha256(a).hexdigest()
    report={'result':'PASS','video':{'file':str(VIDEO.relative_to(ROOT.parent)),'sha256':sha(VIDEO),'bytes':VIDEO.stat().st_size,'width':1080,'height':1080,'fps':'30/1','frames':225,'duration_seconds':7.5,'codec':'h264','pix_fmt':'yuv420p','audio_streams':0,'faststart':True,'all_frame_pts_verified':True,'full_decode_errors':0},'mp4_atoms':boxes,'geometry':{'embedded_raster':0,'font_dependencies':0,'spiral_guide_length_svg_units':arc_table(SPIRAL_GUIDE)[1],'completed_mask_missing_pixels':coverage,'opening_exact_background':True},'final_hold':{'start_frame':212,'end_frame':224,'source_svgs_identical':True,'duration_seconds':13/30,'encoded_character_max_mean_delta':float(d2['character'][212:].max())},'master_comparison':{'reference':'V1 vector master; NOT original PNG','mean_absolute_channel_error':float(diff.mean()),'max_channel_error':float(diff.max())},'deterministic_rerender_rgb_sha256':reproducible,'motion_density':density,'source_reference':{'original_png_binary_available':False,'method':'Canonical V1 Bezier geometry preserved; official image in conversation used for visual reference.'}}
    (QA/'verification-v2.json').write_text(json.dumps(report,indent=2))
    (QA/'ffprobe-v2.json').write_text(json.dumps(probe,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
