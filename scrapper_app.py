# scrapper_app.py

import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import tempfile
import os


st.title("🔎 Scraper de productos Carulla")

# Subida del archivo Excel
uploaded_file = st.file_uploader("📤 Sube el archivo Excel con códigos de barras", type=["xlsx"])

if uploaded_file:
    df_original = pd.read_excel(
        uploaded_file,
        usecols=[0, 1, 2, 3, 4, 5, 6],
        names=["Descripción", "Cód. Barras", "Referencia", "CONSULTA", "NETO", "LINEA", "PROVEEDOR"],
        skiprows=1
    )
    df = df_original.copy()
    df["Descripción_Carulla"] = None
    df["Precio_Carulla"] = None

    if st.button("🚀 Ejecutar scraping"):
        st.info("Abriendo navegador...")

        try:
            # Configuración del driver
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(60)

            try:
                driver.get('https://www.carulla.com')
                time.sleep(5)  # Espera a que cargue completamente
            except Exception as e:
                st.error(f"❌ No se pudo cargar la página de Carulla: {e}")
                driver.quit()
                st.stop()

            progress_bar = st.progress(0)
            status_text = st.empty()

            for index, row in df.iterrows():
                codigo_barras = str(row["Cód. Barras"]).strip()
                status_text.text(f"🔍 Buscando: {codigo_barras}")
                try:
                    # Buscar y limpiar campo de búsqueda
                    search_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/header/section/div/div[1]/div[2]/form/input'))
                    )
                    for _ in range(21):  
                        search_field.send_keys(Keys.BACKSPACE)
                        time.sleep(0.5)

                    search_field.send_keys(codigo_barras)
                    search_field.send_keys(Keys.ENTER)
                    time.sleep(2)

                    # Obtener resultados
                    articlename_element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//h3'))
                    )
                    prices_element = driver.find_element(By.XPATH, '//div[contains(@class,"price")]//p')

                    df.at[index, "Descripción_Carulla"] = articlename_element.text
                    df.at[index, "Precio_Carulla"] = prices_element.text

                except TimeoutException:
                    df.at[index, "Descripción_Carulla"] = "No encontrado"
                    df.at[index, "Precio_Carulla"] = "No encontrado"
                except Exception as e:
                    df.at[index, "Descripción_Carulla"] = "Error"
                    df.at[index, "Precio_Carulla"] = "Error"

                progress_bar.progress((index + 1) / len(df))
                time.sleep(1)

            driver.quit()
            st.success("✅ Scraping completado")

            # Descargar archivo
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                df.to_excel(tmp.name, index=False)
                st.download_button("📥 Descargar resultados", data=open(tmp.name, "rb"), file_name="scraping_resultados.xlsx")

        except Exception as error:
            st.error(f"❌ Ocurrió un error al iniciar el navegador: {error}")
