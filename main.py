from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
import re

app = FastAPI()

def obtener_build_id():
    try:
        response = requests.get("https://www.carulla.com/")
        match = re.search(r'"buildId":"(.*?)"', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error al obtener buildId: {e}")
    return None

@app.get("/buscar/{codigo}")
def buscar_producto(codigo: str):
    build_id = obtener_build_id()
    
    if not build_id:
        return JSONResponse(
            status_code=500,
            content={"error": "No se pudo obtener el buildId de Carulla."}
        )
    
    url = f"https://www.carulla.com/_next/data/{build_id}/es-CO/s.json?q={codigo}&sort=score_desc&page=0"
    response = requests.get(url)

    try:
        data = response.json()
        productos = data.get("pageProps", {}).get("results", {}).get("products", [])

        if not productos:
            return JSONResponse(
                status_code=404,
                content={"mensaje": "Producto no encontrado."}
            )
        
        producto = productos[0]
        return {
            "nombre": producto.get("name"),
            "precio": producto.get("price"),
            "imagen": producto.get("images", [{}])[0].get("imageUrl"),
            "link": f'https://www.carulla.com{producto.get("linkText", "")}'
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al procesar la respuesta: {e}"}
        )
