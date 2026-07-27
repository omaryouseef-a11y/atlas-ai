import os
import sys
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, TextClip, ColorClip
)
from moviepy.video.fx.all import fadein, fadeout

class EditorEngine:
    """
    Atlas Editor Engine
    Assembles final episode video from:
    - Generated video clips (scenes)
    - Voice audio files
    - Background music
    - Text overlays (counting numbers, titles)
    - Transitions (fade in/out)
    """

    def __init__(self, episode_id):
        self.episode_id = episode_id
        self.base_path = f'episodes/{episode_id}'
        self.final_dir = f'{self.base_path}/final'
        os.makedirs(self.final_dir, exist_ok=True)

    def assemble_episode(self, video_clips_dir, audio_dir, output_filename='final_episode.mp4'):
        """
        Assemble the full episode.
        video_clips_dir: directory containing scene_001.mp4, scene_002.mp4, etc.
        audio_dir: directory containing line_001_SOKKAR.mp3, etc.
        """
        print(f'[EditorEngine] Starting assembly for {self.episode_id}...')

        # 1. Load video clips in order
        video_files = sorted([
            f for f in os.listdir(video_clips_dir)
            if f.startswith('scene_') and f.endswith('.mp4')
        ])

        if not video_files:
            print(f'[EditorEngine] No video clips found in {video_clips_dir}')
            return None

        clips = []
        for vf in video_files:
            path = os.path.join(video_clips_dir, vf)
            try:
                clip = VideoFileClip(path)
                # Ensure all clips are same size
                if clip.size != (1920, 1080):
                    clip = clip.resize(newsize=(1920, 1080))
                clips.append(clip)
            except Exception as e:
                print(f'[EditorEngine] Warning: Could not load {vf}: {e}')
                # Insert a placeholder color clip
                placeholder = ColorClip(size=(1920, 1080), color=(34, 139, 34), duration=3)
                clips.append(placeholder)

        # 2. Add fade transitions between clips
        processed_clips = []
        for i, clip in enumerate(clips):
            clip = fadein(clip, 0.5)
            clip = fadeout(clip, 0.5)
            processed_clips.append(clip)

        video_sequence = concatenate_videoclips(processed_clips, method='compose')

        # 3. Load and overlay voice audio
        voice_files = sorted([
            f for f in os.listdir(audio_dir)
            if f.endswith('.mp3')
        ])

        voice_clips = []
        current_time = 0
        for vf in voice_files:
            path = os.path.join(audio_dir, vf)
            try:
                audio = AudioFileClip(path)
                # Position voice at start of corresponding scene (approximate)
                voice_clips.append(audio.set_start(current_time))
                current_time += 3.0  # Approximate scene duration
            except Exception as e:
                print(f'[EditorEngine] Warning: Could not load audio {vf}: {e}')

        if voice_clips:
            voice_track = CompositeVideoClip([video_sequence]).audio
            # Actually, we need to composite audio properly
            from moviepy.editor import CompositeAudioClip
            voice_audio = CompositeAudioClip(voice_clips)
            # Normalize volume
            voice_audio = voice_audio.volumex(1.2)
        else:
            voice_audio = None

        # 4. Add background music (if available)
        bg_music_path = 'media_library/music/background_cheerful.mp3'
        if os.path.exists(bg_music_path):
            bg_music = AudioFileClip(bg_music_path)
            # Loop if shorter than video
            if bg_music.duration < video_sequence.duration:
                loops = int(video_sequence.duration / bg_music.duration) + 1
                bg_music = concatenate_videoclips([bg_music] * loops)
            bg_music = bg_music.subclip(0, video_sequence.duration)
            bg_music = bg_music.volumex(0.15)  # Very quiet background
        else:
            bg_music = None

        # 5. Combine audio tracks
        audio_tracks = []
        if voice_audio:
            audio_tracks.append(voice_audio)
        if bg_music:
            audio_tracks.append(bg_music)

        if audio_tracks:
            from moviepy.editor import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_tracks)
            video_sequence = video_sequence.set_audio(final_audio)

        # 6. Add text overlays for counting numbers
        text_overlays = self._create_counting_overlays(video_sequence.duration, len(clips))
        if text_overlays:
            final_video = CompositeVideoClip([video_sequence] + text_overlays)
        else:
            final_video = video_sequence

        # 7. Add intro title card
        intro = self._create_title_card()
        final_video = concatenate_videoclips([intro, final_video], method='compose')

        # 8. Export
        output_path = f'{self.final_dir}/{output_filename}'
        print(f'[EditorEngine] Exporting to {output_path}...')
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=4,
            preset='medium'
        )

        # Cleanup
        for clip in clips:
            clip.close()
        video_sequence.close()
        final_video.close()

        print(f'[EditorEngine] Episode assembled successfully: {output_path}')
        return output_path

    def _create_counting_overlays(self, total_duration, num_scenes):
        """Create Arabic numeral overlays that appear during each scene."""
        overlays = []
        scene_duration = total_duration / num_scenes if num_scenes > 0 else total_duration

        arabic_numerals = ['١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '١٠']

        for i in range(min(num_scenes, 10)):
            start_time = i * scene_duration
            txt = TextClip(
                arabic_numerals[i],
                fontsize=120,
                color='yellow',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=3
            )
            txt = txt.set_position(('center', 'top')).set_start(start_time).set_duration(scene_duration)
            txt = fadein(txt, 0.3).fadeout(0.3)
            overlays.append(txt)

        return overlays

    def _create_title_card(self):
        """Create a 3-second intro title card."""
        bg = ColorClip(size=(1920, 1080), color=(50, 150, 50), duration=3)
        title = TextClip(
            'Atlas Kids Media\nرحلة النزهة في الغابة',
            fontsize=80,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(1920, 1080),
            align='center'
        )
        title = title.set_duration(3)
        subtitle = TextClip(
            'تعلم العد من ١ إلى ١٠',
            fontsize=50,
            color='yellow',
            font='Arial',
            method='caption',
            size=(1920, 1080),
            align='center'
        )
        subtitle = subtitle.set_position(('center', 700)).set_duration(3)

        card = CompositeVideoClip([bg, title, subtitle])
        card = fadeout(card, 0.5)
        return card


if __name__ == '__main__':
    editor = EditorEngine('ep_001_picnic_journey')
    result = editor.assemble_episode(
        video_clips_dir='episodes/ep_001_picnic_journey/video_v2',
        audio_dir='episodes/ep_001_picnic_journey/voice_v2'
    )
    if result:
        print(f'Final video: {result}')
