from functools import wraps
from telegram.ext import ContextTypes
from ..config import CHANNEL_USERNAME

def member_only(func):
    @wraps(func)
    async def wrapped(update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
            if member.status not in ('member', 'administrator', 'creator'):
                await update.effective_message.reply_text(
                    f"Você precisa ingressar em nosso {CHANNEL_USERNAME} para utilizar o bot."
                )
                return
        except Exception:
            await update.effective_message.reply_text(
                f"Não foi possível verificar sua associação ao canal {CHANNEL_USERNAME}."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
