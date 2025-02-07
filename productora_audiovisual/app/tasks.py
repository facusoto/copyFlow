import os
import multiprocessing
from utils.file_handler import encontrar_videos, copiar_videos
from utils.path_handler import crear_carpeta_destino
from utils.thumbnail_handler import generar_thumbnails_en_subproceso

def test_encontrar_videos(base_path, origen, destino, socketio):
    # Utilizar los videos que se encuentran en la lista
    lista_medios = encontrar_videos(origen)
    total_medios = len(lista_medios)

    if total_medios == 0:
        print('No hay archivos para copiar')
        return

    # Generar la carpeta de destino
    #! Datos de prueba, la idea es obtenerlos con sockets
    # destino = crear_carpeta_destino(base_path, "2021-06-30", "Bomberos", "Prueba")

    # Crear thumbnails y lanza el proceso en segundo plano
    proceso = multiprocessing.Process(target=generar_thumbnails_en_subproceso, args=(lista_medios, 'C:\\Prueba_thumbnails', socketio))
    proceso.start()

    # copiar_videos(lista_medios, total_medios, destino, socketio)

if __name__ == "__main__":
    base_path = 'C:'
    origen = 'D:'
    destino = 'C:\\Prueba_copiado'
    test_encontrar_videos(base_path, origen, destino, None)