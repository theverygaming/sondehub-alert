import logging
import asyncio
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from . import config

_logger = logging.getLogger(__name__)

def _log_cmd(update: Update):
    _logger.info(f"Responding to command '{update.message.text}' from @{update.effective_user.username}")

async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _log_cmd(update)
    await update.message.reply_text("You cannot configure this bot yourself. Use /status to get the current status for your account")

async def _status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _log_cmd(update)
    await update.message.reply_text(
        f"""Status for @{update.effective_user.username}:
chat ID: `{update.message.chat.id}`""", 
        parse_mode="MarkdownV2",
    )

_app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

def launch_bot():
    _logger.info("launching Telegram bot")
    _app.add_handler(CommandHandler("start", _start))
    _app.add_handler(CommandHandler("status", _status))
    _app.run_polling()

def send_message(chat_id, text):
    # https://github.com/iobroker-community-adapters/ioBroker.telegram/issues/309#issuecomment-1434358480
    text = re.sub(r"([-_*\[\]()~>#+=|{}.!])", "\\\\\\1", text)
    async def asyncfunc():
        await _app.bot.send_message(chat_id, text=text, parse_mode="MarkdownV2")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncfunc())
