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

// Obtener los dispositivos desde configuración y dividirlos en conectados/desconectados
function agregarDispositivosAlContenedor() {
    let deviceContainer = document.getElementById("device-container");
    if (!deviceContainer) {
        console.error("No se encontró el contenedor de dispositivos.");
        return;
    }

    let connectedDevices = deviceContainer.querySelector('.connected-devices');
    let disconnectedDevices = deviceContainer.querySelector('.disconnected-devices');

    if (!connectedDevices || !disconnectedDevices) {
        console.error("No se encontraron las secciones para dispositivos.");
        return;
    }

    // Limpiar contenido previo
    connectedDevices.innerHTML = "";
    disconnectedDevices.innerHTML = "";

    // Obtener la lista de dispositivos desde el backend
    fetch('/identificar_dispositivos')
        .then(response => response.json())
        .then(data => {
            const dispositivos = data.unidades;
            
            Object.entries(dispositivos).forEach(([unidad, info]) => {
                let elemento = generarElementoDispositivo({
                    nombre: unidad,
                    imagen: info.imagen,
                    check: info.ignorado ? "checked" : ""
                });
                
                if (info.conectado) {
                    connectedDevices.innerHTML += elemento;
                } else {
                    disconnectedDevices.innerHTML += elemento;
                }
            });
        })
        .catch(error => console.error("Error obteniendo dispositivos:", error));
}

// Función para generar el HTML de un dispositivo
function generarElementoDispositivo(dispositivo) {
    return `
    <div class="col w-25">
        <div class="card">
            <input type="checkbox" class="form-check-input device-checkbox" name="${dispositivo.nombre}" ${dispositivo.check}>
            <div class="card-body text-center external-device selectable-device">
                <img src="${dispositivo.imagen}" alt="Dispositivo" class="external-hard-drive">
                <p class="device-name">${dispositivo.nombre}</p>
            </div>
        </div>
    </div>`;
}

// Llamar a la función para agregar los dispositivos al contenedor
document.addEventListener("DOMContentLoaded", agregarDispositivosAlContenedor);

// Configurar una nueva cámara
let folderArray = [];

function addFolder() {
    const folderInput = document.getElementById("addFolderInput");
    const folderName = folderInput.value.trim();

    if (folderName && !folderArray.includes(folderName)) {
        folderArray.push(folderName);
        
        const listItem = document.createElement("li");
        listItem.className = "list-group-item d-flex justify-content-between align-items-center";
        listItem.innerHTML = `${folderName} 
            <button class="btn btn-danger btn-sm" onclick="removeFolder('${folderName}')">Eliminar</button>`;

        document.getElementById("folderList").appendChild(listItem);
        folderInput.value = "";
    }
}

function removeFolder(folderName) {
    folderArray = folderArray.filter(folder => folder !== folderName);
    renderFolderList();
}

function renderFolderList() {
    const list = document.getElementById("folderList");
    list.innerHTML = "";
    folderArray.forEach(folder => {
        const listItem = document.createElement("li");
        listItem.className = "list-group-item d-flex justify-content-between align-items-center";
        listItem.innerHTML = `${folder} 
            <button class="btn btn-danger btn-sm" onclick="removeFolder('${folder}')">Eliminar</button>`;
        list.appendChild(listItem);
    });
}

function saveSet() {
    const setName = document.getElementById("setName").value.trim();
    if (setName && folderArray.length > 0) {
        const result = { [setName]: folderArray };
        document.getElementById("output").textContent = JSON.stringify(result, null, 4);
        folderArray = [];
        document.getElementById("setName").value = "";
        renderFolderList();
    } else {
        alert("Por favor ingresa un nombre y al menos una carpeta.");
    }
}