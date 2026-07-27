import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from atlas_core.job_manager import AtlasJobManager
from atlas_core.qa_gate import QualityGate
from video_engine import VideoEngine

class AtlasOrchestrator:
    """
    Atlas Orchestrator v2
    Routes approved prompts through the Video Engine for real generation.
    Maintains QA checks, budget tracking, and job recovery.
    """

    def __init__(self):
        self.jm = AtlasJobManager()
        self.qa = QualityGate()
        self.ve = VideoEngine()

    def request_video_generation(self, episode_id, prompt, scene_num=None):
        print(f'\n[Orchestrator] Processing video request for Episode {episode_id}')
        print(f'[Orchestrator] Prompt: {prompt[:60]}...')

        # 1. Pass through QA Gate
        is_approved, qa_message = self.qa.review_video_prompt(episode_id, prompt)
        if not is_approved:
            print(f'❌ {qa_message}')
            return False
        print(f'✅ {qa_message}')

        # 2. Start Job
        job_id = self.jm.start_job(episode_id, 'MotionEngine', 'generate_video', prompt)
        print(f'⏳ Started Job #{job_id}')

        # 3. Generate Video via Video Engine
        output_dir = f'episodes/{episode_id}/video_v2'
        os.makedirs(output_dir, exist_ok=True)
        scene_str = f'scene_{scene_num:03d}' if scene_num else f'clip_{job_id}'
        output_path = f'{output_dir}/{scene_str}.mp4'

        try:
            video_path, cost = self.ve.generate_video(prompt, output_path)

            # 4. Complete Job
            self.jm.complete_job(job_id, episode_id, video_path, cost=cost)
            print(f'🎉 Job #{job_id} completed. Saved to {video_path}. Cost: ${cost:.2f}')
            return video_path

        except Exception as e:
            # Mark job as failed
            self.jm.fail_job(job_id, str(e))
            print(f'❌ Job #{job_id} failed: {e}')
            return False

    def generate_all_clips(self, episode_id, prompts_file):
        """Generate all clips for an episode from a prompts file."""
        if not os.path.exists(prompts_file):
            print(f'[Orchestrator] Prompts file not found: {prompts_file}')
            return []

        with open(prompts_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        results = []
        scene_num = 0
        for line in lines:
            if '**Prompt:**' in line:
                scene_num += 1
                prompt = line.split('**Prompt:**')[1].strip()
                result = self.request_video_generation(episode_id, prompt, scene_num)
                results.append(result)

        return results


if __name__ == '__main__':
    orc = AtlasOrchestrator()
    orc.jm.create_episode('ep_test_02', 'Test Orchestrator V2', budget_limit=10.0)

    # Test 1: Valid Prompt
    prompt1 = 'Sokkar in a magical green forest holding an apple. 3D animated, Pixar style, vibrant colors, highly detailed, 4k resolution, cinematic lighting, calm and child-safe movement.'
    orc.request_video_generation('ep_test_02', prompt1, scene_num=1)

    # Test 2: Duplicate (Should be caught by QA cache)
    orc.request_video_generation('ep_test_02', prompt1, scene_num=2)

    # Test 3: Invalid Prompt (Missing style rule)
    prompt2 = 'Sokkar in a magical green forest holding an apple. Realistic style.'
    orc.request_video_generation('ep_test_02', prompt2, scene_num=3)
