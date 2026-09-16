const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 3000;
const publicDir = path.join(__dirname, 'public');

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, {'content-type': 'application/json'});
    return res.end(JSON.stringify({status: 'ok', app: 'ZabedBook'}));
  }

  let file = req.url === '/' ? 'index.html' : req.url.replace(/^\//, '');
  const filePath = path.join(publicDir, file);
  if (!filePath.startsWith(publicDir)) {
    res.writeHead(400); return res.end('Bad request');
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, {'content-type': 'text/plain'});
      return res.end('Not Found');
    }
    const ext = path.extname(filePath);
    const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.svg':'image/svg+xml'};
    res.writeHead(200, {'content-type': types[ext] || 'application/octet-stream'});
    res.end(data);
  });
});

server.listen(port, '0.0.0.0', () => console.log(`ZabedBook running on port ${port}`));
