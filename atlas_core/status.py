import sqlite3
import os

DB_PATH = 'atlas.db'

def print_dashboard():
    if not os.path.exists(DB_PATH):
        print('❌ Database not found. The factory has not been initialized.')
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print('='*60)
    print('📊 ATLAS KIDS MEDIA - COMPANY DASHBOARD')
    print('='*60)

    cursor.execute('SELECT id, title, status, current_phase, budget_limit, total_cost FROM episodes')
    episodes = cursor.fetchall()
    
    if not episodes:
        print('No episodes found in production.')
    else:
        for ep in episodes:
            ep_id, title, status, phase, budget, cost = ep
            print(f'\n🎬 EPISODE: {title} ({ep_id})')
            print(f'   ├─ Status: {status.upper()}')
            print(f'   ├─ Phase:  {phase.upper()}')
            
            # Budget Bar logic
            percent = (cost / budget) * 100 if budget > 0 else 0
            bar_filled = int(percent / 5)
            bar_empty = 20 - bar_filled
            bar = '█' * bar_filled + '░' * bar_empty
            print(f'   └─ Budget: [{bar}] ${cost:.2f} / ${budget:.2f} ({percent:.1f}%)')
            
            print('\n   📋 RECENT JOBS (Last 5):')
            cursor.execute('SELECT id, department, task_type, status, cost FROM jobs WHERE episode_id=? ORDER BY id DESC LIMIT 5', (ep_id,))
            jobs = cursor.fetchall()
            if jobs:
                for j in jobs:
                    j_id, dept, ttype, jstatus, jcost = j
                    status_icon = '✅' if jstatus == 'completed' else '⏳' if jstatus == 'running' else '❌'
                    print(f'      {status_icon} Job #{j_id:03d} | {dept} | {ttype} | Cost: ${jcost:.2f}')
            else:
                print('      No jobs recorded yet.')
                
    print('\n' + '='*60)
    conn.close()

if __name__ == '__main__':
    print_dashboard()
