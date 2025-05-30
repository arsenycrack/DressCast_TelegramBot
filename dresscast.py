import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Настройки логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API ключи
WEATHER_API_KEY = "ТОКЕН_СКРЫТ_ПО_ПРЕДОСТАВЛЕНИЮ_АВТОРА"
WEATHER_URL = "https://api.weatherapi.com/v1/current.json" 

# Инициализация бота с дефолтными настройками
bot = Bot(token="ТОКЕН_СКРЫТ_ПО_ПРЕДОСТАВЛЕНИЮ_АВТОРА",default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Функция получения совета по одежде
def get_outfit_suggestion(temp_c, precip_mm, wind_kph, condition_code):
    outfit = ""

    if temp_c < -10:
        outfit = "Утепленная куртка, термобелье, свитер, водонепроницаемые штаны, шапка, шарф, перчатки."
    elif temp_c < 0:
        outfit = "Теплая куртка, шапка, шарф, теплый свитер, брюки и зимняя обувь."
    elif temp_c < 10:
        outfit = "Кофта, легкая куртка, джинсы, удобная обувь. Возьми зонт."
    elif temp_c < 20:
        outfit = "Футболка или свитшот, джинсы или юбка, кроссовки."
    elif temp_c < 30:
        outfit = "Легкая футболка, шорты или юбка, сандалии, головной убор."
    else:
        outfit = "Майка, шорты, солнцезащитные очки, головной убор и много воды."

    if precip_mm > 1:
        outfit += " Не забудь взять зонт или дождевик!"

    if wind_kph > 30:
        outfit += " Защити лицо от ветра, выбери ветрозащитную одежду."

    if 1063 <= condition_code <= 1183:
        outfit += " Скорее всего будет дождь — подготовься!"

    if 1066 <= condition_code <= 1072:
        outfit += " Может быть снег — проверь температуру и оденься тепло."

    return outfit


# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я DressCast 🌤️\n"
        "Я помогу тебе выбрать одежду под погоду.\n"
        "Просто напиши мне название города!"
    )


# Обработчик сообщений с названием города
@dp.message(F.text)
async def handle_city(message: types.Message):
    city = message.text.strip()

    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return

    params = {
        'key': WEATHER_API_KEY,
        'q': city,
        'aqi': 'no'
    }

    try:
        response = requests.get(WEATHER_URL, params=params)
        response.raise_for_status()
        data = response.json()

        current = data['current']
        location = data['location']

        temp_c = current['temp_c']
        precip_mm = current['precip_mm']
        wind_kph = current['wind_kph']
        condition_code = current['condition']['code']

        outfit = get_outfit_suggestion(temp_c, precip_mm, wind_kph, condition_code)

        response_message = (
            f"🌤 Погода в {location['name']}, {location['country']}:\n"
            f"🌡 Температура: {temp_c}°C\n"
            f"🌧 Осадки: {precip_mm} мм\n"
            f"🌬 Ветер: {wind_kph} км/ч\n\n"
            f"👗 Совет по одежде:\n{outfit}"
        )

        await message.answer(response_message)

    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            await message.answer("Город не найден. Попробуйте ещё раз.")
        else:
            await message.answer("Ошибка при получении данных о погоде.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
