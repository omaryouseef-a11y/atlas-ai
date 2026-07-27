import os
import time
import functools
from dotenv import load_dotenv

load_dotenv()

class RetryWithBackoff:
    """
    Atlas Retry System
    Decorator for resilient API calls with exponential backoff.
    Automatically retries failed operations and sends notifications.
    """

    def __init__(self, max_retries=3, base_delay=2.0, max_delay=60.0,
                 exceptions=(Exception,), on_retry=None, on_fail=None):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions
        self.on_retry = on_retry
        self.on_fail = on_fail

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                        print(f'[Retry] {func.__name__} failed (attempt {attempt + 1}/{self.max_retries + 1}). Retrying in {delay}s...')
                        if self.on_retry:
                            self.on_retry(func.__name__, attempt + 1, str(e), delay)
                        time.sleep(delay)
                    else:
                        print(f'[Retry] {func.__name__} failed after {self.max_retries + 1} attempts. Giving up.')
                        if self.on_fail:
                            self.on_fail(func.__name__, str(e))
            raise last_exception
        return wrapper


class NotificationEngine:
    """
    Atlas Notification Engine
    Sends alerts via Slack, Email, or console for pipeline events.
    """

    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.alert_email = os.getenv('ALERT_EMAIL')

    def send_slack(self, message, level='info'):
        """Send a Slack notification."""
        if not self.slack_webhook:
            print(f'[Notification] Slack not configured. Message: {message}')
            return False

        import requests
        color_map = {
            'info': '#36a64f',
            'warning': '#ff9900',
            'error': '#ff0000',
            'success': '#00ff00'
        }

        payload = {
            'attachments': [{
                'color': color_map.get(level, '#36a64f'),
                'title': f'Atlas Kids Media - {level.upper()}',
                'text': message,
                'footer': 'Atlas AI Pipeline',
                'ts': int(time.time())
            }]
        }

        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f'[Notification] Slack send failed: {e}')
            return False

    def send_email(self, subject, body, level='info'):
        """Send an email notification."""
        if not self.email_enabled or not self.smtp_host:
            print(f'[Notification] Email not configured. Subject: {subject}')
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = f'[Atlas {level.upper()}] {subject}'
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f'[Notification] Email send failed: {e}')
            return False

    def notify(self, message, level='info', channels=None):
        """
        Send notification through all configured channels.
        levels: info, warning, error, success
        """
        if channels is None:
            channels = ['console']
            if self.slack_webhook:
                channels.append('slack')
            if self.email_enabled:
                channels.append('email')

        results = {}
        for channel in channels:
            if channel == 'console':
                print(f'[Atlas {level.upper()}] {message}')
                results['console'] = True
            elif channel == 'slack':
                results['slack'] = self.send_slack(message, level)
            elif channel == 'email':
                results['email'] = self.send_email(f'Atlas Alert - {level}', message, level)

        return results

    def notify_pipeline_start(self, episode_id):
        self.notify(f'Pipeline started for {episode_id}', 'info')

    def notify_pipeline_complete(self, episode_id, video_url=None):
        msg = f'Pipeline complete for {episode_id}'
        if video_url:
            msg += f' | Video: {video_url}'
        self.notify(msg, 'success')

    def notify_pipeline_failure(self, episode_id, error):
        self.notify(f'Pipeline FAILED for {episode_id}: {error}', 'error')

    def notify_budget_warning(self, episode_id, spent, limit):
        self.notify(f'Budget warning for {episode_id}: ${spent:.2f} / ${limit:.2f}', 'warning')

    def notify_qa_rejection(self, episode_id, reason):
        self.notify(f'QA rejected prompt for {episode_id}: {reason}', 'warning')


# Convenience decorator factory
def resilient(max_retries=3, base_delay=2.0, notify_on_fail=True):
    """Decorator factory that adds retry + notification."""
    notifier = NotificationEngine()

    def on_retry(func_name, attempt, error, delay):
        if notify_on_fail:
            notifier.notify(f'{func_name} retry #{attempt} after error: {error}', 'warning', ['console'])

    def on_fail(func_name, error):
        if notify_on_fail:
            notifier.notify(f'{func_name} failed permanently: {error}', 'error')

    return RetryWithBackoff(
        max_retries=max_retries,
        base_delay=base_delay,
        on_retry=on_retry,
        on_fail=on_fail
    )


if __name__ == '__main__':
    # Test retry decorator
    @resilient(max_retries=2, base_delay=1.0)
    def flaky_api_call():
        import random
        if random.random() < 0.7:
            raise ConnectionError('Simulated API failure')
        return 'Success!'

    try:
        result = flaky_api_call()
        print(f'Result: {result}')
    except Exception as e:
        print(f'Final failure: {e}')

    # Test notifications
    notifier = NotificationEngine()
    notifier.notify('Atlas pipeline test notification', 'info')
