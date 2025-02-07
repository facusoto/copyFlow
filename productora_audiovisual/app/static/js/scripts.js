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

socket.on('progreso', function(data) {
    console.log('Progreso recibido:', data.porcentaje + '%');  // Agrega esto para debug
    $('#progress-bar').css('width', data.porcentaje + '%');
    $('#progress-bar').text(data.porcentaje + '%');
});

socket.on('frame', function(data) {
    console.log('Progreso recibido:', data.frame);
});

function iniciarCopia() {
    fetch('/iniciar_copia')
        .then(response => console.log('Copia iniciada:', response))
        .catch(error => console.error('Error iniciando copia:', error));
}