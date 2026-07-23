import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from atlas_core.job_manager import AtlasJobManager

class AssetVault:
    def __init__(self):
        self.jm = AtlasJobManager()
        self.db_path = 'atlas.db'

    def register_asset(self, asset_id, asset_type, name, file_path, metadata=''):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO assets (id, asset_type, name, file_path, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset_id, asset_type, name, file_path, metadata))
        conn.commit()
        conn.close()
        return True

    def get_asset(self, asset_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM assets WHERE id=?', (asset_id,))
        result = cursor.fetchone()
        conn.close()
        return result

if __name__ == '__main__':
    vault = AssetVault()
    # Registering the character bible as our first foundational asset
    vault.register_asset('bible_v1', 'character_bible', 'Atlas Character Bible', 'media_library/characters/atlas_character_bible.md')
    print('🗄️ Asset Vault Initialized and Character Bible registered.')
