import subprocess
import json
import os

ffmpeg_path = r"C:\Users\Usuario\Desktop\copyFlow\productora_audiovisual\app\utils\ffmpeg\ffmpeg.exe"
ffprobe_path = r"C:\Users\Usuario\Desktop\copyFlow\productora_audiovisual\app\utils\ffmpeg\ffprobe.exe"

def get_video_duration(video_path):
    """
    Obtiene la duración del video en segundos utilizando ffprobe.
    """
    cmd = [
        ffprobe_path, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration", "-of", "json", video_path
    ]
    print(cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    return duration

def generar_sprite(video_path, output_dir, video_name, socketio=None, tile_cols=5, tile_rows=3, scale_width=100):
    """
    Genera un sprite sheet a partir de un video extrayendo un número fijo de frames equidistantes.
    
    Parámetros:
      - video_path: ruta del video de entrada.
      - output_dir: ruta de salida para el sprite.
      - tile_cols: número de columnas en el sprite.
      - tile_rows: número de filas en el sprite.
      - scale_width: ancho a redimensionar cada frame (manteniendo la relación de aspecto).
    """
    sprite_path = f"{output_dir}/{video_name}_sprite.jpg"
    print(sprite_path)
    num_frames = tile_cols * tile_rows  # Total de frames deseados
    duration = get_video_duration(video_path)
    
    # Calcular frames por segundo para extraer 'num_frames' en toda la duración
    fps = num_frames / duration
    
    # Construir el filtro de video para FFmpeg
    filtro = f"fps={fps},scale={scale_width}:-1,tile={tile_cols}x{tile_rows}"

    comando = [
        ffmpeg_path,
        "-hwaccel", "auto",                # Usa aceleración de hardware (detecta la mejor opción)
        "-hwaccel_output_format", "nv12",  # Si tenés una GPU NVIDIA, forzalo a usar CUDA (opcional)
        "-probesize", "5000000",           # Aumenta la cantidad de datos analizados al principio (10MB)
        "-analyzeduration", "5000000",     # Aumenta la duración de análisis
        "-i", video_path,
        "-vf", filtro,
        "-q:v", "10",                      # Calidad de salida (ajustala según necesidad)
        "-frames:v", "1",
        "-preset", "fast",                 # Usa la configuración más rápida de codificación
        sprite_path
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"Sprite generado exitosamente en: {sprite_path}")
        # socketio.emit("nueva_imagen", {"video": video_path, "ruta": f"/static/{sprite_path}"})

    except subprocess.CalledProcessError as e:
        print("Error al generar el sprite:", e)

# Ejemplo de uso
if __name__ == "__main__":
    video_file = "video.mp4"      # Ruta del video de origen
    output_dir = "sprite.jpg"    # Ruta de salida para el sprite
    generar_sprite(video_file, output_dir)
