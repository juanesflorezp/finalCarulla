from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import time
import tempfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

# CORS para permitir acceso desde cualquier origen
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

    # Configurar navegador para Render
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(60)

    try:
        driver.get('https://www.carulla.com')

        for index, row in df.iterrows():
            codigo_barras = str(row["Cód. Barras"]).strip()

            try:
                search_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/header/section/div/div[1]/div[2]/form/input'))
                )
                search_field.clear()
                time.sleep(1)
                for _ in range(21):
                    search_field.send_keys(Keys.BACKSPACE)
                    time.sleep(0.05)
                search_field.send_keys(codigo_barras)
                search_field.send_keys(Keys.ENTER)
                time.sleep(1)

                articlename_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//h3'))
                )
                prices_element = driver.find_element(By.XPATH, '//div[contains(@class,"price")]//p')

                df.at[index, "Descripción_Carulla"] = articlename_element.text
                df.at[index, "Precio_Carulla"] = prices_element.text

            except TimeoutException:
                df.at[index, "Descripción_Carulla"] = "No encontrado"
                df.at[index, "Precio_Carulla"] = "No encontrado"
            except Exception:
                df.at[index, "Descripción_Carulla"] = "Error"
                df.at[index, "Precio_Carulla"] = "Error"

            time.sleep(1)

    finally:
        driver.quit()

    # Guardar y retornar archivo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        df.to_excel(tmp.name, index=False)
        return FileResponse(tmp.name, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="scraping_resultados.xlsx")
