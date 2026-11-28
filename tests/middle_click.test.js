const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../map3d/viewer3d_site.html'), 'utf8');
function setup(saved = false, challenge = false) {
  const p = {id: 'a', c: challenge ? 'challenge' : 'key', n: 'Test', k: ['Gtest']};
  const q = {id: 'b', c: 'challenge', n: 'Test', k: []};
  const m = {userData: p, material: {}}, sibling = {userData: q, material: {}};
  const events = {}, stored = {}, stats = {flights: 0, neighbours: 0, updates: 0};
  const context = vm.createContext({ selected: m, zone: {pois: [p, q]}, markers: [m, sibling], found: {}, unfound: {},
    bySave: row => saved && row === p, hasKey: key => saved && key === 'Gtest',
    localStorage: {setItem(k, v) { stored[k] = JSON.parse(v); }},
    markerTex(row) { row.done = context.isDone(row); return 'texture'; },
    updateCounts() { stats.updates++; }, refresh() {}, renderProg() {}, selectMarker(marker) {context.selected = marker;},
    $: () => ({addEventListener() {}}),
    renderer: {domElement: {addEventListener(type, fn, capture) {events[type] = {fn, capture};}}},
    pick: ev => ev.marker === undefined ? m : ev.marker,
    goTo() {stats.flights++;}, neighbours: {click() {stats.neighbours++;}}
  });
  vm.runInContext('function isDone(p) {return !unfound[p.id] && !!(found[p.id] || bySave(p));}', context);
  vm.runInContext(source.slice(source.indexOf('function twins('), source.indexOf('let yMin =')), context);
  vm.runInContext(source.slice(source.indexOf('let downAt = null;'), source.indexOf("$('cx').addEventListener")), context);
  function event(button, x = 10, marker = m, pointerId = 1) {
    return {button, clientX: x, clientY: 10, marker, pointerId, prevented: false, stopped: false,
      preventDefault() {this.prevented = true;}, stopImmediatePropagation() {this.stopped = true;}};
  }
  function click(button = 1, from = m, to = from, x = 10) {
    const down = event(button, 10, from), up = event(button, x, to);
    events.pointerdown.fn(down); events.pointerup.fn(up); return {down, up};
  }
  return {context, events, stored, stats, m, sibling, click, event};
}
test('middle click toggles and persists Done/Undone without moving the camera', () => {
  const t = setup(); const ev = t.click();
  assert.equal(t.context.isDone(t.m.userData), true);
  assert.equal(t.stored['neasied-found'].a, 1);
  assert.equal(ev.down.prevented && ev.down.stopped, true);
  assert.equal(t.events.pointerdown.capture, true);
  t.click(); assert.equal(t.context.isDone(t.m.userData), false);
  assert.equal(t.stored['neasied-found'].a, undefined);
  assert.equal(t.stats.flights, 0); assert.equal(t.stats.updates, 2);
});
test('save-completed objects can be marked Undone and restored', () => {
  const t = setup(true); t.click();
  assert.deepEqual(t.stored['neasied-unfound'].a, ['Gtest']);
  assert.equal(t.context.isDone(t.m.userData), false);
  t.click(); assert.equal(t.context.isDone(t.m.userData), true);
  assert.equal(t.stored['neasied-unfound'].a, undefined);
});
test('challenge markers toggle together', () => {
  const t = setup(false, true); t.click();
  assert.equal(t.context.isDone(t.sibling.userData), true);
  assert.equal(t.sibling.material.needsUpdate, true);
});
test('drag, marker changes, empty space, right click and cancellation do not toggle', () => {
  const t = setup();
  t.click(1, t.m, t.m, 20); t.click(1, t.m, null); t.click(1, null, t.m); t.click(2);
  t.events.pointerdown.fn(t.event(1)); t.events.pointercancel.fn(); t.events.pointerup.fn(t.event(1));
  assert.equal(t.stats.updates, 0); assert.equal(t.stats.flights, 0);
  assert.equal(t.click(1, null).down.stopped, false);
});
test('left click still visits markers and neighbouring worlds', () => {
  const t = setup(); t.click(0); t.click(0, null);
  assert.equal(t.stats.flights, 1); assert.equal(t.stats.neighbours, 1);
});
test('duplicate releases and other pointers do not toggle twice', () => {
  const t = setup(); t.events.pointerdown.fn(t.event(1));
  t.events.pointerup.fn(t.event(1, 10, t.m, 2)); assert.equal(t.stats.updates, 0);
  t.events.pointerup.fn(t.event(1)); t.events.pointerup.fn(t.event(1)); assert.equal(t.stats.updates, 1);
});
