import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN não encontrado. Defina a variável de ambiente BOT_TOKEN.")

CHANNEL_USERNAME = '@pokedex_ofc'

WELCOME_TEXT = (
    "Seja bem-vindo(a), *{username}*!\n\n"
    "Aqui você poderá capturar, treinar e evoluir diversos pokémons! Aprimore suas habilidades e trave batalhas épicas contra outros jogadores para provar quem é o maior treinador!\n\n"
    "Fique por dentro de todas as novidades através do nosso [canal](https://t.me/pokedex_ofc).\n\n"
    "Se já está tudo pronto, então só falta se registrar e receber seu pokémon."
)

