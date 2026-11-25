import asyncio,json,os,tempfile,unittest,random
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import pygame
from svz.web_assets import WebClips

ROOT=Path(__file__).resolve().parents[2]/".web-build"
class Bridge:
    def busy(self,value):pass
    def statusJSON(self,*args):pass
    def keepAssets(self,*args):pass
    def invalidate(self,*args):pass
class Download:
    def __init__(self,url,mode):self.path=ROOT/'web_game/build/web'/url
    async def __aenter__(self):self.file=self.path.open('rb');return self.file
    async def __aexit__(self,*args):self.file.close()

class StreamingTests(unittest.TestCase):
    def test_map_switch_releases_bank_and_preserves_random_state(self):
        pygame.init();pygame.display.set_mode((1,1))
        bank=WebClips()
        bank.meta=json.loads((ROOT/'web_game/assets/web_clips/clips.json').read_text(encoding='utf-8'))
        rng=random.getstate();metrics={}
        with tempfile.TemporaryDirectory() as folder,patch('platform.fopen',Download,create=True):
            bank.root=Path(folder)
            for region in ('city','desert','beach','city'):
                self.assertTrue(asyncio.run(bank.prepare_region(region,Bridge())))
                self.assertTrue(all(a.startswith(region+'_') for a in bank.keys()))
                self.assertEqual(bank.frames,{})
                surfaces={id(f):f for states in bank.values() for clip in states.values() for f in list(clip.frames)+list(clip.inbetweens.values())}
                size=sum(s.get_pitch()*s.get_height() for s in surfaces.values())
                self.assertLess(size,200*1024*1024)
                metrics[region]={'decoded_actor_bytes':size,'actors':len(bank),'resident_atlases':len(list(bank.root.glob('*.png')))}
                self.assertFalse(asyncio.run(bank.prepare_region(region,Bridge())))
                self.assertEqual(random.getstate(),rng)
        (ROOT/'reports/streaming-memory.json').write_text(json.dumps(metrics,indent=2))
        pygame.quit()

