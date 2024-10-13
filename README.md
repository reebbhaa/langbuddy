# Language Buddy Bot

Language Buddy Bot is a Telegram bot designed to help users practice conversational English through voice messages. The bot utilizes OpenAI's GPT-3.5-turbo model for generating responses and Google Cloud's Speech-to-Text and Text-to-Speech services for audio processing.

## Features

- **Voice Message Support**: Users can send voice messages to practice speaking.
- **Contextual Conversations**: The bot maintains user context to generate personalized responses.
- **Text-to-Speech**: Converts the bot's text responses into voice messages for a more interactive experience.
- **Speech-to-Text**: Converts user voice messages into text for processing.

## Technologies Used

- **Python**: The main programming language for the bot.
- **Telegram Bot API**: For handling messages and interactions.
- **OpenAI**: For generating conversational responses.
- **Google Cloud**: For speech recognition and synthesis.
- **PostgreSQL**: For storing user context data.

## Requirements

Ensure you have the following installed:

- Python 3.12 or higher
- PostgreSQL

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:

   ```bash
   pip install -r requirements.txt

4. Create a .env file in the root directory with the following variables:

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   TELEGRAM_KEY=<your_telegram_bot_token>

5. Set up the PostgreSQL database. You can use the provided docker-compose.yaml to set up PostgreSQL:

   ```bash
   docker-compose up -d

6. Usage:

   ```bash
   python langbuddy.py

Once the bot is running, you can send a voice message to interact with it. The bot will respond with a voice message in return.
