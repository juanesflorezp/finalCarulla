from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Permitir CORS para pruebas desde frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/buscar/{ean}")
def buscar_producto(ean: str):
    url = f"https://www.carulla.com/s?q={ean}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Error {response.status_code} al acceder a Carulla"}

    soup = BeautifulSoup(response.text, "html.parser")

    producto = soup.find("article", {"class": "vtex-product-summary-2-x-container"})

    if not producto:
        return {"mensaje": "Producto no encontrado."}

    try:
        nombre = producto.find("span", {"class": "vtex-product-summary-2-x-productBrand"}).text.strip()
        titulo = producto.find("span", {"class": "vtex-product-summary-2-x-productName"}).text.strip()
        precio = producto.find("span", {"class": "vtex-product-price-1-x-currencyInteger"}).text.strip()

        return {
            "nombre": nombre,
            "producto": titulo,
            "precio": precio
        }
    except Exception as e:
        return {"error": f"No se pudo extraer la información del producto: {str(e)}"}
