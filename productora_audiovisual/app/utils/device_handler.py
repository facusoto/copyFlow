import psutil
from flask import url_for

def manejar_unidades_nuevas(unidades_ignoradas):
    total_unidades = set(part.device for part in psutil.disk_partitions())
    print(f"Unidades iniciales: {total_unidades}")

    if unidades_ignoradas is not None:
        try:
            for unidad in unidades_ignoradas:
                total_unidades.discard(unidad)
        except TypeError:
            # Si unidades_ignoradas no es iterable, se mantiene el conjunto original
            pass # No es necesario hacer nada, ya que total_unidades no se modificó
    
    print(f"Unidades finales: {total_unidades}")

    # Generar el URL de la imagen estática solo una vez
    imagen_comun = url_for('static', filename='img/external-hard-drive.png')

    # Crear la lista de unidades con la imagen correspondiente
    unidades_con_imagenes = [{'nombre': unidad, 'imagen': imagen_comun} for unidad in total_unidades]

    return unidades_con_imagenes  # Retornar las unidades encontradas

if __name__ == "__main__":
    manejar_unidades_nuevas(None)
