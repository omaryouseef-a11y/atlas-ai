import sys
import os
from atlas_core.orchestrator import AtlasOrchestrator
from atlas_core.job_manager import AtlasJobManager

def run_factory(episode_id):
    print(f'🏭 Starting Factory for {episode_id}...')
    jm = AtlasJobManager()
    orc = AtlasOrchestrator()
    
    # Register Episode if not exists
    jm.create_episode(episode_id, 'The Great Forest Picnic Journey - V2', budget_limit=20.0)
    
    print('1. Script Phase... (Skipping API call, linking existing output)')
    # In a real run, call Script Engine here.
    
    print('2. Voice Phase... (Skipping API call, linking existing output)')
    # In a real run, call Voice Engine here.
    
    print('3. Motion Phase... (Reading prompts and passing to Orchestrator)')
    prompts_file = f'episodes/{episode_id}/video_v2/animation_prompts_v2.md'
    if os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        prompts = [line.split('**Prompt:**')[1].strip() for line in lines if '**Prompt:**' in line]
        
        for i, prompt in enumerate(prompts):
            print(f'\n--- Processing Scene {i+1} ---')
            # This is the magic! We use the Orchestrator instead of calling the API directly.
            orc.request_video_generation(episode_id, prompt)
    else:
        print('Prompts not found. Run Motion Engine first.')

if __name__ == '__main__':
    run_factory('ep_001_picnic_journey')
