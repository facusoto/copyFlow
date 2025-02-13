from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from utils.path_handler import crear_carpeta_destino
from utils.file_handler import encontrar_videos, copiar_videos
from utils.thumbnail_handler import generar_thumbnails_en_subproceso
from utils.device_handler import manejar_unidades_nuevas
import json

# Importar gevent y parchearlo
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///producciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)  # Inicializar SocketIO
db = SQLAlchemy(app)  # Inicializar SQLAlchemy

# Función para cargar configuración
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
# Variable global para la configuración
config = load_config()

# Definir el modelo de la base de datos
class Produccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    institucion = db.Column(db.String(100), nullable=False)
    tipo_material = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    observaciones = db.Column(db.String(100), nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()


# Ruta para manejar el formulario
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


# Ruta para identificar los dispositivos
@app.route('/identificar_dispositivos', methods=["POST"])
def identificar_dispositivos():
    # Encontrar las unidades nuevas
    session['unidades'] = manejar_unidades_nuevas(config['ignore_devices'], socketio)

    return "Unidades identificadas"


# Ruta para iniciar el copiado de archivos
@app.route('/iniciar_dispositivo', methods=["POST"])
def iniciar_dispositivo():
    if request.method == "POST":
        print("Datos recibidos del formulario:", request.form)

        # Obtener el dispositivo seleccionado
        selected_device = request.form.get("selected-device")
        medios_encontrados = encontrar_videos(selected_device)

        # Verificar si se encontraron medios y generar thumbnails
        session['medios_encontrados'] = medios_encontrados  # Guardar en sesión
        generar_thumbnails_en_subproceso(medios_encontrados, config['default_thumbnail_directory'])

        return "Proceso iniciado"


# Ruta para iniciar el copiado de archivos
@app.route('/copiar', methods=["POST"])
def copiar():
    if request.method == "POST":
        print("Datos recibidos del formulario:", request.form)  # Depuración

        fecha = request.form.get("fecha")
        ubicacion = request.form.get("ubicacion")
        institucion = request.form.get("institucion")
        tipo_material = request.form.get("tipo_material")
        titulo = request.form.get("titulo")
        observaciones = request.form.get("observaciones")

        # Verificación simple de datos
        if fecha and titulo:
            nueva_produccion = Produccion(
                fecha=fecha,
                ubicacion=ubicacion,
                institucion=institucion,
                tipo_material=tipo_material,
                titulo=titulo,
                observaciones=observaciones
            )
            db.session.add(nueva_produccion)
            db.session.commit()

            # Crear carpeta de destino
            carpeta_destino = crear_carpeta_destino(config['home_directory'],fecha, institucion, titulo)

            # Recuperar los videos desde la sesión del usuario
            medios_encontrados = session.get('medios_encontrados', {})
            copiar_videos(medios_encontrados, len(medios_encontrados), carpeta_destino, socketio)

            print("Datos guardados correctamente.")
            return redirect(url_for("index"))


@socketio.on('connect')
def handle_connect():
    print("Un cliente se ha conectado")


if __name__ == '__main__':
    socketio.run(app, debug=True)
