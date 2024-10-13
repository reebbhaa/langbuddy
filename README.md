Language Buddy Bot
A Telegram bot designed to help users practice conversational English through voice interactions. The bot uses Google Cloud Speech-to-Text for audio transcription and OpenAI's GPT model to generate responses based on the user's input and a personalized context.

Features
Voice Message Interaction: Users can send voice messages, which the bot transcribes to text.
Contextual Responses: The bot maintains a context for each user to provide more relevant and personalized responses.
Text-to-Speech Responses: The bot responds with voice messages synthesized from text using Google Cloud Text-to-Speech.
Database Storage: User contexts are stored in a PostgreSQL database, allowing the bot to remember user-specific information across sessions.
Requirements
Python 3.8+
Docker (for database setup)
Telegram Bot Token
OpenAI API Key
Google Cloud credentials for Speech-to-Text and Text-to-Speech APIs
Python packages listed in requirements.txt
Setup
Clone the Repository:

bash
Copy code
git clone https://langbuddy.git
cd langbuddy
Create a .env File:

Create a file named .env in the project directory and add your Telegram Bot Token and OpenAI API Key:

makefile
Copy code
TELEGRAM_KEY=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
Set Up PostgreSQL Database:

You can use Docker to set up a PostgreSQL database easily:

bash
Copy code
docker-compose up -d
This will create a PostgreSQL database with the necessary tables.

Install Dependencies:

Install the required Python packages:

bash
Copy code
pip install -r requirements.txt
Run the Bot:

Execute the following command to start the bot:

bash
Copy code
python langbuddy.py
Usage
Send a /start command to the bot to initiate the conversation.
After that, you can send voice messages, and the bot will respond accordingly.
Directory Structure
bash
Copy code
langbuddy/
│
├── langbuddy.py             # Main bot script
├── docker-compose.yaml       # Docker configuration for PostgreSQL
└── requirements.txt          # Python package dependencies
Notes
Ensure you have enabled the Google Cloud APIs for Speech-to-Text and Text-to-Speech, and have set up your credentials properly.
Make sure your PostgreSQL connection details are correctly set in DATABASE_URL in the langbuddy.py script.