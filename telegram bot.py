import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store session states and messages for each chat
session_data = {}

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Welcome! Use /start_session to begin logging messages for this group.')

async def start_session(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id

    # Initialize session for the chat if not already started
    if chat_id not in session_data:
        session_data[chat_id] = {'session_started': True, 'messages': []}
        await update.message.reply_text('Session started! You can now send messages.')
    else:
        await update.message.reply_text('Session is already active in this group.')

async def end_session(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id

    if chat_id in session_data and session_data[chat_id]['session_started']:
        messages = session_data[chat_id]['messages']
        session_data[chat_id]['session_started'] = False

        # Collect all messages and end the session
        if messages:
            all_messages = "\n".join(f"{i + 1}: {msg}" for i, msg in enumerate(messages))
            await update.message.reply_text(f'Session ended! Here are your messages:\n{all_messages}')
        else:
            await update.message.reply_text('Session ended! No messages recorded.')
        # Remove session data after ending the session
        del session_data[chat_id]
    else:
        await update.message.reply_text('No active session in this group.')

async def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    if chat_id in session_data and session_data[chat_id]['session_started']:
        user_message = update.message.text
        session_data[chat_id]['messages'].append(user_message)
        logger.info(f'Message logged from chat {chat_id}: {user_message}')

async def view_messages(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id

    if chat_id in session_data and session_data[chat_id]['messages']:
        messages = session_data[chat_id]['messages']
        all_messages = "\n".join(f"{i + 1}: {msg}" for i, msg in enumerate(messages))
        await update.message.reply_text(f'Your messages:\n{all_messages}')
    else:
        await update.message.reply_text('No messages recorded yet or no active session in this group.')

def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's API token
    app = ApplicationBuilder().token("7367817143:AAHs386_qsK7uEwMH5kIdptYn3CrucXCOKg").build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_session", start_session))
    app.add_handler(CommandHandler("end_session", end_session))
    app.add_handler(CommandHandler("view_messages", view_messages))

    # Message handler for non-command text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    app.run_polling()

if __name__ == '__main__':
    main()
