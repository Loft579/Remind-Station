// logger.js
const fs = require('fs');
const path = require('path');

const logFile = path.join(__dirname, 'tracking.log');

function logActivity(activityName) {
  const timestamp = Math.floor(Date.now() / 1000); // epoch en segundos
  const line = `${timestamp} at epoch: ${activityName.replace(/\n/g, " ")}\n`;
  
  fs.appendFileSync(logFile, line);
}

// añade una nueva línea con "?" al final del archivo
function add_question_mark() {
  fs.appendFileSync(logFile, '?\n');
}

// elimina la última línea del log
function undo_last_log() {
  let content = fs.readFileSync(logFile, 'utf-8').trimEnd();
  const lines = content.split('\n');
  if (lines.length > 0) {
    lines.pop();
    fs.writeFileSync(logFile, lines.join('\n') + '\n');
  }
}

module.exports = { logActivity, add_question_mark, undo_last_log };
