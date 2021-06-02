import asyncio
import random

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import config
import logging

import strings
from AssetDao import AssetDao
from ExcelFileDao import ExcelFileDao
from UsersDao import UsersDao

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

users_dao = UsersDao("lohotron.db")
asset_dao = AssetDao("lohotron.db")
excel_dao = ExcelFileDao("data.xlsx")


class Form(StatesGroup):
    start = State()
    name = State()
    age = State()
    city = State()
    exit_callback = State()


@dp.message_handler(commands="start", state="*")
async def start_form(message: types.Message):
    if not users_dao.users_exist(message.from_user.id):
        users_dao.add_user(message.from_user.id)
    await message.answer(strings.name, parse_mode="MarkdownV2")
    await Form.name.set()


@dp.message_handler(state=Form.name)
async def name_picked(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await Form.next()
    await message.answer(strings.age.format(age=message.text), parse_mode="MarkdownV2")


@dp.message_handler(state=Form.age)
async def age_picked(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(strings.age_not_int, parse_mode="MarkdownV2")
        return
    await state.update_data(age=int(message.text))
    await Form.next()
    await message.answer(strings.city, parse_mode="MarkdownV2")


def get_keyboard_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(strings.girl, strings.man)  # Имена кнопок
    return markup


@dp.message_handler(state=Form.city)
async def exit_messaging(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(strings.end_conversation.format(name=user_data['name'], age=user_data['age'], city=message.text), parse_mode="MarkdownV2")
    await asyncio.sleep(random.randint(2, 4))
    await message.answer(strings.whom_search, reply_markup=get_keyboard_markup(), parse_mode="MarkdownV2")
    await state.finish()


@dp.message_handler(content_types=["text"])
async def keyboard_command(message: types.Message):
    # bot.register_next_step_handler(message, callback=process_step)
    if message.text == strings.girl:
        await show_next_girl(message.from_user.id)
    elif message.text == strings.man:
        await show_next_man(message.from_user.id)
    else:
        return


async def show_next_girl(user_id: int):
    user_photo_pos = users_dao.get_user(user_id)[3]
    users_dao.update_user(user_id, (user_photo_pos + 1) % excel_dao.get_rows_number())
    await show_post(user_id, user_photo_pos)


async def show_next_man(user_id: int):
    await bot.send_message(user_id, text=strings.man_search_text, parse_mode="MarkdownV2")


async def show_post(user_id: int, post_number: int):
    entity = excel_dao.get_row_entity(post_number)
    photos = [asset_dao.get_photo_id_by_name(photo_name) for photo_name in entity.photos]
    if len(photos) == 1:
        await bot.send_photo(user_id, photos[0])
    else:
        await bot.send_media_group(user_id, media=[InputMediaPhoto(media=image) for image in photos])
    await bot.send_message(user_id, entity.text, reply_markup=get_post_keyboard(entity.link), parse_mode="MarkdownV2")


def get_post_keyboard(url):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text=strings.link_btn_title, callback_data='link', url=url)
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text=strings.next_grl, callback_data='next')
    keyboard.add(key_no)
    return keyboard


@dp.callback_query_handler()
async def callback_worker(call: types.CallbackQuery):
    if call.data == "next":  # call.data это callback_data, которую мы указали при объявлении кнопки
        await bot.answer_callback_query(call.id)
        await show_next_girl(call.from_user.id)
    elif call.data == "link":
        await bot.answer_callback_query(call.id)


async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(config.WEBHOOK_URL, drop_pending_updates=True)

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=config.WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=config.WEBAPP_HOST,
        port=config.WEBAPP_PORT,
    )
    # executor.start_polling(dp, skip_updates=True)
