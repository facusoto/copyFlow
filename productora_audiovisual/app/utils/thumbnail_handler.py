import os
import subprocess
import multiprocessing
import base64

ffmpeg_path = os.path.join(os.path.dirname(os.getcwd()), 'app', 'bin', 'ffmpeg', 'ffmpeg.exe')

def extraer_primer_frame(video_id, video_path, queue):
    """Extrae el primer frame de un video y lo coloca en una cola."""
    print("path + id", video_path, video_id)

    comando = [
        ffmpeg_path,
        "-i", video_path,
        "-vf", "select=eq(n\\,0)",  # Seleccionar el primer fotograma
        "-s", "320x180",            # Resolución de la imagen
        "-q:v", "10",               # Calidad más baja (más rápido)
        "-frames:v", "1",           # Solo un fotograma
        "-f", "image2pipe",         # Usar un formato de salida adecuado
        "-an",                      # Desactivar audio
        "-vsync", "0",              # Desactivar sincronización de fotogramas
        "-"                         # Salida estándar, para leer el archivo directamente
    ]
    
    # Usa Popen para no bloquear el hilo principal
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    
    # Lee la salida de manera no bloqueante
    stdout, stderr = proceso.communicate()
    
    if stderr:
        print(f"Error en ffmpeg: {stderr.decode('utf-8')}")
    
    imagen_base64 = base64.b64encode(stdout).decode('utf-8')
    imagen_base64_html = f"data:image/png;base64,{imagen_base64}"
    
    # Coloca los datos en la cola para que el hilo principal los procese
    queue.put((video_id, imagen_base64_html))

def generar_thumbnails(videos, queue):
    """Genera thumbnails y los coloca en una cola."""
    for key, value in videos.items():
        extraer_primer_frame(key, value[0], queue)

def generar_thumbnails_en_subproceso(videos, queue):
    """Ejecuta la generación de thumbnails en un proceso separado (NO bloqueante)."""
    proceso = multiprocessing.Process(target=generar_thumbnails, args=(videos, queue))
    proceso.start()

def manejar_socketio(queue, socketio):
    """Maneja la cola y emite eventos a través de SocketIO."""
    while True:
        if not queue.empty():
            video_id, imagen_base64 = queue.get()
            socketio.emit('frame', {'frame': [video_id, imagen_base64]})
            socketio.sleep(0.1)

def generar_y_enviar_thumbnails(videos, socketio):
    """Genera thumbnails de videos en un proceso separado y los envía por SocketIO."""
    # Crear la cola de comunicación entre subprocesos y el hilo principal
    queue = multiprocessing.Queue()

    # Iniciar el manejo de eventos de SocketIO en un hilo de fondo
    socketio.start_background_task(manejar_socketio, queue, socketio)

    # Iniciar el subproceso para generar thumbnails
    generar_thumbnails_en_subproceso(videos, queue)
