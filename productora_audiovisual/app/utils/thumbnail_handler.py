import subprocess
import os

ffmpeg_path = r"C:\Users\Usuario\Desktop\copyFlow\productora_audiovisual\app\utils\ffmpeg\ffmpeg.exe"

def extraer_primer_frame(video_path, output_dir, video_name, socketio=None):
    """Extrae el primer frame de un video y lo guarda como imagen."""
    output_path = os.path.join(output_dir, f"{video_name}_frame.jpg")
    
    comando = [
        ffmpeg_path,
        "-i", video_path,
        "-vf", "select=eq(n\\,0)",  # Selecciona el primer frame
        "-q:v", "2",  # Calidad de la imagen
        "-frames:v", "1",
        output_path
    ]
    
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Espera a que termine
    socketio.emit('frame', {'frame': f"Extracción hecha para {video_name}!"})
    socketio.sleep(0.1)

def generar_thumbnails_en_subproceso(videos, output_dir):
    """Ejecuta la generación de thumbnails en un proceso separado."""
    os.makedirs(output_dir, exist_ok=True)

    for key, value in videos.items():
        extraer_primer_frame(value[0], output_dir, f"{value[1]}_thumb")
