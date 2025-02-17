import os
import shutil

# Tipos de extensión a copiar
extensiones_video = ('.mp4', '.mov', '.avi', '.mkv', '.mxf')
medios = {}

def encontrar_videos(origen):
    i = 0
    for root, dirs, files in os.walk(origen):
        for file in files:
            if file.lower().endswith(extensiones_video) and not file.lower().startswith('.'):
                i += 1
                # Convertir la ruta a absoluta y reemplazar backslashes con slashes compatibles
                ruta_absoluta = os.path.abspath(os.path.join(root, file))
                ruta_ffmpeg = ruta_absoluta.replace("\\", "/")  # FFmpeg en Windows prefiere slashes

                medios[i] = [ruta_ffmpeg, file]

    return medios

def copiar_videos(lista_medios, total_medios, destino, socketio):
    # Proceso de copiado
    print('Copiando medios')
    for key, value in lista_medios.items():
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
    pass