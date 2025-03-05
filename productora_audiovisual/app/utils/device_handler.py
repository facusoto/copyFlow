import psutil
from flask import url_for

def manejar_unidades(unidades_ignoradas=None):
    """Obtiene las particiones conectadas y devuelve un diccionario con su estado de conexión e ignorado."""
    
    # Obtener todas las particiones conectadas
    unidades_detectadas = {part.device for part in psutil.disk_partitions()}
    unidades_ignoradas = set(unidades_ignoradas or [])
    
    # Crear diccionario con el estado de cada unidad
    resultado = {}
    for unidad in unidades_detectadas | unidades_ignoradas:
        resultado[unidad] = {
            'conectado': unidad in unidades_detectadas,
            'ignorado': unidad in unidades_ignoradas,
            'imagen': url_for('static', filename='img/external-hard-drive.png')
        }

    return resultado

if __name__ == "__main__":
    manejar_unidades()
