from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from ..config import WELCOME_TEXT
from ..db.connection import connect_db
import logging
from ..utils.decorators import member_only

@member_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.first_name
    telegram_id = user.id

    try:
        conn = connect_db()
        cur = conn.cursor()
        # Verifica se usuário está registrado
        cur.execute("SELECT 1 FROM usuarios WHERE telegram_id = %s;", (telegram_id,))
        registrado = cur.fetchone() is not None

        if registrado:
            text = f"Olá, {username}! Você já está registrado e pode usar os comandos do bot normalmente."
            markup = None  # Sem botão "Iniciar"
        else:
            text = WELCOME_TEXT.format(username=username)
            keyboard = [
                [InlineKeyboardButton("Iniciar", callback_data="registrar")]
            ]
            markup = InlineKeyboardMarkup(keyboard)

        # Busca a imagem
        cur.execute("SELECT imagem_url FROM WELCOME_image LIMIT 1;")
        result = cur.fetchone()

        if result:
            imagem_url = result[0]
            await context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation=imagem_url,
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=markup
            )
        else:
            await update.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup
            )

    except Exception as e:
        logging.error(f"Erro no start: {e}")
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)

    finally:
        if conn:
            conn.close()

@member_only
async def registrar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE telegram_id = %s;", (telegram_id,))
        registrado = cur.fetchone() is not None
        conn.close()

        if registrado:
            await query.message.reply_text("Você já está registrado e não pode usar o botão iniciar novamente.")
            return

        # Remove o botão da mensagem original
        await query.edit_message_reply_markup(reply_markup=None)

        # Solicita o apelido
        await query.message.reply_text("Digite seu apelido para se registrar:")

        # Marca que o usuário está no fluxo de registro
        context.user_data["registrando"] = True
    except Exception as e:
        logging.error(f"Erro no registrar_callback: {e}")
        await query.message.reply_text("Erro ao processar seu registro. Tente novamente mais tarde.")
