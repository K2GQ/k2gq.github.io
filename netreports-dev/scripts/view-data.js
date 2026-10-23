/* Adapter for the K2GQ Net Reports DEVELOPMENT page.
 * Convert experimental cell OCR v2 to the existing UI schema, overriding
 * complete reviewed dates with the separately checked screenshot transcripts.
 * The original v1 and v2 evidence files are never modified.
 */
(function (root, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.NetReportsDevData = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  var DATE = /^\d{4}-\d{2}-\d{2}$/;
  var SOURCE = /^\/assets\/img\/net-(\d{4}-\d{2}-\d{2})\.png$/;

  function requireArray(obj, field, label) {
    if (!obj || !Array.isArray(obj[field])) {
      throw new Error(label + ' has no ' + field + ' array');
    }
    return obj[field];
  }
  function validDay(day) {
    if (typeof day !== 'string' || !DATE.test(day) ||
        new Date(day + 'T00:00:00Z').toISOString().slice(0, 10) !== day) {
      throw new Error('Invalid net date: ' + String(day));
    }
    return day;
  }
  function safeImage(day, image) {
    if (SOURCE.test(String(image)) && image.slice(16, 26) === day) return image;
    return '/assets/img/net-' + validDay(day) + '.png';
  }
  function indexNets(nets, label) {
    var index = new Map();
    nets.forEach(function (n) {
      var day = validDay(n.date);
      if (index.has(day)) throw new Error(label + ' has duplicate net ' + day);
      index.set(day, n);
    });
    return index;
  }
  function rowNumber(row) {
    var n = Number(row.image_row == null ? row.number : row.image_row);
    if (!Number.isSafeInteger(n) || n < 1) {
      throw new Error('Invalid check-in row position for ' + row.date);
    }
    return n;
  }
  function normalizeCellRow(row) {
    return {
      date: validDay(row.date),
      number: rowNumber(row),
      callsign: String(row.callsign || row.interpreted_callsign || '').trim().toUpperCase(),
      name: String(row.name || ''),
      city: String(row.city || ''),
      county: String(row.county || ''),
      state: String(row.state || ''),
      country: String(row.country || ''),
      remarks: String(row.remarks || ''),
      reviewed: false,
      needs_review: Boolean(row.needs_review || row.uncertain),
      raw_callsign: String(row.raw_callsign || ''),
      alternate_callsign: String(row.alternate_callsign || ''),
      interpretation: String(row.interpretation || '')
    };
  }
  function normalizeReviewedRow(row) {
    return {
      date: validDay(row.date),
      number: rowNumber(row),
      callsign: String(row.callsign || '').trim().toUpperCase(),
      name: String(row.name || ''),
      city: String(row.city || ''),
      county: String(row.county || ''),
      state: String(row.state || ''),
      country: String(row.country || ''),
      remarks: String(row.remarks || ''),
      reviewed: true,
      needs_review: false
    };
  }
  function build(v2, old, reviewed) {
    if (v2.kind !== 'cell-ocr-v2-full-archive-experimental') {
      throw new Error('Expected the full-archive cell OCR v2 dataset');
    }
    var v2Nets = requireArray(v2, 'nets', 'Cell OCR v2');
    var oldNets = requireArray(old, 'nets', 'Original OCR');
    var v2Rows = requireArray(v2, 'checkins', 'Cell OCR v2');
    var oldRows = requireArray(old, 'checkins', 'Original OCR');
    var approved = requireArray(reviewed, 'rows', 'Reviewed screenshot records');
    var first = indexNets(v2Nets, 'Cell OCR v2');
    var previous = indexNets(oldNets, 'Original OCR');
    if (!first.size || first.size !== previous.size ||
        [...first.keys()].some(function (d) { return !previous.has(d); })) {
      throw new Error('OCR datasets cover different net dates; comparison cannot be trusted');
    }
    var cellRows = new Map();
    v2Rows.forEach(function (row) {
      var d = validDay(row.date);
      if (!first.has(d)) throw new Error('OCR row references absent net ' + d);
      if (!cellRows.has(d)) cellRows.set(d, []);
      cellRows.get(d).push(normalizeCellRow(row));
    });
    var verified = new Map();
    approved.forEach(function (r) {
      var d = validDay(r.date);
      if (!first.has(d) || !r.reviewed) {
        throw new Error('Reviewed row lacks a corresponding net or verification: ' + d);
      }
      if (!verified.has(d)) verified.set(d, []);
      verified.get(d).push(normalizeReviewedRow(r));
    });
    verified.forEach(function (rows, day) {
      // Reviewed source dates must contain an ENTIRE, consecutively numbered
      // roster. Never inadvertently treat a partial transcript as complete.
      var positions = rows.map(function (r) { return r.number; }).sort(function (a, b) { return a - b; });
      if (positions.some(function (n, i) { return n !== i + 1; })) {
        throw new Error('Incomplete reviewed roster for ' + day);
      }
    });
    var resultNets = [], resultRows = [], comparison = [], flagCount = 0;
    [...first.keys()].sort().forEach(function (day) {
      var original = first.get(day);
      var prior = previous.get(day);
      var candidate = (cellRows.get(day) || []).sort(function (a, b) { return a.number - b.number; });
      var positions = candidate.map(function (r) { return r.number; });
      if (positions.length !== Number(original.ocr_rows) ||
          new Set(positions).size !== positions.length) {
        throw new Error('Cell OCR row count/positions disagree for ' + day);
      }
      var verifiedRows = verified.get(day);
      var visible = verifiedRows || candidate;
      var flags = candidate.filter(function (r) { return r.needs_review; }).length;
      flagCount += flags;
      var image = safeImage(day, original.image);
      var net = {
        date: day, image: image, ocr_rows: visible.length,
        reviewed: Boolean(verifiedRows),
        cell_ocr_rows: candidate.length,
        original_ocr_rows: Number(prior.ocr_rows),
        cell_review_flags: flags
      };
      resultNets.push(net);
      resultRows.push.apply(resultRows, visible);
      comparison.push({
        date: day, image: image,
        original: net.original_ocr_rows,
        improved: net.cell_ocr_rows,
        delta: net.cell_ocr_rows - net.original_ocr_rows,
        flagged: flags,
        reviewed: net.reviewed
      });
    });
    resultRows.sort(function (a, b) {
      return a.date.localeCompare(b.date) || a.number - b.number;
    });
    var stats = {
      original_rows: oldRows.length,
      cell_rows: v2Rows.length,
      displayed_rows: resultRows.length,
      verified_rows: resultRows.filter(function (r) { return r.reviewed; }).length,
      provisional_rows: resultRows.filter(function (r) { return !r.reviewed; }).length,
      cell_review_flags: flagCount,
      verified_nets: verified.size,
      increased_nets: comparison.filter(function (r) { return r.delta > 0; }).length,
      unchanged_nets: comparison.filter(function (r) { return r.delta === 0; }).length,
      decreased_nets: comparison.filter(function (r) { return r.delta < 0; }).length
    };
    return {
      nets: resultNets,
      checkins: resultRows,
      comparison: comparison,
      stats: stats,
      source_generated_utc: v2.generated_utc,
      provenance: 'Cell OCR v2 with reviewed source-image roster overrides'
    };
  }
  return { build: build };
});
