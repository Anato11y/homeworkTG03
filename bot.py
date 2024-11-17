import os
import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего Telegram-бота
TELEGRAM_TOKEN = "7741555008:AAFhz3mMwk1lugqF6tsQD0RHC5rxxa6BG88"

# Инициализация бота, диспетчера и хранилища памяти
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создание базы данных
if not os.path.exists("school_data.db"):
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Состояния для пользователя
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_grade = State()

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer("Привет! Давайте начнем. Напишите ваше имя.")
    await state.set_state(UserStates.waiting_for_name)

# Обработчик имени
@dp.message(UserStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Спасибо! Теперь введите ваш возраст.")
    await state.set_state(UserStates.waiting_for_age)

# Обработчик возраста
@dp.message(UserStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст числом.")
        return

    await state.update_data(age=int(message.text))
    await message.answer("Отлично! Напишите, в каком классе вы учитесь (например, 10А).")
    await state.set_state(UserStates.waiting_for_grade)

# Обработчик класса
@dp.message(UserStates.waiting_for_grade)
async def process_grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    age = user_data.get("age")
    grade = message.text

    # Сохранение данных в базу
    save_to_db(name, age, grade)

    await message.answer(f"Ваши данные сохранены:\nИмя: {name}\nВозраст: {age}\nКласс: {grade}")
    await state.clear()  # Завершаем состояние

# Функция для сохранения данных в базу
def save_to_db(name, age, grade):
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
    conn.commit()
    conn.close()

# Основная функция запуска бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
