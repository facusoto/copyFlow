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

// Identificar dispositivos al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    fetch('/identificar_dispositivos', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        console.log("Dispositivos identificados:", data.unidades);
        if (data.unidades) {
            agregarDispositivosAlContenedor(data.unidades);
        }
    })
    .catch(error => console.error("Error identificando dispositivos:", error));
});

// Escuchar el evento de actualización de unidades en tiempo real
socket.on('unidades', function(data) {
    console.log('Unidades encontradas (socket):', data.unidades);
    agregarDispositivosAlContenedor(data.unidades);
});

function agregarDispositivosAlContenedor(unidades) {
    let container = document.getElementById("device-container");
    if (!container) {
        console.error("No se encontró el contenedor de dispositivos.");
        return;
    }
    
    if (unidades.length == 0) {
        container.innerHTML = '<p class="text-center">No se encontraron dispositivos.</p>';
        return;
    }

    // Limpiar el contenedor antes de agregar nuevos dispositivos
    container.innerHTML = '';

    // Iterar sobre cada dispositivo encontrado y agregarlo al contenedor
    unidades.forEach((unidad) => {
        let deviceElement = `
        <div class="col w-25">
            <div class="card">
                <div class="card-body text-center external-device selectable-device">
                    <img src="${unidad.imagen}" alt="Dispositivo" class="external-hard-drive">
                    <p class="device-name">${unidad.nombre}</p>
                </div>
            </div>
        </div>
        `;
        container.innerHTML += deviceElement;
    });
}

// Delegación de eventos
document.getElementById('device-container').addEventListener('click', function(event) {
    // Verificar si el clic fue en un dispositivo seleccionable
    if (event.target.closest('.selectable-device')) {
        let device = event.target.closest('.selectable-device');
        
        // Quitar la clase 'selected' de todos los dispositivos
        document.querySelectorAll('.selectable-device').forEach(d => d.classList.remove('selected'));
        
        // Agregar la clase 'selected' al dispositivo clicado
        device.classList.add('selected');
        
        // Almacenar el nombre del dispositivo en el input oculto
        document.getElementById('selected-device').value = device.querySelector('.device-name').innerText;
    }
});

// Validar que se haya seleccionado un dispositivo y luego buscar los medios
function validateAndSearchMedia(event) {
    const selectedDevice = document.getElementById('selected-device').value;
    if (!selectedDevice) {
        event.preventDefault();
        alert('Por favor, selecciona un dispositivo antes de continuar.');
    } else {
        // Realizar la llamada al endpoint para buscar los medios
        fetch('/iniciar_dispositivo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ 'selected-device': selectedDevice })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data);
        
            // Si los datos están en un diccionario y no en una lista
            if (data.data && typeof data.data === 'object') {
                renderMediaList(Object.values(data.data));  // Convertir el diccionario a una lista
            }
            document.getElementById('menu-container').classList.add('d-none');
            document.getElementById('content-container').classList.remove('d-none');
        })
        .catch(error => console.error('Error en la solicitud:', error));
    }
}

// Renderizar la lista de medios encontrados
function renderMediaList(medios) {
    const mediaContainer = document.querySelector('.media-container .row');
    mediaContainer.innerHTML = '';

    // Definir un contador para los id
    let idCounter = 1;

    medios.forEach(media => {
        const fileName = media[1];
        const mediaElement = document.createElement('div');

        mediaElement.classList.add('col');
        mediaElement.innerHTML = `
            <div class="card">
                <div class="card-body text-center" id="media-${idCounter}">
                    <span class="fs-1 text-success" id="media-process-${idCounter}"></span>
                </div>
            </div>
            <p class="mb-0 fs-6 text-center text-body">${fileName}</p>
        `;

        // Incrementar el id para la siguiente iteración
        idCounter++;

        mediaContainer.appendChild(mediaElement);
    });
}

// Escuchar la creacion de thumbnails y agregarlas al frontend
socket.on("frame", function (data) {
    console.log("Datos recibidos", data.data);
    // console.log("Frame recibido para el elemento:", data.video_id);
    // let videoCard = document.getElementById(`media-${data.video_id}`);
    // videoCard.style.backgroundImage = `url(${data.imagen_base64})`;
});


// Agregar evento al botón con id "search-media"
document.getElementById('search-media').addEventListener('click', validateAndSearchMedia);

// Validar datos del formulario y copiar
document.getElementById("copiar-btn").addEventListener("click", function () {
    let form = document.getElementById("project-form");
    let formData = new FormData(form);

    // Validar campos obligatorios antes de enviar
    let requiredFields = ["fecha", "titulo", "institucion"];
    for (let field of requiredFields) {
        if (!form[field].value.trim()) {
            alert(`El campo ${field} es obligatorio.`);
            return;
        }
    }

    // Iniciar el proceso de copiado
    fetch("/copiar", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("Copia iniciada con éxito");
        }
    })
    .catch(error => console.error("Error:", error));
});

// Escuchar progreso y actualizar la barra
socket.on("progreso", function (data) {
    console.log("Progreso recibido:", data.porcentaje + "%");
    let progressBar = document.getElementById("progress-bar");
    progressBar.style.width = data.porcentaje + "%";
    progressBar.textContent = data.porcentaje + "%";
});
