from ..connection import connect_db

def buscar_dados_pokemon(nome):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT nome, tipo, sprite, ataque1, ataque2, ataque3, ataque4 
            FROM pokemons_iniciais WHERE nome = %s
        """, (nome,))
        row = cur.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Erro ao buscar Pokémon no banco: {e}")
        return None
