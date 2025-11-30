# Standard libraries imports
from asyncio import run as asyncio_run
from asyncio import sleep as asyncio_sleep
from os import getenv
from secrets import choice as secret_choice

# Third-party libraries imports
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import Redis, RedisStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# Moduls imports
from db import add_user, get_data, get_statistics, get_user, init_db, update_desire, update_name
from schema import Statistics, User
from utils import create_name

ADMIN_ID: int = int(getenv("ADMIN_ID", "0"))
BOT_TOKEN: str = getenv("BOT_TOKEN", "")

redis: Redis = Redis(host="redis", port=6379)
dp: Dispatcher = Dispatcher(storage=RedisStorage(redis))

class UsersStates(StatesGroup):
    new = State()
    name = State()
    change_name = State()
    change_desire = State()
    done = State()
    admin_roll = State()

change_name: InlineKeyboardButton = InlineKeyboardButton(text="Изменить имя", callback_data="change_name")
change_desire: InlineKeyboardButton = InlineKeyboardButton(text="Изменить пожелание", callback_data="change_desire")
info: InlineKeyboardButton = InlineKeyboardButton(text="Посмотреть свои данные", callback_data="info")
admin_info: InlineKeyboardButton = InlineKeyboardButton(text="Статистика", callback_data="admin_info")
admin_roll: InlineKeyboardButton = InlineKeyboardButton(text="Розыгрыш", callback_data="admin_roll")
yes: InlineKeyboardButton = InlineKeyboardButton(text="Да", callback_data="yes")
no: InlineKeyboardButton = InlineKeyboardButton(text="Нет", callback_data="no")

keyboard_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [info],
        [change_name],
        [change_desire],
    ]
)
keyboard_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [info],
        [change_name],
        [change_desire],
        [admin_info],
        [admin_roll],
    ]
)
keyboard_roll = InlineKeyboardMarkup(
    inline_keyboard=[
        [yes],
        [no],
    ]
)

bot: Bot = Bot(token=BOT_TOKEN)

async def alert_admin(query: CallbackQuery, func: str) -> None:
    tg_name: str = create_name(query.from_user.first_name, query.from_user.last_name, query.from_user.username)
    text: str = f"Пользователь не найден в базе данных! ID: {query.from_user.id} name: {tg_name} func: {func}"
    await bot.send_message(chat_id=ADMIN_ID, text=text)

async def send_mails() -> bool:
    users: list[User] = get_data()
    if len(users) < 2:
        await bot.send_message(chat_id=ADMIN_ID, text="Зарегистрировано менее 2 пользователей, розыгрыш невозможен!")
        return False

    recipients: set[int] = {user.id for user in users}
    pairs: dict[int, int | None] = {user.id: None for user in users}

    for user_id in pairs:
        possible_recipients: set[int] = recipients - {user_id}
        recipient_id: int = secret_choice(list(possible_recipients))
        pairs[user_id] = recipient_id
        recipients.remove(recipient_id)

    for giver_id, recipient_id in pairs.items():
        recipient: User = next(user for user in users if user.id == recipient_id)
        text: str = f"Ты даришь подарок {recipient.name} ({recipient.tg_name}), вот его пожелание: {recipient.desire}"
        await bot.send_message(chat_id=giver_id, text=text)
        await asyncio_sleep(1)

    return True

def get_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get appropriate keyboard for user (admin or regular user)."""
    return keyboard_admin if user_id == ADMIN_ID else keyboard_user

@dp.message(UsersStates.new)
async def process_name(message: types.Message, state: FSMContext) -> None:
    update_name(message.from_user.id, message.text)
    await state.set_state(UsersStates.name)
    await message.answer("Теперь напиши, что бы ты хотел получить в подарок. Чем подробнее, тем лучше!")

@dp.message(UsersStates.name)
async def process_desire(message: types.Message, state: FSMContext) -> None:
    update_desire(message.from_user.id, message.text)
    await state.set_state(UsersStates.done)
    response_keyboard: InlineKeyboardMarkup = get_keyboard(message.from_user.id)
    await message.answer("Спасибо! Твоя информация сохранена. Жди розыгрыша!", reply_markup=response_keyboard)

@dp.message(UsersStates.done)
async def process_done(message: types.Message) -> None:
    response_keyboard: InlineKeyboardMarkup = get_keyboard(message.from_user.id)
    await message.answer("Yo!", reply_markup=response_keyboard)

@dp.message(UsersStates.change_name)
async def process_change_name(message: types.Message, state: FSMContext) -> None:
    update_name(message.from_user.id, message.text)
    await state.set_state(UsersStates.done)
    response_keyboard: InlineKeyboardMarkup = get_keyboard(message.from_user.id)
    await message.answer("Спасибо! Твоя информация сохранена. Жди розыгрыша!", reply_markup=response_keyboard)

@dp.message(UsersStates.change_desire)
async def process_change_desire(message: types.Message, state: FSMContext) -> None:
    update_desire(message.from_user.id, message.text)
    await state.set_state(UsersStates.done)
    response_keyboard: InlineKeyboardMarkup = get_keyboard(message.from_user.id)
    await message.answer("Спасибо! Твоя информация сохранена. Жди розыгрыша!", reply_markup=response_keyboard)

@dp.message(UsersStates.admin_roll)
async def process_admin_roll(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UsersStates.done)
    await message.answer("Санта пока подождет", reply_markup=keyboard_admin)

@dp.callback_query(F.data == "info")
async def handle_info(query: CallbackQuery, state: FSMContext) -> None:
    user: User | None = get_user(query.from_user.id)
    response_keyboard: InlineKeyboardMarkup = get_keyboard(query.from_user.id)
    if user is None:
        await alert_admin(query, "handle_info")
        response: str = "Произошла ошибка, уже разбираемся!"
    else:
        response: str = (f"Твои данные:\n Имя: {user.name}\n Пожелание: {user.desire}")
    await query.message.answer(response, reply_markup=response_keyboard)

@dp.callback_query(F.data == "change_name")
async def handle_change_name(query: CallbackQuery, state: FSMContext) -> None:
    response_keyboard: InlineKeyboardMarkup = get_keyboard(query.from_user.id)
    mails_sent = await redis.get("roll_done")
    mails_sent = mails_sent.decode() if mails_sent is not None else None
    if mails_sent == "yes":
        await query.message.answer(
            "Розыгрыш уже был проведен, изменение имени невозможно!", reply_markup=response_keyboard
        )
        return
    user: User | None = get_user(query.from_user.id)
    if user is None:
        await alert_admin(query, "handle_change_name")
        await query.message.answer("Произошла ошибка, уже разбираемся!", reply_markup=response_keyboard)
    else:
        await state.set_state(UsersStates.change_name)
        await query.message.answer("Напиши свое имя, чтобы другие знали кому дарить подарок")

@dp.callback_query(F.data == "change_desire")
async def handle_change_desire(query: CallbackQuery, state: FSMContext) -> None:
    response_keyboard: InlineKeyboardMarkup = get_keyboard(query.from_user.id)
    mails_sent = await redis.get("roll_done")
    mails_sent = mails_sent.decode() if mails_sent is not None else None
    if mails_sent == "yes":
        await query.message.answer(
            "Розыгрыш уже был проведен, изменение пожелания невозможно!", reply_markup=response_keyboard
        )
        return
    user: User | None = get_user(query.from_user.id)
    if user is None:
        await alert_admin(query, "handle_change_desire")
        await query.message.answer("Произошла ошибка, уже разбираемся!", reply_markup=response_keyboard)
    else:
        await state.set_state(UsersStates.change_desire)
        await query.message.answer("Напиши, что бы ты хотел получить в подарок. Чем подробнее, тем лучше!")

@dp.callback_query(F.data == "admin_info")
async def handle_admin_info(query: CallbackQuery) -> None:
    statistics: Statistics = get_statistics()
    await query.message.answer(str(statistics), reply_markup=keyboard_admin)

@dp.callback_query(F.data == "admin_roll")
async def handle_admin_roll(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UsersStates.admin_roll)
    await query.message.answer("Запустить тайного санту?", reply_markup=keyboard_roll)

@dp.callback_query(F.data == "no")
async def handle_no(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UsersStates.done)
    await query.message.answer("Санта пока подождет", reply_markup=keyboard_admin)

@dp.callback_query(F.data == "yes")
async def handle_yes(query: CallbackQuery, state: FSMContext) -> None:
    mails_sent = await redis.get("roll_done")
    mails_sent = mails_sent.decode() if mails_sent is not None else None
    await state.set_state(UsersStates.done)
    if mails_sent == "yes":
        await query.message.answer("Розыгрыш уже был проведен!", reply_markup=keyboard_admin)
        return
    success = await send_mails()
    if success:
        await redis.set("roll_done", "yes")
        await query.message.answer("Письма отправлены!", reply_markup=keyboard_admin)
    else:
        await query.message.answer("Произошла ошибка при отправке!!!", reply_markup=keyboard_admin)

@dp.message()
async def first_contact(message: types.Message, state: FSMContext) -> None:
    tg_name = create_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    add_user(message.from_user.id, tg_name)
    await state.set_state(UsersStates.new)
    await message.answer("Напиши свое имя, чтобы другие знали кому дарить подарок")

async def main() -> None:
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio_run(main())
