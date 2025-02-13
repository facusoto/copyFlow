import psutil

def manejar_unidades_nuevas(unidades_ignoradas, socketio):
    total_unidades = set(part.device for part in psutil.disk_partitions())
    print(f"Unidades iniciales: {total_unidades}")

    for unidad in unidades_ignoradas:
        total_unidades.discard(unidad)  # Usa discard en lugar de remove para evitar errores
    
    print(f"Unidades finales: {total_unidades}")

    # Emitir los dispositivos detectados
    socketio.emit('unidades', {'unidades': list(total_unidades)})

    return total_unidades  # Retornar las unidades encontradas

if __name__ == "__main__":
    manejar_unidades_nuevas()
