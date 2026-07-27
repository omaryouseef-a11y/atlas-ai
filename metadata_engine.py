import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
os.environ['GOOGLE_API_KEY'] = api_key

gemini_llm = LLM(model='gemini/gemini-3.1-pro-preview', api_key=api_key)

class MetadataEngine:
    """
    Atlas Metadata Engine
    Generates YouTube-optimized metadata:
    - Title (clickable, SEO-friendly)
    - Description (with timestamps, links, keywords)
    - Tags (hashtags and search keywords)
    - Category
    """

    def __init__(self):
        self.agent = Agent(
            role='YouTube SEO Specialist',
            goal='Write metadata that maximizes views, watch time, and search ranking for childrens educational content.',
            backstory='You are a YouTube growth expert specializing in kids educational channels. You know exactly what parents search for and what makes kids click. You write in Arabic and English.',
            verbose=True,
            allow_delegation=False,
            llm=gemini_llm
        )

    def generate_metadata(self, episode_title, episode_description, characters, educational_goal, target_age='3-7'):
        """
        Generate complete YouTube metadata package.
        """
        task = Task(
            description=f'''
            Generate complete YouTube metadata for this episode:
            
            Episode Title: {episode_title}
            Description: {episode_description}
            Characters: {', '.join(characters)}
            Educational Goal: {educational_goal}
            Target Age: {target_age}
            Channel: Atlas Kids Media (قناة أطلس للأطفال)
            
            Output must include:
            1. TITLE: Max 100 chars. Mix Arabic + English. Include numbers/emojis. Make it irresistible to parents.
            2. DESCRIPTION: 500+ words. Include:
               - Hook in first 2 lines
               - Episode summary
               - Educational benefits
               - Character list with emojis
               - Timestamps for each scene
               - Links to other episodes
               - Subscribe CTA
               - Hashtags
            3. TAGS: 15 high-volume search keywords in Arabic and English
            4. CATEGORY: YouTube category ID
            
            Format as structured markdown.
            ''',
            expected_output='A complete metadata package with Title, Description, Tags, and Category.',
            agent=self.agent
        )

        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        return str(result)

    def save_metadata(self, episode_id, metadata):
        """Save metadata to episode folder."""
        output_dir = f'episodes/{episode_id}/final'
        os.makedirs(output_dir, exist_ok=True)
        path = f'{output_dir}/youtube_metadata.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(metadata)
        return path

    def parse_metadata(self, metadata_text):
        """Parse markdown metadata into structured dict."""
        lines = metadata_text.split('\n')
        data = {'title': '', 'description': '', 'tags': [], 'category': 'Education'}
        current_section = None
        buffer = []

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('## ') or line_stripped.startswith('**'):
                if current_section and buffer:
                    content = '\n'.join(buffer).strip()
                    if 'title' in current_section.lower():
                        data['title'] = content
                    elif 'description' in current_section.lower():
                        data['description'] = content
                    elif 'tag' in current_section.lower():
                        data['tags'] = [t.strip() for t in content.replace('#', '').split(',') if t.strip()]
                    elif 'category' in current_section.lower():
                        data['category'] = content
                    buffer = []
                current_section = line_stripped
            else:
                buffer.append(line)

        # Handle last section
        if current_section and buffer:
            content = '\n'.join(buffer).strip()
            if 'title' in current_section.lower():
                data['title'] = content
            elif 'description' in current_section.lower():
                data['description'] = content
            elif 'tag' in current_section.lower():
                data['tags'] = [t.strip() for t in content.replace('#', '').split(',') if t.strip()]
            elif 'category' in current_section.lower():
                data['category'] = content

        return data


if __name__ == '__main__':
    engine = MetadataEngine()
    meta = engine.generate_metadata(
        episode_title='The Great Forest Picnic Journey - V2',
        episode_description='10 animal friends go on a picnic and learn to count from 1 to 10 in Arabic.',
        characters=['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy'],
        educational_goal='Counting from 1 to 10 in Arabic'
    )
    print(meta)
    engine.save_metadata('ep_001_picnic_journey', meta)
