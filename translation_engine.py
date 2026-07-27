import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

class TranslationEngine:
    """
    Atlas Translation Engine
    Translates scripts, metadata, and prompts between languages.
    Primary: Arabic -> English, French, Spanish
    Maintains character names, educational intent, and cultural appropriateness.
    """

    def __init__(self):
        self.agent = Agent(
            role='Translation Specialist',
            goal='Translate childrens educational content while preserving meaning, rhythm, and cultural appropriateness.',
            backstory='You are a bilingual childrens content expert. You translate Arabic educational scripts into other languages while keeping the character names, counting sequences, and fun energy intact. You never translate character names.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

    def translate_script(self, script_path, target_language, output_path):
        """
        Translate a full script to target language.
        target_language: 'english', 'french', 'spanish', etc.
        """
        if not os.path.exists(script_path):
            print(f'[TranslationEngine] Script not found: {script_path}')
            return None

        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()

        task = Task(
            description=f'''
            Translate the following children's educational script into {target_language.upper()}.

            CRITICAL RULES:
            - DO NOT translate character names (Sokkar, Felix, Bonnie, Barnaby, Tweety, Bambi, Torti, Ricky, Henry, Freddy stay as-is)
            - Keep the counting numbers in Arabic numerals (1, 2, 3...) but write the number words in {target_language}
            - Preserve the [Visual] and [Audio/Dialogue] format
            - Keep the educational intent identical
            - Maintain the fast-paced, energetic tone
            - Keep scene structure identical
            - Keep the finale counting sequence structure

            SCRIPT TO TRANSLATE:
            {script}
            ''',
            expected_output=f'A fully translated markdown script in {target_language} with identical structure.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(result))

        print(f'[TranslationEngine] Script translated to {target_language}: {output_path}')
        return output_path

    def translate_metadata(self, metadata_path, target_language, output_path):
        """Translate YouTube metadata to target language."""
        if not os.path.exists(metadata_path):
            return None

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = f.read()

        task = Task(
            description=f'''
            Translate this YouTube metadata into {target_language.upper()}.
            Keep all hashtags and SEO keywords. Translate the title, description, and tags.
            Make it culturally appropriate for {target_language}-speaking parents of children aged 3-7.

            METADATA:
            {metadata}
            ''',
            expected_output=f'Translated metadata in {target_language}.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(result))

        return output_path

    def translate_motion_prompts(self, prompts_path, output_path):
        """
        Translate motion prompts to English if they are in Arabic.
        Video AI models typically require English prompts.
        """
        if not os.path.exists(prompts_path):
            return None

        with open(prompts_path, 'r', encoding='utf-8') as f:
            content = f.read()

        task = Task(
            description='''
            Translate any Arabic text in these video generation prompts to English.
            Keep all technical terms, style descriptions, and character names intact.
            Only translate narrative/descriptive text.

            PROMPTS:
            ''' + content,
            expected_output='English video generation prompts with identical technical structure.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(result))

        return output_path

    def batch_translate_episode(self, episode_id, languages=['english', 'french']):
        """
        Translate an entire episode to multiple languages.
        Creates parallel folder structure: episodes/{id}_en/, episodes/{id}_fr/
        """
        base_path = f'episodes/{episode_id}'
        results = {}

        for lang in languages:
            lang_code = lang[:2].lower()
            lang_path = f'episodes/{episode_id}_{lang_code}'
            os.makedirs(f'{lang_path}/script', exist_ok=True)
            os.makedirs(f'{lang_path}/metadata', exist_ok=True)

            # Translate script
            script_result = self.translate_script(
                f'{base_path}/script/story_v2.md',
                lang,
                f'{lang_path}/script/story_{lang_code}.md'
            )

            # Translate metadata if exists
            meta_path = f'{base_path}/final/youtube_metadata.md'
            if os.path.exists(meta_path):
                self.translate_metadata(
                    meta_path,
                    lang,
                    f'{lang_path}/metadata/youtube_metadata_{lang_code}.md'
                )

            results[lang] = lang_path
            print(f'[TranslationEngine] Episode {episode_id} translated to {lang} -> {lang_path}')

        return results


if __name__ == '__main__':
    engine = TranslationEngine()
    # Translate Episode 001 to English
    engine.translate_script(
        'episodes/ep_001_picnic_journey/script/story_v2.md',
        'english',
        'episodes/ep_001_picnic_journey/script/story_en.md'
    )
