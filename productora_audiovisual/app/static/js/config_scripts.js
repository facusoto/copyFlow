// Funciones de Socket.IO
var socket = io('http://127.0.0.1:5000');

socket.on('connect', function () {
    console.log('✅ Conectado al servidor Socket.IO');
});

socket.on('connect_error', function (error) {
    console.error('❌ Error de conexión a Socket.IO:', error);
});

socket.on('disconnect', function (reason) {
    console.warn('⚠️ Desconectado de Socket.IO:', reason);
});

// Función para identificar dispositivos y agregar al contenedor
function identificarDispositivos() {
    fetch('/identificar_dispositivos', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log("Dispositivos identificados:", data.unidades);
            if (data.unidades) {
                agregarDispositivosAlContenedor(data.unidades);
            }
        })
        .catch(error => console.error("Error identificando dispositivos:", error));
}

// Identificar dispositivos al cargar la página
document.addEventListener("DOMContentLoaded", identificarDispositivos);

function agregarDispositivosAlContenedor(unidades) {
    let deviceContainer = document.getElementById("device-container");
    if (!deviceContainer) {
        console.error("No se encontró el contenedor de dispositivos.");
        return;
    }

    if (unidades.length == 0) {
        deviceContainer.innerHTML = '<p class="text-center">No se encontraron dispositivos.</p>';
        return;
    }

    // Obtener la lista de dispositivos ignorados
    fetch('/obtener_ignorados')
        .then(response => response.json())
        .then(ignorados => {
            // Limpiar el contenedor antes de agregar nuevos dispositivos
            deviceContainer.innerHTML = '';

            // Ordenar las unidades alfabéticamente por el nombre
            unidades.sort((a, b) => a.nombre.localeCompare(b.nombre));

            // Iterar sobre cada dispositivo encontrado y agregarlo al contenedor
            unidades.forEach((unidad) => {
                let checked = ignorados.includes(unidad.nombre) ? 'checked' : '';
                let deviceElement = `
                <div class="col w-25">
                    <div class="card">
                        <input type="checkbox" class="form-check-input device-checkbox" name="${unidad.nombre}" ${checked}>
                        <div class="card-body text-center external-device selectable-device">
                            <img src="${unidad.imagen}" alt="Dispositivo" class="external-hard-drive">
                            <p class="device-name">${unidad.nombre}</p>
                        </div>
                    </div>
                </div>
                `;
                deviceContainer.innerHTML += deviceElement;
            });
        })
        .catch(error => console.error("Error obteniendo dispositivos ignorados:", error));
}
