#!/usr/bin/env python3
"""Delivery QA: decode every frame, measure hold, verify vector mask coverage."""
import csv,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from animate import *
from raster import render_svg

video=ROOT/'deliverables/ji-afk-cinematic-logo-animation.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
stream=probe['streams'][0]
assert stream['codec_name']=='h264'
assert (int(stream['width']),int(stream['height']))==(1080,1080)
assert stream['avg_frame_rate']=='60/1'
assert int(stream['nb_read_frames'])==480
assert float(probe['format']['duration'])==8

# Inspect all 480 decoded frames. Read at 270px for temporal analysis.
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-vf','scale=270:270','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
frames=[];diffs=[];count=0;last=None
while True:
    raw=proc.stdout.read(270*270*3)
    if not raw: break
    assert len(raw)==270*270*3
    current=np.frombuffer(raw,dtype=np.uint8).reshape(270,270,3)
    if last is not None:
        diffs.append(float(abs(current.astype(float)-last.astype(float)).mean()))
    frames.append(current.copy())
    last=current;count+=1
assert proc.wait()==0 and count==480
source_hold=[frame(f/60) for f in (351,360,400,479)]
assert len(set(source_hold))==1, 'Unwanted motion in final hold'
hold_delta=max(diffs[360:])
assert hold_delta<.06, f'Unstable encoded final hold: {hold_delta}'

# All geometry must stay clear of the frame boundaries.
edge_delta=max(float(abs(f.astype(int)-frames[0].astype(int))[[0,-1],:,:].max()) for f in frames)
side_delta=max(float(abs(f.astype(int)-frames[0].astype(int))[:,[0,-1],:].max()) for f in frames)
assert max(edge_delta,side_delta)<10

# Check the static final source against the editable master, in the same square view.
master_square=master().replace('viewBox="0 0 1536 1383"','viewBox="0 -76.5 1536 1536"').replace('height="972.421875"','height="1080"')
static=np.asarray(render_svg(master_square,1080)).astype(int)
final=np.asarray(render_svg(frame(8),1080)).astype(int)
master_error=abs(static-final)
assert master_error.mean()<.01

# Filled interior must remain covered when the canonical outline is separated.
white='<rect width="1536" height="1383" fill="white"/>'
outline=path(OUTLINE,fill='black')
pieces=''.join(group('test-'+str(i),outline,clip_path=f'url(#{name}-clip)') for i,name in enumerate(['head','left-ear','right-ear','left-lateral','right-lateral']))
a=np.asarray(render_svg(svg(white+outline),1536,1383)).astype(int)
b=np.asarray(render_svg(svg(white+pieces),1536,1383)).astype(int)
holes=int(((a.min(axis=2)==0)&(b.max(axis=2)>1)).sum())
assert holes==0, f'{holes} uncovered silhouette pixels'

# Pen masks fully cover each letter before masks are removed.
unmasked='';masked='';masks=''
for k,d in LETTERS.items():
    masks+=stroke_mask('test-'+k,PENS[k],10,0,.6,100 if k not in ('J','K') else 111)
    glyph=path(d,fill='black',fill_rule='evenodd')
    unmasked+=glyph
    masked+=group('test-letter-'+k,glyph,mask='url(#test-'+k+')')
a=np.asarray(render_svg(svg(white+unmasked),1536,1383)).astype(int)
b=np.asarray(render_svg(svg(white+masked,masks),1536,1383)).astype(int)
mask_missing=int((abs(a-b).max(axis=2)>8).sum())
assert mask_missing==0

tree=ET.fromstring(master())
assert not list(tree.iter('{http://www.w3.org/2000/svg}image'))
assert not list(tree.iter('{http://www.w3.org/2000/svg}text'))
assert 'data:image' not in master()
groups=[e.attrib['id'] for e in tree.iter('{http://www.w3.org/2000/svg}g') if 'id' in e.attrib]
assert len(groups)>=25

with (ROOT/'qa/temporal-analysis.csv').open('w') as file:
    writer=csv.writer(file);writer.writerow(['frame','time_seconds','mean_absolute_delta_from_previous'])
    writer.writerows((i+1,(i+1)/60,d) for i,d in enumerate(diffs))

# A 6fps overview supplements the twelve large phase captures.
sheet=Image.new('RGB',(8*270,6*294),'#24151d');draw=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
except OSError: font=ImageFont.load_default()
for j,i in enumerate(range(0,480,10)):
    x=j%8*270;y=j//8*294
    sheet.paste(Image.fromarray(frames[i]),(x,y))
    draw.text((x+10,y+275),f'{i/60:05.2f}s · frame {i:03d}',font=font,fill='#f6d6df')
sheet.save(ROOT/'qa/motion-overview-48-frames.jpg',quality=94)

extra=[]
hi=ROOT/'deliverables/ji-afk-cinematic-logo-animation-2160.mp4'
if hi.exists():
    hi_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(hi)]))
    hs=hi_probe['streams'][0]
    assert hs['codec_name']=='h264' and hs['avg_frame_rate']=='60/1'
    assert (int(hs['width']),int(hs['height']))==(2160,2160)
    assert int(hs['nb_read_frames'])==480 and float(hi_probe['format']['duration'])==8
    subprocess.run(['ffmpeg','-v','error','-i',str(hi),'-f','null','-'],check=True)
    (ROOT/'qa/ffprobe-2160.json').write_text(json.dumps(hi_probe,indent=2))
    extra.append({'file':str(hi.relative_to(ROOT)),'codec':'h264','width':2160,'height':2160,
                  'fps':60,'duration_seconds':8,'decoded_frames':480,'bytes':hi.stat().st_size,
                  'sha256':hashlib.sha256(hi.read_bytes()).hexdigest()})

report={
 'result':'PASS',
 'video':{'file':str(video.relative_to(ROOT)),'codec':stream['codec_name'],'profile':stream['profile'],
          'width':1080,'height':1080,'fps':60,'duration_seconds':8,'decoded_frames':count,
          'pixel_format':stream['pix_fmt'],'audio':'intentionally silent','bytes':video.stat().st_size,
          'sha256':hashlib.sha256(video.read_bytes()).hexdigest()},
 'additional_masters':extra,
 'geometry':{'raster_images_in_svg':0,'font_dependencies':0,'named_groups':len(groups),
             'silhouette_interior_holes':holes,'letter_pen_mask_missing_pixels':mask_missing},
 'final_hold':{'source_stable_from_seconds':5.85,'duration_seconds':2.15,
               'sampled_svg_frames_identical':True,'encoded_max_mean_delta_after_6s':hold_delta},
 'master_comparison':{'method':'same square composition; source SVG frame vs editable master',
                       'mean_absolute_channel_error':float(master_error.mean()),
                       'max_channel_error_at_antialiased_edges':int(master_error.max())},
 'temporal':{'max_mean_delta':max(diffs),'time_of_max_delta':(int(np.argmax(diffs))+1)/60,
              'maximum_boundary_change':max(edge_delta,side_delta)},
 'visual_review':{'reference':'official image visible in user message; manually rebuilt',
                  'original_png_binary_available':False,
                  'review_artifacts':['contact-sheet.jpg','motion-overview-48-frames.jpg','master-full.png'],
                  'note':'Visual fidelity reviewed; no pixel equality claim against unavailable original PNG.'}
}
(ROOT/'qa/verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
