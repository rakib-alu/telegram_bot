import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from telegram import Update
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable missing!")

BAD_WORDS_FILE = "badwords.txt"

# ---------------------- UTILITIES ----------------------
def load_bad_words():
    if not os.path.exists(BAD_WORDS_FILE):
        return []
    with open(BAD_WORDS_FILE, "r") as file:
        return [w.strip() for w in file.readlines()]


def save_bad_words(words):
    with open(BAD_WORDS_FILE, "w") as file:
        file.write("\n".join(words))


# ---------------------- COMMAND HANDLERS ----------------------
async def rank_command(update: Update, context):
    await update.message.reply_text("Your Rank: Member 👤")


async def add_bad(update: Update, context):
    if not context.args:
        return await update.message.reply_text("Usage: /addbad word")

    new_word = context.args[0].lower()
    words = load_bad_words()

    if new_word in words:
        return await update.message.reply_text("Already exists!")

    words.append(new_word)
    save_bad_words(words)
    await update.message.reply_text(f"Added bad word: {new_word}")


async def del_bad(update: Update, context):
    if not context.args:
        return await update.message.reply_text("Usage: /delbad word")

    target = context.args[0].lower()
    words = load_bad_words()

    if target not in words:
        return await update.message.reply_text("Not found!")

    words.remove(target)
    save_bad_words(words)
    await update.message.reply_text(f"Deleted: {target}")


async def list_bad(update: Update, context):
    words = load_bad_words()
    await update.message.reply_text("\n".join(words) if words else "No bad words!")


# ---------------------- MESSAGE HANDLER ----------------------
async def auto_clean(update: Update, context):
    text = update.message.text.lower()
    words = load_bad_words()

    if any(bad in text for bad in words):
        try:
            await update.message.delete()
        except:
            pass
        return


async def welcome_message(update: Update, context):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome {member.mention_html()}", parse_mode=ParseMode.HTML)


# ---------------------- MAIN FUNCTION ----------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # EVENT HANDLERS
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_clean))

    # COMMANDS
    app.add_handler(CommandHandler("rank", rank_command))
    app.add_handler(CommandHandler("addbad", add_bad))
    app.add_handler(CommandHandler("delbad", del_bad))
    app.add_handler(CommandHandler("badlist", list_bad))

    print("BOT STARTED SUCCESSFULLY…")
    app.run_polling()


if __name__ == "__main__":
    main()
