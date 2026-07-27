import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

class AnalyticsEngine:
    """
    Atlas Analytics Engine
    Pulls YouTube performance data and generates improvement recommendations.
    Feeds insights back into the content creation pipeline.
    """

    def __init__(self, credentials_path='token.pickle'):
        self.credentials_path = credentials_path
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube Analytics API."""
        if not os.path.exists(self.credentials_path):
            print('[AnalyticsEngine] WARNING: No credentials found. Running in simulation mode.')
            return

        with open(self.credentials_path, 'rb') as token:
            creds = pickle.load(token)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        self.youtube = build('youtube', 'v3', credentials=creds)
        print('[AnalyticsEngine] Authenticated with YouTube API.')

    def get_video_stats(self, video_id):
        """Get basic stats for a single video."""
        if not self.youtube:
            return self._simulate_stats(video_id)

        response = self.youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=video_id
        ).execute()

        if not response['items']:
            return None

        item = response['items'][0]
        stats = item['statistics']
        snippet = item['snippet']

        return {
            'video_id': video_id,
            'title': snippet['title'],
            'published_at': snippet['publishedAt'],
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments': int(stats.get('commentCount', 0)),
            'duration': snippet.get('duration', 'N/A')
        }

    def get_channel_stats(self):
        """Get overall channel statistics."""
        if not self.youtube:
            return {'status': 'simulated'}

        # Get channel ID from token
        channels = self.youtube.channels().list(
            part='statistics,snippet',
            mine=True
        ).execute()

        if not channels['items']:
            return None

        channel = channels['items'][0]
        return {
            'channel_name': channel['snippet']['title'],
            'subscribers': int(channel['statistics'].get('subscriberCount', 0)),
            'total_views': int(channel['statistics'].get('viewCount', 0)),
            'total_videos': int(channel['statistics'].get('videoCount', 0)),
            'hidden_subscribers': channel['statistics'].get('hiddenSubscriberCount', False)
        }

    def generate_performance_report(self, video_ids):
        """
        Generate a performance report for multiple videos.
        Returns insights and recommendations.
        """
        videos = []
        for vid in video_ids:
            stats = self.get_video_stats(vid)
            if stats:
                videos.append(stats)

        if not videos:
            return None

        # Calculate metrics
        total_views = sum(v['views'] for v in videos)
        total_likes = sum(v['likes'] for v in videos)
        total_comments = sum(v['comments'] for v in videos)
        avg_views = total_views / len(videos) if videos else 0

        # Engagement rate
        engagement_rates = []
        for v in videos:
            if v['views'] > 0:
                rate = ((v['likes'] + v['comments']) / v['views']) * 100
                engagement_rates.append(rate)
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_videos_analyzed': len(videos),
                'total_views': total_views,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'average_views_per_video': round(avg_views, 2),
                'average_engagement_rate': round(avg_engagement, 2)
            },
            'videos': videos,
            'recommendations': self._generate_recommendations(videos, avg_engagement)
        }

        return report

    def _generate_recommendations(self, videos, avg_engagement):
        """AI-powered recommendations based on performance data."""
        recommendations = []

        # Sort by views
        sorted_videos = sorted(videos, key=lambda x: x['views'], reverse=True)
        best = sorted_videos[0] if sorted_videos else None
        worst = sorted_videos[-1] if len(sorted_videos) > 1 else None

        if best:
            recommendations.append(f"Top performer: '{best['title']}' with {best['views']} views. Analyze what made it successful.")

        if worst and best:
            recommendations.append(f"Lowest performer: '{worst['title']}' with {worst['views']} views. Consider A/B testing thumbnails or titles.")

        if avg_engagement < 2.0:
            recommendations.append("Engagement rate is low. Consider adding call-to-action prompts in videos (e.g., 'Count with us!').")
        elif avg_engagement > 5.0:
            recommendations.append("Excellent engagement! The audience loves this content. Produce more episodes with similar themes.")

        if len(videos) >= 3:
            recent = videos[-3:]
            recent_views = sum(v['views'] for v in recent) / 3
            older = videos[:-3]
            if older:
                older_views = sum(v['views'] for v in older) / len(older)
                if recent_views > older_views * 1.2:
                    recommendations.append("Recent videos are outperforming older ones. The content is improving!")
                elif recent_views < older_views * 0.8:
                    recommendations.append("Recent videos are underperforming. Consider refreshing the format or educational topic.")

        recommendations.append("Schedule: Maintain consistent publishing (e.g., 2 episodes per week) to build audience habit.")
        recommendations.append("SEO: Ensure titles include high-value keywords like 'تعلم', 'أطفال', 'عد', 'colors', 'counting'.")

        return recommendations

    def save_report(self, report, output_path):
        """Save report as JSON."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f'[AnalyticsEngine] Report saved: {output_path}')
        return output_path

    def _simulate_stats(self, video_id):
        """Simulate stats when API is unavailable."""
        return {
            'video_id': video_id,
            'title': 'Simulated Video',
            'published_at': datetime.now().isoformat(),
            'views': 1500,
            'likes': 120,
            'comments': 15,
            'duration': 'PT1M30S',
            'simulated': True
        }

    def update_episode_analytics(self, episode_id, video_id, db_path='atlas.db'):
        """Store analytics in the database for long-term tracking."""
        import sqlite3
        stats = self.get_video_stats(video_id)
        if not stats:
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analytics (episode_id, platform, views, likes, comments, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            episode_id,
            'youtube',
            stats['views'],
            stats['likes'],
            stats['comments'],
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        print(f'[AnalyticsEngine] Analytics stored for {episode_id}')
        return True


if __name__ == '__main__':
    engine = AnalyticsEngine()
    # Simulate report
    report = engine.generate_performance_report(['SIMULATED_ID_1', 'SIMULATED_ID_2'])
    if report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        engine.save_report(report, 'reports/performance_report.json')
