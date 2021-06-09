import os
import asyncio
import logging
from aiogram import Bot

from database.AssetDao import AssetDao
from properties import DB_NAME, BOT_TOKEN, MY_ID, BASE_FILE_PATH

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

bot = Bot(token=BOT_TOKEN)
asset_dao = AssetDao(DB_NAME)
asset_dao.clear()


async def uploadMediaFiles(folder, method, file_attr):
    folder_path = os.path.join(BASE_FILE_PATH, folder)
    for filename in os.listdir(folder_path):
        if filename.startswith('.'):
            continue

        logging.info(f'Started processing {filename}')
        with open(os.path.join(folder_path, filename), 'rb') as file:
            msg = await method(MY_ID, file, disable_notification=True)
            if file_attr == 'photo':
                file_id = msg.photo[-1].file_id
            else:
                file_id = getattr(msg, file_attr).file_id
            try:
                asset_dao.add_asset(file_id=file_id, filename=filename)
            except Exception as e:
                logging.error(
                    'Couldn\'t upload {}. Error is {}'.format(filename, e))
            else:
                logging.info(
                    f'Successfully uploaded and saved to DB file {filename} with id {file_id}')

loop = asyncio.get_event_loop()

tasks = [
    loop.create_task(uploadMediaFiles('', bot.send_photo, 'photo')),
    # loop.create_task(uploadMediaFiles('pics', bot.send_photo, 'photo')),
    # loop.create_task(uploadMediaFiles('videos', bot.send_video, 'video')),
    # loop.create_task(uploadMediaFiles('videoNotes', bot.send_video_note, 'video_note')),
    # loop.create_task(uploadMediaFiles('files', bot.send_document, 'document')),
    # loop.create_task(uploadMediaFiles('ogg', bot.send_voice, 'voice')),
]

wait_tasks = asyncio.wait(tasks)

loop.run_until_complete(wait_tasks)
if not loop.is_closed():
    loop.close()
asset_dao.close()
