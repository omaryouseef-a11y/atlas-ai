import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

FAL_API_KEY = os.getenv('FAL_API_KEY')
FAL_VIDEO_ENDPOINT = 'https://queue.fal.run/fal-ai/veo3'  # Veo 3 via Fal.ai

class VideoEngine:
    """
    Atlas Video Engine
    Integrates with Fal.ai to generate video clips from text prompts.
    Supports Veo 3, Kling, and other models via Fal.ai's unified API.
    """

    def __init__(self):
        self.api_key = FAL_API_KEY
        if not self.api_key:
            print('WARNING: FAL_API_KEY not found. Video generation will be simulated.')
        self.headers = {
            'Authorization': f'Key {self.api_key}',
            'Content-Type': 'application/json'
        }

    def generate_video(self, prompt, output_path, aspect_ratio='16:9', duration=5):
        """
        Generate a video clip from a text prompt.
        Returns the path to the downloaded video file.
        """
        if not self.api_key:
            print(f'[VideoEngine] SIMULATING video generation for: {prompt[:50]}...')
            # Create a placeholder file
            with open(output_path, 'w') as f:
                f.write('MOCK_VIDEO')
            return output_path, 0.0

        print(f'[VideoEngine] Submitting prompt to Fal.ai: {prompt[:60]}...')

        # 1. Submit request
        payload = {
            'prompt': prompt,
            'aspect_ratio': aspect_ratio,
            'duration': duration,
        }

        try:
            response = requests.post(
                FAL_VIDEO_ENDPOINT,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            request_id = data.get('request_id')

            if not request_id:
                raise ValueError(f'No request_id in response: {data}')

            print(f'[VideoEngine] Request queued. ID: {request_id}')

            # 2. Poll for completion
            video_url = self._poll_for_result(request_id)

            # 3. Download video
            self._download_video(video_url, output_path)

            # Veo 3 costs approximately $0.35-$0.50 per 5-second clip on Fal.ai
            estimated_cost = 0.50
            print(f'[VideoEngine] Video saved to {output_path}. Cost: ${estimated_cost}')
            return output_path, estimated_cost

        except requests.exceptions.RequestException as e:
            print(f'[VideoEngine] API Error: {e}')
            raise

    def _poll_for_result(self, request_id, max_retries=60, delay=10):
        """Poll Fal.ai status endpoint until video is ready."""
        status_url = f'https://queue.fal.run/fal-ai/veo3/requests/{request_id}'

        for attempt in range(max_retries):
            resp = requests.get(status_url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            status = data.get('status')
            if status == 'COMPLETED':
                return data['video']['url']
            elif status == 'FAILED':
                raise RuntimeError(f'Video generation failed: {data.get("error", "Unknown error")}')

            print(f'[VideoEngine] Polling... ({attempt + 1}/{max_retries}) Status: {status}')
            time.sleep(delay)

        raise TimeoutError('Video generation timed out after polling.')

    def _download_video(self, url, output_path):
        """Download video from URL to local file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    def generate_episode_clips(self, episode_id, prompts_file, output_dir):
        """
        Generate all video clips for an episode from a prompts markdown file.
        Returns list of (scene_num, video_path, cost) tuples.
        """
        if not os.path.exists(prompts_file):
            raise FileNotFoundError(f'Prompts file not found: {prompts_file}')

        with open(prompts_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clips = []
        scene_num = 0

        for line in lines:
            if '**Prompt:**' in line:
                scene_num += 1
                prompt = line.split('**Prompt:**')[1].strip()
                output_path = f'{output_dir}/scene_{scene_num:03d}.mp4'

                # Skip if already exists (idempotency)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                    print(f'[VideoEngine] Scene {scene_num} already exists. Skipping.')
                    clips.append((scene_num, output_path, 0.0))
                    continue

                print(f'\n--- Generating Scene {scene_num} ---')
                path, cost = self.generate_video(prompt, output_path)
                clips.append((scene_num, path, cost))

        return clips


if __name__ == '__main__':
    ve = VideoEngine()
    # Test with a single prompt
    test_prompt = 'A cute fluffy squirrel in a magical green forest. 3D animated, Pixar style.'
    ve.generate_video(test_prompt, 'test_output.mp4')
