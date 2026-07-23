import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from atlas_core.job_manager import AtlasJobManager
from atlas_core.qa_gate import QualityGate

class AtlasOrchestrator:
    def __init__(self):
        self.jm = AtlasJobManager()
        self.qa = QualityGate()

    def request_video_generation(self, episode_id, prompt):
        print(f'\n[Orchestrator] Requesting video generation for: {prompt[:50]}...')
        
        # 1. Pass through QA Gate (checks budget, rules, and cache)
        is_approved, qa_message = self.qa.review_video_prompt(episode_id, prompt)
        
        if not is_approved:
            print(f'❌ {qa_message}')
            return False
            
        print(f'✅ {qa_message}')
        
        # 2. Start Job
        job_id = self.jm.start_job(episode_id, 'MotionEngine', 'generate_video', prompt)
        print(f'⏳ Started Job #{job_id}. Calling external API...')
        
        # Simulate API call (This is where Veo3 call happens)
        # ... API logic here ...
        simulated_output_path = f'/opt/atlas-ai/episodes/{episode_id}/video/mock_video_{job_id}.mp4'
        cost_of_api_call = 1.50 # Simulated cost
        
        # 3. Complete Job
        self.jm.complete_job(job_id, episode_id, simulated_output_path, cost=cost_of_api_call)
        print(f'🎉 Job #{job_id} completed. Saved to {simulated_output_path}. Cost: ')
        return simulated_output_path

if __name__ == '__main__':
    orc = AtlasOrchestrator()
    orc.jm.create_episode('ep_test_01', 'Test Infrastructure', budget_limit=5.0)
    
    # Test 1: Valid Prompt
    prompt1 = 'Sokkar in a magical green forest holding an apple. Pixar style.'
    orc.request_video_generation('ep_test_01', prompt1)
    
    # Test 2: Duplicate Prompt (Should be caught by QA cache)
    orc.request_video_generation('ep_test_01', prompt1)
    
    # Test 3: Invalid Prompt (Missing style rule)
    prompt2 = 'Sokkar in a magical green forest holding an apple. Realistic style.'
    orc.request_video_generation('ep_test_01', prompt2)
