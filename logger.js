// logger.js
const fs = require('fs');

const { TRACKING_LOG: logFile } = require('./paths');

// Cada función devuelve true si de verdad cambió el log, false si no pudo / no había nada

function logActivity(activityName) {
  const timestamp = Math.floor(Date.now() / 1000); // epoch en segundos
  const line = `${timestamp} at epoch: ${activityName.replace(/\n/g, " ")}\n`;
  try {
    fs.appendFileSync(logFile, line);
    return true;
  } catch { return false; }
}

// añade una nueva línea con "?" al final del archivo
function add_question_mark() {
  try {
    fs.appendFileSync(logFile, '?\n');
    return true;
  } catch { return false; }
}

// elimina la última línea del log
function undo_last_log() {
  let content;
  try { content = fs.readFileSync(logFile, 'utf-8').trimEnd(); }
  catch { return false; }               // todavía no hay log
  if (!content) return false;           // log vacío: nada que deshacer
  const lines = content.split('\n');
  lines.pop();
  try {
    fs.writeFileSync(logFile, lines.length ? lines.join('\n') + '\n' : '');
    return true;
  } catch { return false; }
}

module.exports = { logActivity, add_question_mark, undo_last_log };
