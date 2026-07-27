import os
import yaml
from datetime import datetime

class ConfigManager:
    """
    Atlas Config Manager
    Manages episode configurations via YAML files.
    Allows non-technical users to define episodes without touching code.
    """

    def __init__(self, config_dir='configs'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

    def create_episode_config(self, episode_id, title, educational_goal, characters,
                               target_age='3-7', language='arabic', budget_limit=20.0,
                              duration_seconds=60, num_scenes=10, setting='magical green forest',
                              style='3D animated, Pixar style, vibrant colors, highly detailed, 4k resolution, cinematic lighting, calm and child-safe movement'):
        """
        Create a new episode configuration YAML file.
        """
        config = {
            'episode': {
                'id': episode_id,
                'title': title,
                'title_arabic': '',
                'version': '1.0',
                'status': 'concept',
                'created_at': datetime.now().isoformat()
            },
            'target_audience': {
                'age_range': target_age,
                'language': language,
                'region': 'MENA',
                'platforms': ['youtube', 'facebook', 'instagram']
            },
            'educational': {
                'primary_goal': educational_goal,
                'secondary_goals': [],
                'learning_objectives': []
            },
            'production': {
                'budget_limit': budget_limit,
                'duration_seconds': duration_seconds,
                'num_scenes': num_scenes,
                'setting': setting,
                'style': style,
                'aspect_ratio': '16:9',
                'resolution': '1080p',
                'frame_rate': 24
            },
            'characters': {
                'cast': characters,
                'new_characters': [],
                'guest_characters': []
            },
            'content_safety': {
                'coppa_compliant': True,
                'age_appropriate': True,
                'no_violence': True,
                'no_scary_content': True,
                'positive_message': True
            },
            'publishing': {
                'youtube': {
                    'category': 'Education',
                    'privacy': 'public',
                    'made_for_kids': True,
                    'schedule': None,
                    'playlists': ['Atlas Kids Media - Season 1']
                },
                'facebook': {
                    'enabled': False
                },
                'instagram': {
                    'enabled': False,
                    'reels': False
                }
            },
            'analytics': {
                'track_views': True,
                'track_likes': True,
                'track_comments': True,
                'track_watch_time': True,
                'improvement_loop': True
            }
        }

        path = f'{self.config_dir}/{episode_id}.yaml'
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f'[ConfigManager] Created config: {path}')
        return path

    def load_config(self, episode_id):
        """Load an episode configuration."""
        path = f'{self.config_dir}/{episode_id}.yaml'
        if not os.path.exists(path):
            print(f'[ConfigManager] Config not found: {path}')
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def update_config(self, episode_id, updates):
        """Update specific fields in a config."""
        config = self.load_config(episode_id)
        if not config:
            return False

        # Deep merge updates
        self._deep_update(config, updates)
        config['episode']['updated_at'] = datetime.now().isoformat()

        path = f'{self.config_dir}/{episode_id}.yaml'
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f'[ConfigManager] Updated config: {path}')
        return True

    def _deep_update(self, d, u):
        """Recursively update nested dict."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def list_configs(self):
        """List all episode configs."""
        files = [f for f in os.listdir(self.config_dir) if f.endswith('.yaml')]
        return [f.replace('.yaml', '') for f in files]

    def get_production_plan(self, episode_id):
        """Generate a production plan from config."""
        config = self.load_config(episode_id)
        if not config:
            return None

        plan = {
            'episode_id': episode_id,
            'title': config['episode']['title'],
            'phases': [
                {'phase': 'script', 'estimated_cost': 0.01, 'estimated_time': '5 min'},
                {'phase': 'voice', 'estimated_cost': 0.0, 'estimated_time': '3 min'},
                {'phase': 'motion_prompts', 'estimated_cost': 0.01, 'estimated_time': '5 min'},
                {'phase': 'video_generation', 'estimated_cost': config['production']['num_scenes'] * 0.50, 'estimated_time': f"{config['production']['num_scenes'] * 2} min"},
                {'phase': 'editing', 'estimated_cost': 0.0, 'estimated_time': '10 min'},
                {'phase': 'thumbnail', 'estimated_cost': 0.04, 'estimated_time': '2 min'},
                {'phase': 'metadata', 'estimated_cost': 0.01, 'estimated_time': '3 min'},
                {'phase': 'publishing', 'estimated_cost': 0.0, 'estimated_time': '5 min'},
            ],
            'total_estimated_cost': sum(p['estimated_cost'] for p in [
                {'phase': 'script', 'estimated_cost': 0.01},
                {'phase': 'voice', 'estimated_cost': 0.0},
                {'phase': 'motion_prompts', 'estimated_cost': 0.01},
                {'phase': 'video_generation', 'estimated_cost': config['production']['num_scenes'] * 0.50},
                {'phase': 'editing', 'estimated_cost': 0.0},
                {'phase': 'thumbnail', 'estimated_cost': 0.04},
                {'phase': 'metadata', 'estimated_cost': 0.01},
                {'phase': 'publishing', 'estimated_cost': 0.0},
            ]),
            'total_estimated_time': '33 min'
        }
        return plan


if __name__ == '__main__':
    cm = ConfigManager()

    # Create config for Episode 003
    cm.create_episode_config(
        episode_id='ep_003_space_journey',
        title='The Space Journey',
        title_arabic='رحلة الفضاء',
        educational_goal='Learning shapes in Arabic',
        characters=['Sokkar', 'Felix', 'Bonnie', 'Barnaby', 'Tweety', 'Bambi', 'Torti', 'Ricky', 'Henry', 'Freddy'],
        target_age='3-7',
        language='arabic',
        budget_limit=25.0,
        duration_seconds=90,
        num_scenes=12,
        setting='colorful space station with planets and stars'
    )

    # Load and print
    config = cm.load_config('ep_003_space_journey')
    print(yaml.dump(config, allow_unicode=True))

    # Get production plan
    plan = cm.get_production_plan('ep_003_space_journey')
    print(f"\nEstimated cost: ${plan['total_estimated_cost']:.2f}")
