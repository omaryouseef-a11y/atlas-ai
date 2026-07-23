import os
import re
from gtts import gTTS

def generate_voices():
    script_path = 'episodes/ep_001_picnic_journey/script/story.md'
    output_dir = 'episodes/ep_001_picnic_journey/voice'
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(script_path):
        print('Script not found!')
        return

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find dialogues like: **Character Name**: (Emotion) Dialogue text
    # Or just **Character Name**: Dialogue text
    lines = content.split('\n')
    
    audio_count = 1
    for line in lines:
        if '**' in line and ':' in line:
            parts = line.split(':', 1)
            character_part = parts[0].replace('*', '').strip()
            dialogue_part = parts[1].strip()
            
            # Remove action cues like (يبتسم) or (بحب)
            dialogue_clean = re.sub(r'\(.*?\)', '', dialogue_part).strip()
            
            if dialogue_clean:
                print(f'🎙️ Recording {character_part} (Line {audio_count})...')
                try:
                    # Using Google TTS (Arabic)
                    tts = gTTS(text=dialogue_clean, lang='ar', slow=False)
                    filename = f'{output_dir}/line_{audio_count:03d}_{character_part.split()[0]}.mp3'
                    tts.save(filename)
                    audio_count += 1
                except Exception as e:
                    print(f'Error generating audio: {e}')

if __name__ == '__main__':
    print('🔊 Triggering Phase 2: Voice Engine (Google TTS)...')
    generate_voices()
    print('\n✅ Voice generation complete! Audio files saved to episodes/ep_001_picnic_journey/voice/')
