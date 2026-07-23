import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

script_agent = Agent(
    role='Script Engine',
    goal='Write a fast-paced, highly engaging children\'s script focused on counting from 1 to 10.',
    backstory='You are an expert children\'s scriptwriter. The Founder requested a total rewrite of Episode 001. The new goal is to teach counting from 1 to 10 by having the 10 characters incrementally join the scene and interact. The pacing must be very fast (under 1 minute total dialogue).',
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm
)

script_task = Task(
    description='''Write a completely new script for Episode 001: 'The Great Forest Picnic Journey - V2'.
    
    CRITICAL FOUNDER DIRECTIVES:
    - The core educational goal is COUNTING from 1 to 10.
    - The script must be extremely fast-paced (the whole dialogue should be under 1 minute).
    - It is cumulative: 1 character appears, says 'One', then the 2nd joins, they say 'Two', then the 3rd, etc.
    - Add dynamic interactions: e.g., when the 4th joins the 5th, maybe a tiny playful conflict happens, the 6th resolves it, and they continue counting.
    - At the very end, all 10 are together on screen, and they all count rapidly '1, 2, 3, 4, 5, 6, 7, 8, 9, 10!' together.
    
    The 10 Characters (must appear in order):
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
    
    Requirements:
    - Language: Simple Arabic.
    - Format: Scene by scene. Include [Visual] showing how the characters group up in the frame, and [Audio/Dialogue].
    ''',
    expected_output='A fully formatted markdown script for the new counting-focused, fast-paced V2 episode.',
    agent=script_agent
)

script_crew = Crew(
    agents=[script_agent],
    tasks=[script_task],
    process=Process.sequential
)

if __name__ == '__main__':
    print('🎬 Triggering Phase 1 (V2): Script Engine with new Counting Directive...')
    result = script_crew.kickoff()
    
    output_dir = 'episodes/ep_001_picnic_journey/script'
    os.makedirs(output_dir, exist_ok=True)
    with open(f'{output_dir}/story_v2.md', 'w', encoding='utf-8') as f:
        f.write(str(result))
    
    print('\n✅ V2 Script successfully written and saved to episodes/ep_001_picnic_journey/script/story_v2.md')
