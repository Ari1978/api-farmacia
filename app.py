import folium
print(folium.__version__)
import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# URL de la API gratuita de OpenStreetMap (Nominatim)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

PROVINCIAS = ["Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán"]
PARTIDOS = {
    "Buenos Aires": ["La Plata", "Mar del Plata", "Quilmes", "Morón", "Avellaneda", "Berazategui", "Escobar", "San Isidro", "Tigre", "Vicente López", "Lomas de Zamora", "Lanús", "San Miguel", "José C. Paz", "San Fernando", "San Martín", "Hurlingham", "Malvinas Argentinas", "Ezeiza", "Merlo", "Moreno", "Ituzaingó"],
    "Córdoba": ["Córdoba Capital", "Villa María", "Río Cuarto"],
    "Santa Fe": ["Rosario", "Santa Fe Capital", "Rafaela"],
    "Mendoza": ["Mendoza Capital", "San Rafael", "Godoy Cruz"],
    "Tucumán": ["San Miguel de Tucumán", "Yerba Buena", "Tafí Viejo"]
}

def obtener_coordenadas(provincia, partido):
    params = {
        "q": f"{partido}, {provincia}, Argentina",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "FarmaciasApp"})
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        lat = result.get("lat")
        lon = result.get("lon")
        return lat, lon
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
    if response.status_code == 200 and response.json():
        return response.json()
    return []

def mostrar_logo():
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Pharmacy_green_cross.svg/1200px-Pharmacy_green_cross.svg.png", width=100)

def mostrar_detalles_farmacia(farmacia):
    nombre = farmacia.get("display_name", "Desconocido")
    direccion = farmacia.get("address", {}).get("road", "Sin dirección")
    horas = farmacia.get("extratags", {}).get("opening_hours", "Sin horarios disponibles")
    lat = farmacia.get("lat", None)
    lon = farmacia.get("lon", None)
    
    if lat and lon:
        link_google_maps = f"https://www.google.com/maps?q={lat},{lon}"
        st.markdown(f"### {nombre}")
        st.markdown(f"**Dirección:** {direccion}")
        st.markdown(f"**Horario de apertura:** {horas}")
        st.markdown(f"[Abrir en Google Maps]({link_google_maps})")
    else:
        st.error("❌ La ubicación de la farmacia no está disponible.")

def main():
    st.set_page_config(page_title="Farmacias de Turno", page_icon="💊", layout="wide")
    mostrar_logo()
    st.title("🔍 Encuentra Farmacias de Turno Cercanas")
    
    col1, col2 = st.columns(2)
    with col1:
        provincia = st.selectbox("🌎 Selecciona una Provincia", PROVINCIAS)
    with col2:
        partido = st.selectbox("🏙️ Selecciona un Partido", PARTIDOS[provincia])
    
    if st.button("Buscar Farmacias", use_container_width=True):
        farmacias = obtener_farmacias(provincia, partido)
        
        if farmacias:
            lat, lon = obtener_coordenadas(provincia, partido)
            mapa = folium.Map(location=[float(lat), float(lon)], zoom_start=14, tiles='cartodbpositron')
            
            for farmacia in farmacias:
                nombre = farmacia.get("display_name", "Desconocido")
                lat_farmacia = farmacia.get("lat", None)
                lon_farmacia = farmacia.get("lon", None)
                
                if lat_farmacia and lon_farmacia:
                    folium.Marker(
                        [float(lat_farmacia), float(lon_farmacia)],
                        popup=f"<b>{nombre}</b>",
                        icon=folium.Icon(color="red", icon="plus")
                    ).add_to(mapa)
            
            st.subheader("📍 Mapa de Farmacias Cercanas")
            folium_static(mapa)
            
            st.subheader("🏥 Lista de Farmacias")
            for farmacia in farmacias:
                mostrar_detalles_farmacia(farmacia)
        else:
            st.error("❌ No se encontraron farmacias cercanas.")

if __name__ == "__main__":
    main()
