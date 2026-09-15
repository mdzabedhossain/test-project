const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const root = __dirname;
const server = http.createServer((req, res) => {
  let pathname = new URL(req.url, `http://${req.headers.host}`).pathname;
  if (pathname === '/health') {
    res.writeHead(200, {'Content-Type':'application/json'});
    return res.end(JSON.stringify({status:'ok'}));
  }
  if (pathname === '/') pathname = '/index.html';
  const safe = path.normalize(pathname).replace(/^([.][.][\\/])+/, '');
  const file = path.join(root, safe);
  fs.readFile(file, (err, data) => {
    if (err) {
      res.writeHead(404, {'Content-Type':'text/plain'});
      return res.end('Not found');
    }
    const ext = path.extname(file);
    const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json'};
    res.writeHead(200, {'Content-Type': types[ext] || 'application/octet-stream'});
    res.end(data);
  });
});
server.listen(PORT, '0.0.0.0', () => console.log(`Store running on port ${PORT}`));
