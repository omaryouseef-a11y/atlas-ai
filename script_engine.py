import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

# 1. Define the Script Agent
script_agent = Agent(
    role='Script Engine',
    goal='Write a highly engaging, safe, and educational children\'s script for Atlas Kids Media.',
    backstory='You are an expert children\'s storyteller and scriptwriter. You specialize in COPPA-compliant, educational content for 3-7 year olds. You know the Atlas Kids Media characters perfectly.',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

# 2. Define the Task
script_task = Task(
    description='''Write the complete script for Episode 001: 'The Great Forest Picnic Journey'.
    Include these exact characters from the Brand Bible:
    1. Squirrel: Sokkar (Active and bouncy)
    2. Fox: Felix (Smart and fast)
    3. Rabbit: Bonnie (Gentle and light)
    4. Bear: Barnaby (Kind with a warm voice)
    5. Bird: Tweety (Sweet voice)
    6. Deer: Bambi (Loves flowers)
    7. Turtle: Torti (Slow but wise)
    8. Raccoon: Ricky (Playful and clean)
    9. Hedgehog: Henry (Small and cute)
    10. Frog: Freddy (Welcoming and friendly)
    
    Requirements:
    - Language: Simple, clear English (for global pilot) or Arabic (based on OS). Let's use simple Arabic since the target audience is Arab children.
    - Format: Scene by scene. For each scene, include [Visual] (for the Vision Engine) and [Audio/Dialogue] (for the Voice Engine).
    - Length: About 2-3 minutes of screen time.
    - Educational Goal: Teamwork and sharing.
    ''',
    expected_output='A fully formatted markdown script with Scene numbers, Visual descriptions, and exact Dialogues.',
    agent=script_agent
)

# 3. Form the Crew
script_crew = Crew(
    agents=[script_agent],
    tasks=[script_task],
    process=Process.sequential
)

if __name__ == '__main__':
    print('🎬 Triggering Phase 1: Script Engine...')
    result = script_crew.kickoff()
    
    # Save the output to the episode folder
    output_dir = 'episodes/ep_001_picnic_journey/script'
    os.makedirs(output_dir, exist_ok=True)
    with open(f'{output_dir}/story.md', 'w', encoding='utf-8') as f:
        f.write(str(result))
    
    print('\n✅ Script successfully written and saved to episodes/ep_001_picnic_journey/script/story.md')
