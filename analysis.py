import pandas as pd
import folium
from branca.element import Template, MacroElement
import os
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from folium.plugins import MarkerCluster

CACHE_FILE = "uploads/coordinates_cache.csv"

def cargar_cache_coordenadas():
    if os.path.exists(CACHE_FILE):
        try:
            cache = pd.read_csv(CACHE_FILE)
            if cache.empty:
                return pd.DataFrame(columns=["Country", "Latitude", "Longitude"])
            return cache
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["Country", "Latitude", "Longitude"])
    else:
        return pd.DataFrame(columns=["Country", "Latitude", "Longitude"])

def guardar_cache_coordenadas(cache):
    cache.to_csv(CACHE_FILE, index=False)

def geocode_country(country_name):
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    try:
        location = geolocator.geocode(country_name)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None, None
    return None, None

def cargar_datos_calidad_aire(ruta_csv, limite=40):
    """Carga los datos de calidad del aire y los agrupa por país."""
    # Cargar el archivo CSV original
    datos = pd.read_csv(ruta_csv)

    # Agrupar por país y calcular el AQI promedio
    datos = datos.groupby("Country", as_index=False).agg({
        "Status": "first",  # Mantener el primer estado
        "AQI Value": "mean"  # Calcular el promedio del AQI
    })

    # Limitar a un número específico de filas
    if len(datos) > limite:
        datos = datos.sample(n=limite, random_state=42)  # Selección aleatoria de filas

    # Cargar la caché de coordenadas
    cache = cargar_cache_coordenadas()

    # Añadir coordenadas para cada país
    for i, row in datos.iterrows():
        if row["Country"] not in cache["Country"].values:
            lat, lon = geocode_country(row["Country"])
            cache = pd.concat([cache, pd.DataFrame({"Country": [row["Country"]], "Latitude": [lat], "Longitude": [lon]})], ignore_index=True)
            time.sleep(0.5)

    # Guardar la caché actualizada
    guardar_cache_coordenadas(cache)

    # Unir los datos con las coordenadas
    datos = datos.merge(cache, on="Country", how="left")
    datos = datos.dropna(subset=["Latitude", "Longitude"])  # Eliminar filas sin coordenadas
    return datos

def crear_mapa_interactivo(datos):
    # Calcular el centro del mapa
    centro_mapa = [datos["Latitude"].mean(), datos["Longitude"].mean()]
    mapa = folium.Map(location=centro_mapa, zoom_start=2, tiles="CartoDB positron")

    # Agrupar marcadores con MarkerCluster
    marker_cluster = MarkerCluster().add_to(mapa)

    for idx, row in datos.iterrows():
        color = "red" if row["AQI Value"] > 100 else "green"
        popup_content = f"""
        <b>País:</b> {row['Country']}<br>
        <b>AQI Promedio:</b> {row['AQI Value']:.2f}<br>
        <b>Estado:</b> {row['Status']}
        """
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color),
        ).add_to(marker_cluster)

    # Añadir leyenda
    legend_html = """
    <div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 200px;
    background-color: white;
    z-index: 1000;
    padding: 10px;
    border: 2px solid grey;
    border-radius: 5px;">
    <h4>Colores del AQI</h4>
    <p style="margin: 0;"><i style="background:green; width:20px; height:20px; display:inline-block;"></i> AQI <= 100 (Bueno)</p>
    <p style="margin: 0;"><i style="background:red; width:20px; height:20px; display:inline-block;"></i> AQI > 100 (No saludable)</p>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legend_html))
    mapa.save("static/mapa_calidad_aire.html")
