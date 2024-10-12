import geopandas as gpd
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

def geocode_country(country_name, retries=3):
    geolocator = Nominatim(user_agent="brendabbrios@gmail.com", timeout=10)
    for attempt in range(retries):
        try:
            location = geolocator.geocode(country_name)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Error en el intento {attempt + 1}: {e}. Reintentando...")
            time.sleep(2)
    return None, None

def cargar_datos_calidad_aire(ruta_csv):
    datos = pd.read_csv(ruta_csv).head(20)

    datos['Latitude'] = None
    datos['Longitude'] = None

    for i, row in datos.iterrows():
        lat, lon = geocode_country(row['Country'])
        datos.at[i, 'Latitude'] = lat
        datos.at[i, 'Longitude'] = lon
        time.sleep(1)

    datos = datos.dropna(subset=['Latitude', 'Longitude'])

    gdf = gpd.GeoDataFrame(
        datos, geometry=gpd.points_from_xy(datos['Longitude'], datos['Latitude'])
    )
    
    return gdf

def analizar_calidad_aire(datos):
    ciudades_peor_calidad = datos.sort_values(by="AQI Value", ascending=False).head(10)
    return ciudades_peor_calidad

def crear_mapa_interactivo(datos, ciudades_peor_calidad):
    centro_mapa = [datos['Latitude'].mean(), datos['Longitude'].mean()]
    
    mapa = folium.Map(location=centro_mapa, zoom_start=5)

    for idx, row in ciudades_peor_calidad.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Country']}: AQI {row['AQI Value']}",
            icon=folium.Icon(color='red' if row['AQI Value'] > 100 else 'green')
        ).add_to(mapa)
    
    mapa.save("static/mapa_calidad_aire.html")

    return "Mapa generado en static/mapa_calidad_aire.html"

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar')
def analizar():
    ruta_csv = "C:/Users/Ximena/.kaggle/data_date.csv"
    datos = cargar_datos_calidad_aire(ruta_csv)
    ciudades_peor_calidad = analizar_calidad_aire(datos)
    crear_mapa_interactivo(datos, ciudades_peor_calidad)
    return render_template('mapa.html')

if __name__ == '__main__':
    app.run(debug=True)