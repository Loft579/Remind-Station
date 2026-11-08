const { app, BrowserWindow, Tray, Menu, ipcMain, session } = require('electron');
const path = require('path');
const fs = require('fs');
const { NOTIFICATIONS_PERMISSION_FILE } = require('./paths');

// Ruta de datos para las ventanas (paths.js)
ipcMain.on('get-user-data-path', (e) => { e.returnValue = app.getPath('userData'); });

// Permiso nativo de notificaciones (Notification.requestPermission / Notification.permission).
// En Electron no hay cartel del navegador: este proceso hace de navegador, lo concede cuando
// la ventana lo pide (click en 🔔) y lo guarda en la sesión. Sesión nueva = sin permiso.
let notificationsGranted = false;
try { notificationsGranted = fs.readFileSync(NOTIFICATIONS_PERMISSION_FILE, 'utf-8').trim() === 'granted'; } catch {}

function setNotificationsGranted(granted) {
  notificationsGranted = granted;
  try { fs.writeFileSync(NOTIFICATIONS_PERMISSION_FILE, granted ? 'granted' : 'denied'); } catch {}
}

// Sacar el permiso: la API web no lo permite, así que sólo existe en Electron
ipcMain.on('revoke-notifications-permission', (e) => {
  setNotificationsGranted(false);
  e.returnValue = true;
});

// .ico sólo lo entiende Windows; Mac y Linux usan el PNG
const ICON = path.join(__dirname, process.platform === 'win32' ? 'icon.ico' : 'icon.png');

let win;
let tray;
let isQuitting = false;

// Una sola instancia: si se abre la app otra vez, se muestra la ventana que ya corre.
// Así la ventana nunca queda perdida, aunque el escritorio no muestre el tray.
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) app.quit();
app.on('second-instance', () => showWindow());

function showWindow() {
  if (!win) return;
  if (win.isMinimized()) win.restore();
  win.show();
  win.focus();
}

// Cualquier forma de salir (tray, Ctrl+Q / Cmd+Q, menú "Quit") cierra de verdad
app.on('before-quit', () => { isQuitting = true; });

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: ICON,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile('index.html');

  // La "X" no cierra: la app sigue corriendo para que suenen los recordatorios.
  // En Linux minimiza en vez de ocultar, porque muchos escritorios (ej. GNOME)
  // no muestran el tray y la ventana oculta quedaría inalcanzable.
  win.on('close', (event) => {
    if (isQuitting) return;
    event.preventDefault();
    if (process.platform === 'linux') win.minimize();
    else win.hide();
  });
}

app.whenReady().then(() => {
  if (!gotLock) return;

  // Los demás permisos siguen como siempre (concedidos); sólo las notificaciones dependen de 🔔
  session.defaultSession.setPermissionCheckHandler((wc, permission) =>
    permission === 'notifications' ? notificationsGranted : true);
  session.defaultSession.setPermissionRequestHandler((wc, permission, callback) => {
    if (permission === 'notifications') setNotificationsGranted(true);
    callback(true);
  });

  createWindow();

  // Configuración del Tray (Bandeja)
  tray = new Tray(ICON);
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Mostrar', click: () => showWindow() },
    { label: 'Salir', click: () => app.quit() }
  ]);

  tray.setToolTip('Remind-Station');
  tray.setContextMenu(contextMenu);

  tray.on('click', () => showWindow());

  ipcMain.on('open-game', () => {
    const gameWin = new BrowserWindow({
      width: 680,
      height: 780,
      title: 'R-S Game Beta',
      icon: ICON,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      }
    });
    gameWin.loadFile('game.html');
    gameWin.setMenuBarVisibility(false);
  });
});

// Asegura que el proceso termine al cerrar todas las ventanas
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
