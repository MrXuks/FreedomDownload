import os
import pytube
import telegram
import telegram.ext
from pytube import YouTube
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import ChatAction
from telegram.ext.dispatcher.filters import Filters

# функция-обработчик для команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет, это FreedomDownload_bot и я умею скачивать видео по ссылке из YouTube прямо сюда. Отправь мне ссылку на любое видео YouTube и ты увидишь меня в действии. Если возникли проблемы с ботом, то введите команду /help.")


# функция-обработчик для команды /help
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Если у вас возникли проблемы с ботом или есть идеи как улучшить его, пишите в телеграмм @MrXuks. Всегда рад помочь!")


# функция-обработчик для текстовых сообщений
def handle_text(update, context):
    text = update.message.text
    if 'youtube.com/watch?v=' not in text:
        # если сообщение не является ссылкой на видео в YouTube
        if 'youtube.com/playlist?list=' in text:
            # если ссылка на плейлист в YouTube
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Ссылка которую вы отправили, является ссылкой на плейлист. Пожалуйста, отправьте корректную ссылку на видео в YouTube.")
        else:
            # если сообщение не является ссылкой на видео или плейлист в YouTube
            context.bot.send_message(chat_id=update.effective_chat.id, text="Неверная ссылка")
    else:
        try:
            # загрузка и отправка видео и аудио
            file_name_video, file_name_audio = download_video_and_audio(text)
            context.bot.send_video(chat_id=update.effective_chat.id, video=open(file_name_video, 'rb'),
                                   supports_streaming=True)
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(file_name_audio, 'rb'))
            # вывод сообщения об успешной загрузке
            context.bot.send_message(chat_id=update.effective_chat.id, text="Видео успешно загружено")
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
        finally:
            # удаление загруженных файлов
            os.remove(file_name_video)
            os.remove(file_name_audio)


# функция для загрузки видео и аудио
def download_video_and_audio(url):
    # загрузка видео с YouTube
    video = YouTube(url)
    # сортировка видеодорожек по размеру файла
    video_streams = video.streams.filter(progressive=True).order_by('filesize').desc()
    for stream in video_streams:
        # проверка размера файла
        if stream.filesize <= 500000000:
            # загрузка видео
            file_name_video = f"{video.title}.mp4"
            stream.download(filename=file_name_video)
            # загрузка аудио
            file_name_audio = f"{video.title}.mp3"
            video.streams.get_audio_only().download(filename=file_name_audio)
            return file_name_video, file_name_audio
    # если размер видео превышает 500 МБ, загружаем видеодорожку с наименьшим размером
    file_name_video = f"{video.title}.mp4"
    video_streams.last().download(filename=file_name_video)
    # загрузка аудио
    file_name_audio = f"{video.title}.mp3"
    video.streams.get_audio_only().download(filename=file_name_audio)
    return file_name_video, file_name_audio


# функция main
def main():
    # Инициализируем бота и создаем обработчиков команд и текстовых сообщений
    bot = telegram.Bot(token='TOKEN')
    job_queue = JobQueue()
    updater = Updater(bot=bot, use_context=True, job_queue=job_queue, workers=4)

    # Добавляем обработчики команд и текстовых сообщений
    start_handler = CommandHandler('start', start_callback)
    help_handler = CommandHandler('help', help_callback)
    message_handler = MessageHandler(Filters.text & ~Filters.command, message_callback)
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(message_handler)

    # Запускаем бота и начинаем обработку сообщений
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
