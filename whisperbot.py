

from telegram.ext import Updater, MessageHandler, Filters, Dispatcher, CallbackContext
from telegram import Update
import requests
import os
import logging
import openai
from threading import Lock
import dotenv

dotenv.load_dotenv()

audio_lock = Lock()
video_note_lock = Lock()
client = openai.Client()

def summary(input: str) -> str:
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
            {'role': 'system', 'content': 'The assistant returns a title out of the message. The format is just the title.'},
            {'role': 'user', 'content': input},
        ]
    )

    result = response.choices[0].message.content
    assert type(result) is str
    return result

def openai_whisper_api(local_filepath: str):
    file = open(local_filepath, "rb")
    transcription = client.audio.transcriptions.create(file=file, model="whisper-1")
    logging.debug(transcription)
    return transcription.text

def handle_audio(update: Update, context: CallbackContext):
    # Download audio file from the message
    file = context.bot.getFile(update.message.voice.file_id)
    file.download('audio.ogg')

    whisper_result = openai_whisper_api(local_filepath='audio.ogg')

    # Send the transcription
    update.message.reply_text(whisper_result)

# Function to handle errors occurred in the dispatcher
def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a message to notify the user."""
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

def handle_video_note(update: Update, context: CallbackContext):
    raise Exception('Deprecated')
    from moviepy.editor import VideoFileClip
    file = context.bot.getFile(update.message.video_note.file_id)
    video_file_path = 'video.mp4'
    file.download(video_file_path)

    # Extract audio from the video note
    with VideoFileClip(video_file_path) as video:
        audio_file_path = 'audio.mp3'
        audio = video.audio
        assert audio is not None
        audio.write_audiofile(audio_file_path, logger=None)

    result = openai_whisper_api(local_filepath='audio.mp3')

    summary_result = summary(result)

    # Send the transcription
    update.message.reply_text(summary_result)

