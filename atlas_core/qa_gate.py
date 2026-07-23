import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from atlas_core.job_manager import AtlasJobManager

class QualityGate:
    def __init__(self):
        self.jm = AtlasJobManager()

    def review_video_prompt(self, episode_id, prompt_text):
        # 1. Budget Check
        budget_ok, budget_msg = self.jm.check_budget(episode_id)
        if not budget_ok:
            return False, f'REJECTED BY QA: {budget_msg}'

        # 2. Consistency Check
        required_phrase = 'magical green forest'
        if required_phrase.lower() not in prompt_text.lower():
            return False, 'REJECTED BY QA: Missing required background consistency phrase.'

        # 3. Style Check
        required_style = 'Pixar style'
        if required_style.lower() not in prompt_text.lower():
            return False, 'REJECTED BY QA: Missing required Pixar style phrase.'

        # 4. Duplication Check (Did we already generate this?)
        existing_video = self.jm.check_job_exists(episode_id, 'MotionEngine', 'generate_video', prompt_text)
        if existing_video:
            return False, 'REJECTED BY QA CACHED: Video already generated for this prompt.'

        return True, 'QA APPROVED: Prompt is valid, safe, and within budget.'

if __name__ == '__main__':
    qa = QualityGate()
    print('🛡️ QA Gate Initialized successfully.')
