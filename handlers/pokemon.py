from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from ..db.connection import connect_db
from ..utils.decorators import member_only
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from ..db.connection import connect_db

POKEMONS = ["Charmander", "Bulbasaur", "Squirtle"]

POKEMON_GIFS = {
    "Charmander": "https://i.imgur.com/nawMohS.mp4",
    "Bulbasaur": "https://i.imgur.com/TAHYbZp.mp4",
    "Squirtle": "https://i.imgur.com/DRwesz9.mp4"
}

@member_only
async def pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        telegram_id = update.effective_user.id
        conn = connect_db()
        cur = conn.cursor()
        
        # Verifica se o usuário já escolheu um Pokémon
        cur.execute("SELECT pokemon_inicial FROM usuarios WHERE telegram_id = %s", (telegram_id,))
        result = cur.fetchone()
        if result and result[0]:
            await update.message.reply_text("Você já escolheu seu Pokémon inicial e não pode escolher outro.")
            conn.close()
            return

        # Busca o gif de introdução
        cur.execute("SELECT intro_url FROM pokemon_intro LIMIT 1;")
        result = cur.fetchone()
        intro_gif = result[0] if result else None
        conn.close()

        if intro_gif:
            buttons = [
                [InlineKeyboardButton("Charmander", callback_data="select_Charmander")],
                [InlineKeyboardButton("Bulbasaur", callback_data="select_Bulbasaur")],
                [InlineKeyboardButton("Squirtle", callback_data="select_Squirtle")]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            caption = "Escolha seu Pokémon inicial!\n"
            await context.bot.send_animation(
                chat_id=update.effective_chat.id,
                animation=intro_gif,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("GIF de introdução não encontrado no banco.")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

@member_only
async def escolher_pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    escolha = query.data.replace("select_", "")
    gif = POKEMON_GIFS.get(escolha)

    try:
        conn = connect_db()
        cur = conn.cursor()

        # Verifica se o usuário já escolheu um Pokémon
        cur.execute("SELECT pokemon_inicial FROM usuarios WHERE telegram_id = %s;", (query.from_user.id,))
        result = cur.fetchone()

        if result and result[0]:
            await query.message.reply_text("Você já escolheu seu Pokémon inicial e não pode escolher outro.")
        elif gif:
            # Remove a mensagem original com gif e botões
            await query.message.delete()

            # Salva o nome do pokémon escolhido no contexto para aguardar o apelido
            context.user_data["aguardando_apelido"] = escolha

            # Atualiza o Pokémon inicial no banco
            cur.execute(
                "UPDATE usuarios SET pokemon_inicial = %s WHERE telegram_id = %s;",
                (escolha, query.from_user.id)
            )
            conn.commit()

            # Envia nova mensagem só com o gif do pokémon escolhido e texto
            await context.bot.send_animation(
                chat_id=query.message.chat_id,
                animation=gif,
                caption=f"Você escolheu *{escolha}*! Qual nome você quer dar a ele?",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.message.reply_text("Erro ao carregar Pokémon.")
    except Exception as e:
        await query.message.reply_text(f"Erro ao registrar sua escolha: {e}")
    finally:
        if conn:
            conn.close()

@member_only
async def processar_apelido_pokemon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "aguardando_apelido" not in context.user_data:
        await update.message.reply_text("Você ainda não escolheu um Pokémon para nomear.")
        return

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
        await update.message.reply_text(f"*{pokemon}* agora se chama *{apelido}*! use /menu para consultar mais comandos.",
                                        parse_mode=ParseMode.MARKDOWN)
        context.user_data.pop("aguardando_apelido")
    except Exception as e:
        await update.message.reply_text("Erro ao salvar o apelido do Pokémon.")
    finally:
        if conn:
            conn.close()
