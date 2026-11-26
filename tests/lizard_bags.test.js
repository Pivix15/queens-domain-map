const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'map/data.json'), 'utf8'));
const lizards = data.zones.flatMap(z => z.pois.filter(p => p[0] === 'lizard').map(p => ({ zone: z.id, poi: p })));
const points = lizards.map(({poi: p}) => [+p[4].match(/Potion Lizer (\d+)/)[1] - 1, ...p.slice(1, 4), p[7]]);
const helper = fs.readFileSync(path.join(root, 'map/lizard_bags.js'), 'utf8').replace('/*__LIZARD_POINTS__*/[]', JSON.stringify(points));
function i32(n) { const b = Buffer.alloc(4); b.writeInt32LE(n); return b; }
function fstr(s) { const b = Buffer.from(s + '\0'); return Buffer.concat([i32(b.length), b]); }
function tag(name, type, value, sub) {
  const extra = sub ? Buffer.concat([fstr(sub), Buffer.alloc(16)]) : Buffer.alloc(0);
  return Buffer.concat([fstr(name), fstr(type), i32(value.length), i32(0), extra, Buffer.from([0]), value]);
}
function drop(point, offset = [0, 0, 0], variant = point[0]) {
  const xyz = Buffer.alloc(12); point.slice(1, 4).forEach((n, i) => xyz.writeFloatLE(n + offset[i], i * 4));
  const transform = Buffer.concat([tag('Translation', 'StructProperty', xyz, 'Vector'), fstr('None')]);
  return Buffer.concat([Buffer.alloc(16), tag('Position_2_GUID', 'StructProperty', transform, 'Transform'),
    tag('Pickupclass_16_GUID', 'ObjectProperty', fstr(`/Game/Items/Treasure/LizerBag/LizerTreasure_${String(variant).padStart(2, '0')}/Pickup`)), fstr('None')]);
}
function apply(drops, have, truncate = false) {
  const b = Buffer.concat([i32(0), i32(drops.length), ...drops]);
  const buf = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength - (truncate ? 1 : 0));
  const tracker = vm.runInNewContext(helper + '; LizardBags');
  tracker.apply(buf, {off: 0, size: b.length}, have);
  return have;
}
const key = points[0][4][0];
const kill = 'G' + key.slice(1);
test('all 36 mapped spawns have individual treasure keys; category is enabled', () => {
  assert.equal(points.length, 36);
  assert.equal(new Set(points.flatMap(p => p[4])).size, 36);
  assert.ok(points.every(p => p[4].every(k => /^T[0-9a-f]{32}$/.test(k))));
  assert.equal(data.cats.find(c => c.id === 'lizard').on, 1);
});
test('bag IDs cannot inherit a bestiary entry or its manual checkmark', () => {
  const source = fs.readFileSync(path.join(root, 'map/template.html'), 'utf8');
  const keyFn = source.match(/function key\(z, p\) \{[^\n]+/)[0];
  const keyOf = vm.runInNewContext(keyFn + '; key');
  const z = data.zones[0], p = z.pois.find(p => p[0] === 'lizard');
  const bestiary = z.pois.find(q => q[0] === 'bestiaire' && q[6] === p[6]);
  assert.ok(bestiary);
  assert.notEqual(keyOf(z, p), keyOf(z, bestiary));
});
test('alive lizards stay pending; killed lizards without a bag are completed', () => {
  assert.equal(apply([], {})[key], undefined);
  assert.equal(apply([], {[kill]: 1})[key], 1);
});
test('a bag at the spawn keeps its killed lizard visible', () => {
  assert.equal(apply([drop(points[0], [0.2, -0.3, 2.1])], {[kill]: 1})[key], undefined);
});
test('one remaining bag does not reopen every lizard of its variant', () => {
  const other = points.find((p, i) => i > 0 && p[0] === points[0][0]);
  const otherKey = other[4][0];
  const result = apply([drop(points[0])], {[kill]: 1, ['G' + otherKey.slice(1)]: 1});
  assert.equal(result[key], undefined); assert.equal(result[otherKey], 1);
});
test('a far-away bag conservatively keeps candidates; other variants remain completed', () => {
  const other = points.find(p => p[0] !== points[0][0]), otherKey = other[4][0];
  const result = apply([drop(points[0], [1e7, 0, 0])], {[kill]: 1, ['G' + otherKey.slice(1)]: 1});
  assert.equal(result[key], undefined); assert.equal(result[otherKey], 1);
});
test('a missing ItemDrops property cannot prove collection', () => {
  const tracker = vm.runInNewContext(helper + '; LizardBags');
  const have = {[kill]: 1}; tracker.apply(new ArrayBuffer(0), undefined, have);
  assert.equal(have[key], undefined);
});
test('truncated drop data rejects the save instead of silently hiding lizards', () => {
  assert.throws(() => apply([drop(points[0])], {[kill]: 1}, true), /Invalid/);
});
test('completion keys survive the same JSON key cache used by both viewers', () => {
  const have = apply([], {[kill]: 1});
  const cache = JSON.parse(JSON.stringify({have: Object.keys(have)}));
  assert.ok(new Set(cache.have).has(key));
});
const savePath = process.env.QD_TEST_SAVE;
test('user save: both reader implementations agree on 23 collected and 13 pending', {skip: !savePath}, () => {
  const b = fs.readFileSync(savePath), buf = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
  const results = [];
  for (const file of ['map/template.html', 'map3d/viewer3d_site.html']) {
    const source = fs.readFileSync(path.join(root, file), 'utf8');
    const reader = source.match(/function readSave\(buf\) \{[\s\S]*?\n\s*return have;\n\s*\}/)[0];
    const have = vm.runInNewContext(helper + '\n' + reader + '; readSave')(buf);
    const completed = points.filter(p => p[4].some(k => have[k]));
    assert.equal(completed.length, 23);
    const pending = lizards.filter(({poi: p}) => !p[7].some(k => have[k]));
    assert.equal(pending.length, 13);
    assert.equal(pending.filter(({poi: p}) => p[7].some(k => have['G' + k.slice(1)])).length, 3);
    const cached = new Set(JSON.parse(JSON.stringify({have: Object.keys(have)})).have);
    assert.equal(points.filter(p => p[4].some(k => cached.has(k))).length, 23);
    if (file === 'map/template.html') {
      // Bestiary entries share the spawn actor name, but must not complete its bag.
      const context = vm.createContext({ ZONES: data.zones, S: {zone: 6, on: {lizard: true}, q: ''},
        found: {}, unfound: {}, saveDone: {}, saveHave: null, have,
        localStorage: {setItem() {}}, showSaveInfo() {}, refresh() {}, saveUnfound() {} });
      const hasKeyFn = source.match(/function hasKey\(have, k\) \{[^\n]+/)[0];
      const keyFn = source.match(/function key\(z, p\) \{[^\n]+/)[0];
      const doneFn = source.match(/function isDone\(z, p\) \{[^\n]+/)[0];
      const matchesFn = source.match(/function matches\(p\) \{[\s\S]*?return true;\n\s*\}/)[0];
      const applyFn = source.slice(source.indexOf('function applySave('), source.indexOf('// dernier cristal de sauvegarde utilisé : retrouvé'));
      vm.runInContext([hasKeyFn, keyFn, doneFn, matchesFn, applyFn].join('\n') + '\napplySave(have, "test.sav");', context);
      const pendingCount = vm.runInContext('ZONES.reduce((n,z,i) => { S.zone=i; return n+z.pois.filter(p => p[0] === "lizard" && matches(p)).length; },0)', context);
      assert.equal(pendingCount, 13, 'UI filtering must not inherit bestiary completion');
      const castleCount = vm.runInContext('S.zone=6; ZONES[6].pois.filter(p => p[0] === "lizard" && matches(p)).length', context);
      assert.equal(castleCount, 2);
    }
    results.push(Object.keys(have).sort());
  }
  assert.deepEqual(results[0], results[1]);
});
