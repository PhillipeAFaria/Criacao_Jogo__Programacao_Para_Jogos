"""Generate the browser edition from this checkout, never from a sibling project."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.web-build'


def source_hashes():
    paths = [ROOT/'main.py', ROOT/'project.toml']
    for folder in ('src', 'assets'):
        paths.extend(p for p in (ROOT/folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def prepare():
    # Only remove a workspace created by this command, inside this checkout.
    if WORK.exists():
        if WORK.is_symlink() or WORK.resolve().parent != ROOT.resolve() or not (WORK/'.generated-workspace').is_file():
            raise RuntimeError('Refusing to replace an unrecognized web workspace')
        shutil.rmtree(WORK)
    WORK.mkdir()
    (WORK/'.generated-workspace').touch()
    for name in ('src', 'assets'):
        shutil.copytree(ROOT/name, WORK/name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'web_clips'))
    for p in (WORK/'src').rglob('*.py'):
        p.write_text(p.read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
    shutil.copy2(ROOT/'project.toml', WORK/'project.toml')
    # A patch fails loudly if the shared source changes incompatibly, instead of
    # silently replacing a newer Windows module with a stale browser copy.
    command = ['git', 'apply', '--directory=.web-build']
    subprocess.run(command+['--check', 'web/patches/browser.patch'], cwd=ROOT, check=True)
    subprocess.run(command+['web/patches/browser.patch'], cwd=ROOT, check=True)
    shutil.copy2(ROOT/'web/runtime/main.py', WORK/'main.py')
    shutil.copytree(ROOT/'web/runtime/svz', WORK/'src/svz', dirs_exist_ok=True)
    shutil.copytree(ROOT/'web/ui', WORK/'web')
    (WORK/'reports').mkdir()


def promote(output):
    target = ROOT/'web/site'
    names = json.loads((output/'site-files.json').read_text(encoding='utf-8'))
    if target.is_symlink() or target.resolve() != ROOT.resolve()/'web/site':
        raise RuntimeError('Unexpected site directory')
    # Refuse to remove files outside the old generated manifest.
    old = json.loads((ROOT/'web/manifest.json').read_text(encoding='utf-8'))
    actual = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
    if actual != set(old):
        raise RuntimeError('Unrecognized site files; review them before updating')
    for name, digest in old.items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Modified site file: '+name)
    for name in names:
        dest = target/name
        if not dest.resolve().is_relative_to(target.resolve()):
            raise RuntimeError('Invalid generated path')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output/name, dest)
    for name in set(old)-set(names):
        (target/name).unlink()
    manifest = {name: hashlib.sha256((target/name).read_bytes()).hexdigest() for name in names}
    (ROOT/'web/manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT/'web/build_site.py')], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update-site', action='store_true', help='Replace the tracked generated site after verification; never deploy')
    args = parser.parse_args()
    baseline = source_hashes()
    prepare()
    env = dict(os.environ, FDM_WEB_WORKSPACE=str(WORK), SDL_VIDEODRIVER='dummy',
               SDL_AUDIODRIVER='dummy', SVZ_DATA_DIR=str(WORK/'test-data'), PYTHONUTF8='1')
    for script in ('prepare_web_assets.py', 'build_web.py', 'verify_generated.py'):
        subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'web/tools'/script)],
                       cwd=ROOT, env=env, check=True)
    env['PYTHONPATH'] = str(WORK/'src')
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'web/tests', '-v'],
                   cwd=ROOT, env=env, check=True)
    if baseline != source_hashes():
        raise RuntimeError('Shared source or original assets changed during generation')
    output = WORK/'web_game/build/web'
    if args.update_site:
        promote(output)
    print('Generated and verified:', output)
    print('Windows source/assets unchanged. Deployment remains manual.')


if __name__ == '__main__':
    main()
