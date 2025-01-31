import os
import psutil
import time
from utils.file_handler import copiar_y_verificar
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

            # consultar_datos()
            # copiar_y_verificar()

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

if __name__ == "__main__":
    manejar_unidades_nuevas()
