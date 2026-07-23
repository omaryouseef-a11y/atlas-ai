import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Setup Gemini LLM
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('WARNING: GEMINI_API_KEY not found in .env')

llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-pro', 
    google_api_key=api_key if api_key else 'dummy_key'
)

# 1. Define the CEO Agent
ceo_agent = Agent(
    role='CEO Engine',
    goal='Manage the Atlas Kids Media automated pipeline according to ATLAS_OS.md, ensuring kid safety, high quality, and profitability.',
    backstory='You are the AI heart of Atlas Kids Media. Your Founder, Omar, has set the vision. Your job is to orchestrate the Research, Script, Storyboard, Voice, and Animation agents to produce content like Episode 001 seamlessly.',
    verbose=True,
    allow_delegation=True,
    llm=llm
)

# 2. Define the First Task
planning_task = Task(
    description='Review the company mission and outline the exact workflow to start processing Episode 001 (The Great Forest Picnic Journey).',
    expected_output='A brief, structured action plan for Episode 001 matching the Episode Factory pipeline.',
    agent=ceo_agent
)

# 3. Form the Crew
atlas_crew = Crew(
    agents=[ceo_agent],
    tasks=[planning_task],
    process=Process.sequential
)

if __name__ == '__main__':
    print('🚀 Atlas Kids Media - CEO Engine Initialized.')
    # result = atlas_crew.kickoff()
    # print(result)
