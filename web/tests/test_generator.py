"""Guard generated outputs against replacing unrelated files."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('web_generator', REPO/'web/generate.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def test_unrecognized_workspace_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            work = root/'.web-build'
            work.mkdir()
            personal = work/'notes.txt'
            personal.write_text('keep', encoding='utf-8')
            with patch.object(generator, 'ROOT', root), patch.object(generator, 'WORK', work):
                with self.assertRaises(RuntimeError):
                    generator.prepare()
            self.assertEqual(personal.read_text(), 'keep')

    def test_promote_updates_manifest_and_removes_only_obsolete_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            site = root/'web/site'
            site.mkdir(parents=True)
            old = site/'old.png'
            old.write_bytes(b'old')
            (root/'web/manifest.json').write_text(json.dumps({'old.png': hashlib.sha256(b'old').hexdigest()}))
            shutil.copy2(REPO/'web/build_site.py', root/'web/build_site.py')
            output = root/'generated'
            output.mkdir()
            (output/'index.html').write_bytes(b'new site')
            (output/'site-files.json').write_text('["index.html"]')
            with patch.object(generator, 'ROOT', root):
                extra = site/'notes.txt'
                extra.write_text('keep')
                with self.assertRaises(RuntimeError):
                    generator.promote(output)
                self.assertEqual(extra.read_text(), 'keep')
                self.assertEqual(old.read_bytes(), b'old')
                extra.unlink()
                old.write_bytes(b'edited')
                with self.assertRaises(RuntimeError):
                    generator.promote(output)
                self.assertEqual(old.read_bytes(), b'edited')
                old.write_bytes(b'old')
                generator.promote(output)
            self.assertFalse(old.exists())
            self.assertEqual((root/'dist/index.html').read_bytes(), b'new site')
            manifest = json.loads((root/'web/manifest.json').read_text())
            self.assertEqual(manifest, {'index.html': hashlib.sha256(b'new site').hexdigest()})
