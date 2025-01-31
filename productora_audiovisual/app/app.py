from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils.file_handler import copiar_y_verificar
import threading
from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('barra_copia.html')

@app.route('/iniciar_copia')
def iniciar_copia():
    origen = 'F:\\BPAV\\CLPR'
    destino = 'E:\\Prueba_copiado'
    extension = '.mp4'
    threading.Thread(target=copiar_y_verificar, args=(origen, destino, extension, socketio)).start()
    return 'Copia iniciada'

@socketio.on('connect')
def handle_connect():
    print("Un cliente se ha conectado")

if __name__ == '__main__':
    socketio.run(app, debug=True)
