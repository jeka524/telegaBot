import asyncio
import random

import emoji
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import config
import logging

from AssetDao import AssetDao
from ExcelFileDao import ExcelFileDao
from UsersDao import UsersDao

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

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
    await message.answer("Як вас звати?")
    await Form.name.set()


@dp.message_handler(state=Form.name)
async def name_picked(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await Form.next()
    await message.answer(f"Здраствуйте {message.text}! Сколько вам лет?")


@dp.message_handler(state=Form.age)
async def age_picked(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введить ваш возраст (цифри)")
        return
    await state.update_data(age=int(message.text))
    await Form.next()
    await message.answer("Окей. Которий город?")


def get_keyboard_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Девушку', 'Парня')  # Имена кнопок
    return markup


@dp.message_handler(state=Form.city)
async def exit_messaging(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(f"Отлично. {user_data['name']} подождите немного, сейчас я настрою для вас подбор, исходя из "
                         f"вашого возраста ({user_data['age']}) и города ({message.text})")
    await asyncio.sleep(random.randint(2, 4))
    await message.answer("Отже, кого вы ищете?", reply_markup=get_keyboard_markup())
    await state.finish()


@dp.message_handler(content_types=["text"])
async def keyboard_command(message: types.Message):
    # bot.register_next_step_handler(message, callback=process_step)
    if message.text == "Девушку":
        await startShowGirl(message)
    elif message.text == "Парня":
        await show_next_man(message.from_user.id)
    else:
        return


async def startShowGirl(message: types.Message):
    await message.answer(text="Ми тілкьи по парням, спробуй того красавчика")


async def show_next_man(user_id: int):
    user_photo_pos = users_dao.get_user(user_id)[3]
    users_dao.update_user(user_id, (user_photo_pos + 1) % excel_dao.get_rows_number())
    await show_post(user_id, user_photo_pos)


async def show_post(user_id: int, post_number: int):
    entity = excel_dao.get_row_entity(post_number)
    photos = [asset_dao.get_photo_id_by_name(photo_name) for photo_name in entity.photos]
    if len(photos) == 1:
        await bot.send_photo(user_id, photos[0])
    else:
        await bot.send_media_group(user_id, media=[InputMediaPhoto(media=image) for image in photos])
    await bot.send_message(user_id, entity.text, reply_markup=get_post_keyboard(entity.link))


def get_post_keyboard(url):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text=emoji.emojize('Написать :heart:', use_aliases=True), callback_data='link', url=url)
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Следуящая ->', callback_data='next')
    keyboard.add(key_no)
    return keyboard


@dp.callback_query_handler()
async def callback_worker(call: types.CallbackQuery):
    if call.data == "next":  # call.data это callback_data, которую мы указали при объявлении кнопки
        await bot.answer_callback_query(call.id)
        await show_next_man(call.from_user.id)
    elif call.data == "link":
        await bot.answer_callback_query(call.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
