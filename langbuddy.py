import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from openai import OpenAI
from telegram import Audio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from google.cloud import texttospeech, speech_v1
from pydub import AudioSegment
from sqlalchemy import create_engine, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from datetime import datetime, timezone
from test_llamaindex import generate_response_with_tools

load_dotenv()

OpenAIclient = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
telegram_key=os.getenv("TELEGRAM_KEY")

DATABASE_URL = "postgresql://telegram_bot_user:your_password@localhost:5432/telegram_bot_db"

class Base(DeclarativeBase):
    pass

# Define the user context model
class UserContext(Base):
    __tablename__ = "user_context"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(index=True)
    context_data = mapped_column(Text)
    last_updated = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

# Initialize the database
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return engine

# Create a session
engine = init_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to store or update user context
def store_user_context(db, user_id, context):
    user_context = db.query(UserContext).filter(UserContext.user_id == user_id).first()
    
    if user_context:
        user_context.context_data = context
        user_context.last_updated = datetime.now(timezone.utc)
    else:
        user_context = UserContext(user_id=user_id, context_data=context)
        db.add(user_context)
    
    db.commit()

# Function to retrieve user context
def get_user_context(db, user_id):
    user_context = db.query(UserContext).filter(UserContext.user_id == user_id).first()
    
    if user_context:
        return user_context.context_data
    return None
    
async def handle_all(update: Update, context: CallbackContext):
    message = update.message
    user_id = str(update.message.from_user.id)
    db = next(get_db())  # Get a session from the generator

    if message.text:
        await update.message.reply_text("You sent a text message.")
    elif message.audio:
        update.message.reply_text("You sent an audio message.")
    elif message.document:
        await update.message.reply_text("You sent a document.")
    elif message.photo:
        await update.message.reply_text("You sent a photo.")
    elif message.video:
        await update.message.reply_text("You sent a video.")
    elif message.voice:
        voice_id = update.message.voice.file_id  
        await (await context.bot.getFile(voice_id)).download_to_drive(f"{voice_id}.ogg")
        transcript=convert_audio_to_text(f"{voice_id}.ogg")
        os.remove(f"{voice_id}.ogg")  # Clean up locally saved file
        if transcript != "":
            # Retrieve the existing context
            user_context = get_user_context(db, user_id)
            if user_context=="" or user_context==None:
                user_context=f"You are a friendly agent, \
                with a limited vocabulary of 100 words to \
                help me practice basic conversational english. \
                Please try to carry the conversation forward \
                whenever you can. Try to learn about me, help\
                me learn things about you. Your name is chatterbot,\
                you are fun and playful too."
            print("user_context")
            print(user_context)
            # response_text = await generate_response(transcript, user_context) 
            response_text = await generate_response_with_tools(transcript, user_context) 
            print("response text")
            print(response_text)
            # Update the context after the response
            store_user_context(db, user_id, response_text)
            await send_voice_clip(update, context, response_text)
    else:
        await update.message.reply_text("Unknown message type.")

def convert_text_to_speech(text, output_path='output.mp3'):
    # Initialize the TTS client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    input_text = texttospeech.SynthesisInput(text=text)

    # Select the language and gender of the voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",  # Change to the desired language code
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Configure the audio format (MP3)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

    # Save the synthesized audio to an MP3 file
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

    return output_path

def convert_mp3_to_ogg(mp3_path, ogg_output_path='output.ogg'):
    # Convert MP3 to OGG
    sound = AudioSegment.from_mp3(mp3_path)
    sound.export(ogg_output_path, format="ogg")
    return ogg_output_path

async def send_voice_clip(update: Update, context: CallbackContext, text_response: str):
    # Step 1: Convert text to speech and get the MP3 file path
    mp3_path = convert_text_to_speech(text_response)

    # Step 2: Convert the MP3 file to OGG format for Telegram
    # ogg_path = convert_mp3_to_ogg(mp3_path)

    # Step 3: Send the OGG file as a voice message
    with open(ogg_path, 'rb') as ogg_file:
        # await update.message.reply_voice(voice=ogg_file)
        await update.message.reply_voice(voice=mp3_path)

def get_context(user_input):

    return

async def generate_response(prompt, user_context, max_tokens=150):
    """Generate a response from the AI model based on the agent's personality."""

    response = OpenAIclient.chat.completions.create(
        model="gpt-3.5-turbo",  # Use the chat model
        messages=[
            {"role": "system", "content": user_context},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
        stop=None
    )
    response=response.to_dict()
    response_text = response['choices'][0]['message']['content']
    return response_text

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Language Learning Bot! Send me a voice message to start practicing.")

def convert_audio_to_text(audio_file):
    # Prepare audio for STT
    # Initialize Google STT client
    # Convert the .ogg audio to a format Google Cloud can accept (e.g., .wav)
    client = speech_v1.SpeechClient()
    
    sound = AudioSegment.from_file(audio_file)
    sound = sound.set_sample_width(2)  # 2 bytes = 16 bits per sample (required)

    converted_audio_path = 'converted_audio.wav'
    sound.export(converted_audio_path, format="wav")

    # Read the converted audio file
    with open(converted_audio_path, "rb") as audio:
        content = audio.read()

    # Set up the recognition audio and configuration
    recognition_audio = speech_v1.RecognitionAudio(content=content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,  # Match the audio sample rate
        language_code="en-US",  # Change this to the desired language
    )

    # Send the audio to Google Cloud Speech-to-Text for transcription
    response = client.recognize(config=config, audio=recognition_audio)

    # Process and return the transcription result
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript
    print("transcription")
    print(transcription)
    return transcription


def main():    
    app = ApplicationBuilder().token(telegram_key).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_all))
    app.run_polling()

if __name__ == '__main__':
    main()