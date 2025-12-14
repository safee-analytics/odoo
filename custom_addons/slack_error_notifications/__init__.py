import logging
import os
import traceback
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

_logger = logging.getLogger(__name__)


class SlackHandler(logging.Handler):
    """Custom logging handler that sends errors to Slack"""

    def __init__(self, webhook_url, channel='#odoo-errors'):
        super().__init__()
        self.webhook_url = webhook_url
        self.channel = channel
        self.setLevel(logging.ERROR)

    def emit(self, record):
        """Send log record to Slack"""
        try:
            # Format the message
            message = self.format_slack_message(record)

            # Send to Slack
            self.send_to_slack(message)
        except Exception as e:
            # Don't let Slack errors break the application
            _logger.error(f"Failed to send error to Slack: {e}")

    def format_slack_message(self, record):
        """Format log record as Slack message"""
        # Get database/company context
        db_name = getattr(record, 'dbname', 'unknown')

        # Build attachment
        attachment = {
            'color': 'danger',
            'title': f'🚨 Odoo Error: {record.levelname}',
            'text': record.getMessage(),
            'fields': [
                {
                    'title': 'Database',
                    'value': db_name,
                    'short': True
                },
                {
                    'title': 'Logger',
                    'value': record.name,
                    'short': True
                },
                {
                    'title': 'File',
                    'value': f"{record.pathname}:{record.lineno}",
                    'short': False
                }
            ],
            'footer': 'Safee Odoo',
            'ts': int(record.created)
        }

        # Add traceback if available
        if record.exc_info:
            tb = ''.join(traceback.format_exception(*record.exc_info))
            attachment['fields'].append({
                'title': 'Traceback',
                'value': f"```{tb[:2000]}```",  # Limit to 2000 chars
                'short': False
            })

        return {
            'channel': self.channel,
            'username': 'Odoo Error Bot',
            'icon_emoji': ':rotating_light:',
            'attachments': [attachment]
        }

    def send_to_slack(self, message):
        """Send message to Slack webhook"""
        data = json.dumps(message).encode('utf-8')
        request = Request(
            self.webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            with urlopen(request, timeout=5) as response:
                if response.status != 200:
                    _logger.error(f"Slack returned status {response.status}")
        except URLError as e:
            _logger.error(f"Failed to send to Slack: {e}")


def setup_slack_logging():
    """Initialize Slack error logging"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    if not webhook_url:
        _logger.info("SLACK_WEBHOOK_URL not set - Slack error notifications disabled")
        return

    channel = os.environ.get('SLACK_ERROR_CHANNEL', '#odoo-errors')

    # Add handler to root logger
    root_logger = logging.getLogger()
    slack_handler = SlackHandler(webhook_url, channel)

    # Format errors nicely
    formatter = logging.Formatter(
        '%(levelname)s %(name)s: %(message)s'
    )
    slack_handler.setFormatter(formatter)

    root_logger.addHandler(slack_handler)

    _logger.info(f"Slack error notifications enabled for channel: {channel}")


# Initialize on module load
setup_slack_logging()
