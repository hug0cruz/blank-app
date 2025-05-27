import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(layout="wide", page_title="Field Map Tools V2.3 SKYLINE")

# --- CSS Animado: fundo, título, ícones SVG animados, modo escuro total, texto preto nos marcadores ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">

<style>
  /* Fundo gradiente animado "noite neon" */
  @keyframes bgGradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  body, .main {
    background: linear-gradient(270deg, #0f0f27, #1a1a40, #0f0f27, #001f3f);
    background-size: 800% 800%;
    animation: bgGradient 30s ease infinite;
    color: #00f0ff;
  }

  /* Título Neon Pulsante sem caixa */
  @keyframes neonPulse {
    0%, 100% {
      color: #00f0ff;
      text-shadow:
        0 0 5px #00f0ff,
        0 0 10px #00f0ff,
        0 0 20px #0ff,
        0 0 30px #0ff;
    }
    50% {
      color: #ffffff;
      text-shadow:
        0 0 10px #0ff,
        0 0 20px #00e6ff,
        0 0 40px #00d4ff,
        0 0 60px #00caff;
    }
  }
  .title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.5em;
    font-weight: 700;
    text-align: center;
    animation: neonPulse 1s ease-in-out infinite;
    margin: 1rem 0 2rem;
    letter-spacing: 3px;
    background: none !important;
    border: none !important;
    box-shadow: none !important;
  }

  /* Botões personalizados com efeito neon */
  div.stButton > button {
    background: transparent;
    border: 2px solid #00f0ff;
    color: #00f0ff;
    font-weight: 700;
    padding: 0.5rem 1.5rem;
    border-radius: 0.4rem;
    transition: all 0.3s ease-in-out;
    box-shadow:
      0 0 5px #00f0ff,
      0 0 10px #00f0ff,
      0 0 20px #0ff;
  }
  div.stButton > button:hover {
    background: #00f0ff;
    color: #001f3f;
    box-shadow:
      0 0 10px #00fff7,
      0 0 20px #00fff7,
      0 0 30px #00fff7;
    transform: scale(1.05);
  }

  /* Ícones SVG animados (exemplo pulsante) */
  .icon-svg {
    width: 48px;
    height: 48px;
    fill: #00f0ff;
    filter: drop-shadow(0 0 5px #00f0ff);
    animation: pulseIcon 0.5s infinite;
    vertical-align: middle;
    margin-right: 0.5rem;
  }
  @keyframes pulseIcon {
    0%, 100% {
      filter: drop-shadow(0 0 5px #00f0ff);
      transform: scale(1);
      fill: #00f0ff;
    }
    50% {
      filter: drop-shadow(0 0 15px #00fff7);
      transform: scale(1.1);
      fill: #00fff7;
    }
  }

  /* Custom scrollbar dark mode */
  ::-webkit-scrollbar {
    width: 10px;
  }
  ::-webkit-scrollbar-track {
    background: #001f3f;
  }
  ::-webkit-scrollbar-thumb {
    background: #00f0ff;
    border-radius: 10px;
  }

  /* Inputs */
  .stTextInput > label, .stFileUploader > label {
    color: #00f0ff !important;
    font-weight: 700;
  }
  .stTextInput > div > input {
    background-color: #00294d !important;
    color: #00f0ff !important;
    border: 2px solid #00f0ff !important;
  }
</style>
""", unsafe_allow_html=True)

# --- Título com ícone SVG animado ---
st.markdown("""
<div style="text-align:center;">
  <svg class="icon-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
  </svg>
  <span class="title">FIELD MAP TOOLS V2.3 SKYLINE</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Localização ---
location = streamlit_geolocation()
if not location or location["latitude"] is None or location["longitude"] is None:
    st.info("🔒 Permita o acesso à sua localização para usar a aplicação.")
    st.stop()

user_lat = location["latitude"]
user_lon = location["longitude"]

if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
    st.error("Coordenadas inválidas detectadas.")
    st.stop()

# --- Upload ---
uploaded_file = st.file_uploader("📁 Carregar base de dados: DataBaseColabe.xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=["Latitudine", "Longitudine", "Cod Site"])
    df["Cod Site"] = df["Cod Site"].astype(str).str.strip().str.upper()

    search_input = st.text_input("🔍 Pesquisar Códigos dos Sites (separados por espaço)").upper()

    if st.button("🔎 Pesquisar"):
        cod_sites = [cod.strip() for cod in search_input.split() if cod.strip()]
        result = df[df["Cod Site"].isin(cod_sites)]

        if result.empty:
            st.warning("❌ Nenhum site encontrado.")
        else:
            result["Distância (km)"] = result.apply(
                lambda row: geodesic((user_lat, user_lon), (row["Latitudine"], row["Longitudine"])).km,
                axis=1
            )
            result_sorted = result.sort_values(by="Distância (km)", ascending=False)

            # --- Criar mapa ---
            mapa = folium.Map(location=[user_lat, user_lon], zoom_start=10, control_scale=True)
            folium.Marker(
                location=[user_lat, user_lon],
                popup="📍 Tu estás aqui",
                icon=folium.Icon(color='blue', icon='user')
            ).add_to(mapa)

            for _, row in result_sorted.iterrows():
                lat, lon = row["Latitudine"], row["Longitudine"]
                cod = row["Cod Site"]
                google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                waze_url = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=1.0
                ).add_to(mapa)

                # Texto do marker em PRETO
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"<div style='font-size:12px; color: black; font-weight:bold;'>{cod}</div>"
                    ),
                    popup=folium.Popup(
                        f"<b>{cod}</b><br>"
                        f"<a href='{google_maps_url}' target='_blank' style='color:#00f0ff'>Google Maps</a><br>"
                        f"<a href='{waze_url}' target='_blank' style='color:#00f0ff'>Waze</a>",
                        max_width=250
                    )
                ).add_to(mapa)

            folium_static(mapa, width=1600, height=600)

            # --- Exportar HTML do mapa ---
            mapa.save("/tmp/mapa_resultado.html")
            with open("/tmp/mapa_resultado.html", "r", encoding="utf-8") as f:
                mapa_html = f.read()

            st.download_button(
                label="⬇️ Descarregar Mapa HTML",
                data=mapa_html,
                file_name="mapa_com_pontos.html",
                mime="text/html"
            )

            # --- Mostrar Tabela ---
            st.subheader("📊 Resultados da Pesquisa")
            st.dataframe(result_sorted.reset_index(drop=True))

            # --- Criar Rota ---
            waypoints = result_sorted[["Latitudine", "Longitudine"]].values.tolist()
            google_maps_route = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/" + "/".join(
                [f"{lat},{lon}" for lat, lon in waypoints]
            )

            st.markdown("### 🧭 Navegar pelos sites ordenados por distância")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"[🗺️ Abrir rota no Google Maps]({google_maps_route})", unsafe_allow_html=True)

            with col2:
                if waypoints:
                    waze_url = f"https://waze.com/ul?ll={waypoints[0][0]},{waypoints[0][1]}&navigate=yes"
                    st.markdown(f"[🚘 Iniciar com Waze (1º destino)]({waze_url})", unsafe_allow_html=True)
