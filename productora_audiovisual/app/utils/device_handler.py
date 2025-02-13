import psutil

def manejar_unidades_nuevas(unidades_ignoradas, socketio):
    total_unidades = set(part.device for part in psutil.disk_partitions())
    print(f"Unidades iniciales: {total_unidades}")

    for unidad in unidades_ignoradas:
        total_unidades.remove(unidad)
    
    print(f"Unidades finales: {total_unidades}")
    socketio.emit('unidades', {'unidades': total_unidades})

if __name__ == "__main__":
    manejar_unidades_nuevas()
