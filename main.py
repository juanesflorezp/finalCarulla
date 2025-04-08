import requests

def verificar_producto_existe(codigo_barras: str):
    url = f"https://www.carulla.com/s?q={codigo_barras}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {"mensaje": "Página encontrada ✅"}
    else:
        return {"mensaje": f"Página no encontrada ❌. Código: {response.status_code}"}
