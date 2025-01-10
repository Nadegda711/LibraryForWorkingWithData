from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

#--------------------------------------------------------------
products = get_all_products()
#--------------------------------------------------------------
kl = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формула расчёта', callback_data='formulas')
kl.add(button)
kl.add(button2)


kb = InlineKeyboardMarkup(resize_keyboard=True)
button_ = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
button_2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
button_3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
button_4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
kb.insert(button_)
kb.insert(button_2)
kb.insert(button_3)
kb.insert(button_4)


kp = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="Информация"),
            KeyboardButton(text="Рассчитать"),
            KeyboardButton(text="Регистрация")
        ],
        [KeyboardButton(text="Купить")]
    ], resize_keyboard = True
)
#---------------------------------------------------------

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

#------------------------------------------------------
@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет, я бот помогающий твоему здоровью!', reply_markup=kp)
#
@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Привет, я бот помогающий твоему здоровью!')


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kl)

@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.reply("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    with open('files/product1.jpg', 'rb') as img:
        await message.answer_photo(img)
        await message.answer(f'Название: {products[0][1]} | Описание: {products[0][2]} | Цена: {products[0][3]} руб.')
    with open('files/product2.jpg', 'rb') as img:
        await message.answer_photo(img)
        await message.answer(f'Название: {products[1][1]} | Описание: {products[1][2]} | Цена: {products[1][3]} руб.')
    with open('files/product3.jpg', 'rb') as img:
        await message.answer_photo(img)
        await message.answer(f'Название: {products[2][1]} | Описание: {products[2][2]} | Цена: {products[2][3]} руб.')
    with open('files/product4.jpg', 'rb') as img:
        await message.answer_photo(img)
        await message.answer(f'Название: {products[3][1]} | Описание: {products[3][2]} | Цена: {products[3][3]} руб.')
    await message.answer('Выберите продукт для покупки:', reply_markup=kb)


#--------------------------------------------------------------------------------------

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
   await state.update_data(growth=int(message.text))
   await message.answer('Введите свой вес:')
   await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f"Ваша дневная норма калорий: {calories} ккал")
    await state.finish()



@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    connection = sqlite3.connect('products.db')
    cursor = connection.cursor()
    user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
    connection.close()

    if user:
        await message.answer("Пользователь существует, введите другое имя:")
    else:
        await state.update_data(username=username)  # Сохранение имени пользователя в состоянии
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()  # Установка состояния для email

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    await state.update_data(email=email)  # Сохранение email в состоянии
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()  # Установка состояния для возраста

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    age = message.text

    # Получение данных из состояния
    user_data = await state.get_data()
    username = user_data.get('username')
    email = user_data.get('email')

    # Добавление пользователя в базу данных
    add_user(username, email, age)

    await message.answer("Регистрация завершена! Добро пожаловать, {}!".format(username))
    await state.finish()  # Завершение состояния


#----------------------------------------------------------
@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()
#-------------------------------------------------------------------------


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

