import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from urllib.parse import quote

st.set_page_config(layout="wide", page_title="Field Map Tools V3.1 THUNDERSTORM")

# --- CSS THUNDERSTORM Profissional ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Montserrat:wght@700&display=swap" rel="stylesheet">

<style>
/* Fundo dark thunderstorm */
body, .main {
  background: linear-gradient(270deg, #0b0b1a, #1a1a40, #0b0b1a, #001122);
  background-size: 800% 800%;
  animation: bgGradient 25s ease infinite;
  color: #f0f0f0;
}
@keyframes bgGradient {
  0% { background-position:0% 50%; }
  50% { background-position:100% 50%; }
  100% { background-position:0% 50%; }
}

/* Título profissional */
.title-thunder {
  font-family: 'Orbitron','Montserrat', sans-serif;
  font-size: 3.5em;
  font-weight: 900;
  text-align: center;
  color: #FFFF00; /* amarelo */
  -webkit-text-stroke: 2px #000; /* borda preta */
  text-shadow: 0 0 5px #000, 0 0 10px #333;
  display: inline-block;
  padding: 0.2em 0.5em;
  border-radius: 0.3em;
  margin: 1rem 0 2rem;
}

/* Ícone de raio animado sutil */
.icon-lightning {
  width:48px;
  height:48px;
  fill:#FFFF00;
  filter: drop-shadow(0 0 5px #000);
  animation: flash 1.5s infinite alternate;
  vertical-align: middle;
  margin-right:0.5rem;
}
@keyframes flash {
  0% { filter: drop-shadow(0 0 5px #000); transform: scale(1); }
  50% { filter: drop-shadow(0 0 20px #FFFF00); transform: scale(1.1); }
  100% { filter: drop-shadow(0 0 5px #000); transform: scale(1); }
}

/* Botões neon amarelo */
div.stButton > button {
  background:transparent;
  border:2px solid #ffff00;
  color:#ffff00;
  font-weight:700;
  padding:0.5rem 1.5rem;
  border-radius:0.4rem;
  transition:all 0.3s ease-in-out;
  box-shadow:0 0 5px #ffff00,0 0 10px #ffff00,0 0 20px #ff0;
}
div.stButton > button:hover {
  background:#ffff00;
  color:#001122;
  box-shadow:0 0 15px #ff0,0 0 25px #ff0,0 0 35px #ff0;
  transform:scale(1.05);
}

/* Scrollbar dark */
::-webkit-scrollbar { width:10px; }
::-webkit-scrollbar-track { background:#001122; }
::-webkit-scrollbar-thumb { background:#ffff00; border-radius:10px; }

/* Inputs */
.stTextInput > label, .stFileUploader > label { color:#ffff00 !important; font-weight:700; }
.stTextInput > div > input { background-color:#001122 !important; color:#ffff00 !important; border:2px solid #ffff00 !important; }
</style>
""", unsafe_allow_html=True)

# --- Título ---
st.markdown("""
<div style="text-align:center;">
  <svg class="icon-lightning" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M13 2L3 14h7v8l10-12h-7z"/>
  </svg>
  <span class="title-thunder">FIELD MAP TOOLS V3.1 THUNDERSTORM</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Localização ---
location = streamlit_geolocation()
user_lat = location.get("latitude") if location else None
user_lon = location.get("longitude") if location else None

if user_lat is None or user_lon is None:
    st.info("🔒 Permita o acesso à sua localização para usar a aplicação.")
    st.stop()

try:
    user_lat = float(user_lat)
    user_lon = float(user_lon)
except (ValueError, TypeError):
    st.error("Coordenadas inválidas detectadas.")
    st.stop()

if not (-90 <= user_lat <= 90) or not (-180 <= user_lon <= 180):
    st.error("Coordenadas fora do intervalo permitido.")
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
                cod_raw = row.get("Cod Site", "SEM_CODIGO")
                cod = str(cod_raw).strip().upper()
                if not cod or cod.lower() == 'nan':
                    cod = "SEM_CODIGO"
                cod_clean = quote(cod)

                google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                waze_url = f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
                tsi_url = (
                    "https://tsi.digi.pt/web/ViewTicket?"
                    "start_ticket_id=&ticket_subtype=0&solution=0&client_id=-1"
                    "&source=0&affected_state=0&affected_city=&street_name="
                    "&street_id=0&street_nr=&showall=0"
                    f"&title={cod_clean}"
                    "&fttb_code=&search_tipfj=&status_n=on&status_o=on"
                    "&status_p=on&status_w=on&status_c=on&status_s=on"
                    "&status_v=on&status_f=on&status_u=on&status_r=on"
                    "&status_i=on&search=Vizualizeaza"
                )

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=1
                ).add_to(mapa)

                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f"<div style='font-size:12px; color:black; font-weight:bold;'>{cod}</div>"
                    ),
                    popup=folium.Popup(
                        f"<b>{cod}</b><br>"
                        f"<a href='{google_maps_url}' target='_blank'>Google Maps</a><br>"
                        f"<a href='{waze_url}' target='_blank'>Waze</a><br>"
                        f"<a href='{tsi_url}' target='_blank'>TSI</a>",
                        max_width=250
                    )
                ).add_to(mapa)

            folium_static(mapa, width=1600, height=600)

            # --- Exportar HTML ---
            mapa.save("/tmp/mapa_resultado.html")
            with open("/tmp/mapa_resultado.html", "r", encoding="utf-8") as f:
                mapa_html = f.read()
            st.download_button(
                label="⬇️ Descarregar Mapa HTML",
                data=mapa_html,
                file_name="mapa_com_pontos.html",
                mime="text/html"
            )

            # --- Tabela ---
            st.subheader("📊 Resultados da Pesquisa")
            st.dataframe(result_sorted.reset_index(drop=True))

            # --- Rotas ---
            waypoints = result_sorted[["Latitudine","Longitudine"]].values.tolist()
            google_maps_route = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/" + "/".join([f"{lat},{lon}" for lat, lon in waypoints])
            st.markdown("### 🧭 Navegar pelos sites ordenados por distância")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"[🗺️ Abrir rota no Google Maps]({google_maps_route})", unsafe_allow_html=True)
            with col2:
                if waypoints:
                    waze_url = f"https://waze.com/ul?ll={waypoints[0][0]},{waypoints[0][1]}&navigate=yes"
                    st.markdown(f"[🚘 Iniciar com Waze (1º destino)]({waze_url})", unsafe_allow_html=True)
