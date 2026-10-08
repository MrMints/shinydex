// Offline descriptions use National species IDs; hunts use exact collection/form keys.
// Returned descriptions retain source form labels. Never silently apply default text to a form.
export function createPokedexIndex(descriptions, hunts) {
  const normalize = value => value.replace(/^Pokémon\s+/i, "").replaceAll("’", "'").toLowerCase().replace(/[^a-z0-9]+/g, "");
  const aliases = new Map(Object.values(descriptions.games).map(g => [normalize(g.name), g.id]));
  aliases.set("xdgaleofdarkness", "xd");
  aliases.set("redjapan", "red-japan");
  aliases.set("greenjapan", "green-japan");
  aliases.set("bluejapan", "blue-japan");
  const gameIds = label => {
    // DLC remains explicit on the hunting record; the source lists its text under the parent game.
    const parent = label.split(/\s+[·–]\s+/)[0];
    return parent.replace(/^Pokémon\s+/, "").split(/\s+\/\s+/).map(part => {
      const normalized = normalize(part);
      if (aliases.has(normalized)) return aliases.get(normalized);
      const dlc = normalized.match(/^the(?:isleofarmor|crowntundra)(sword|shield)$/);
      if (dlc) return dlc[1];
      return normalized === "go" || normalized === "home" ? normalized : null;
    }).filter(Boolean);
  };
  return {
    gameIds,
    gameName(id) { return descriptions.games[id]?.name || `Pokémon ${id.toUpperCase()}`; },
    forPokemon(pokemon, gameId = null) {
      const entries = descriptions.species[String(pokemon.id)] || [];
      const guide = hunts[String(pokemon.key)] || { entries: [], locked: false };
      const ids = [...new Set([...entries.map(e => e.gameId), ...guide.entries.flatMap(e => gameIds(e.game))])];
      return ids.filter(id => !gameId || id === gameId).map(id => ({
        gameId: id,
        gameName: descriptions.games[id]?.name || `Pokémon ${id.toUpperCase()}`,
        descriptions: entries.filter(e => e.gameId === id),
        huntingRecords: guide.entries.filter(e => gameIds(e.game).includes(id)),
        // No missing record is converted into a shiny lock or an availability claim.
        descriptionStatus: entries.some(e => e.gameId === id) ? "recorded" : "not-recorded",
        huntingStatus: guide.entries.some(e => gameIds(e.game).includes(id)) ? "recorded" : "not-recorded",
        formKey: pokemon.key,
      }));
    },
  };
}
