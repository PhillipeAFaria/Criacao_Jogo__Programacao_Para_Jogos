import base64,json,tempfile,unittest
from pathlib import Path
from svz.web_storage import BrowserStorage

class Bridge:
    def __init__(self,raw=''):self.raw=raw;self.error=''
    def load(self):return self.raw
    def save(self,raw):
        if self.error:return self.error
        self.raw=raw;return ''

class StorageTests(unittest.TestCase):
    def test_roundtrip_json_and_sqlite_bytes(self):
        bridge=Bridge()
        with tempfile.TemporaryDirectory() as first,tempfile.TemporaryDirectory() as second:
            storage=BrowserStorage(first,bridge);storage.restore()
            for name,data in [('campanha.json',b'{"best_wave":4}'),('campanha.pontuacoes.sqlite3',bytes(range(256)))]:
                (Path(first)/name).write_bytes(data)
            self.assertTrue(storage.flush())
            restored=BrowserStorage(second,bridge);restored.restore()
            for file in Path(first).iterdir():self.assertEqual(file.read_bytes(),(Path(second)/file.name).read_bytes())
    def test_corrupt_record_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            bridge=Bridge('not json');storage=BrowserStorage(folder,bridge);storage.restore()
            self.assertFalse(storage.flush());self.assertEqual(bridge.raw,'not json')
    def test_quota_failure_preserves_last_record(self):
        with tempfile.TemporaryDirectory() as folder:
            bridge=Bridge();storage=BrowserStorage(folder,bridge);storage.restore();storage.flush();previous=bridge.raw
            (Path(folder)/'campanha.json').write_text('{}');bridge.error='quota exceeded'
            self.assertFalse(storage.flush());self.assertEqual(bridge.raw,previous)
    def test_traversal_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as folder:
            bridge=Bridge(json.dumps({'version':1,'files':{'../campanha.json':base64.b64encode(b'{}').decode()}}))
            storage=BrowserStorage(folder,bridge);storage.restore()
            self.assertTrue(storage.read_failed);self.assertEqual(list(Path(folder).iterdir()),[])
