import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

# 1. Define the Motion Agent
motion_agent = Agent(
    role='Motion Engine',
    goal='Create consistent, highly detailed Text-to-Video prompts for Episode 001, ensuring the environment perfectly matches the 10 Atlas Kids Media characters.',
    backstory='You are the Lead 3D Animator and Video Prompt Engineer at Atlas Kids Media. You ensure that every shot looks like a high-budget Pixar movie. You are obsessed with visual consistency, making sure the background (magical green forest) and character designs never change between shots.',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 2. Define the Task
motion_task = Task(
    description='''Review the Episode 001 Script and the Character Bible.
    We have 10 established characters: 
    1. Sokkar (Squirrel)
    2. Felix (Fox)
    3. Bonnie (Rabbit)
    4. Barnaby (Bear)
    5. Tweety (Bird)
    6. Bambi (Deer)
    7. Torti (Turtle)
    8. Ricky (Raccoon)
    9. Henry (Hedgehog)
    10. Freddy (Frog)
    
    Task: Write the exact 'Video Generation Prompts' for each scene to be fed into the Video AI (like Veo 3 or Sora).
    CRITICAL RULE: Ensure the setting (a bright, sunlit, magical green forest with a picnic area) is explicitly described in EVERY prompt so the video AI keeps the background consistent across all 10 characters.
    Style rule to append to every prompt: '3D animated, Pixar style, vibrant colors, highly detailed, 4k resolution, cinematic lighting, calm and child-safe movement.'
    ''',
    expected_output='A markdown list of Scene numbers with their corresponding exact Video Generation Prompts in English.',
    agent=motion_agent
)

# 3. Form the Crew
motion_crew = Crew(
    agents=[motion_agent],
    tasks=[motion_task],
    process=Process.sequential
)

if __name__ == '__main__':
    print('🎥 Triggering Phase 3 & 4: Motion Engine...')
    result = motion_crew.kickoff()
    
    output_dir = 'episodes/ep_001_picnic_journey/video'
    os.makedirs(output_dir, exist_ok=True)
    with open(f'{output_dir}/animation_prompts.md', 'w', encoding='utf-8') as f:
        f.write(str(result))
    
    print('\n✅ Motion prompts successfully generated and saved to episodes/ep_001_picnic_journey/video/animation_prompts.md')
