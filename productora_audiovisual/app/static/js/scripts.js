// 
// Mostrar los medios encontrados
function showContent() {
    document.getElementById('menu-container').classList.add('d-none');
    document.getElementById('content-container').classList.remove('d-none');
}

// Funciones de Socket.IO
var socket = io('http://127.0.0.1:5000');

socket.on('connect', function() {
    console.log('✅ Conectado al servidor Socket.IO');
});

socket.on('connect_error', function(error) {
    console.error('❌ Error de conexión a Socket.IO:', error);
});

socket.on('disconnect', function(reason) {
    console.warn('⚠️ Desconectado de Socket.IO:', reason);
});

// Escuchar eventos de generacion de frames
socket.on('frame', function(data) {
    console.log('Progreso recibido:', data.frame);
});

// 
// Comienza la busqueda de medios
// document.getElementById("seach-media").addEventListener("click", function() {
//     let formData = new FormData(document.getElementById("formulario-media"));
    
//     fetch("/iniciar_dispositivo", {
//         method: "POST",
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => alert(data.message))  // Mostrar mensaje de éxito o error
//     .catch(error => console.error("Error:", error));
// });

// Indica el dispositivo seleccionado
document.querySelectorAll('.selectable-device').forEach(device => {
    device.addEventListener('click', function() {
        document.querySelectorAll('.selectable-device').forEach(d => d.classList.remove('selected'));
        this.classList.add('selected');

        // Almacenar el nombre del dispositivo en el input oculto
        document.getElementById('selected-device').value = this.querySelector('.device-name').innerText;
    });
});

// Validar que se haya seleccionado un dispositivo
document.getElementById('device-form').addEventListener('submit', function(event) {
    if (!document.getElementById('selected-device').value) {
        event.preventDefault();
        alert('Por favor, selecciona un dispositivo antes de continuar.');
    }
});

// 
// Comenzar el proceso de copia
document.getElementById("copiar-btn").addEventListener("click", function() {
    let formData = new FormData(document.getElementById("formulario"));
    
    fetch("/copiar", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => alert(data.message))  // Mostrar mensaje de éxito o error
    .catch(error => console.error("Error:", error));
});

// Escuchar eventos de progreso de copiado
socket.on('progreso', function(data) {
    console.log('Progreso recibido:', data.porcentaje + '%');  // Agrega esto para debug
    $('#progress-bar').css('width', data.porcentaje + '%');
    $('#progress-bar').text(data.porcentaje + '%');
});

// Identificar dispositivos al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    // Llamar a la ruta Flask para identificar dispositivos al cargar la página
    fetch('/identificar_dispositivos', { method: 'POST' })
        .then(response => response.text())
        .then(data => {
            console.log("Dispositivos identificados:", data);
        })
        .catch(error => console.error("Error identificando dispositivos:", error));
});

// Agregar dispositivos encontrados al contenedor
socket.on('unidades', function(data) {
    console.log('Unidades encontradas:', data.unidades);

    // Obtener el contenedor donde se agregarán los dispositivos
    let container = document.getElementById("device-container");
    if (!container) {
        console.error("No se encontró el contenedor de dispositivos.");
        return;
    }

    if (data.unidades.length == 0) {
        container.innerHTML = '<p class="text-center">No se encontraron dispositivos.</p>';
        return;
    }

    // Limpiar el contenedor antes de agregar nuevos dispositivos
    container.innerHTML = '';

    // Iterar sobre cada dispositivo encontrado y agregarlo al contenedor
    data.unidades.forEach((unidad, index) => {
        let deviceElement = `
            <div class="col w-25">
                <div class="card">
                    <div class="card-body text-center external-device selectable-device">
                        <img src="external-hard-drive.png" alt="Dispositivo" class="external-hard-drive">
                        <p class="device-name">Dispositivo ${index + 1}: ${unidad}</p>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += deviceElement;
    });
});
