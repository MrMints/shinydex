// Version-2 ownership IDs are independent of the installed catalog revision.
// Keep valid newer IDs through an older renderer's saves and portable exports.
export function decodeCollection(record, knownKeys) {
  if (!record || record.version !== 2) throw Error("Unsupported collection format");
  const ids = (value) => {
    if (!Array.isArray(value) || value.length > 20000) throw Error("Invalid collection");
    return new Set(value.filter((id) => Number.isSafeInteger(id) && id > 0 && id <= 1000000));
  };
  const allCaptured = ids(record.captured);
  const allShinies = ids(record.shinies);
  allShinies.forEach((id) => allCaptured.add(id));
  const split = (values, known) => new Set([...values].filter((id) => knownKeys.has(id) === known));
  return {
    captured: split(allCaptured, true), shinies: split(allShinies, true),
    futureCaptured: split(allCaptured, false), futureShinies: split(allShinies, false),
  };
}

export function encodeCollection({ captured, shinies, futureCaptured, futureShinies }) {
  const allShinies = new Set([...shinies, ...futureShinies]);
  const allCaptured = new Set([...captured, ...futureCaptured, ...allShinies]);
  return {
    version: 2,
    captured: [...allCaptured].sort((a, b) => a - b),
    shinies: [...allShinies].sort((a, b) => a - b),
  };
}

// Assignment moves one previously unspecified record, preserving unrelated IDs.
export function assignCapture(record, fromKey, toKey) {
  if (!Number.isSafeInteger(fromKey) || !Number.isSafeInteger(toKey) || fromKey === toKey ||
      fromKey <= 0 || toKey <= 0 || fromKey > 1000000 || toKey > 1000000) throw Error("Invalid form assignment");
  const state = decodeCollection(record, new Set([fromKey, toKey]));
  if (!state.captured.has(fromKey)) throw Error("No saved capture to assign");
  state.captured.add(toKey);
  if (state.shinies.has(fromKey)) state.shinies.add(toKey);
  state.captured.delete(fromKey);
  state.shinies.delete(fromKey);
  return encodeCollection(state);
}
