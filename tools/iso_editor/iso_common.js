'use strict';
// Gemeinsame Logik für den 2D-Iso-Editor (index.html) und den 3D-Editor (3d.html):
// Raster, Hausgrössen, Grundriss, Belegungsmaske, Hausflächen, Einrasten, Speichern.
// Weltkoordinaten: x, y in Kacheln (y nach "unten links" im Iso-Bild), z = Höhe.

const N = 12;              // Kacheln je Seite
const SS = 8;              // Abtastung je Kachel für die Belegungsmaske (SS×SS Punkte)
const SIZES = { '1x2': { w: 1, d: 2, name: '1×2' }, '2x2': { w: 2, d: 2, name: '2×2' }, '4x2': { w: 4, d: 2, name: '4×2' } };
const DIRNAMES = ['SW', 'W', 'NW', 'N', 'NO', 'O', 'SO', 'S'];
const KEY = (x, y) => x + ',' + y;
const PARSE = k => k.split(',').map(Number);
const inGrid = k => { const [x, y] = PARSE(k); return x >= 0 && y >= 0 && x < N && y < N; };

// ---- Haus: Lage und Grundriss -------------------------------------------
function rot(h) { const th = h.dir * Math.PI / 4; return [Math.cos(th), Math.sin(th)]; }
function toWorld(h, a, b, z) { const [c, s] = rot(h); return [h.cx + a * c - b * s, h.cy + a * s + b * c, z]; }
function facing(h) { const [c, s] = rot(h); return [-s, c]; }  // lokale +y-Richtung (Türseite)

function footprint(h) {
  const { w, d } = SIZES[h.size], hw = w / 2, hd = d / 2;
  return [[-hw, -hd], [hw, -hd], [hw, hd], [-hw, hd]].map(([a, b]) => toWorld(h, a, b, 0).slice(0, 2));
}

function inPoly(poly, x, y) {
  let sgn = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length];
    const cr = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1);
    if (Math.abs(cr) < 1e-9) continue;
    const s = cr > 0 ? 1 : -1;
    if (sgn === 0) sgn = s; else if (s !== sgn) return false;
  }
  return true;
}

// Flächenanteil je Kachel (Map "x,y" -> 0..1), nur Kacheln mit Anteil > 0; je Haus zwischengespeichert
function maskOf(h) {
  if (h._mask) return h._mask;
  const poly = footprint(h);
  const xs = poly.map(p => p[0]), ys = poly.map(p => p[1]);
  const x0 = Math.floor(Math.min(...xs) - 1e-9), x1 = Math.ceil(Math.max(...xs) + 1e-9);
  const y0 = Math.floor(Math.min(...ys) - 1e-9), y1 = Math.ceil(Math.max(...ys) + 1e-9);
  const m = new Map();
  for (let ty = y0; ty < y1; ty++) for (let tx = x0; tx < x1; tx++) {
    let cnt = 0;
    for (let i = 0; i < SS; i++) for (let j = 0; j < SS; j++)
      if (inPoly(poly, tx + (i + .5) / SS, ty + (j + .5) / SS)) cnt++;
    if (cnt) m.set(KEY(tx, ty), cnt / (SS * SS));
  }
  h._mask = m;
  return m;
}
function blockedKeys(h, threshold) {
  const out = [];
  for (const [k, f] of maskOf(h)) if (f * 100 >= threshold - 1e-6) out.push(k);
  return out;
}
function entranceTile(h) {
  const { d } = SIZES[h.size];
  const [dx, dy] = toWorld(h, 0, d / 2, 0);
  const [fx, fy] = facing(h);
  return [Math.floor(dx + fx * 0.6), Math.floor(dy + fy * 0.6)];
}

// Mittelpunkt so einrasten, dass gerade Häuser genau auf Kacheln liegen:
// halbe Ausdehnung ganzzahlig -> Mittelpunkt auf Kachelecke, sonst auf Kachelmitte.
// Diagonale Häuser: Drehpunkt wahlweise auf Kachelecke oder Kachelmitte.
function snapHouse(wx, wy, dir, size, anchor) {
  const diag = dir % 2 === 1;
  const snap = (v, half) => Number.isInteger(half) ? Math.round(v) : Math.floor(v) + 0.5;
  if (diag) return anchor === 'center' ? [Math.floor(wx) + 0.5, Math.floor(wy) + 0.5] : [Math.round(wx), Math.round(wy)];
  const { w, d } = SIZES[size];
  const swap = dir % 4 === 2;            // 90° / 270°: lokale x-Achse liegt auf Welt-y
  return [snap(wx, swap ? d / 2 : w / 2), snap(wy, swap ? w / 2 : d / 2)];
}

// ---- Belegung ------------------------------------------------------------
function occupancy(W, threshold) {
  const blocked = new Map(), partial = new Map();
  for (const h of W.houses) {
    const bl = new Set(blockedKeys(h, threshold));
    for (const [k] of maskOf(h)) { if (bl.has(k)) blocked.set(k, h); else if (!partial.has(k)) partial.set(k, h); }
  }
  const trees = new Set(W.trees.map(t => KEY(t.x, t.y)));
  return { blocked, partial, trees };
}
function houseValid(h, W, occ, threshold) {
  const bl = blockedKeys(h, threshold);
  if (!bl.length) return false;
  return bl.every(k => inGrid(k) && !occ.blocked.has(k) && !occ.trees.has(k) && !W.paths.has(k));
}
function tileFree(k, W, occ) { return inGrid(k) && !occ.blocked.has(k) && !occ.trees.has(k) && !W.paths.has(k); }

// ---- Hausflächen (Wände, Giebel, Dach, Tür) in Weltkoordinaten ----------
const vsub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const vdot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const vcross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const vnorm = a => { const l = Math.hypot(...a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const COL = { WALL: [216, 200, 164], ROOF: [168, 90, 53], DOOR: [74, 48, 24] };

// Liefert [{pts: [[x,y,z]...] (von aussen gegen den Uhrzeigersinn), n: Normale, col: [r,g,b]}]
function houseFaces(h) {
  const { w, d } = SIZES[h.size], hw = w / 2, hd = d / 2, H = 1, R = H + 0.3 * Math.min(w, d) + 0.1;
  const F = [];
  const add = (pts, col) => F.push({ pts: pts.map(p => toWorld(h, ...p)), col });
  add([[-hw, -hd, 0], [hw, -hd, 0], [hw, -hd, H], [-hw, -hd, H]], COL.WALL);
  add([[-hw, hd, 0], [hw, hd, 0], [hw, hd, H], [-hw, hd, H]], COL.WALL);
  add([[hw, -hd, 0], [hw, hd, 0], [hw, hd, H], [hw, -hd, H]], COL.WALL);
  add([[-hw, -hd, 0], [-hw, hd, 0], [-hw, hd, H], [-hw, -hd, H]], COL.WALL);
  if (w > d) { // First entlang der langen Seite (x)
    add([[-hw, -hd, H], [-hw, hd, H], [-hw, 0, R]], COL.WALL);
    add([[hw, -hd, H], [hw, hd, H], [hw, 0, R]], COL.WALL);
    add([[-hw, -hd, H], [hw, -hd, H], [hw, 0, R], [-hw, 0, R]], COL.ROOF);
    add([[-hw, hd, H], [hw, hd, H], [hw, 0, R], [-hw, 0, R]], COL.ROOF);
  } else {     // First entlang y, Giebel vorne und hinten
    add([[-hw, -hd, H], [hw, -hd, H], [0, -hd, R]], COL.WALL);
    add([[-hw, hd, H], [hw, hd, H], [0, hd, R]], COL.WALL);
    add([[-hw, -hd, H], [-hw, hd, H], [0, hd, R], [0, -hd, R]], COL.ROOF);
    add([[hw, -hd, H], [hw, hd, H], [0, hd, R], [0, -hd, R]], COL.ROOF);
  }
  add([[-0.22, hd + 0.02, 0], [0.22, hd + 0.02, 0], [0.22, hd + 0.02, 0.68], [-0.22, hd + 0.02, 0.68]], COL.DOOR);
  const C = [h.cx, h.cy, 0.6];
  for (const f of F) {
    let n = vcross(vsub(f.pts[1], f.pts[0]), vsub(f.pts[2], f.pts[0]));
    const m = f.pts.reduce((a, p) => [a[0] + p[0] / f.pts.length, a[1] + p[1] / f.pts.length, a[2] + p[2] / f.pts.length], [0, 0, 0]);
    if (vdot(n, vsub(m, C)) < 0) { f.pts.reverse(); n = n.map(v => -v); }
    f.n = vnorm(n);
  }
  return F;
}

// ---- Speichern / Laden (beide Editoren teilen sich den Zustand) ----------
const LS = 'isoEditor.v1';
function saveState(S, W) {
  try {
    localStorage.setItem(LS, JSON.stringify({
      S, houses: W.houses.map(h => ({ cx: h.cx, cy: h.cy, dir: h.dir, size: h.size })),
      trees: W.trees, paths: [...W.paths]
    }));
  } catch (e) { /* privater Modus o.ä. */ }
}
function loadState(S, W) {
  try {
    const d = JSON.parse(localStorage.getItem(LS) || 'null');
    if (!d) return false;
    Object.assign(S, d.S || {});
    W.houses = (d.houses || []).map(h => ({ cx: h.cx, cy: h.cy, dir: h.dir, size: SIZES[h.size] ? h.size : '2x2' }));
    W.trees = d.trees || [];
    W.paths = new Set(d.paths || []);
    return true;
  } catch (e) { return false; }
}
function exampleScene(W) {
  W.houses.push({ cx: 4, cy: 4, dir: 0, size: '2x2' });   // gerade, Tür nach SW, Eingang (4,5)
  W.houses.push({ cx: 8, cy: 6, dir: 1, size: '2x2' });   // diagonal, Eingang (6,7)
  W.trees.push({ x: 9, y: 4 }, { x: 8, y: 8 }, { x: 2, y: 3 });
  for (const [x, y] of [[4, 5], [4, 6], [4, 7], [5, 7], [6, 7], [3, 8], [2, 9], [1, 10]]) W.paths.add(KEY(x, y));
}
