const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let win;
let tray;
let isQuitting = false;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true
    }
  });

  win.loadFile('index.html');

  // Lógica para que la "X" oculte la ventana en lugar de cerrarla
  win.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      win.hide();
    }
    return false;
  });
}

app.whenReady().then(() => {
  createWindow();

  // Configuración del Tray (Bandeja)
  tray = new Tray(path.join(__dirname, 'icon.ico')); 
  const contextMenu = Menu.buildFromTemplate([
    { 
      label: 'Mostrar', 
      click: () => win.show() 
    },
    { 
      label: 'Salir', 
      click: () => {
        isQuitting = true; // Ahora sí está definida
        app.quit(); 
      } 
    }
  ]);

  tray.setToolTip('Remind-Station');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    win.show();
  });
});

// Asegura que el proceso termine al cerrar todas las ventanas
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});