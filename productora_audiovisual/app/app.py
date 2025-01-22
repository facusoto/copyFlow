from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils.prueba_copiado import copiar_y_verificar
import threading
import time
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar_copia')
def iniciar_copia():
    origen = 'J:\\BPAV\\CLPR'
    destino = 'D:\\Prueba_copiado'
    extension = '.mp4'
    threading.Thread(target=copiar_y_verificar, args=(origen, destino, extension, 'sha256', socketio)).start()
    return 'Copia iniciada'

if __name__ == '__main__':
    socketio.run(app, debug=True)
