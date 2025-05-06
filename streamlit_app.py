import streamlit as st

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static


st.title("Mapa Dinamico V2.0")

uploaded_file = st.file_uploader("CarregarDataBaseColabe.xlsx", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=["Latitudine", "Longitudine", "Cod Site"])

    search_input = st.text_input("Insere os Codigos do Sites separados espaço")

    if st.button("Pesquisar"):
        cod_sites = [cod.strip() for cod in search_input.split() if cod.strip()]
        result = df[df["Cod Site"].astype(str).str.strip().isin(cod_sites)]

        if result.empty:
            st.warning("Nenhum site encontrado.")
        else:
            mapa = folium.Map(location=[result["Latitudine"].mean(), result["Longitudine"].mean()], zoom_start=10)
            for _, row in result.iterrows():
                folium.CircleMarker(
                    location=[row["Latitudine"], row["Longitudine"]],
                    radius=5,
                    color="red",
                    fill=True,
                    fill_color="red"
                ).add_to(mapa)

                folium.Marker(
                    location=[row["Latitudine"], row["Longitudine"]],
                    icon=folium.DivIcon(html=f"<b>{row['Cod Site']}</b>")
                ).add_to(mapa)

            folium_static(mapa)
