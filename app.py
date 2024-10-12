from flask import Flask, render_template
import os
from analysis import cargar_datos_calidad_aire, analizar_calidad_aire, crear_mapa_interactivo

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