import telegram
import json
import logging
import asyncio
from dateutil import parser
from flask import Flask, request
from flask_basicauth import BasicAuth
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.request import HTTPXRequest
from time import sleep

app = Flask(__name__)
app.secret_key = 'ehemsss2012221'
basic_auth = BasicAuth(app)

chatID = "-1002199003399"

app.config['BASIC_AUTH_FORCE'] = True
app.config['BASIC_AUTH_USERNAME'] = 'devops'
app.config['BASIC_AUTH_PASSWORD'] = 'J@t15Pass@!'

trequest = HTTPXRequest(connection_pool_size=1000)
bot = telegram.Bot(token="<token>", request=trequest)

async def send_message_async(chat_id, text, message_thread_id=None):
    attempt = 0
    while attempt < 3:  # Retry up to 3 times
        try:
            await bot.send_message(chat_id=chat_id, text=text, message_thread_id=message_thread_id)
            return
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (TimedOut, NetworkError):
            await asyncio.sleep(60)
        except Exception as error:
            app.logger.info("Error sending message: %s", error)
            return
        attempt += 1

@app.route('/alert', methods=['POST'])
def postAlertmanager():
    try:
        content = json.loads(request.get_data())
        for alert in content['alerts']:
            # Default values for instance and namespace
            instance = alert['labels'].get('instance', 'none')
            namespace = alert['labels'].get('namespace', 'unknown')

            message = "[Low] K8s Alert\n"
            message += f"Status: {alert['status']}\n"
            message += f"Instance: {instance}\n"
            message += f"Product: {namespace}\n"

            # Summary and description
            summary = alert['annotations'].get('summary', 'No summary provided.')
            description = alert['annotations'].get('description', 'No description provided.')
            if '/' in description:
                description_parts = description.split('/')
                if len(description_parts) > 1:
                    description = description_parts[1]  # Get everything after the namespace
            message += f"Summary: {summary}\n"
            message += f"Description: {description}\n"

            # Resolved or started timestamp
            if alert['status'] == "resolved":
                resolved_time = parser.parse(alert['endsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += f"Resolved: {resolved_time}\n"
            elif alert['status'] == "firing":
                started_time = parser.parse(alert['startsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += f"Started: {started_time}\n"

            asyncio.run(send_message_async(chat_id=chatID, text=message, message_thread_id=1269))
        return "Alert OK", 200
    except Exception as error:
        asyncio.run(send_message_async(chat_id=chatID, text=f"Error: {str(error)}"))
        app.logger.info("Error: %s", error)
        return "Alert fail", 200

@app.route('/alert-crit', methods=['POST'])
def postcritAlertmanager():
    try:
        content = json.loads(request.get_data())
        for alert in content['alerts']:
            # Default values for instance and namespace
            instance = alert['labels'].get('instance', 'none')
            namespace = alert['labels'].get('namespace', 'unknown')

            message = "[Critical] K8s Alert\n"
            message += f"Status: {alert['status']}\n"
            message += f"Instance: {instance}\n"
            message += f"Product: {namespace}\n"

            # Summary and description
            summary = alert['annotations'].get('summary', 'No summary provided.')
            description = alert['annotations'].get('description', 'No description provided.')

            # Remove namespace from the description (e.g., "default/nginx-crashloop" -> "nginx-crashloop")
            if '/' in description:
                description_parts = description.split('/')
                if len(description_parts) > 1:
                    description = description_parts[1]  # Get everything after the namespace
            message += f"Summary: {summary}\n"
            message += f"Description: {description}\n"

            # Resolved or started timestamp
            if alert['status'] == "resolved":
                resolved_time = parser.parse(alert['endsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += f"Resolved: {resolved_time}\n"
            elif alert['status'] == "firing":
                started_time = parser.parse(alert['startsAt']).strftime('%Y-%m-%d %H:%M:%S')
                message += f"Started: {started_time}\n"

            asyncio.run(send_message_async(chat_id=chatID, text=message, message_thread_id=4))
        return "Alert OK", 200
    except Exception as error:
        asyncio.run(send_message_async(chat_id=chatID, text=f"Error: {str(error)}"))
        app.logger.info("Error: %s", error)
        return "Alert fail", 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=9119)