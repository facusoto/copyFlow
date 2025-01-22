import os
import shutil
import hashlib
from flask_socketio import SocketIO, emit

def calcular_hash(archivo, algoritmo='sha256'):
    hash_func = hashlib.new(algoritmo)
    with open(archivo, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def copiar_y_verificar(origen, destino, extension, algoritmo='sha256', socketio=None):
    if not os.path.exists(destino):
        os.makedirs(destino)
    
    medios = {}
    i = 0
    for root, dirs, files in os.walk(origen):
        for file in files:
            if file.lower().endswith(extension):
                i += 1
                medios[i] = [os.path.join(root, file), file]

    total_medios = len(medios)

    if total_medios == 0:
        print('No hay archivos para copiar')
        return

    print('Copiando medios')
    for key, value in medios.items():
        medio_path = value[0]
        medio = value[1]

        print(medio_path, medio)

        ruta_origen = medio_path
        ruta_destino = os.path.join(destino, medio)

        print(ruta_origen, ruta_destino)
        
        # Calcular hash antes de copiar
        hash_origen = calcular_hash(ruta_origen, algoritmo)
        
        # Copiar archivo de medios
        shutil.copy2(ruta_origen, ruta_destino)

        print(f'archivo {medio} copiado en {ruta_destino}')
        
        # Calcular hash después de copiar
        hash_destino = calcular_hash(ruta_destino, algoritmo)
        
        # Verificar integridad
        if hash_origen == hash_destino:
            print(f'Integridad verificada para: {medio}')
        else:
            print(f'Error de integridad en: {medio}')

        porcentaje = int((key / total_medios) * 100)
        socketio.emit('progreso', {'porcentaje': porcentaje})

if __name__ == "__main__":
    copiar_y_verificar('J:\\BPAV\\CLPR', 'D:\\Prueba_copiado', '.mp4')
