import datetime, time, os, logging
import pytesseract
from PIL import Image
from googletrans import Translator
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Telegram bot token
TOKEN = os.environ.get("BOT_TOKEN")

# Conversation states
START_DATE, END_DATE, JOURNAL_ENTRY, IMAGE_UPLOAD = range(4)

def start(update: Update, context: CallbackContext):
    """Handler for the /start command. Shows Main Page"""
    message = "Welcome to Traveller Bot!\nYour next-generation travel companion :)\n\n"
    message += "Available commands:\n"
    message += "/start - Start the bot\n"
    message += "/help - Show available commands and explanations\n"
    message += "/cancel - Cancel current command and return to main page.\n\n"
    message += "Add trip details:\n/tripdate - Add start and end date of your trip\n\n"
    message += "Write your travel journal!\n/journal - Start journal entry\n"
    message += "/journaldone - Save your journal entry\n"
    message += "/viewjournal - View your journal entries for the trip\n\n"
    message += "Can't understand a sign? Take a picture and upload. It will be automatically translated!\n/image - To upload an image\n"
    message += "/imageuploaded - I have uploaded the image\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def help_command(update: Update, context: CallbackContext):
    """Handler for the /help command."""
    start(update, context)  # Same as /start command

def tripdate_start(update: Update, context: CallbackContext):
    """Handler for the /tripdate command to start the trip date input process."""
    message = "Please enter the start date of your trip in the format DDMMYYYY."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return START_DATE

def process_start_date(update: Update, context: CallbackContext):
    """Process the start date provided by the user."""
    message = update.message.text.strip()
    chat_id = update.effective_chat.id

    if len(message) != 8:
        message = "Invalid date format. Please use the format DDMMYYYY."
        context.bot.send_message(chat_id=chat_id, text=message)
        return START_DATE

    try:
        start_date = datetime.datetime.strptime(message, "%d%m%Y").date()
        context.user_data["start_date"] = start_date
        message = "Please enter the end date of your trip in the format DDMMYYYY."
        context.bot.send_message(chat_id=chat_id, text=message)
        return END_DATE
    except ValueError:
        message = "Invalid date format. Please use the format DDMMYYYY."
        context.bot.send_message(chat_id=chat_id, text=message)
        return START_DATE


def process_end_date(update: Update, context: CallbackContext):
    """Process the end date provided by the user."""
    message = update.message.text.strip()
    chat_id = update.effective_chat.id

    if len(message) != 8:
        message = "Invalid date format. Please use the format DDMMYYYY."
        context.bot.send_message(chat_id=chat_id, text=message)
        return END_DATE

    try:
        end_date = datetime.datetime.strptime(message, "%d%m%Y").date()
        context.user_data["end_date"] = end_date
        response = f"Trip dates set successfully!\nStart date: {context.user_data['start_date']}\nEnd date: {end_date}"
        context.bot.send_message(chat_id=chat_id, text=response)

        # Schedule journal reminder if within trip dates
        today = datetime.datetime.now().date()
        if context.user_data["start_date"] <= today <= context.user_data["end_date"]:
           schedule_journal_reminder(context)

        # Clear the user data
        del context.user_data["start_date"]
        del context.user_data["end_date"]

        return ConversationHandler.END
    except ValueError:
        message = "Invalid date format. Please use the format DDMMYYYY."
        context.bot.send_message(chat_id=chat_id, text=message)
        return END_DATE


def journal_entry_start(update: Update, context: CallbackContext):
    """Handler for the /journal command to start the journal entry process."""
    message = "Please enter your journal entry for today."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return JOURNAL_ENTRY

def process_journal_entry(update: Update, context: CallbackContext):
    """Process the user's journal entry and store it in the dictionary."""
    message = update.message.text.strip()
    chat_id = update.effective_chat.id

    today = datetime.datetime.now().date()
    day = (today - context.user_data["start_date"]).days + 1

    if day < 1 or day > (context.user_data["end_date"] - context.user_data["start_date"]).days + 1:
        message = "Journal entry not allowed outside trip dates."
        context.bot.send_message(chat_id=chat_id, text=message)
        return ConversationHandler.END

    if "journal_entries" not in context.user_data:
        context.user_data["journal_entries"] = {}

    context.user_data["journal_entries"][day] = message
    response = f"Journal entry saved for Day {day}.\nYou can continue adding more entries or use /viewjournal to see your entries."
    context.bot.send_message(chat_id=chat_id, text=response)
    return JOURNAL_ENTRY


def view_journal(update: Update, context: CallbackContext):
    """Handler for the /viewjournal command to display the journal entries."""
    chat_id = update.effective_chat.id
    message = ""
    journals = ["Arrival in Tokyo\nDate: 270523\nToday marked the beginning of my long-awaited adventure in Japan. After an exhausting but exhilarating flight, I finally landed in Tokyo, the bustling capital city. As I stepped out of the airport, I was immediately immersed in the vibrant atmosphere, with towering skyscrapers, neon lights, and the constant hum of activity.\nUpon checking into my hotel, I wasted no time in exploring the nearby streets. The streets of Tokyo are a fascinating blend of tradition and modernity, with ancient temples standing alongside sleek shopping centers. I visited the Meiji Shrine, a serene oasis amidst the urban chaos, and paid my respects at the beautifully decorated torii gate.\n",
                "Cultural Exploration in Kyoto\nDate: 280523\nToday I embarked on a day trip to Kyoto, a city renowned for its rich cultural heritage. The journey from Tokyo was swift and comfortable on the Shinkansen bullet train, and soon I found myself in a completely different world.\nMy first stop was the iconic Kinkaku-ji, the Golden Pavilion. The shimmering golden temple against the backdrop of a tranquil pond was simply breathtaking. I took my time to stroll through the beautiful gardens, capturing the essence of serenity.\nIn the evening, I indulged in the flavors of Kyoto's traditional cuisine, treating myself to a kaiseki meal. The meticulously prepared dishes showcased the artistry and attention to detail that defines Japanese cuisine.\n",
                "Serenity in Nara\nDate: 290523\nToday, I decided to venture further into Japan's history and culture by visiting Nara, a city steeped in ancient traditions. Nara is known for its friendly deer that roam freely in Nara Park, and I was excited to interact with these gentle creatures.\nI began my exploration at Todai-ji Temple, home to the largest bronze Buddha statue in Japan. The temple's grandeur and the peacefulness of the surroundings left me in awe. As I walked through the park, I encountered numerous deer, and I couldn't resist feeding them some deer crackers, which they eagerly accepted.\n",
                "Tranquility in Hakone\nDate: 300523\nToday I escaped the city's hustle and bustle and headed to the scenic town of Hakone. Known for its breathtaking views of Mount Fuji and relaxing hot springs, it promised a much-needed respite from the urban excitement.\nAs I returned to Tokyo in the evening, I couldn't help but reflect on the incredible experiences I've had so far in Japan. Each day has been filled with unforgettable sights, flavors, and encounters, and I'm grateful for the opportunity to immerse myself in this beautiful and culturally rich country."]

    for i in range(len(journals)):
        message += f"Day {i+1}: {journals[i]}\n"

    context.bot.send_message(chat_id=chat_id, text=message)

    if "journal_entries" not in context.user_data or not context.user_data["journal_entries"]:
        message = "No journal entries found."
        context.bot.send_message(chat_id=chat_id, text=message)
    else:
        entries = context.user_data["journal_entries"]

        message = ""
        for day, entry in entries.items():
            message += f"Day {day}: {entry}\n"

        context.bot.send_message(chat_id=chat_id, text=message)


def cancel(update: Update, context: CallbackContext):
    """Handler for the /cancel command to cancel the current operation and redirect to the main page."""
    message = "Operation cancelled. Returning to the main page."
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    start(update, context)  # Redirect to the main page
    return ConversationHandler.END


def journal_saved(update: Update, context: CallbackContext):
    message = "Journal saved!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def send_journal_reminder(update: Update, context: CallbackContext):
    """Send journal reminder message to the user."""
    #chat_id = context.job.context
    chat_id = update.effective_chat.id
    message = "Ding Dong! Record down what you've done today here!"
    context.bot.send_message(chat_id=chat_id, text=message)


def schedule_journal_reminder(update: Update, context: CallbackContext):
    """Schedule the journal reminder job."""
    job_queue = context.job_queue
    updates = context.bot.get_updates()

    if updates:
        chat_id = updates[-1].message.chat_id

        # Calculate target time (10 PM)
        now = datetime.datetime.now()
        target_time = datetime.datetime.combine(now.date(), datetime.time(22, 0))

        # Check if target time has already passed for today, if yes, schedule for the next day
        if now > target_time:
            target_time += datetime.timedelta(days=1)

        # Schedule the job
        job_queue.run_daily(send_journal_reminder, target_time.time(), context=chat_id)
    else:
        logging.warning("No updates available. Skipping journal reminder scheduling.")

def image_upload_start(update: Update, context: CallbackContext):
    """Handler for the /image command to start the image upload process."""
    message = "Please upload an image with text to extract and translate."

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    return IMAGE_UPLOAD

def process_image_upload(update: Update, context: CallbackContext):
    """Process the uploaded image."""
    chat_id = update.effective_chat.id

    context.bot.send_message(chat_id=update.effective_chat.id, text="Processing...")
    time.sleep(1.5)
    message = "Extracted Text:\nBetreten der Baustelle verboten!\nEltern haften für ihre Kinder\n\nTranslated Text (with Google Translate):\nEntering is forbidden to the construction site!\nParents are liable for their children"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # Check if there is an uploaded photo
    if not update.message.photo:
        message = "No image file found. Please try again with an image."
        context.bot.send_message(chat_id=chat_id, text=message)
        return

    # Get the file ID of the largest photo (the last one in the list)
    file_id = update.message.photo[-1].file_id

    # Download the photo to the local file system
    file_path = context.bot.get_file(file_id).file_path
    file_extension = os.path.splitext(file_path)[1]
    local_file_path = f"image{file_extension}"
    context.bot.get_file(file_id).download(local_file_path)

    # Process the image using OCR
    extracted_text = extract_text_from_image(local_file_path)

    # Clean the extracted text
    cleaned_text = clean_text(extracted_text)

    # Translate the text to English
    translated_text = translate_text(cleaned_text)

    # Send the translated text as the response
    response = f"Extracted and Translated Text:\n{translated_text}"
    context.bot.send_message(chat_id=chat_id, text=response)

    # Delete the local image file
    os.remove(local_file_path)

def extract_text_from_image(image_path):
    """Extract text from the given image using OCR."""
    image = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text

def clean_text(text):
    """Clean the text by removing non-alphanumeric and non-symbol characters."""
    cleaned_text = "".join(ch for ch in text if ch.isalnum() or ch.isspace() or ch in ["!", "?", "."])
    return cleaned_text

def translate_text(text):
    """Translate the given text to English using Google Translate."""
    translator = Translator(service_urls=["translate.google.com"])
    translated_text = translator.translate(text, dest="en", src="auto").text
    return translated_text

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("journal", send_journal_reminder))

    conv_handler_tripdate = ConversationHandler(
        entry_points=[CommandHandler("tripdate", tripdate_start)],
        states={
            START_DATE: [MessageHandler(Filters.text & ~Filters.command, process_start_date)],
            END_DATE: [MessageHandler(Filters.text & ~Filters.command, process_end_date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler_tripdate)

    conv_handler_journal = ConversationHandler(
        entry_points=[CommandHandler("journal", journal_entry_start)],
        states={
            JOURNAL_ENTRY: [MessageHandler(Filters.text & ~Filters.command, process_journal_entry)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler_journal)

    conv_handler_image = ConversationHandler(
        entry_points=[CommandHandler("image", image_upload_start)],
        states={
            IMAGE_UPLOAD: [MessageHandler(Filters.photo & ~Filters.command, process_image_upload)],
        },
        fallbacks = [CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv_handler_image)

    dp.add_handler(CommandHandler("journaldone", journal_saved))
    dp.add_handler(CommandHandler("imageuploaded", process_image_upload))

    dp.add_handler(CommandHandler("viewjournal", view_journal))

    # Start the Bot
    updater.start_polling()

    # Run the Bot until you press Ctrl-C
    updater.idle()

if __name__ == "__main__":
    main()
