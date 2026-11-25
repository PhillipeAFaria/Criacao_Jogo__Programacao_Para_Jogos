import os
"""Build an isolated static package, without touching Windows or saves."""
from pathlib import Path
import shutil, subprocess, sys, zipfile
ROOT = Path(os.environ["FDM_WEB_WORKSPACE"]).resolve()
stage = ROOT/'web_game'
stage.mkdir(exist_ok=True)
for name in ('main.py','project.toml'):
    shutil.copy2(ROOT/name,stage/name)
shutil.copytree(ROOT/'src',stage/'src',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for name in ('interface','audio','environment','frames','web_clips'):
    shutil.copytree(ROOT/'assets'/name,stage/'assets'/name,dirs_exist_ok=True)
(stage/'assets/actors').mkdir(exist_ok=True)
for pattern in ('*_boss_portraits_3x1_v1.png','muzzle_cycle_source_v1.png'):
    for path in (ROOT/'assets/actors').glob(pattern):
        shutil.copy2(path,stage/'assets/actors'/path.name)
subprocess.run([sys.executable,'-X','utf8','-m','pygbag','--build','--no_opt','--disable-sound-format-error',str(stage)],cwd=ROOT,check=True)
output=stage/'build/web'
index=output/'index.html'
html=index.read_text(encoding='utf-8')
html=html.replace('<html lang="en-us">', '<!doctype html><html lang="pt-BR"><meta charset="UTF-8">', 1)
html=html.replace('<head>','<head>\n<link rel="stylesheet" href="web_ui.css">')
html=html.replace('</body>','<script src="web_ui.js"></script>\n</body>')
html=html.replace('content="width=device-width, initial-scale=1.0"','content="width=device-width, initial-scale=1.0, viewport-fit=cover"')
index.write_text(html,encoding='utf-8')
for name in ('web_ui.js','web_ui.css'):
    shutil.copy2(ROOT/'web'/name,output/name)
print('Static preview:',output)
from optimize_web_build import optimize
optimize()
