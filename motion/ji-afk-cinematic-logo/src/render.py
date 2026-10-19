#!/usr/bin/env python3
"""Render all frames from SVG geometry and encode a real H.264 MP4."""
import argparse, json, subprocess, time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from animate import frame,CFG,ROOT
from raster import render_svg
from logo import master

parser=argparse.ArgumentParser()
parser.add_argument('--size',type=int,default=CFG['resolution'])
parser.add_argument('--supersample',type=int,default=CFG['supersample'])
parser.add_argument('--output',type=Path,default=ROOT/'deliverables/ji-afk-cinematic-logo-animation.mp4')
parser.add_argument('--crf',type=int,default=16)
parser.add_argument('--qa-only',action='store_true')
parser.add_argument('--skip-qa',action='store_true',help='Encode an additional master without overwriting the delivery QA')
args=parser.parse_args()
args.output.parent.mkdir(parents=True,exist_ok=True)
(ROOT/'assets/ji-afk-cinematic-master.svg').write_text(master())

fps=CFG['fps'];n=round(CFG['duration']*fps)
if not args.qa_only:
    cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-vcodec','rawvideo',
         '-pix_fmt','rgb24','-s',f'{args.size}x{args.size}','-r',str(fps),'-i','-',
         '-an','-c:v','libx264','-preset','slow','-crf',str(args.crf),'-pix_fmt','yuv420p',
         '-profile:v','high','-movflags','+faststart','-color_primaries','bt709',
         '-color_trc','bt709','-colorspace','bt709',
         '-metadata','title=JI AFK CINEMATIC | Vector logo animation',str(args.output)]
    start=time.time()
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
        for f in range(n):
            im=render_svg(frame(f/fps),args.size*args.supersample)
            if args.supersample>1:
                im=im.resize((args.size,args.size),Image.Resampling.LANCZOS)
            proc.stdin.write(im.tobytes())
            if f%60==0: print(f'{f:3d}/{n} | {f/fps:.1f}s | elapsed {time.time()-start:.1f}s',flush=True)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('FFmpeg encoding failed')
    print(f'Encoded {n} frames: {args.output}',flush=True)

if args.skip_qa:
    raise SystemExit(0)

# Key images are decoded from the actual encoded delivery, not just source previews.
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
shots=[(.35,'Despertar'),(.85,'Rasgos'),(1.38,'Curiosidad izquierda'),(2.28,'Respuesta derecha'),
       (3.08,'Anticipacion'),(3.38,'Revelado geometrico'),(3.80,'Asentamiento'),
       (4.20,'Construccion JI'),(4.65,'Construccion AFK'),(5.40,'Subtitulo'),(5.90,'Marca completa'),(7.98,'Hold final')]
sheet=Image.new('RGB',(4*360,3*400),'#24151d')
draw=ImageDraw.Draw(sheet)
try:
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:
    font=ImageFont.load_default(size=15)
for i,(t,label) in enumerate(shots):
    dest=qa/f'{i+1:02d}-{t:04.2f}s.png'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(args.output),'-frames:v','1',str(dest)],check=True)
    im=Image.open(dest).resize((360,360),Image.Resampling.LANCZOS)
    x=i%4*360;y=i//4*400
    sheet.paste(im,(x,y))
    draw.text((x+12,y+372),f'{t:04.2f}s  {label}',font=font,fill='#f8dbe1')
sheet.save(qa/'contact-sheet.jpg',quality=95)
(qa/'final-frame.svg').write_text(frame((n-1)/fps))
render_svg(master(),1536,1383).save(qa/'master-full.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(args.output)]))
(qa/'ffprobe.json').write_text(json.dumps(probe,indent=2))
s=probe['streams'][0]
assert s['codec_name']=='h264'
assert int(s['width'])==args.size and int(s['height'])==args.size
assert s['avg_frame_rate']=='60/1'
assert int(s['nb_read_frames'])==n
assert abs(float(probe['format']['duration'])-CFG['duration'])<.001
subprocess.run(['ffmpeg','-v','error','-i',str(args.output),'-f','null','-'],check=True)
print('Verified H.264, dimensions, 60fps, 8s, 480 decoded frames and full decode.',flush=True)
