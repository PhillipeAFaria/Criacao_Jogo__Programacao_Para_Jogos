"""Browser-only atomic storage; never reads desktop save directories."""
import base64
import json
from pathlib import Path

KEY = 'fabrica-dos-mortos:web:save:v1'
MAX_BYTES = 12 * 1024 * 1024

class BrowserStorage:
    def __init__(self, directory, bridge):
        self.directory = Path(directory)
        self.bridge = bridge
        self.last = None
        self.error = ''
        self.read_failed = False

    def restore(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        try:
            raw = self.bridge.load()
            if not raw:
                return
            if len(raw) > MAX_BYTES:
                raise ValueError('Progresso excede o limite de leitura.')
            data = json.loads(raw)
            if data.get('version') != 1 or not isinstance(data.get('files'), dict):
                raise ValueError('Formato de progresso incompatível.')
            decoded = {}
            for name, content in data['files'].items():
                if Path(name).name != name or '/' in name or '\\' in name or not name.startswith('campanha.'):
                    raise ValueError('Nome de arquivo inválido.')
                decoded[name] = base64.b64decode(content, validate=True)
            for name, content in decoded.items():
                (self.directory / name).write_bytes(content)
            self.last = raw
        except Exception:
            self.read_failed = True
            self.error = 'Progresso não pôde ser lido. O registro anterior foi preservado; exporte uma cópia.'

    def flush(self):
        if self.read_failed:
            return False
        try:
            files = {p.name:base64.b64encode(p.read_bytes()).decode('ascii')
                     for p in sorted(self.directory.glob('campanha.*')) if p.is_file()
                     and not p.name.endswith(('-journal','-wal','-shm','.tmp'))}
            raw = json.dumps({'version':1,'files':files}, separators=(',',':'))
            if raw != self.last:
                outcome = self.bridge.save(raw)
                if outcome:
                    raise OSError(str(outcome))
                self.last = raw
            self.error = ''
            return True
        except Exception:
            self.error = 'Não foi possível salvar no navegador. Libere espaço ou exporte o progresso antes de fechar.'
            return False
