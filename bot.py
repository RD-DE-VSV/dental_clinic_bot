import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import requests
from config import TOKEN, WEATHER_API_KEY

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for conversation handler
CHOOSING, ABOUT_US, SPECIALISTS, SERVICES, ADDRESSES, APPOINTMENT, WEATHER = range(7)

# Welcome message handler
def start(update: Update, context: CallbackContext) -> int:
    welcome_text = (
        "Welcome to the Dental Clinic Bot!\n"
        "I can help you with information about our clinic, specialists, and services.\n"
        "You can also schedule an appointment with us.\n"
        "Use /commands to see the available commands."
    )
    keyboard = [
        [InlineKeyboardButton("Let's start", callback_data=str(CHOOSING))],
        [InlineKeyboardButton("Visit our website", url="https://clinicwebsite.com")],
        [InlineKeyboardButton("Later", callback_data='END')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return CHOOSING

# Command to show list of commands
def commands(update: Update, context: CallbackContext):
    commands_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/commands - Show available commands\n"
        "/about - About the clinic\n"
        "/specialists - Our specialists\n"
        "/services - Our services\n"
        "/addresses - Our addresses\n"
        "/appointment - Schedule an appointment\n"
        "/weather - Get weather information\n"
    )
    update.message.reply_text(commands_text)

# Conversation handler for choosing options
def choosing(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Have you been to our clinic yet?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("New User", callback_data=str(ABOUT_US))],
            [InlineKeyboardButton("Returning User", callback_data=str(SERVICES))],
        ])
    )
    return CHOOSING

# About Us handler
def about_us(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="We are a modern dental clinic offering a variety of services to keep your teeth healthy and beautiful."
    )
    return CHOOSING

# Specialists handler
def specialists(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Our specialists:\n1. Dr. Smith - Orthodontist\n2. Dr. Johnson - Pediatric Dentist"
    )
    return CHOOSING

# Services handler
def services(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Our services:\n1. Teeth Cleaning\n2. Whitening\n3. Braces\n4. Root Canal Treatment"
    )
    return CHOOSING

# Addresses handler
def addresses(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Our addresses:\n1. 123 Main St, Cityville\n2. 456 Elm St, Townsville"
    )
    return CHOOSING

# Appointment handler
def appointment(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Please provide your phone number to schedule an appointment."
    )
    return APPOINTMENT

# Collect phone number for appointment
def collect_phone(update: Update, context: CallbackContext) -> int:
    phone_number = update.message.text
    update.message.reply_text(f"Thank you! We will call you soon at {phone_number}.")
    return ConversationHandler.END

# Weather handler
def weather(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please enter the city name:")
    return WEATHER

# Fetch weather information
def fetch_weather(update: Update, context: CallbackContext) -> int:
    city_name = update.message.text
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(weather_url).json()
    if response["cod"] != "404":
        weather_description = response["weather"][0]["description"]
        temperature = response["main"]["temp"]
        update.message.reply_text(f"The weather in {city_name} is {weather_description} with a temperature of {temperature}°C.")
    else:
        update.message.reply_text("City not found.")
    return ConversationHandler.END

# Main function to start the bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(about_us, pattern='^' + str(ABOUT_US) + '$'),
                CallbackQueryHandler(specialists, pattern='^' + str(SPECIALISTS) + '$'),
                CallbackQueryHandler(services, pattern='^' + str(SERVICES) + '$'),
                CallbackQueryHandler(addresses, pattern='^' + str(ADDRESSES) + '$'),
                CallbackQueryHandler(appointment, pattern='^' + str(APPOINTMENT) + '$')
            ],
            APPOINTMENT: [MessageHandler(filters.text & ~filters.command, collect_phone)],
            WEATHER: [MessageHandler(filters.text & ~filters.command, fetch_weather)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler('commands', commands))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
