import os
import re
import json
from datetime import timedelta

class SubtitleEngine:
    """
    Atlas Subtitle Engine
    Generates SRT subtitle files from scripts and audio timing.
    Supports Arabic and English subtitles.
    Can also integrate with OpenAI Whisper for auto-transcription.
    """

    def __init__(self):
        self.default_duration = 2.5  # seconds per dialogue line
        self.gap = 0.3  # gap between subtitles

    def generate_srt_from_script(self, script_path, output_path, language='ar'):
        """
        Parse a markdown script and generate an SRT subtitle file.
        Estimates timing based on word count and scene structure.
        """
        if not os.path.exists(script_path):
            print(f'[SubtitleEngine] Script not found: {script_path}')
            return None

        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        subtitles = []
        current_time = 0.0
        subtitle_index = 1

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match dialogue lines: **CHARACTER:** dialogue
            if '**' in line and ':' in line and not line.startswith('**['):
                parts = line.split(':', 1)
                character = parts[0].replace('*', '').strip()
                dialogue = parts[1].strip() if len(parts) > 1 else ''

                # Remove action cues like (Playfully grumpy...)
                dialogue_clean = re.sub(r'\(.*?\)', '', dialogue).strip()
                if not dialogue_clean:
                    continue

                # Estimate duration based on word count
                word_count = len(dialogue_clean.split())
                duration = max(1.5, min(4.0, word_count * 0.4))

                start = current_time
                end = current_time + duration

                subtitles.append({
                    'index': subtitle_index,
                    'start': start,
                    'end': end,
                    'text': dialogue_clean,
                    'character': character
                })

                subtitle_index += 1
                current_time = end + self.gap

        # Write SRT file
        with open(output_path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                f.write(f"{sub['index']}\n")
                f.write(f"{self._format_time(sub['start'])} --> {self._format_time(sub['end'])}\n")
                f.write(f"{sub['text']}\n\n")

        print(f'[SubtitleEngine] Generated {len(subtitles)} subtitles -> {output_path}')
        return output_path

    def generate_burned_subtitles(self, video_path, srt_path, output_path, font='Arial', fontsize=48, color='yellow'):
        """
        Burn subtitles directly into the video using moviepy.
        Creates a new video with embedded Arabic/English text.
        """
        try:
            from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
        except ImportError:
            print('[SubtitleEngine] moviepy not installed. Skipping subtitle burn.')
            return video_path

        if not os.path.exists(srt_path):
            print(f'[SubtitleEngine] SRT file not found: {srt_path}')
            return video_path

        video = VideoFileClip(video_path)
        subtitle_clips = []

        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # Parse SRT
        blocks = re.split(r'\n\n+', srt_content.strip())
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                text = '\n'.join(lines[2:])

                # Parse time
                match = re.match(r'(\d+:\d+:\d+,\d+)\s+-->\s+(\d+:\d+:\d+,\d+)', time_line)
                if match:
                    start = self._parse_time(match.group(1))
                    end = self._parse_time(match.group(2))

                    txt_clip = TextClip(
                        text,
                        fontsize=fontsize,
                        color=color,
                        font=font,
                        stroke_color='black',
                        stroke_width=2,
                        method='caption',
                        size=(video.w * 0.9, None),
                        align='center'
                    )
                    txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start).set_duration(end - start)
                    subtitle_clips.append(txt_clip)

        final = CompositeVideoClip([video] + subtitle_clips)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', threads=4)
        video.close()
        final.close()

        print(f'[SubtitleEngine] Burned subtitles into {output_path}')
        return output_path

    def _format_time(self, seconds):
        """Convert seconds to SRT time format: HH:MM:SS,mmm"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _parse_time(self, time_str):
        """Parse SRT time format back to seconds."""
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    def generate_whisper_transcription(self, audio_path, output_srt_path, model_size='base'):
        """
        Use OpenAI Whisper to auto-transcribe audio and generate SRT.
        Requires whisper package: pip install openai-whisper
        """
        try:
            import whisper
        except ImportError:
            print('[SubtitleEngine] Whisper not installed. Run: pip install openai-whisper')
            return None

        print(f'[SubtitleEngine] Loading Whisper model: {model_size}')
        model = whisper.load_model(model_size)

        print(f'[SubtitleEngine] Transcribing: {audio_path}')
        result = model.transcribe(audio_path, language='ar', task='transcribe')

        # Write SRT from segments
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], 1):
                start = segment['start']
                end = segment['end']
                text = segment['text'].strip()
                f.write(f"{i}\n")
                f.write(f"{self._format_time(start)} --> {self._format_time(end)}\n")
                f.write(f"{text}\n\n")

        print(f'[SubtitleEngine] Whisper transcription saved: {output_srt_path}')
        return output_srt_path


if __name__ == '__main__':
    engine = SubtitleEngine()
    # Generate from script
    engine.generate_srt_from_script(
        'episodes/ep_001_picnic_journey/script/story_v2.md',
        'episodes/ep_001_picnic_journey/final/subtitles.srt'
    )
