import requests

def get_pokemon_data(nome):
    nome = nome.lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{nome}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "name": data["name"].capitalize(),
        "id": data["id"],
        "types": [t["type"]["name"].capitalize() for t in data["types"]],
        "sprite": data["sprites"]["other"]["official-artwork"]["front_default"]
    }
import requests

def get_pokemon_data_com_ataques(nome):
    nome = nome.lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{nome}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    tipos = [t["type"]["name"].capitalize() for t in data["types"]]
    sprite = data["sprites"]["other"]["official-artwork"]["front_default"]

    ataques = []
    for move in data["moves"][:4]:  # primeiros 4 ataques
        nome_ataque = move["move"]["name"]
        url_ataque = move["move"]["url"]
        r = requests.get(url_ataque)
        if r.status_code != 200:
            continue
        dados_ataque = r.json()
        ataques.append({
            "nome": nome_ataque.capitalize(),
            "tipo": dados_ataque["type"]["name"].capitalize(),
            "categoria": dados_ataque["damage_class"]["name"].capitalize(),
            "poder": dados_ataque.get("power") or "—"
        })

    return {
        "name": data["name"].capitalize(),
        "id": data["id"],
        "types": tipos,
        "sprite": sprite,
        "ataques": ataques
    }
