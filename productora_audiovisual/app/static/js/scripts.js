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

// Función para identificar dispositivos y agregar al contenedor
function identificarDispositivos() {
    fetch('/identificar_dispositivos', { method: 'POST' })
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

// Identificar nuevos dispositivos al clickear
document.getElementById('reload-partitions').addEventListener('click', identificarDispositivos);

// Escuchar el evento de actualización de unidades en tiempo real
socket.on('unidades', function(data) {
    console.log('Unidades encontradas (socket):', data.unidades);
    agregarDispositivosAlContenedor(data.unidades);
});

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

    // Limpiar el contenedor antes de agregar nuevos dispositivos
    deviceContainer.innerHTML = '';

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
        deviceContainer.innerHTML += deviceElement;
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
            document.getElementById('form-mask').classList.add('d-none');

        })
        .catch(error => console.error('Error en la solicitud:', error));
    }
}

// Volver al menú de selección de dispositivos
document.getElementById('back-to-devices').addEventListener('click', function(event) {
    // Eliminar los medios encontrados
    const mediaContainer = document.querySelector('.media-container .row');
    mediaContainer.innerHTML = '';

    // Cambiar los display de los contenedores
    document.getElementById('content-container').classList.add('d-none');
    document.getElementById('menu-container').classList.remove('d-none');
    document.getElementById('form-mask').classList.remove('d-none');
});

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
                <div class="card-body media-card text-center position-relative" id="media-${idCounter}">
                    <span class="fs-1 text-success" id="media-process-${idCounter}"></span>
                    <div class="indeterminate-progress-bar progress progress-striped active position-absolute bottom-0 left-0 d-none">
                        <div class="indeterminate-progress progress-bar" role="progressbar"></div>
                    </div>
                </div>
            </div>
            <p class="mb-0 fs-6 text-center text-body video-name">${fileName}</p>
        `;

        // Incrementar el id para la siguiente iteración
        idCounter++;

        mediaContainer.appendChild(mediaElement);
    });
}

// Seleccionamos el contenedor donde los media-cards serán agregados
const container = document.querySelector('.media-container');

// Escuchar el evento de hover en el contenedor y mostrar la barra de progreso
container.addEventListener('mouseenter', (event) => {
    if (event.target && event.target.classList.contains('media-card')) {
      let hoverTimeout;
  
      hoverTimeout = setTimeout(() => {
        // Buscar la barra de progreso existente
        const progressBar = event.target.querySelector('.indeterminate-progress-bar');
  
        // Verificar si la barra de progreso existe y quitar la clase 'd-none' para hacerla visible
        if (progressBar) {
          progressBar.classList.remove('d-none');
        }
      }, 1000); // Esperamos 1 segundo de hover
  
      event.target.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimeout);
      });
    }
  }, true);
  

// Escuchar la creacion de thumbnails y agregarlas al frontend
socket.on("frame", function (data) {
    console.log("Datos recibidos", data.frame);
    console.log("Frame recibido para el elemento:", data.frame[0]);
    let videoCard = document.getElementById(`media-${data.frame[0]}`);
    videoCard.style.backgroundImage = `url(${data.frame[1]})`;
});

// Agregar evento al botón con id "search-media"
document.getElementById('search-media').addEventListener('click', validateAndSearchMedia);

// Validar datos del formulario y copiar
document.getElementById("copiar-btn").addEventListener("click", function (event) {
    event.preventDefault(); // Evita que el formulario se envíe y la página se recargue

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
    let copyProgress = data.porcentaje[0]
    let mediaCardNumber = data.porcentaje[1];
    console.log("Progreso recibido:", copyProgress + "%");

    // Actualizar la barra de progreso
    let progressBar = document.getElementById("progress-bar");
    progressBar.style.width = copyProgress + "%";
    progressBar.textContent = copyProgress + "%";

    // Agregar el spinner de carga
    let mediaCardSelect = document.getElementById(`media-${mediaCardNumber}`);
    let spinner = mediaCardSelect.querySelector(".indeterminate-progress-bar");
    spinner.classList.remove('d-none');

    if (copyProgress >= 1) {
        let processElement = mediaCardSelect.querySelector(`#media-process-${mediaCardNumber}`);

        // Actualizar su contenido de texto para agregar el ✓
        if (processElement) {
            processElement.textContent = "✓";
        }

        let lastCard = document.getElementById(`media-${mediaCardNumber - 1}`);
        let lastSpinner = lastCard.querySelector(".indeterminate-progress-bar");
        lastSpinner.classList.add('d-none');
    }
    else if (copyProgress == 100) {
        mediaCardSelect.getElementById(`media-process-${mediaCardNumber}`).textContent = "✓";
        spinner.classList.add('d-none');
    }
});