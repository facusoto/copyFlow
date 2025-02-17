import os
import subprocess
import multiprocessing
import base64

ffmpeg_path = os.path.join(os.path.dirname(os.getcwd()), 'app', 'bin', 'ffmpeg', 'ffmpeg.exe')

def extraer_primer_frame(video_id, video_path, socketio=None):
    """Extrae el primer frame de un video y lo devuelve como base64."""
    print(ffmpeg_path)
    
    # Usamos pipe para obtener la imagen directamente en memoria, sin guardar en disco
    comando = [
        ffmpeg_path,
        "-i", video_path,
        "-vf", "select=eq(n\\,0)",  # Selecciona el primer frame
        "-s", "320x180",  # Resolución de la imagen
        "-q:v", "2",  # Calidad de la imagen
        "-frames:v", "1",
        "pipe:1"  # Salida por pipe
    ]
    
    # Ejecutamos el comando y obtenemos la salida
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Convertimos la imagen en bytes a base64
    imagen_base64 = base64.b64encode(resultado.stdout).decode('utf-8')
    
    if socketio:
        socketio.emit('frame', {'frame': [video_id, imagen_base64]})
        socketio.sleep(0.1)

def generar_thumbnails(videos, socketio):
    """Genera thumbnails y los envía como base64."""
    for key, value in videos.items():
        extraer_primer_frame(key, value[0], socketio)

def generar_thumbnails_en_subproceso(videos, socketio):
    """Ejecuta la generación de thumbnails en un proceso separado (NO bloqueante)."""
    proceso = multiprocessing.Process(target=generar_thumbnails, args=(videos,socketio))
    proceso.start()
