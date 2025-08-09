from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from ..db.connection import connect_db
import logging
from ..utils.decorators import member_only

@member_only
async def mostrar_prompt_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Digite seu apelido de treinador para se registrar:")
    context.user_data["registrando"] = True

@member_only
async def processar_apelido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apelido = update.message.text.strip()
    telegram_id = update.effective_user.id
    nome = update.effective_user.first_name

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE telegram_id = %s;", (telegram_id,))
        exists = cur.fetchone()

        if exists:
            await update.message.reply_text("Você já está registrado e não pode se registrar novamente.")
        else:
            cur.execute(
                "INSERT INTO usuarios (telegram_id, nick, nome) VALUES (%s, %s, %s);",
                (telegram_id, apelido, nome)
            )
            conn.commit()
            await update.message.reply_text(
                f"Boas vindas ao mundo pokémon, {apelido}! Use o comando /pokemon para escolher seu primeiro inicial!."
            )
    except Exception as e:
        logging.error(f"Erro ao registrar apelido: {e}")
        await update.message.reply_text("Erro ao registrar seu apelido.")
    finally:
        conn.close()
        context.user_data["registrando"] = False

@member_only
async def processar_apelido_pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apelido = update.message.text.strip()
    pokemon = context.user_data["aguardando_apelido"]
    telegram_id = update.effective_user.id

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE usuarios SET apelido_pokemon = %s WHERE telegram_id = %s;",
            (apelido, telegram_id)
        )
        conn.commit()
        await update.message.reply_text(
            f"*{pokemon}* agora se chama *{apelido}*! Use o comando /pokédex para visualizar seus pokémons obtidos.",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data.pop("aguardando_apelido")
    except Exception as e:
        logging.error(f"Erro ao salvar apelido do Pokémon: {e}")
        await update.message.reply_text("Erro ao salvar o apelido do Pokémon.")
    finally:
        conn.close()

@member_only
async def processar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("registrando"):
        await processar_apelido(update, context)
    elif context.user_data.get("aguardando_apelido"):
        await processar_apelido_pokemon(update, context)
    else:
        await update.message.reply_text("Não entendi. Use um comando ou botão para começar.")
