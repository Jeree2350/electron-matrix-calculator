const { app, BrowserWindow, Menu, shell, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess;

function createWindow() {
    // Crear la ventana principal
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        icon: path.join(__dirname, 'assets', 'icon.png'), // Opcional: icono de la app
        titleBarStyle: 'default',
        show: false // No mostrar hasta que esté lista
    });

    // Cargar el archivo HTML
    mainWindow.loadFile('index.html');

    // Mostrar la ventana cuando esté lista
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        
        // Abrir DevTools en modo desarrollo
        if (isDev) {
            mainWindow.webContents.openDevTools();
        }
    });

    // Manejar el cierre de la ventana
    mainWindow.on('closed', () => {
        mainWindow = null;
        // Cerrar el proceso de Python
        if (pythonProcess) {
            pythonProcess.kill();
        }
    });

    // Prevenir navegación a URLs externas
    mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        
        if (parsedUrl.origin !== 'http://localhost:5000') {
            event.preventDefault();
        }
    });

    // Abrir enlaces externos en el navegador predeterminado
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });
}

function startPythonBackend() {
    return new Promise((resolve, reject) => {
        let pythonExec;

        // Diferenciar desarrollo y producción
        if (isDev) {
            // Desarrollo: backend en la carpeta ../backend/dist
            pythonExec = path.join(__dirname, '..', 'backend', 'dist', process.platform === 'win32' ? 'app.exe' : 'app');
        } else {
            // Producción: backend dentro de resources/backend
            pythonExec = path.join(process.resourcesPath, 'backend', process.platform === 'win32' ? 'app.exe' : 'app');
        }

        console.log('Ejecutable Python:', pythonExec);

        // Verificar si el archivo existe antes de ejecutar
        if (!require('fs').existsSync(pythonExec)) {
            return reject(new Error(`No se encontró el backend Python en la ruta: ${pythonExec}`));
        }

        // Ejecutar el backend
        pythonProcess = spawn(pythonExec, [], {
            cwd: path.dirname(pythonExec),
            stdio: 'pipe'
        });

        let serverStarted = false;

        pythonProcess.stdout.on('data', (data) => {
            console.log(`Python stdout: ${data}`);
            if (data.toString().includes('Running on') && !serverStarted) {
                serverStarted = true;
                // Esperamos 2s para asegurarnos de que el servidor esté listo
                setTimeout(resolve, 2000);
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`Python stderr: ${data}`);
        });

        pythonProcess.on('error', (err) => {
            reject(err);
        });

        pythonProcess.on('close', (code) => {
            console.log(`Backend de Python cerrado con el código ${code}`);
        });

        // Timeout por si el backend no responde rápido
        setTimeout(() => {
            if (!serverStarted) {
                console.log('Timeout esperando backend, continuando...');
                resolve();
            }
        }, 5000);
    });
}


function createMenu() {
    const template = [
        {
            label: 'Archivo',
            submenu: [
                {
                    label: 'Nueva Operación',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        mainWindow.webContents.send('new-operation');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Exportar Historial',
                    accelerator: 'CmdOrCtrl+E',
                    click: () => {
                        mainWindow.webContents.send('export-history');
                    }
                },
                { type: 'separator' },
                {
                    label: 'Salir',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Editar',
            submenu: [
                { role: 'undo', label: 'Deshacer' },
                { role: 'redo', label: 'Rehacer' },
                { type: 'separator' },
                { role: 'cut', label: 'Cortar' },
                { role: 'copy', label: 'Copiar' },
                { role: 'paste', label: 'Pegar' },
                { role: 'selectall', label: 'Seleccionar todo' }
            ]
        },
        {
            label: 'Matrices',
            submenu: [
                {
                    label: 'Suma',
                    accelerator: 'CmdOrCtrl+1',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'suma');
                    }
                },
                {
                    label: 'Resta',
                    accelerator: 'CmdOrCtrl+2',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'resta');
                    }
                },
                {
                    label: 'Multiplicación',
                    accelerator: 'CmdOrCtrl+3',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'multiplicacion');
                    }
                },
                {
                    label: 'Determinante',
                    accelerator: 'CmdOrCtrl+4',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'determinante');
                    }
                },
                {
                    label: 'Transpuesta',
                    accelerator: 'CmdOrCtrl+5',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'transpuesta');
                    }
                },
                {
                    label: 'Inversa',
                    accelerator: 'CmdOrCtrl+6',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'inversa');
                    }
                }
            ]
        },
        {
            label: 'Ver',
            submenu: [
                {
                    label: 'Historial',
                    accelerator: 'CmdOrCtrl+H',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'historial');
                    }
                },
                {
                    label: 'Configuración',
                    accelerator: 'CmdOrCtrl+,',
                    click: () => {
                        mainWindow.webContents.send('navigate-to', 'configuracion');
                    }
                },
                { type: 'separator' },
                { role: 'reload', label: 'Recargar' },
                { role: 'forceReload', label: 'Forzar Recarga' },
                { role: 'toggleDevTools', label: 'Herramientas de Desarrollador' },
                { type: 'separator' },
                { role: 'resetZoom', label: 'Zoom Normal' },
                { role: 'zoomin', label: 'Acercar' },
                { role: 'zoomout', label: 'Alejar' },
                { type: 'separator' },
                { role: 'togglefullscreen', label: 'Pantalla Completa' }
            ]
        },
        {
            label: 'Ventana',
            submenu: [
                { role: 'minimize', label: 'Minimizar' },
                { role: 'close', label: 'Cerrar' }
            ]
        },
        {
            label: 'Ayuda',
            submenu: [
                {
                    label: 'Acerca de',
                    click: () => {
                        const { dialog } = require('electron');
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'Acerca de Calculadora de Matrices',
                            message: 'Calculadora de Matrices v1.0.0',
                            detail: 'Una aplicación completa para realizar operaciones matemáticas con matrices.\n\nDesarrollado con Electron y Python.',
                            buttons: ['OK']
                        });
                    }
                },
                {
                    label: 'Atajos de Teclado',
                    click: () => {
                        const { dialog } = require('electron');
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'Atajos de Teclado',
                            message: 'Atajos Disponibles',
                            detail: 'Ctrl+1: Suma\nCtrl+2: Resta\nCtrl+3: Multiplicación\nCtrl+4: Determinante\nCtrl+5: Transpuesta\nCtrl+6: Inversa\nCtrl+H: Historial\nCtrl+,: Configuración',
                            buttons: ['OK']
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Evento cuando la app está lista
app.whenReady().then(async () => {
    console.log('Iniciando aplicación...');
    
    try {
        // Iniciar el backend de Python
        console.log('Iniciando servidor Python...');
        await startPythonBackend();
        console.log('Servidor Python iniciado correctamente');
        
        // Crear la ventana principal
        createWindow();
        
        // Crear el menú
        createMenu();
        
    } catch (error) {
        console.error('Error iniciando la aplicación:', error);
        
        // Mostrar mensaje de error al usuario
        const { dialog } = require('electron');
        dialog.showErrorBox(
            'Error de Inicio',
            'No se pudo iniciar el servidor Python. Asegúrate de tener Python y las dependencias instaladas.'
        );
        
        app.quit();
    }

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

// Cerrar la app cuando todas las ventanas estén cerradas
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Cerrar el proceso Python cuando la app se cierre
app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// Manejar comunicación con el renderer process
ipcMain.on('get-app-info', (event) => {
    event.reply('app-info', {
        version: app.getVersion(),
        name: app.getName()
    });
});

// Prevenir la creación de múltiples instancias
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        // Alguien trató de ejecutar una segunda instancia, enfocar nuestra ventana en su lugar
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
        }
    });
}