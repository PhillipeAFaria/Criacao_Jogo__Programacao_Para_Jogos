"""Validate and assemble the optimized static site in GitHub Actions."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
root=HERE/'site';output=HERE.parent/'dist'
manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
assert actual==set(manifest),'Site manifest does not match files'
for name,digest in manifest.items():
 path=root/name
 assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
 assert path.stat().st_size<100*1024*1024,name
if output.exists():
 assert output.resolve()==(HERE.parent/'dist').resolve()
 shutil.rmtree(output)
shutil.copytree(root,output)
(output/'.nojekyll').touch()
print('Ready:',output)
