import os
import shutil

# Tipos de extensión a copiar
extensiones_video = ('.mp4', '.mov', '.avi', '.mkv', '.mxf')

def copiar_y_verificar(origen, destino, extension, socketio):
    if not os.path.exists(destino):
        os.makedirs(destino)
    
    medios = {}
    i = 0
    for root, dirs, files in os.walk(origen):
        for file in files:
            if file.lower().endswith(extensiones_video):
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
        porcentaje = int((key / total_medios) * 100)
        print(f'Copiado el {porcentaje}%, archivo {key} de {total_medios}')

        print(medio_path, medio)

        ruta_origen = medio_path
        ruta_destino = os.path.join(destino, medio)

        print(ruta_origen, ruta_destino)
        
        # Copiar archivo de medios y enviar actualización
        shutil.copy2(ruta_origen, ruta_destino)
        print(f'archivo {medio} copiado en {ruta_destino}')

        socketio.emit('progreso', {'porcentaje': porcentaje})
        socketio.sleep(0.1)

if __name__ == "__main__":
    # Prueba de funcionamiento
    copiar_y_verificar('J:\\BPAV\\CLPR', 'D:\\Prueba_copiado', '.mp4')
