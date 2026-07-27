import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

class SafetyEngine:
    """
    Atlas Safety Engine
    Advanced content moderation beyond the basic QA Gate.
    Checks for: violence, fear, inappropriate language, stereotypes,
    cultural sensitivity, educational accuracy, and COPPA compliance.
    """

    def __init__(self):
        self.agent = Agent(
            role='Child Safety Specialist',
            goal='Ensure all Atlas Kids Media content is 100% safe, appropriate, and beneficial for children aged 3-7.',
            backstory='You are a certified child psychologist and content safety expert. You have reviewed thousands of childrens media pieces. You are extremely strict about safety, educational value, and cultural appropriateness. You never approve content that could scare, confuse, or negatively influence a child.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

    def review_script(self, script_path):
        """Perform comprehensive safety review of a script."""
        if not os.path.exists(script_path):
            return {'approved': False, 'reason': 'Script file not found'}

        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()

        task = Task(
            description=f'''
            Perform a comprehensive safety review of this children's script.
            
            CHECKLIST (must pass ALL):
            1. NO violence, aggression, or physical conflict (even playful)
            2. NO scary content, monsters, dark themes, or frightening situations
            3. NO inappropriate language, sarcasm, or negative role models
            4. NO stereotypes about gender, race, or culture
            5. ALL educational claims must be factually accurate
            6. Characters must show positive behaviors (sharing, kindness, teamwork)
            7. Pacing must be appropriate for 3-7 year olds (not too fast or overwhelming)
            8. Cultural sensitivity: no appropriation, all representations respectful
            9. COPPA compliance: no data collection prompts, no external links to unsafe sites
            10. The script must have a clear, positive moral lesson
            
            For each item, state PASS or FAIL with specific evidence.
            If ANY item fails, the script is REJECTED.
            
            SCRIPT:
            {script}
            ''',
            expected_output='A structured safety report with PASS/FAIL for each category, specific evidence, and a final APPROVED or REJECTED verdict.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        return self._parse_safety_report(str(result))

    def review_video_prompt(self, prompt_text):
        """Safety check a video generation prompt."""
        task = Task(
            description=f'''
            Review this AI video generation prompt for child safety:
            
            PROMPT: {prompt_text}
            
            Check for:
            1. No frightening imagery (dark forests, scary animals, storms)
            2. No realistic weapons or dangerous situations
            3. Appropriate clothing/body representation for characters
            4. Safe color palette (bright, warm, not dark or violent)
            5. Movement descriptions are calm and child-safe
            
            Return: SAFE or UNSAFE with specific reasoning.
            ''',
            expected_output='A brief safety verdict: SAFE or UNSAFE with reasoning.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        report = str(result)
        return {
            'approved': 'UNSAFE' not in report.upper() and 'REJECT' not in report.upper(),
            'report': report
        }

    def review_thumbnail(self, image_path):
        """Review a thumbnail image for safety and CTR optimization."""
        # For now, review the prompt used to generate it
        prompt_path = image_path.replace('.png', '_prompt.md').replace('.jpg', '_prompt.md')
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
            return self.review_video_prompt(prompt)
        return {'approved': True, 'report': 'No prompt found for review. Manual check required.'}

    def review_metadata(self, metadata_text):
        """Review YouTube metadata for safety and compliance."""
        task = Task(
            description=f'''
            Review this YouTube metadata for child safety and COPPA compliance:
            
            METADATA:
            {metadata_text}
            
            Check:
            1. Title is not clickbait or misleading
            2. Description contains no external links to unsafe sites
            3. No requests for personal information from children
            4. Tags are appropriate and not exploiting child-related search terms inappropriately
            5. Made for Kids flag is correctly set
            
            Return: COMPLIANT or NON-COMPLIANT with specific issues.
            ''',
            expected_output='Compliance report with specific issues if any.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        report = str(result)
        return {
            'approved': 'NON-COMPLIANT' not in report.upper() and 'REJECT' not in report.upper(),
            'report': report
        }

    def _parse_safety_report(self, report_text):
        """Parse the safety report into structured data."""
        approved = 'REJECTED' not in report_text.upper() and 'FAIL' not in report_text.upper()
        return {
            'approved': approved,
            'report': report_text,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }

    def save_report(self, episode_id, report, output_dir='reports/safety'):
        """Save safety report to file."""
        os.makedirs(output_dir, exist_ok=True)
        path = f'{output_dir}/{episode_id}_safety_report.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'# Safety Report: {episode_id}\n\n')
            f.write(f'**Status:** {"APPROVED" if report["approved"] else "REJECTED"}\n\n')
            f.write(f'**Timestamp:** {report.get("timestamp", "N/A")}\n\n')
            f.write('## Detailed Report\n\n')
            f.write(report['report'])
        return path


if __name__ == '__main__':
    engine = SafetyEngine()
    result = engine.review_script('episodes/ep_001_picnic_journey/script/story_v2.md')
    print(f'Safety check: {"APPROVED" if result["approved"] else "REJECTED"}')
    engine.save_report('ep_001_picnic_journey', result)
