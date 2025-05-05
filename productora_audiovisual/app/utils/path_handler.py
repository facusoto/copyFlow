import os
from datetime import datetime

def crear_carpeta_destino(base_path, tipo_camara, fecha, institucion, titulo):
    """
    Crea la estructura de carpetas según los datos ingresados en el formulario.
    """
    # Convertir la fecha a formato adecuado (YYYY-MM-DD)
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
    año = fecha_obj.strftime("%Y")
    mes = fecha_obj.strftime("%m")
    mes_nombre = [None, "Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][int(mes)]

    # Construir la ruta
    carpeta_destino = os.path.join(base_path, "Gobierno_CABA", institucion, año, f"{mes.zfill(2)} - {mes_nombre}", f"{fecha} - {titulo}", tipo_camara)

    # Crear la carpeta si no existe
    os.makedirs(carpeta_destino, exist_ok=True)

    return carpeta_destino
