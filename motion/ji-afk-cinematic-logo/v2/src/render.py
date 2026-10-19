#!/usr/bin/env python3
"""Native 30fps SVG renderer; six temporal samples only around fast gestures."""
import argparse,json,subprocess,time,multiprocessing
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
from animate import frame,sample_count,CFG,ROOT
from raster import render_svg

LEVELS=np.arange(256,dtype=np.float32)/255
LINEAR=np.where(LEVELS<=.04045,LEVELS/12.92,((LEVELS+.055)/1.055)**2.4)

def render_frame(job):
    f,size,ss,blur=job
    count=sample_count(f) if blur else 1
    # A 120-degree centered shutter, integrated in linear light. It never spans
    # a whole frame, avoiding long trails and ghost silhouettes.
    offsets=np.linspace(-.5,.5,count)*CFG['shutter_angle']/360 if count>1 else [0]
    accum=None
    for offset in offsets:
        im=render_svg(frame(max(0,min(224,f+float(offset)))/30),size*ss)
        if ss>1:im=im.resize((size,size),Image.Resampling.LANCZOS)
        if count==1:return im.tobytes()
        lin=LINEAR[np.asarray(im)]
        if accum is None:accum=lin.copy()
        else:accum+=lin
    accum/=count
    srgb=np.where(accum<=.0031308,accum*12.92,1.055*np.power(accum,1/2.4)-.055)
    return np.uint8(np.clip(np.rint(srgb*255),0,255)).tobytes()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--draft',action='store_true')
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--output',type=str)
    args=ap.parse_args()
    size=540 if args.draft else 1080;ss=1 if args.draft else CFG['supersample']
    dest=ROOT/'work/draft-v2.mp4' if args.draft else ROOT.parent/'deliverables/ji-afk-cinematic-logo-animation-v2.mp4'
    if args.output:dest=ROOT/args.output
    dest.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{size}x{size}','-r','30','-i','-','-an','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709',
         '-c:v','libx264','-preset','slow','-crf','15','-profile:v','high','-pix_fmt','yuv420p',
         '-fps_mode','cfr','-r','30','-movflags','+faststart','-color_primaries','bt709',
         '-color_trc','bt709','-colorspace','bt709','-color_range','tv',
         '-metadata','title=JI AFK CINEMATIC | V2 | 30fps vector character animation',str(dest)]
    start=time.time()
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as enc:
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            jobs=((f,size,ss,not args.draft) for f in range(225))
            for f,data in enumerate(pool.map(render_frame,jobs,chunksize=1)):
                enc.stdin.write(data)
                if f%30==0:print(f'{f:03d}/225 · {f/30:.1f}s · {time.time()-start:.1f}s elapsed',flush=True)
        enc.stdin.close()
        if enc.wait()!=0:raise RuntimeError('FFmpeg encoder failed')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]))
    s=probe['streams'][0]
    assert s['codec_name']=='h264' and s['pix_fmt']=='yuv420p'
    assert s['avg_frame_rate']==s['r_frame_rate']=='30/1' and int(s['nb_read_frames'])==225
    assert s['width']==s['height']==size and float(probe['format']['duration'])==7.5
    subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-f','null','-'],check=True)
    if not args.draft:
        (ROOT/'qa/ffprobe-v2.json').write_text(json.dumps(probe,indent=2))
        (ROOT/'assets/ji-afk-cinematic-v2-final.svg').write_text(frame(224/30))
        (ROOT/'qa/render-settings.json').write_text(json.dumps({'version':2,'frames':225,'fps':30,'size':size,
            'spatial_supersample':ss,'temporal_samples':CFG['temporal_samples'],'shutter_angle_degrees':CFG['shutter_angle'],
            'temporal_integration':'linear-light, selective fast intervals','elapsed_seconds':time.time()-start},indent=2))
    print('PASS: 225 frames, H.264 yuv420p, 30/1 fps, 7.5 seconds; complete decode.',flush=True)

if __name__=='__main__':main()
