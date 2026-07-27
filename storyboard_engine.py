import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

class StoryboardEngine:
    """
    Atlas Storyboard Engine
    Generates detailed visual storyboards from scripts before video production.
    Creates shot-by-shot descriptions that can be used for image generation or manual review.
    """

    def __init__(self):
        self.agent = Agent(
            role='Storyboard Artist',
            goal='Create detailed visual storyboards for childrens animation, specifying camera angles, character positions, and scene composition.',
            backstory='You are a senior storyboard artist for Pixar-style childrens animation. You think in shots, frames, and camera movements. You ensure visual continuity and maximize educational impact through composition.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

    def generate_storyboard(self, script_path, episode_id):
        """
        Generate a complete storyboard from a script.
        Returns a markdown file with shot-by-shot breakdowns.
        """
        if not os.path.exists(script_path):
            print(f'[StoryboardEngine] Script not found: {script_path}')
            return None

        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()

        task = Task(
            description=f'''
            Create a detailed visual storyboard for this children's animation script.
            
            For EACH scene, provide:
            1. SHOT NUMBER (e.g., Scene 1A, Scene 1B)
            2. SHOT TYPE (Wide, Medium, Close-up, Extreme Close-up, Over-the-shoulder, Aerial)
            3. CAMERA MOVEMENT (Static, Pan, Tilt, Zoom in, Zoom out, Tracking, Dolly)
            4. COMPOSITION (Where characters are positioned in frame)
            5. BACKGROUND DETAILS (Specific elements visible)
            6. CHARACTER ACTIONS (Exact poses and expressions)
            7. LIGHTING (Time of day, light direction, mood)
            8. COLOR PALETTE (Dominant colors for this shot)
            9. DURATION (Estimated seconds)
            10. TRANSITION TO NEXT SHOT (Cut, Fade, Dissolve, Wipe)
            
            CRITICAL: Ensure character designs remain consistent across all shots.
            The magical green forest setting must look identical in every wide shot.
            
            SCRIPT:
            {script}
            ''',
            expected_output='A complete markdown storyboard with shot-by-shot breakdown for every scene.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()

        # Save storyboard
        output_dir = f'episodes/{episode_id}/storyboard'
        os.makedirs(output_dir, exist_ok=True)
        path = f'{output_dir}/storyboard.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(result))

        print(f'[StoryboardEngine] Storyboard saved: {path}')
        return path

    def generate_image_prompts(self, storyboard_path, episode_id):
        """
        Convert storyboard shots into image generation prompts.
        These can be used with DALL-E or Stable Diffusion to create reference images.
        """
        if not os.path.exists(storyboard_path):
            return None

        with open(storyboard_path, 'r', encoding='utf-8') as f:
            storyboard = f.read()

        task = Task(
            description=f'''
            Convert this storyboard into image generation prompts.
            For each shot, create ONE detailed prompt suitable for DALL-E 3 or Midjourney.
            
            Rules:
            - 16:9 aspect ratio
            - Pixar 3D animation style
            - Highly detailed
            - Include all characters mentioned in the shot
            - Specify exact camera angle and composition
            
            STORYBOARD:
            {storyboard}
            ''',
            expected_output='A list of image generation prompts, one per shot, numbered sequentially.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()

        output_dir = f'episodes/{episode_id}/storyboard'
        path = f'{output_dir}/image_prompts.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(result))

        print(f'[StoryboardEngine] Image prompts saved: {path}')
        return path

    def generate_shot_list(self, storyboard_path):
        """Generate a concise shot list for production tracking."""
        if not os.path.exists(storyboard_path):
            return None

        with open(storyboard_path, 'r', encoding='utf-8') as f:
            storyboard = f.read()

        task = Task(
            description=f'''
            Extract a concise shot list from this storyboard.
            Format as a table: Shot # | Type | Duration | Characters | Background | Notes
            
            STORYBOARD:
            {storyboard}
            ''',
            expected_output='A markdown table shot list for production tracking.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        return str(result)


if __name__ == '__main__':
    engine = StoryboardEngine()
    engine.generate_storyboard(
        'episodes/ep_001_picnic_journey/script/story_v2.md',
        'ep_001_picnic_journey'
    )
