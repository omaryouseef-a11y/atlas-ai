import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# YouTube Data API v3 scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubePublisher:
    """
    Atlas YouTube Publisher
    Handles OAuth2 authentication and video upload to YouTube.
    Also manages playlist organization and scheduling.
    """

    def __init__(self, credentials_path='client_secrets.json'):
        self.credentials_path = credentials_path
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube Data API via OAuth2."""
        creds = None
        token_file = 'token.pickle'

        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f'[YouTubePublisher] WARNING: {self.credentials_path} not found.')
                    print('Please download client secrets from Google Cloud Console.')
                    print('Publisher will run in SIMULATION mode.')
                    return
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token for future runs
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.youtube = build('youtube', 'v3', credentials=creds)
        print('[YouTubePublisher] Authenticated successfully.')

    def upload_video(self, video_path, title, description, tags, category_id='27',
                     privacy_status='private', thumbnail_path=None):
        """
        Upload a video to YouTube.
        privacy_status: 'private', 'unlisted', or 'public'
        category_id: 27 = Education, 1 = Film & Animation, etc.
        """
        if not self.youtube:
            print('[YouTubePublisher] SIMULATION MODE: Would upload:')
            print(f'  Video: {video_path}')
            print(f'  Title: {title}')
            print(f'  Tags: {tags}')
            return {'id': 'SIMULATED_VIDEO_ID', 'status': 'simulated'}

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id,
                'defaultLanguage': 'ar',
                'defaultAudioLanguage': 'ar'
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': True,  # COPPA compliance
                'embeddable': True,
                'license': 'youtube'
            }
        }

        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)

        print(f'[YouTubePublisher] Uploading {video_path}...')
        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f'[YouTubePublisher] Upload progress: {int(status.progress() * 100)}%')

        video_id = response['id']
        print(f'[YouTubePublisher] Upload complete! Video ID: {video_id}')

        # Upload thumbnail if provided
        if thumbnail_path and os.path.exists(thumbnail_path):
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype='image/png')
            ).execute()
            print(f'[YouTubePublisher] Thumbnail uploaded.')

        return response

    def add_to_playlist(self, video_id, playlist_id):
        """Add video to a playlist."""
        if not self.youtube:
            print(f'[YouTubePublisher] SIMULATION: Would add {video_id} to playlist {playlist_id}')
            return

        self.youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        ).execute()
        print(f'[YouTubePublisher] Added to playlist.')

    def schedule_video(self, video_id, publish_at):
        """
        Schedule a video for future publication.
        publish_at: ISO 8601 datetime string (e.g., '2026-08-01T10:00:00Z')
        """
        if not self.youtube:
            print(f'[YouTubePublisher] SIMULATION: Would schedule {video_id} for {publish_at}')
            return

        self.youtube.videos().update(
            part='status',
            body={
                'id': video_id,
                'status': {
                    'privacyStatus': 'private',
                    'publishAt': publish_at,
                    'selfDeclaredMadeForKids': True
                }
            }
        ).execute()
        print(f'[YouTubePublisher] Scheduled for {publish_at}.')


if __name__ == '__main__':
    pub = YouTubePublisher()
    # Simulation test
    pub.upload_video(
        video_path='episodes/ep_001_picnic_journey/final/final_episode.mp4',
        title='تعلم العد من 1 إلى 10 | رحلة النزهة في الغابة | Atlas Kids Media',
        description='Test description',
        tags=['تعليم الأطفال', 'العد', 'أطفال', 'عربي', 'kids education', 'counting'],
        privacy_status='private'
    )
