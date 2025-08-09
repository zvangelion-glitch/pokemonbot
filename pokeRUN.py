import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from .handlers.start import start, registrar_callback
from .handlers.pokemon import pokemon, escolher_pokemon, processar_apelido_pokemon
from .handlers.registrar import mostrar_prompt_registro, processar_apelido

logging.basicConfig(level=logging.INFO)
logging.info("Bot iniciado")

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado. Defina a variável de ambiente BOT_TOKEN.")

async def processar_apelido_wrapper(update, context):
    if context.user_data.get("registrando", False):
        await processar_apelido(update, context)
    elif context.user_data.get("aguardando_apelido", False):
        await processar_apelido_pokemon(update, context)
    else:
        await update.message.reply_text("Não entendi. Use um comando ou botão para começar.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pokemon", pokemon))
    app.add_handler(CallbackQueryHandler(escolher_pokemon, pattern=r"^select_"))
    app.add_handler(CallbackQueryHandler(mostrar_prompt_registro, pattern="^registrar$"))
    app.add_handler(CallbackQueryHandler(registrar_callback, pattern="^registrar$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_apelido_wrapper))

    app.run_polling()
