#!/usr/bin/env python3
"""Play the real MP4 to completion in Chromium and capture presented video frames."""
import argparse,functools,http.server,json,threading,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from playwright.sync_api import sync_playwright
from rig import ROOT

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--draft',action='store_true');args=ap.parse_args()
    rel='v2/work/draft-v2.mp4' if args.draft else 'deliverables/ji-afk-cinematic-logo-animation-v2.mp4'
    out=ROOT/'work/draft-playback' if args.draft else ROOT/'qa/playback'
    out.mkdir(parents=True,exist_ok=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*a):pass
    handler=functools.partial(Handler,directory=str(ROOT.parent))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required'])
        page=browser.new_page(viewport={'width':1120,'height':1120})
        page.goto(f'http://127.0.0.1:{server.server_port}/')
        page.set_content(f'<html><body style="margin:0;background:#20141a"><video id="v" src="http://127.0.0.1:{server.server_port}/{rel}" width="1080" height="1080" muted playsinline preload="auto"></video></body></html>')
        result=page.evaluate('''async () => {
          const v=document.querySelector('#v');
          if(v.readyState<1) await new Promise((ok,bad)=>{v.onloadedmetadata=ok;v.onerror=bad});
          const frames=[];
          let active=true;
          function grab(now,meta){
            frames.push({frame:Math.round(meta.mediaTime*30),time:meta.mediaTime,presented:meta.presentedFrames});
            if(active)v.requestVideoFrameCallback(grab);
          }
          v.requestVideoFrameCallback(grab);
          const ended=new Promise((ok,bad)=>{v.onended=ok;v.onerror=bad});
          const start=performance.now();await v.play();await ended;active=false;
          const quality=v.getVideoPlaybackQuality();
          return {ended:v.ended,duration:v.duration,elapsed_ms:performance.now()-start,totalVideoFrames:quality.totalVideoFrames,droppedVideoFrames:quality.droppedVideoFrames,frames};
        }''')
        page.screenshot(path=str(out/'player-ended.png'))
        browser.close()
    server.shutdown()
    captured=result.pop('frames')
    unique={x['frame']:x for x in captured}
    result['captured_frame_indices']=sorted(unique)
    result['missing_frame_indices']=sorted(set(range(225))-set(unique))
    result['file_sha256']=hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()
    assert result['ended'] and result['duration']==7.5
    assert result['totalVideoFrames']==225 and result['droppedVideoFrames']==0
    # Browser callbacks may coalesce under headless scheduling. Keep their exact
    # indices in the report; inspect every decoded frame separately, with no
    # PNG serialization in the real-time playback callback.
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT.parent/rel),'-vf','scale=180:180','-f','rawvideo','-pix_fmt','rgb24','-'])
    assert len(raw)==225*180*180*3
    result['contact_sheet_source']='All 225 decoded MP4 frames; browser playback telemetry recorded separately.'
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    for block in range(5):
        sheet=Image.new('RGB',(9*180,5*202),'#24151d');draw=ImageDraw.Draw(sheet)
        for j in range(45):
            f=block*45+j;x=j%9*180;y=j//9*202
            im=Image.frombytes('RGB',(180,180),raw[f*180*180*3:(f+1)*180*180*3])
            sheet.paste(im,(x,y))
            draw.text((x+7,y+183),f'{f:03d} | {f/30:.2f}s',font=font,fill='white')
        sheet.save(out/f'playback-{block+1:02d}.jpg',quality=95)
    (out/'playback-report.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='captured_frame_indices'},indent=2))

if __name__=='__main__':main()
