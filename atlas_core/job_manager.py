import sqlite3
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_core.db_setup

DB_PATH = 'atlas.db'

class AtlasJobManager:
    def __init__(self):
        atlas_core.db_setup.setup_database()

    def create_episode(self, ep_id, title, budget_limit=5.0):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO episodes (id, title, status, current_phase, budget_limit) VALUES (?, ?, ?, ?, ?)',
                       (ep_id, title, 'pending', 'script', budget_limit))
        conn.commit()
        conn.close()
        return ep_id

    def check_job_exists(self, episode_id, department, task_type, input_data):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT output_data FROM jobs 
            WHERE episode_id=? AND department=? AND task_type=? AND input_data=? AND status='completed'
        ''', (episode_id, department, task_type, str(input_data)))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def start_job(self, episode_id, department, task_type, input_data):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (episode_id, department, task_type, input_data, status)
            VALUES (?, ?, ?, ?, 'running')
        ''', (episode_id, department, task_type, str(input_data)))
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def complete_job(self, job_id, episode_id, output_data, cost=0.0):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE jobs SET status='completed', output_data=?, cost=? WHERE id=?
        ''', (str(output_data), cost, job_id))
        cursor.execute('UPDATE episodes SET total_cost = total_cost + ? WHERE id=?', (cost, episode_id))
        conn.commit()
        conn.close()

    def fail_job(self, job_id, error_message):
        """Mark a job as failed with error log."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE jobs SET status='failed', error_log=? WHERE id=?
        ''', (error_message, job_id))
        conn.commit()
        conn.close()

    def check_budget(self, episode_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT total_cost, budget_limit FROM episodes WHERE id=?', (episode_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            total, limit = result
            if total is None:
                total = 0.0
            if total >= limit:
                return False, f'BUDGET EXCEEDED: Spent ${total:.2f} out of ${limit:.2f}'
            return True, f'Budget OK: Spent ${total:.2f} out of ${limit:.2f}'
        return False, 'Episode not found'

    def update_phase(self, episode_id, phase):
        """Update the current production phase of an episode."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE episodes SET current_phase=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                       (phase, episode_id))
        conn.commit()
        conn.close()

    def update_status(self, episode_id, status):
        """Update the overall status of an episode."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE episodes SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
                       (status, episode_id))
        conn.commit()
        conn.close()

    def get_episode_stats(self, episode_id):
        """Get full stats for an episode."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, status, current_phase, budget_limit, total_cost, created_at, updated_at
            FROM episodes WHERE id=?
        ''', (episode_id,))
        ep = cursor.fetchone()

        cursor.execute('''
            SELECT COUNT(*), SUM(cost) FROM jobs WHERE episode_id=? AND status='completed'
        ''', (episode_id,))
        job_stats = cursor.fetchone()

        cursor.execute('''
            SELECT COUNT(*) FROM jobs WHERE episode_id=? AND status='failed'
        ''', (episode_id,))
        failed_count = cursor.fetchone()[0]

        conn.close()
        return {
            'episode': ep,
            'completed_jobs': job_stats[0] or 0,
            'total_job_cost': job_stats[1] or 0.0,
            'failed_jobs': failed_count
        }

if __name__ == '__main__':
    jm = AtlasJobManager()
    jm.create_episode('ep_001', 'The Great Forest Picnic Journey - V2', budget_limit=20.0)
    print('Atlas Job Manager loaded and Episode 001 registered.')
