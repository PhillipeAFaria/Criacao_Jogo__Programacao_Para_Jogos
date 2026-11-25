import os
"""Lossless encoding and hashed, on-demand assets. Never touches source artwork."""
from pathlib import Path
from PIL import Image
import json,hashlib,tarfile,zipfile,shutil
from functools import lru_cache
ROOT=Path(os.environ["FDM_WEB_WORKSPACE"]).resolve()
def optimize():
 stage=ROOT/'web_game';out=stage/'build/web';source=ROOT/'assets/web_clips'
 meta=json.loads((source/'clips.json').read_text(encoding='utf-8'))
 chunks=out/'chunks';chunks.mkdir(exist_ok=True)
 pages=[];downloads={};total=0
 original_pages=meta['pages'];original_rects=meta['rects']
 rects=[None]*len(original_rects)
 @lru_cache(maxsize=2)
 def read_page(number):return Image.open(source/original_pages[number]).convert('RGBA')
 def save_page(image):
  nonlocal total
  stem=f'atlas_{len(pages):03d}'
  temp=chunks/(stem+'.png')
  image.save(temp,optimize=True,compress_level=9)
  assert Image.open(temp).convert('RGBA').tobytes()==image.tobytes(),stem
  raw=temp.read_bytes();digest=hashlib.sha256(raw).hexdigest()
  name=stem+'-'+digest[:16]+'.png';dest=chunks/name
  temp.replace(dest);pages.append(name)
  downloads[name]={'url':'chunks/'+name,'sha256':digest,'bytes':len(raw)};total+=len(raw)
 for region in ('city','desert','beach'):
  indices=sorted({i for actor,states in meta['actors'].items() if actor.startswith(region+'_') for spec in states.values() for i in spec['frames']})
  image=Image.new('RGBA',(2048,2048));x=y=row_height=0
  for i in indices:
   old,ox,oy,w,h,digest=original_rects[i]
   if x+w>2048:x=0;y+=row_height+2;row_height=0
   if y+h>2048:
    save_page(image);image=Image.new('RGBA',(2048,2048));x=y=row_height=0
   assert rects[i] is None,'Unexpected cross-region frame'
   frame=read_page(old).crop((ox,oy,ox+w,oy+h))
   assert hashlib.sha256(frame.tobytes()).hexdigest()==digest
   image.paste(frame,(x,y))
   rects[i]=[len(pages),x,y,w,h,digest];x+=w+2;row_height=max(row_height,h)
  save_page(image)
 assert all(rects)
 meta['rects']=rects
 meta['pages']=pages;meta['downloads']=downloads
 (stage/'assets/web_clips/clips.json').write_text(json.dumps(meta),encoding='utf-8')
 files=[p for p in stage.rglob('*') if p.is_file() and not set(p.relative_to(stage).parts)&{'build','__pycache__'}
        and p.suffix!='.pyc' and not (p.parent.name=='web_clips' and p.suffix == '.png')]
 archive=out/'bootstrap.tar.gz'
 with tarfile.open(archive,'w:gz',compresslevel=9) as tar:
  for path in sorted(files):tar.add(path,arcname='assets/'+path.relative_to(stage).as_posix(),recursive=False)
 digest=hashlib.sha256(archive.read_bytes()).hexdigest()[:16]
 boot='bootstrap-'+digest+'.tar.gz';archive.replace(out/boot)
 html=(out/'index.html').read_text(encoding='utf-8')
 # Both hosts use the same bootstrap; the optional .apk is no longer needed.
 start=html.index('    if platform.window.location.host.find')
 end=html.index('    # preloader will change',start)
 html=html[:start]+f'''    import tarfile
    async with platform.fopen("{boot}", "rb") as archive:
        with tarfile.open(fileobj=archive, mode="r:gz") as tar:
            tar.extractall(path=appdir.as_posix(), filter='tar')

'''+html[end:]
 html=html.replace('<title>web_game</title>','<title>Fábrica dos Mortos</title>')
 (out/'index.html').write_text(html,encoding='utf-8')
 shipped=['index.html','web_ui.js','web_ui.css','favicon.png',boot]+['chunks/'+p for p in pages]
 (out/'site-files.json').write_text(json.dumps(shipped,indent=2))
 report={'initial_bytes':(out/boot).stat().st_size,'animation_bytes':total,'total_bytes':sum((out/p).stat().st_size for p in shipped),'previous_initial_bytes':171782894,'lossless_pages_verified':len(pages)}
 (ROOT/'reports/optimization.json').write_text(json.dumps(report,indent=2))
 print(report)
if __name__=='__main__':optimize()
