const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let win;
let tray;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, 'icon.ico'), // tu ícono
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true
    }
  });

  win.loadFile('index.html');

  // Cuando se cierra la ventana, no salir del todo
  win.on('close', (event) => {
    event.preventDefault();
    win.hide(); // oculta la ventana
  });
}

app.whenReady().then(() => {
  createWindow();

  tray = new Tray(path.join(__dirname, 'icon.ico')); // ícono en bandeja
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Mostrar', click: () => win.show() },
    { label: 'Salir', click: () => app.quit() }
  ]);
  tray.setToolTip('Mi App');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => {
    win.show(); // restaurar al hacer clic
  })
  //setInterval(checkRings, 1000);
});

