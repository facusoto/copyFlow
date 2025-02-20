from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from utils.path_handler import crear_carpeta_destino
from utils.file_handler import encontrar_videos, copiar_videos
from utils.thumbnail_handler import generar_y_enviar_thumbnails
from utils.device_handler import manejar_unidades_nuevas
import json

# Importar gevent y parchearlo
from gevent import monkey
monkey.patch_all()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///producciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Función para cargar configuración
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)
    
# Variable global para la configuración
config = load_config()

socketio = SocketIO(app)  # Inicializar SocketIO
db = SQLAlchemy(app)  # Inicializar SQLAlchemy

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
    unidades_detectadas = manejar_unidades_nuevas(config['ignore_partitions'])

    # Emitir la señal de dispositivos detectados al frontend
    socketio.emit('unidades', {'unidades': list(unidades_detectadas)})

    # Devolver la lista de unidades encontradas como respuesta JSON
    return jsonify({'unidades': list(unidades_detectadas)})


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
        # generar_y_enviar_thumbnails(medios_encontrados, socketio)

        response = jsonify({
            'status': 'success',
            'message': 'Proceso iniciado',
            'data': medios_encontrados  # Puedes incluir datos relevantes si es necesario
        })

        response.headers['Content-Type'] = 'application/json; charset=utf-8'

        # Devolver respuesta JSON
        return response


# Ruta para iniciar el copiado de archivos
@app.route('/copiar', methods=["POST"])
def copiar():
    datos = request.form

    # Validar que los campos requeridos estén completos
    campos_requeridos = ["fecha", "titulo", "institucion"]
    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"error": f"El campo {campo} es obligatorio"}), 400

    # Guardar en la base de datos
    nueva_produccion = Produccion(
        fecha=datos["fecha"],
        ubicacion=datos["ubicacion"],
        institucion=datos["institucion"],
        tipo_material=datos["tipo_material"],
        titulo=datos["titulo"],
        observaciones=datos["observaciones"]
    )
    db.session.add(nueva_produccion)
    db.session.commit()

    print('Datos guardados en la base de datos')

    # Crear carpeta de destino
    carpeta_destino = crear_carpeta_destino(
        config['home_directory'], datos["fecha"], datos["institucion"], datos["titulo"]
    )

    # Recuperar los medios desde la sesión
    medios_encontrados = session.get('medios_encontrados', [])
    total_medios = int(len(medios_encontrados))

    if not medios_encontrados:
        return jsonify({"error": "No hay medios para copiar"}), 400

    # Iniciar copiado con actualización en tiempo real
    copiar_videos(medios_encontrados, total_medios, carpeta_destino, socketio)

    return jsonify({"message": "Proceso de copiado iniciado"}), 200


@socketio.on('connect')
def handle_connect():
    print("Un cliente se ha conectado")


if __name__ == '__main__':
    socketio.run(app, debug=True)