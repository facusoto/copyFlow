import os
import psutil
import time
from plyer import notification
import webbrowser

def manejar_unidades_nuevas():
    unidades_previas = set(part.device for part in psutil.disk_partitions())
    print(f"Unidades iniciales: {unidades_previas}")

    while True:
        time.sleep(5)  # Escanea cada 5 segundos
        unidades_actuales = set(part.device for part in psutil.disk_partitions())
        nuevas_unidades = unidades_actuales - unidades_previas

        if nuevas_unidades:
            for unidad in nuevas_unidades:
                print(f"Nueva unidad detectada: {unidad}")
                notificar_dispositivo_detectado()
                videos = analizar_dispositivo(unidad)

                # Preguntar los datos y almacenar los videos
                if videos:
                    print("Videos encontrados:")
                    for video in videos:
                        print(video)
                
                    consultar_datos()
                    copiar_videos()
                else:
                    print("No se encontraron videos en esta unidad.")

            unidades_previas = unidades_actuales

# Función para notificar de un nuevo dispositivo
def notificar_dispositivo_detectado():
    app_url = "http://127.0.0.1:5000"
    notification.notify(
        title="Nuevo dispositivo detectado",
        message="Haz clic aquí para gestionar los datos.",
        app_name="Productora Audiovisual",
        timeout=10,
    )
    webbrowser.open(app_url)

# Función para analizar el contenido del dispositivo
def analizar_dispositivo(ruta):
    videos = []
    extensiones_video = ['.mp4', '.mov', '.avi', '.mkv', '.mxf']

    for root, dirs, files in os.walk(ruta):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensiones_video):
                videos.append(os.path.join(root, file))

    return videos

# Función para consultar datos de guardado
def consultar_datos():
    pass

# Función para realiar la copia
def copiar_videos():
    pass

if __name__ == "__main__":
    manejar_unidades_nuevas()
