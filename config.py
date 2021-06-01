# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv, find_dotenv

# Loading .env variables
load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise Exception("Please setup the .env variable TELEGRAM_TOKEN.")

MY_ID = "467277928"

BASE_FILE_PATH = "./photos"

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
# PORT = int(os.environ.get('PORT', '8443'))

# WEBHOOK_URL=f"https://{HEROKU_APP_NAME}.herokuapp.com/{BOT_TOKEN}"

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', '8443'))
