// Minimal local server; the browser app itself uses only static files.
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const mime = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
};

function handler(req, res) {
  let pathname;
  try {
    pathname = decodeURIComponent(req.url.split("?")[0]);
  } catch {
    res.writeHead(400);
    return res.end("Invalid URL");
  }

  // Resolve paths before reading so requests cannot escape the project folder.
  const file = path.resolve(
    root,
    "." + (pathname === "/" ? "/index.html" : pathname),
  );
  if (!file.startsWith(root + path.sep)) {
    res.writeHead(403);
    return res.end();
  }

  fs.readFile(file, (error, contents) => {
    if (error) {
      res.writeHead(404);
      return res.end("Not found");
    }
    res.writeHead(200, {
      "Content-Type": mime[path.extname(file)] || "application/octet-stream",
    });
    res.end(contents);
  });
}

// Export the handler for verification without starting another server process.
module.exports = handler;
if (require.main === module) {
  http.createServer(handler).listen(5173, "127.0.0.1", () => {
    console.log("ShinyDex ready at http://localhost:5173");
  });
}
