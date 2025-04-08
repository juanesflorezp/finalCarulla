import streamlit as st
import requests
import pandas as pd

st.title("📤 Scraper de productos Carulla")

uploaded_file = st.file_uploader("Sube tu archivo Excel con los códigos de barras", type=["xlsx"])

if uploaded_file is not None:
    if st.button("🚀 Ejecutar Scraping"):
        with st.spinner("Enviando archivo a la API..."):

            files = {"file": (uploaded_file.name, uploaded_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

            try:
                response = requests.post("https://finalcarulla.onrender.com/scrap/", files=files)

                if response.status_code == 200:
                    st.success("✅ Archivo procesado correctamente")
                    
                    st.download_button(
                        label="📥 Descargar archivo procesado",
                        data=response.content,
                        file_name="resultados_carulla.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(f"❌ Error desde la API: {response.status_code}\n{response.text}")

            except Exception as e:
                st.error(f"❌ Error al conectar con la API: {e}")
