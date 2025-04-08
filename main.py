from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import time
import tempfile
import requests

app = FastAPI()

# Permitir acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scrap/")
async def scrap_excel(file: UploadFile = File(...)):
    df_original = pd.read_excel(file.file, usecols=[0, 1, 2, 3, 4, 5, 6],
                                 names=["Descripción", "Cód. Barras", "Referencia", "CONSULTA", "NETO", "LINEA", "PROVEEDOR"],
                                 skiprows=1)
    df = df_original.copy()
    df["Descripción_Carulla"] = None
    df["Precio_Carulla"] = None

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for index, row in df.iterrows():
        codigo_barras = str(row["Cód. Barras"]).strip()
        try:
            url = f"https://www.carulla.com/_next/data/qtIJHd7TbEvg8fSQmdTw8/es-CO/s.json?q={codigo_barras}&sort=score_desc&page=0"
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            productos = data.get("pageProps", {}).get("results", {}).get("products", [])
            if productos:
                producto = productos[0]
                nombre = producto.get("name", "No encontrado")
                precio = producto.get("price", "No encontrado")
            else:
                nombre = "No encontrado"
                precio = "No encontrado"

            df.at[index, "Descripción_Carulla"] = nombre
            df.at[index, "Precio_Carulla"] = precio

        except Exception as e:
            df.at[index, "Descripción_Carulla"] = "Error"
            df.at[index, "Precio_Carulla"] = "Error"
            print(f"Error en {codigo_barras}: {e}")

        time.sleep(1)  # evitar ser bloqueado por el servidor

    # Guardar el archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df.to_excel(tmp.name, index=False)
        return FileResponse(tmp.name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="scraping_resultados.xlsx")
