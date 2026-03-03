import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import yt_dlp

# Вставь сюда свой токен от @BotFather
TOKEN = "8761890419:AAF2wjwxbQF2Eo9VjZ6M9zr4OqXKhVQC8nw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройки ограничений (чтобы сервер не упал)
MAX_SIZE = 45 * 1024 * 1024  # 45 МБ (безопасный предел для Telegram)


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот готов! Пришли ссылку на TikTok, Shorts или YouTube.\n⚠️ Лимит: до 45 МБ.")


@dp.message(F.text.contains("http"))
async def download_video(message: types.Message):
    url = message.text
    status_msg = await message.answer("⏳ Проверяю видео...")

    # Настройки умного скачивания
    ydl_opts = {
        'format': 'best[ext=mp4][filesize<50M]/worst[ext=mp4]',  # Ищем лучшее до 50МБ, иначе берем худшее
        'outtmpl': f'video_{message.chat.id}.mp4',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Проверка на размер перед скачиванием
            filesize = info.get('filesize') or info.get('filesize_approx')
            if filesize and filesize > MAX_SIZE:
                return await status_msg.edit_text("❌ Видео слишком тяжелое! Попробуй ролик поменьше.")

            await status_msg.edit_text("📥 Скачиваю... Пожалуйста, подожди.")
            ydl.download([url])

        # Отправка
        video_file = types.FSInputFile(f'video_{message.chat.id}.mp4')
        await bot.send_video(message.chat.id, video=video_file, caption="Ваше видео готово! ✨")

    except Exception as e:
        await status_msg.edit_text(f"⚠️ Ошибка: Возможно, это видео защищено или слишком длинное.")

    finally:
        # Всегда удаляем файл, чтобы не забить память сервера
        file_path = f'video_{message.chat.id}.mp4'
        if os.path.exists(file_path):
            os.remove(file_path)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
