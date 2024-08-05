import time
import requests
from datetime import datetime, timedelta
import os

# Choose notification method: 'discord', 'telegram', or 'both'
NOTIFICATION_METHOD = 'both'

# Discord webhook
DISCORD_WEBHOOK_URL = '' # Put your Discord webhook URL here

# Telegram Bot
TELEGRAM_BOT_TOKEN = '' # Put your Telegram bot token here
TELEGRAM_CHAT_ID = '' # Put your Telegram chat ID here

# Path to the text log files
FAIL2BAN_LOGS = '/var/log/fail2ban.log'
AUTH_LOGS = '/var/log/auth.log'
MAIL_LOGS = '/var/log/mail.log'
HISTORY_LOGS = '/var/log/apt/history.log'
TERM_LOGS = '/var/log/apt/term.log'
EXIM4_LOGS = '/var/log/exim4/mainlog'
DB_LOGS = '/var/log/mysql/error.log'
APACHE2_LOGS_ACCESS = '/var/log/apache2/access.log'
APACHE2_LOGS_ERROR = '/var/log/apache2/error.log'
NGINX_LOGS_ACCESS = '/var/log/nginx/access.log'
NGINX_LOGS_ERROR = '/var/log/nginx/error.log'

LOG_FILES = [FAIL2BAN_LOGS, AUTH_LOGS, MAIL_LOGS, HISTORY_LOGS, TERM_LOGS, EXIM4_LOGS, DB_LOGS, 
             APACHE2_LOGS_ACCESS, APACHE2_LOGS_ERROR, NGINX_LOGS_ACCESS, NGINX_LOGS_ERROR]

def send_discord_message(content):
    if NOTIFICATION_METHOD in ['discord', 'both']:
        data = {
            "content": content
        }
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send Discord message: {str(e)}")

def send_telegram_message(message):
    if NOTIFICATION_METHOD in ['telegram', 'both']:
        try:
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(telegram_url, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send Telegram message: {str(e)}")

def send_notification(content):
    send_discord_message(content)
    send_telegram_message(content)

def main():
    log_file_last_lines = {}
    for log_file in LOG_FILES:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    log_file_last_lines[log_file] = lines[-1]
                else:
                    log_file_last_lines[log_file] = ''
        else:
            log_file_last_lines[log_file] = ''

    while True:
        for log_file in LOG_FILES:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines and lines[-1] != log_file_last_lines[log_file]:
                        current_time = datetime.now().strftime('%m-%d %H:%M:%S')
                        new_content = ''.join(lines[len(lines) - len(log_file_last_lines[log_file].split('\n')):])
                        log_type = os.path.basename(log_file).split('.')[0].upper()
                        if 'error' in log_file.lower():
                            message = f'❗️ **{log_type}** Ubuntu Server, date: {current_time} **ERROR LOG:**\n```\n{new_content}\n```'
                        else:
                            message = f'📃 **{log_type}** Ubuntu Server, date: {current_time} **LOG:**\n```\n{new_content}\n```'
                        send_notification(message)
                        log_file_last_lines[log_file] = lines[-1]
        time.sleep(1)

if __name__ == '__main__': # Everything in loop in case of any error
    while True:
        try:
            main()
        except Exception as error:
            error_message = f'❗️ An error occurred ERROR: \n{str(error)}'
            print(error_message)
            send_notification(error_message)
            time.sleep(60)  # Wait for 60 seconds before retrying
