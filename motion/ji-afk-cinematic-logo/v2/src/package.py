#!/usr/bin/env python3
"""Build a self-contained reproducible V2 delivery without caches or scratch files."""
from pathlib import Path
import hashlib,zipfile
from rig import ROOT
project=ROOT.parent
files=[project/x for x in ['README.md','README-V1.md','CHANGELOG.md','preview.html','preview-v1.html']]
files += [p for p in ROOT.rglob('*') if p.is_file() and not any(x in ('work','__pycache__') for x in p.relative_to(ROOT).parts) and p.suffix!='.pyc']
files += [project/'deliverables'/x for x in ['ji-afk-cinematic-logo-animation-v2.mp4','ji-afk-cinematic-logo-animation.mp4']]
files=sorted(set(files));dest=project/'deliverables/ji-afk-cinematic-logo-project-v2.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:
        item=zipfile.ZipInfo('ji-afk-cinematic-logo/'+p.relative_to(project).as_posix(),date_time=(2026,10,19,0,0,0))
        item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
        z.writestr(item,p.read_bytes())
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
sums=[]
for p in [project/'deliverables/ji-afk-cinematic-logo-animation-v2.mp4',ROOT/'assets/ji-afk-cinematic-v2-final.svg',dest]:
    sums.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(project).as_posix())
(project/'deliverables/SHA256SUMS-V2.txt').write_text('\n'.join(sums)+'\n')
print(f'{dest.name}: {len(files)} files, {dest.stat().st_size} bytes; archive integrity PASS')
