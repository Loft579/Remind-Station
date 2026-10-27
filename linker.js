const fs = require('fs');
const path = require('path');
const os = require('os');
const { fileURLToPath } = require('url');
const { execFileSync, spawn } = require('child_process');

// ── Detección ────────────────────────────────────────────────────────────────
// Reglas:
//  1. Con al menos un slash (/ o \) y existe en la compu → path (se abre como archivo).
//  2. Si no es path: con un host clave (ver WEB_HOSTS), un slash o "//" → link de internet (se le pasa al
//     navegador el texto tal cual, sin agregarle nada).

// Lista oficial de TLDs (https://data.iana.org/TLD/tlds-alpha-by-domain.txt)
let tlds = null;
function getTlds() {
  if (!tlds) {
    let raw = '';
    try { raw = fs.readFileSync(path.join(__dirname, 'tlds.txt'), 'utf-8'); } catch {}
    tlds = new Set(raw.split(/\r?\n/).filter(l => l && !l.startsWith('#')).map(l => l.trim().toLowerCase()));
  }
  return tlds;
}

// Tokens con su posición en el texto; lo que va entre comillas es un solo token (paths con espacios)
function tokenize(text) {
  const tokens = [];
  const re = /"([^"\r\n]+)"|(\S+)/g;
  let m;
  while ((m = re.exec(text))) {
    const start = m[1] != null ? m.index + 1 : m.index;
    let t = m[1] != null ? m[1] : m[2];
    // el [ ] de una IPv6 ([::1]:8080) no es puntuación
    const ipv6 = /^[(<'"¿¡]*\[[0-9a-f:.]+\]/i.test(t);
    const lead = t.match(ipv6 ? /^[(<'"¿¡]*/ : /^[(\[<'"¿¡]*/)[0].length;
    const trail = t.match(ipv6 && /\]$/.test(t) ? /(?!)/ : /[)\]>,.;:!?'"]*$/)?.[0].length || 0;
    t = t.slice(lead, t.length - trail);
    if (t) tokens.push({ text: t, start: start + lead, end: start + lead + t.length });
  }
  return tokens;
}

// Si el token es un path que existe en la compu, devuelve su ruta absoluta
function resolveExistingPath(token) {
  let p = token;
  if (/^file:\/\//i.test(p)) { try { p = fileURLToPath(p); } catch { return null; } }
  p = p.replace(/^~(?=[\\/]|$)/, os.homedir());
  p = p.replace(/%([^%]+)%/g, (all, name) => process.env[name] != null ? process.env[name] : all);
  const full = path.isAbsolute(p) ? p : path.resolve(os.homedir(), p);
  try { return fs.existsSync(full) ? path.normalize(full) : null; } catch { return null; }
}

// Hosts clave que hacen que algo sea link de internet (con o sin :puerto)
const WEB_HOSTS = [
  host => { const dot = host.lastIndexOf('.'); return dot > 0 && getTlds().has(host.slice(dot + 1)); },  // algo.TLD
  host => host === 'localhost' || host.endsWith('.localhost'),                                           // localhost
  host => /^(\d{1,3})(\.\d{1,3}){3}$/.test(host) && host.split('.').every(n => +n <= 255),               // IP: 192.168.0.1
  host => /^\[[0-9a-f:.]+\]$/.test(host),                                                                 // IPv6: [::1]
];

function hasWebHost(token) {
  const host = token.replace(/^[a-z][a-z0-9+.-]*:\/\//i, '').replace(/^[^@\/]*@/, '')
    .match(/^(\[[^\]]*\]|[^\/?#:]*)/)[0].toLowerCase();
  return WEB_HOSTS.some(test => test(host));
}

// [{ kind:'path'|'web', target, start, end }]
function findLinks(text) {
  const links = [];
  for (const tok of tokenize(text || '')) {
    const hasSlash = /[\/\\]/.test(tok.text);
    const existing = hasSlash ? resolveExistingPath(tok.text) : null;
    if (existing) links.push({ kind: 'path', target: existing, start: tok.start, end: tok.end });
    else if (hasSlash || hasWebHost(tok.text)) links.push({ kind: 'web', target: tok.text, start: tok.start, end: tok.end });
  }
  return links;
}

// ── Abrir ────────────────────────────────────────────────────────────────────

// Comando del navegador predeterminado de Windows (ej. "...\msedge.exe" --single-argument %1)
let browserCommand;
function getBrowserCommand() {
  if (browserCommand !== undefined) return browserCommand;
  browserCommand = null;
  try {
    const choice = execFileSync('reg', ['query', 'HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice', '/v', 'ProgId'], { encoding: 'utf-8', windowsHide: true });
    const progId = choice.match(/ProgId\s+REG_SZ\s+(\S+)/)[1];
    const cmd = execFileSync('reg', ['query', `HKCR\\${progId}\\shell\\open\\command`, '/ve'], { encoding: 'utf-8', windowsHide: true });
    browserCommand = cmd.match(/REG_(?:EXPAND_)?SZ\s+(.+)/)[1].trim();
  } catch {}
  return browserCommand;
}

// Partes del comando del navegador con el texto en lugar de %1
function browserArgs(cmd, target) {
  const parts = cmd.match(/"[^"]*"|\S+/g).map(p => p.replace(/^"|"$/g, ''));
  const args = parts.slice(1).map(a => a.replace('%1', target));
  if (!parts.slice(1).some(a => a.includes('%1'))) args.push(target);
  return { exe: parts[0], args };
}

function openLink(link) {
  const { shell } = require('electron');
  if (link.kind === 'path') {
    // Igual que doble clic en el Explorador. shell.openPath de Electron abre desde un hilo
    // propio que en Windows puede trabarse y soltar varias aperturas juntas mucho después.
    const child = spawn('explorer.exe', [link.target], { detached: true, stdio: 'ignore', windowsHide: false });
    child.on('error', () => {
      shell.openPath(link.target).then(err => { if (err) alert(`No se pudo abrir:\n${link.target}\n\n${err}`); });
    });
    child.unref();
    return;
  }
  // El texto tal cual al navegador, como si lo pegaras en la barra de direcciones
  const cmd = getBrowserCommand();
  if (cmd) {
    const { exe, args } = browserArgs(cmd, link.target);
    spawn(exe, args, { detached: true, stdio: 'ignore' }).unref();
  } else if (/^[a-z][a-z0-9+.-]*:/i.test(link.target)) {
    shell.openExternal(link.target);
  } else {
    alert(`No encontré el navegador predeterminado para abrir:\n${link.target}`);
  }
}

// ── Subrayado al pasar el mouse + clic para abrir ───────────────────────────
// Las cajas editables no pueden subrayar una parte de su texto, así que encima
// se pone una copia invisible (mismo texto, misma letra) donde sólo se ve el
// subrayado del link que tiene el mouse.

const MIRROR_STYLES = ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'letterSpacing', 'wordSpacing',
  'textTransform', 'textIndent', 'lineHeight', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'tabSize'];

const fields = new Set();   // cajas con copia, para reubicarlas todas juntas

function attachToField(field) {
  if (field.dataset.links) return;
  field.dataset.links = '1';
  const isArea = field.tagName === 'TEXTAREA';
  const mirror = document.createElement('div');
  mirror.className = 'linkMirror';
  document.body.appendChild(mirror);
  let links = [];
  let hovered = -1;

  function render() {
    links = findLinks(field.value);
    mirror.textContent = '';
    let pos = 0;
    links.forEach((l, i) => {
      mirror.appendChild(document.createTextNode(field.value.slice(pos, l.start)));
      const span = document.createElement('span');
      span.textContent = field.value.slice(l.start, l.end);
      if (i === hovered) span.className = 'linkHover';
      mirror.appendChild(span);
      pos = l.end;
    });
    mirror.appendChild(document.createTextNode(field.value.slice(pos) + '​'));
    place();
  }

  function place() {
    if (!field.isConnected) { mirror.remove(); fields.delete(entry); return; }
    const cs = getComputedStyle(field);
    for (const k of MIRROR_STYLES) mirror.style[k] = cs[k];
    const r = field.getBoundingClientRect();
    Object.assign(mirror.style, {
      left: `${r.left + window.scrollX + field.clientLeft}px`,
      top: `${r.top + window.scrollY + field.clientTop}px`,
      width: `${field.clientWidth}px`,
      height: `${field.clientHeight}px`,
      whiteSpace: isArea ? 'pre-wrap' : 'pre',
      overflowWrap: isArea ? 'break-word' : 'normal',
      display: field.offsetParent ? 'block' : 'none',
    });
    if (!isArea) {
      // el texto de un <input> va centrado verticalmente
      mirror.style.lineHeight = `${field.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom)}px`;
    }
    mirror.scrollTop = field.scrollTop;
    mirror.scrollLeft = field.scrollLeft;
  }

  function linkAt(x, y) {
    place();
    const spans = mirror.querySelectorAll('span');
    for (let i = 0; i < spans.length; i++) {
      for (const rect of spans[i].getClientRects()) {
        if (x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) return i;
      }
    }
    return -1;
  }

  function setHovered(i) {
    if (i === hovered) return;
    hovered = i;
    mirror.querySelectorAll('span').forEach((s, j) => { s.className = j === i ? 'linkHover' : ''; });
    field.style.cursor = i >= 0 ? 'pointer' : '';
  }

  field.addEventListener('input', render);
  field.addEventListener('scroll', place);
  field.addEventListener('mousemove', e => setHovered(linkAt(e.clientX, e.clientY)));
  field.addEventListener('mouseleave', () => setHovered(-1));
  field.addEventListener('click', e => {
    if (field.selectionStart !== field.selectionEnd) return;   // estaba seleccionando texto
    const i = linkAt(e.clientX, e.clientY);
    if (i >= 0) openLink(links[i]);
  });
  new ResizeObserver(place).observe(field);

  const entry = { place };
  fields.add(entry);
  render();
}

function placeAll() { for (const f of [...fields]) f.place(); }

// Texto común (no editable): envuelve los links en <span> con subrayado al pasar el mouse
function linkifyElement(el) {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    if (node.parentElement.closest('.linkText, .linkMirror, script, style, textarea')) continue;
    const text = node.nodeValue;
    const links = findLinks(text);
    if (!links.length) continue;
    const frag = document.createDocumentFragment();
    let pos = 0;
    for (const l of links) {
      frag.appendChild(document.createTextNode(text.slice(pos, l.start)));
      const span = document.createElement('span');
      span.className = 'linkText';
      span.textContent = text.slice(l.start, l.end);
      span.addEventListener('click', e => { e.stopPropagation(); openLink(l); });
      frag.appendChild(span);
      pos = l.end;
    }
    frag.appendChild(document.createTextNode(text.slice(pos)));
    node.replaceWith(frag);
  }
}

// Activa todo: cajas editables (actuales y futuras) y texto común del documento
function enableLinks(root = document.body) {
  const style = document.createElement('style');
  style.textContent = `
    .linkMirror { position: absolute; pointer-events: none; overflow: hidden; color: transparent;
                  box-sizing: border-box; z-index: 10000; margin: 0; border: 0; }
    .linkMirror .linkHover, .linkText:hover { text-decoration: underline; text-decoration-color: #0645ad; }
    .linkText { cursor: pointer; }`;
  document.head.appendChild(style);

  const scan = () => {
    root.querySelectorAll('textarea, input[type="text"], input:not([type])').forEach(attachToField);
    linkifyElement(root);
    placeAll();
  };
  scan();
  // cartas nuevas, borradas o reordenadas → revisar y reubicar las copias
  new MutationObserver(muts => {
    if (muts.every(m => m.target.closest && m.target.closest('.linkMirror'))) return;
    scan();
  }).observe(root, { childList: true, subtree: true, characterData: true });
  window.addEventListener('resize', placeAll);
  window.addEventListener('scroll', placeAll, true);
}

module.exports = { findLinks, openLink, enableLinks, browserArgs };
