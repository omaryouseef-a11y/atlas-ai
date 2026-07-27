import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

class ThumbnailEngine:
    """
    Atlas Thumbnail Engine
    Generates YouTube-optimized thumbnail concepts and prompts.
    Can also generate actual images via AI image APIs.
    """

    def __init__(self):
        self.agent = Agent(
            role='Thumbnail Designer',
            goal='Create eye-catching, CTR-optimized YouTube thumbnails for Atlas Kids Media episodes.',
            backstory='You are a senior YouTube thumbnail designer. You know that bright colors, expressive character faces, and minimal text drive clicks. You specialize in childrens content thumbnails.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

    def generate_thumbnail_prompt(self, episode_title, characters, educational_topic):
        """
        Generate a detailed image generation prompt for the thumbnail.
        """
        task = Task(
            description=f'''
            Create a YouTube thumbnail image generation prompt for:
            - Episode Title: {episode_title}
            - Main Characters: {', '.join(characters)}
            - Educational Topic: {educational_topic}

            Rules:
            - Must be 16:9 aspect ratio (1280x720)
            - Bright, saturated colors that pop on small screens
            - Characters should have BIG expressive faces and eyes
            - Include the educational element visually (e.g., numbers 1-10 floating)
            - No text in the image (text will be added later by editor)
            - Style: 3D Pixar animation, highly detailed, cinematic lighting
            - Background should be simple but colorful
            ''',
            expected_output='A single, highly detailed image generation prompt (English) ready for DALL-E, Midjourney, or Stable Diffusion.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        return str(result)

    def save_thumbnail_prompt(self, episode_id, prompt):
        """Save thumbnail prompt to episode folder."""
        output_dir = f'episodes/{episode_id}/final'
        os.makedirs(output_dir, exist_ok=True)
        path = f'{output_dir}/thumbnail_prompt.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        return path


if __name__ == '__main__':
    engine = ThumbnailEngine()
    prompt = engine.generate_thumbnail_prompt(
        episode_title='The Great Forest Picnic Journey',
        characters=['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy'],
        educational_topic='Counting from 1 to 10'
    )
    print(prompt)
    engine.save_thumbnail_prompt('ep_001_picnic_journey', prompt)
