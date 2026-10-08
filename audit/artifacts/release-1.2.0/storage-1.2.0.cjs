// Stable per-user collection files live outside installed version directories.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');

function validate(record) {
  if (!record || record.version !== 2) throw Error('Unsupported collection format');
  const ids = value => {
    if (!Array.isArray(value) || value.length > 20000 || value.some(id => !Number.isSafeInteger(id) || id <= 0 || id > 1000000)) throw Error('Invalid collection IDs');
    return new Set(value);
  };
  const captured = ids(record.captured), shinies = ids(record.shinies);
  shinies.forEach(id => captured.add(id));
  return {version:2, captured:[...captured].sort((a,b)=>a-b), shinies:[...shinies].sort((a,b)=>a-b)};
}

class CollectionStore {
  constructor(directory, keys) {
    this.directory = directory;
    this.file = path.join(directory, 'collection-v2.json');
    this.keys = new Set(keys);
    this.pending = Promise.resolve();
  }
  async load() {
    await this.pending;
    try { return JSON.stringify(validate(JSON.parse(await fs.readFile(this.file,'utf8')))); }
    catch(error) { if (error.code === 'ENOENT') return null; throw error; }
  }
  save(record) {
    const next = validate(record);
    const operation = this.pending.then(async () => {
      let previous;
      try { previous = validate(JSON.parse(await fs.readFile(this.file,'utf8'))); }
      catch(error) { if (error.code !== 'ENOENT') throw error; }
      // Keep IDs introduced by newer catalogs when an older version saves.
      if (previous) for (const field of ['captured','shinies']) {
        next[field] = [...new Set([...next[field],...previous[field].filter(id=>!this.keys.has(id))])].sort((a,b)=>a-b);
      }
      await fs.mkdir(this.directory,{recursive:true});
      const temporary = this.file + '.' + crypto.randomUUID() + '.tmp';
      try { await fs.writeFile(temporary,JSON.stringify(next,null,2),'utf8'); await fs.rename(temporary,this.file); }
      finally { await fs.rm(temporary,{force:true}); }
      return next;
    });
    this.pending = operation.catch(()=>{});
    return operation;
  }
  async backup() {
    const saved = await this.load();
    if (saved === null) return null;
    const directory = path.join(this.directory,'backups');
    await fs.mkdir(directory,{recursive:true});
    const file = path.join(directory, new Date().toISOString().replace(/[:.]/g,'-')+'-'+crypto.randomUUID()+'.json');
    await fs.writeFile(file,saved,'utf8');
    return file;
  }
}
module.exports = {CollectionStore,validate};
