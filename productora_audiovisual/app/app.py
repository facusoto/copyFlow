# Importar gevent y parchearlo
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from utils.config_handler import load_config
from utils.path_handler import crear_carpeta_destino
from utils.file_handler import encontrar_videos, copiar_videos, identificar_camara
from utils.thumbnail_handler import generar_y_enviar_thumbnails
from utils.device_handler import manejar_unidades
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///producciones.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
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


# Ruta para cambiar la configuracion del programa
@app.route('/configuracion', methods=["GET", "POST"])
def configuracion():
    return render_template('configuracion.html')


# Ruta para identificar los dispositivos conectados
@app.route('/identificar_dispositivos', methods=["GET", "POST"])
def identificar_dispositivos():
    total_unidades = manejar_unidades(config['ignore_partitions'])

    # Devolver la lista de unidades encontradas como respuesta JSON
    return jsonify({'unidades': total_unidades})


# Ruta para iniciar el copiado de archivos
@app.route('/device/media-discovery', methods=["POST"])
def discover_media():
    if request.method == "POST":
        print("Datos recibidos del formulario:", request.form)

        # Obtener el dispositivo seleccionado
        selected_device = request.form.get("selected-device")

        # Encontrar los medios
        medios_encontrados = encontrar_videos(selected_device)

        # Identificar el tipo de cámara
        tipo_camara = identificar_camara(selected_device)

        # Guardar datos en sesión
        session['selected_device'] = selected_device
        session['medios_encontrados'] = medios_encontrados 
        session['tipo_camara'] = tipo_camara

        # Verificar si se encontraron medios y generar thumbnails
        # generar_y_enviar_thumbnails(medios_encontrados, socketio)

        response = jsonify({
            'status': 'success',
            'message': 'Proceso iniciado',
            'data': [medios_encontrados, tipo_camara]
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

        # Devolver respuesta JSON
        return response


# Ruta para iniciar el copiado de archivos
@app.route('/start-copy', methods=["POST"])
def start_copy():
    datos = request.form

    # Validar campos requeridos (solo la primera vez)
    campos_requeridos = ["fecha", "titulo", "institucion"]
    for campo in campos_requeridos:
        if not datos.get(campo):
            return jsonify({"error": f"El campo {campo} es obligatorio"}), 400

    # Verificar si ya hay una producción en la sesión
    if not session.get('produccion_id'):
        # Guardar en la base de datos la primera vez
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
        produccion_id = nueva_produccion.id
        session['produccion_id'] = produccion_id  # Guardamos el ID para futuras copias

        print('Datos guardados en la base de datos')

        # Crear carpeta de destino usando los datos previos
        tipo_camara = session.get('tipo_camara', [])
        carpeta_destino = crear_carpeta_destino(
            config['home_directory'],
            tipo_camara,
            datos["fecha"],
            datos["institucion"],
            datos["titulo"]
        )
        session['carpeta_destino'] = carpeta_destino

    else:
        # Ya hay una sesión activa, usamos los datos anteriores
        carpeta_destino = session.get('carpeta_destino')
        if not carpeta_destino:
            return jsonify({"error": "No se encontró la carpeta de destino en sesión"}), 500

    # Recuperar los medios desde la sesión
    medios_encontrados = session.get('medios_encontrados', [])
    if not medios_encontrados:
        return jsonify({"error": "No hay medios para copiar"}), 400

    total_medios = int(len(medios_encontrados))

    # Iniciar copiado con actualización en tiempo real
    copiar_videos(medios_encontrados, total_medios, carpeta_destino, socketio)

    return jsonify({"message": "Proceso de copiado iniciado"}), 200


# Ruta para limpiar la sesión
@app.route('/clear-session', methods=["POST"])
def clear_session():
    session.clear()
    return jsonify({"message": "Sesión limpiada"}), 200


@socketio.on('connect')
def handle_connect():
    print("Un cliente se ha conectado")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)