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

// Comienza el proceso de copia
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