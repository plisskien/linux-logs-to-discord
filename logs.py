import os
import time
import requests
from datetime import datetime, timedelta

WEBHOOK_URL = '' # Put here you Discord webhook

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

LOG_FILES = [FAIL2BAN_LOGS, AUTH_LOGS, MAIL_LOGS, HISTORY_LOGS, TERM_LOGS, EXIM4_LOGS, DB_LOGS, APACHE2_LOGS_ACCESS, APACHE2_LOGS_ERROR, NGINX_LOGS_ACCESS, NGINX_LOGS_ERROR]

def discord_logs(content):
    data = {
        "content": content
    }
    requests.post(WEBHOOK_URL, json=data)


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
                            discord_logs(f'❗️ **{log_type}** Ubuntu Server, date: {current_time} **ERROR LOG:** ```diff\n-{new_content}```') # For ERRORS
                        else:
                            discord_logs(f'📃 **{log_type}** Ubuntu Server, date: {current_time} **LOG:** ```css\n{new_content}```') # For LOGS
                        log_file_last_lines[log_file] = lines[-1]
        time.sleep(1)

if __name__ == '__main__': # Everything in loop in case of any error
    while True:
        try:
            main()
        except Exception as error:
            error_message = f'❗️ An error occurred ERROR: \n{str(error)}'
            print(f'An error occurred ERROR: \n{str(error)}')
            discord_logs(error_message)
            continue