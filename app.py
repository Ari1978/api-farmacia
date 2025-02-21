import folium
print(folium.__version__)
import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

# URL de la API gratuita de OpenStreetMap (Nominatim)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def obtener_coordenadas(provincia, partido):
    params = {
        "q": f"{partido}, {provincia}, Argentina",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "FarmaciasApp"})
    if response.status_code == 200 and response.json():
        return response.json()[0]["lat"], response.json()[0]["lon"]
    return None, None

def obtener_farmacias(provincia, partido):
    lat, lon = obtener_coordenadas(provincia, partido)
    if not lat or not lon:
        return []
    params = {
        "q": "pharmacy",
        "format": "json",
        "lat": lat,
        "lon": lon,
        "addressdetails": 1,
        "extratags": 1,
        "limit": 10
    }
    response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "FarmaciasApp"})
    if response.status_code == 200:
        return response.json()
    return []

def main():
    st.title("Farmacias de Turno Cercanas")
    
    # Entrada del usuario (Provincia y Partido)
    provincia = st.text_input("Provincia", value="Buenos Aires")
    partido = st.text_input("Partido", value="La Plata")
    
    if st.button("Buscar Farmacias"):
        farmacias = obtener_farmacias(provincia, partido)
        
        if farmacias:
            lat, lon = obtener_coordenadas(provincia, partido)
            mapa = folium.Map(location=[float(lat), float(lon)], zoom_start=14)
            
            for farmacia in farmacias:
                nombre = farmacia.get("display_name", "Desconocido")
                lat_farmacia = farmacia["lat"]
                lon_farmacia = farmacia["lon"]
                folium.Marker(
                    [float(lat_farmacia), float(lon_farmacia)],
                    popup=nombre,
                    icon=folium.Icon(color="blue", icon="plus")
                ).add_to(mapa)
            
            st.subheader("Mapa de farmacias cercanas")
            folium_static(mapa)
            
            df = pd.DataFrame([{ "Nombre": f["display_name"] } for f in farmacias])
            st.table(df)
        else:
            st.error("No se encontraron farmacias cercanas.")

if __name__ == "__main__":
    main()
