import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation

# ⚠️ Esta deve ser a primeira instrução Streamlit
st.set_page_config(layout="wide")
st.title("📍 Mapa Dinâmico V2.1")

# Obter localização atual do usuário
location = streamlit_geolocation()

# Verificar se a localização foi obtida corretamente
if not location or location["latitude"] is None or location["longitude"] is None:
    st.info("Clique no botão acima para permitir acesso à sua localização.")
    st.stop()

user_lat = location["latitude"]
user_lon = location["longitude"]

# Verificar se as coordenadas estão dentro dos limites válidos
if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
    st.error("Coordenadas inválidas. Verifique a sua localização.")
    st.stop()

uploaded_file = st.file_uploader("Carregar arquivo: DataBaseColabe.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=["Latitudine", "Longitudine", "Cod Site"])
    df["Cod Site"] = df["Cod Site"].astype(str).str.strip().str.upper()

    search_input = st.text_input("Insira os Códigos dos Sites (separados por espaço)").upper()

    if st.button("Buscar Sites no Mapa"):
        cod_sites = [cod.strip() for cod in search_input.split() if cod.strip()]
        result = df[df["Cod Site"].isin(cod_sites)]

        if result.empty:
            st.warning("Nenhum site encontrado. Verifique os códigos inseridos.")
        else:
            # Calcular distância do usuário até cada ponto
            result["Distância (km)"] = result.apply(
                lambda row: geodesic((user_lat, user_lon), (row["Latitudine"], row["Longitudine"])).km,
                axis=1
            )

            result_sorted = result.sort_values(by="Distância (km)", ascending=False)

            # Criar mapa
            mapa = folium.Map(location=[user_lat, user_lon], zoom_start=10)

            # Marcador da localização atual
            folium.Marker(
                location=[user_lat, user_lon],
                popup="📍 Tu estás aqui",
                icon=folium.Icon(color='blue', icon='user')
            ).add_to(mapa)

            # Adicionar marcadores de sites com círculos e texto
            for _, row in result_sorted.iterrows():
                lat, lon = row["Latitudine"], row["Longitudine"]
                cod = row["Cod Site"]
                google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                waze_url = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"

                # Círculo vermelho
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=1.0
                ).add_to(mapa)

                # Texto do nome do site (Cod Site) em preto
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"""
                        <div style="font-size: 12px; color: black;"><b>{cod}</b></div>
                        """
                    ),
                    popup=folium.Popup(
                        f"""
                        <b>{cod}</b><br>
                        <a href="{google_maps_url}" target="_blank">Abrir no Google Maps</a><br>
                        <a href="{waze_url}" target="_blank">Abrir no Waze</a>
                        """,
                        max_width=300
                    )
                ).add_to(mapa)

            # Exibir mapa no app
            folium_static(mapa)

            st.subheader("📊 Resultados da Pesquisa")
            st.dataframe(result_sorted.reset_index(drop=True))

            # Criar link de trajeto entre os pontos ordenados
            waypoints = result_sorted[["Latitudine", "Longitudine"]].values.tolist()
            google_maps_route = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/" + "/".join(
                [f"{lat},{lon}" for lat, lon in waypoints]
            )

            st.markdown("### 🧭 Criar rota entre os sites +longe+perto")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"[🗺️ Abrir rota no Google Maps]({google_maps_route})",
                    unsafe_allow_html=True
                )
            with col2:
                if waypoints:
                    waze_url = f"https://waze.com/ul?ll={waypoints[0][0]},{waypoints[0][1]}&navigate=yes"
                    st.markdown(
                        f"[🚘 Iniciar com Waze (1º destino)]({waze_url})",
                        unsafe_allow_html=True
                    )
