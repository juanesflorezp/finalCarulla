from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Permitir CORS
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

    # Buscar contenedor del producto
    contenedor = soup.find("div", class_="vtex-search-result-3-x-galleryItem")

    if not contenedor:
        return {"mensaje": "Producto no encontrado."}

    try:
        nombre = contenedor.find("span", class_="vtex-product-summary-2-x-productBrand")
        titulo = contenedor.find("span", class_="vtex-product-summary-2-x-productName")
        precio_entero = contenedor.find("span", class_="vtex-product-price-1-x-currencyInteger")
        precio_decimal = contenedor.find("span", class_="vtex-product-price-1-x-currencyFraction")

        return {
            "marca": nombre.text.strip() if nombre else "Desconocida",
            "producto": titulo.text.strip() if titulo else "Sin nombre",
            "precio": f"{precio_entero.text.strip()},{precio_decimal.text.strip()}" if precio_entero and precio_decimal else "No disponible"
        }

    except Exception as e:
        return {"error": f"No se pudo extraer la información del producto: {str(e)}"}
