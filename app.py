from flask import Flask, render_template
from analysis import cargar_datos_calidad_aire, crear_mapa_interactivo

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar')
def analizar():
    ruta_csv = "uploads/data_date.csv"  # Ruta del archivo CSV
    datos = cargar_datos_calidad_aire(ruta_csv)
    crear_mapa_interactivo(datos)
    return render_template('mapa.html')

if __name__ == '__main__':
    app.run(debug=True)
