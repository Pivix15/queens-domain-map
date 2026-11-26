// Inline in both viewers so save uploads and cached saves use identical bag tracking.
var LizardBags = (function () {
  // [treasure type (00–06), x, y, z, completion keys]; coordinates are Unreal centimetres.
  var points = /*__LIZARD_POINTS__*/[];
  function apply(buf, property, have) {
    // Old saves without ItemDrops cannot prove that a killed lizard's bag was collected.
    if (!property) return;
    var dv = new DataView(buf), bytes = new Uint8Array(buf), p = property.off;
    var end = p + property.size, pending = {};
    if (p < 0 || end > buf.byteLength || end < p) throw new Error('Invalid lizard drop bounds');
    function need(n, limit) {
      if (n < 0 || p + n > limit) throw new Error('Invalid lizard drop data');
    }
    function int(limit) { need(4, limit); var v = dv.getInt32(p, true); p += 4; return v; }
    function str(limit) {
      var n = int(limit), size = Math.abs(n) * (n < 0 ? 2 : 1), s = '';
      need(size, limit);
      for (var i = 0; i < Math.abs(n) - 1; i++) s += String.fromCharCode(n < 0 ? dv.getUint16(p + i * 2, true) : bytes[p + i]);
      p += size; return s;
    }
    function tags(limit) {
      var out = {};
      while (p < limit) {
        var name = str(limit); if (name === 'None') return out;
        var type = str(limit), size = int(limit), high = int(limit), sub = '';
        if (size < 0 || high !== 0) throw new Error('Invalid lizard drop property size');
        if (type === 'StructProperty') { sub = str(limit); need(16, limit); p += 16; }
        else if (type === 'MapProperty') { str(limit); str(limit); }
        else if (type === 'ArrayProperty' || type === 'SetProperty' || type === 'ByteProperty' || type === 'EnumProperty') str(limit);
        else if (type === 'BoolProperty') { need(1, limit); p++; }
        need(1, limit); var hasGuid = bytes[p++];
        if (hasGuid) { need(16, limit); p += 16; }
        need(size, limit); var next = p + size, value;
        if (type === 'StructProperty' && sub === 'Transform') value = tags(next);
        else if (type === 'StructProperty' && sub === 'Vector' && size === 12) {
          value = [dv.getFloat32(p, true), dv.getFloat32(p + 4, true), dv.getFloat32(p + 8, true)];
        } else if (type === 'ObjectProperty') value = str(next);
        if (value !== undefined) out[name.split('_')[0]] = value;
        p = next;
      }
      throw new Error('Unterminated lizard drop properties');
    }
    need(8, end);
    var removed = int(end);
    if (removed < 0) throw new Error('Invalid removed drop count');
    need(removed * 16, end); p += removed * 16;
    var count = int(end);
    if (count < 0 || count > (end - p) / 16) throw new Error('Invalid drop count');
    for (var i = 0; i < count; i++) {
      need(16, end); p += 16; // Generated pickup GUID, distinct from the enemy/spawner GUID.
      var drop = tags(end), match = /\/LizerBag\/LizerTreasure_(\d+)\//.exec(drop.Pickupclass || '');
      if (!match) continue;
      var variant = +match[1], xyz = drop.Position && drop.Position.Translation;
      var candidates = points.filter(function (q) { return q[0] === variant; });
      var nearest = null, distance = Infinity;
      if (xyz && xyz.every(Number.isFinite)) candidates.forEach(function (q) {
        var d = Math.pow(xyz[0] - q[1], 2) + Math.pow(xyz[1] - q[2], 2) + Math.pow(xyz[2] - q[3], 2);
        if (d < distance) { distance = d; nearest = q; }
      });
      // Persisted drops sit at their spawn points. Keep every candidate if a moved or
      // unknown drop cannot be associated safely within 15 m, rather than hiding it.
      (nearest && distance <= 1500 * 1500 ? [nearest] : candidates).forEach(function (q) {
        q[4].forEach(function (key) { pending[key] = true; });
      });
    }
    if (p !== end) throw new Error('Invalid lizard drop map size');
    points.forEach(function (q) {
      q[4].forEach(function (key) {
        // T = killed spawner with no remaining bag; a kill by itself is insufficient.
        if (have['G' + key.slice(1)] && !pending[key]) have[key] = 1;
      });
    });
  }
  return { apply: apply };
})();
