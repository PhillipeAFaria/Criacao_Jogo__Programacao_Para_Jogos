"""Valores por tipo regional e histórico transacional de partidas concluídas."""
from pathlib import Path
import sqlite3
from contextlib import closing
from .config import SAVE_PATH
from .content import REGION_ENEMIES, REGION_SUBBOSSES, REGION_BOSSES

SCORE_TABLE = {
    region: {key: (index + 1) * 10 for index, key in enumerate(
        (*REGION_ENEMIES[region], *REGION_SUBBOSSES[region], *REGION_BOSSES[region]))}
    for region in REGION_ENEMIES
}


def points_for(region, key):
    # Criaturas auxiliares invocadas equivalem ao zumbi básico (10 pontos).
    return SCORE_TABLE[region].get(key, 10)


class ScoreStore:
    def __init__(self, campaign_path=None):
        self.path = Path(campaign_path or SAVE_PATH).with_suffix('.pontuacoes.sqlite3')
        self.error = ''

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path, timeout=2)
        try:
            db.execute('CREATE TABLE IF NOT EXISTS scores (id TEXT PRIMARY KEY, date TEXT NOT NULL, region TEXT NOT NULL, difficulty TEXT NOT NULL, wave INTEGER NOT NULL, victory INTEGER NOT NULL, points INTEGER NOT NULL CHECK(points >= 0))')
            db.commit()
        except Exception:
            db.close()
            raise
        return db

    def record(self, battle):
        if not battle.finished:
            return False
        try:
            with closing(self.connect()) as db, db:
                db.execute("INSERT OR IGNORE INTO scores VALUES (?, strftime('%Y-%m-%d %H:%M:%S','now','localtime'), ?, ?, ?, ?, ?)",
                           (battle.match_id, battle.region, battle.difficulty, battle.wave, int(battle.victory), battle.score))
            self.error = ''
            return True
        except (OSError, sqlite3.Error):
            self.error = 'Não foi possível salvar a pontuação. Tente voltar ao mapa novamente.'
            return False

    def page(self, index=0):
        try:
            with closing(self.connect()) as db:
                total = db.execute('SELECT count(*) FROM scores').fetchone()[0]
                rows = db.execute('SELECT date,region,difficulty,wave,victory,points FROM scores ORDER BY rowid DESC LIMIT 10 OFFSET ?', (max(0,index)*10,)).fetchall()
            self.error = ''
            return rows, total
        except (OSError, sqlite3.Error):
            self.error = 'Não foi possível ler o histórico de pontuações.'
            return [], 0
