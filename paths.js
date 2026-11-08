// paths.js — rutas de datos compartidas por las ventanas
const fs = require('fs');
const path = require('path');
const electron = require('electron');

// Carpeta de datos de Electron (Windows: %APPDATA%\Remind-Station,
// Linux: ~/.config/Remind-Station, Mac: ~/Library/Application Support/Remind-Station).
// El proceso principal la pide directo; las ventanas se la piden a main.js.
const USER_DATA_DIR = process.type === 'browser'
  ? electron.app.getPath('userData')
  : electron.ipcRenderer.sendSync('get-user-data-path');

// Carpeta que abre el botón 📤/📥 (la que contiene a "leveldb")
const LOCAL_STORAGE_DIR = path.join(USER_DATA_DIR, 'Local Storage');

// La sesión: lo que se copia para exportar/importar el progreso
const SESSION_DIR = path.join(LOCAL_STORAGE_DIR, 'leveldb');

// Archivos de la sesión: viajan con la carpeta "leveldb"
const TRACKING_LOG = path.join(SESSION_DIR, 'tracking.log');
const REPLAY_FILE  = path.join(SESSION_DIR, 'gamification-replay.json');
const NOTIFICATIONS_PERMISSION_FILE = path.join(SESSION_DIR, 'notifications-permission.txt');

try { fs.mkdirSync(SESSION_DIR, { recursive: true }); } catch {}

module.exports = { USER_DATA_DIR, LOCAL_STORAGE_DIR, SESSION_DIR, TRACKING_LOG, REPLAY_FILE, NOTIFICATIONS_PERMISSION_FILE };
