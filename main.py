import telebot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import random
import subprocess
import tempfile
try:
    subprocess.run(["ffmpeg", "-version"], check=True)
    print("ffmpeg доступний")
except FileNotFoundError:
    print("ffmpeg не знайдено")


bot = telebot.TeleBot("8042129376:AAFQ7oSmFfep7UwrP1xwm4XpyzUF90TmTg8")

print("Started")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Hello, send me your sound or video 🎬.")

@bot.message_handler(content_types="audio")
def audio_to_voice(msg):
    bot.send_message(msg.chat.id, "Starting...⏳")

    try:
        file_info = bot.get_file(msg.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
    except ApiTelegramException as e:
        if "file is too big" in str(e).lower():
            bot.send_message(msg.chat.id, "File is too big(file must be less than 20mb)")
            return

    input_path = "input.mp3"
    output_path = "output.ogg"

    with open(input_path, "wb") as f:
        f.write(downloaded_file)

    if os.path.getsize(input_path) < 1000:
        bot.send_message(msg.chat.id, "Audio file is too small or invalid.")
        return 
    
    bot.send_message(msg.chat.id, "Almost done....⌛️")

    subprocess.run([
        "ffmpeg", "-y", "-i", input_path, "-map",
        "0:a", "-f", "ogg", "-acodec", "libopus",
        "-ar", "48000", "-ac", "1", output_path
    ])

    with open(output_path, 'rb') as f:
        bot.send_voice(msg.chat.id, f)

    os.remove(input_path)
    os.remove(output_path)

    bot.send_message(msg.chat.id, "Done✅")
    print("Audio")

@bot.message_handler(content_types=['video'])
def video_to_circle(msg):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    bot.send_message(msg.chat.id, "Starting...⏳")

    try:
        file_info = bot.get_file(msg.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
    except ApiTelegramException as e:
        if "file is too big" in str(e).lower():
            bot.send_message(msg.chat.id, "File is too big(file must be shorter that 1 minute and less than 20mb)")
            return

    
    bot.send_message(msg.chat.id, "Almost done....⌛️")

    with tempfile.NamedTemporaryFile(delete=False) as input_temp:
        input_path = input_temp.name
        input_temp.write(downloaded_file)

    output_path = input_path + "_circle.mp4"
    
    result = subprocess.run([
         'ffmpeg',
        '-y',
        '-i', input_path,
        '-t', "60",
        '-vf', 'scale=512:512:force_original_aspect_ratio=increase,crop=512:512',
        '-c:v', 'libx264',
        '-profile:v', 'baseline',
        '-level', '3.1',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    if result.returncode != 0:
        bot.send_message(msg.chat.id, "Error processing video. Probablyy an unupported or broken format.")
        os.remove(input_path)
        return

    with open(output_path, "rb") as f:
        bot.send_video_note(msg.chat.id, f)

    os.remove(input_path)
    os.remove(output_path)

    bot.send_message(msg.chat.id, "Done✅")
    print("Video")

bot.infinity_polling()