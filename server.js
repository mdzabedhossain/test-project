const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const root = __dirname;

const products = [
  {id:1,name:'Wireless Headphones',price:49.99,category:'Electronics',stock:25,image:'https://placehold.co/600x400?text=Headphones'},
  {id:2,name:'Smart Watch',price:79.99,category:'Electronics',stock:18,image:'https://placehold.co/600x400?text=Smart+Watch'},
  {id:3,name:'Running Shoes',price:59.99,category:'Fashion',stock:30,image:'https://placehold.co/600x400?text=Running+Shoes'},
  {id:4,name:'Backpack',price:34.99,category:'Fashion',stock:40,image:'https://placehold.co/600x400?text=Backpack'}
];
const orders = new Map();

function json(res, status, data) {
  res.writeHead(status, {
    'Content-Type':'application/json; charset=utf-8',
    'Access-Control-Allow-Origin':'*',
    'Access-Control-Allow-Methods':'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers':'Content-Type, Authorization'
  });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 1_000_000) req.destroy();
    });
    req.on('end', () => {
      if (!body) return resolve({});
      try { resolve(JSON.parse(body)); } catch { reject(new Error('Invalid JSON')); }
    });
    req.on('error', reject);
  });
}

function sendFile(req, res, pathname) {
  if (pathname === '/') pathname = '/index.html';
  const safe = path.normalize(pathname).replace(/^([.][.][\\/])+/, '');
  const file = path.join(root, safe);
  fs.readFile(file, (err, data) => {
    if (err) return json(res, 404, {error:'Not found'});
    const ext = path.extname(file);
    const types = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json'};
    res.writeHead(200, {'Content-Type': types[ext] || 'application/octet-stream'});
    res.end(data);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;

  if (req.method === 'OPTIONS') return json(res, 204, {});

  if (pathname === '/health') return json(res, 200, {status:'ok', service:'NovaCart API'});

  if (pathname === '/api' || pathname === '/api/') {
    return json(res, 200, {
      name:'NovaCart API',
      version:'1.0.0',
      endpoints:['GET /api/products','GET /api/products/:id','GET /api/categories','POST /api/orders','GET /api/orders/:id']
    });
  }

  if (pathname === '/api/products' && req.method === 'GET') {
    const category = url.searchParams.get('category');
    const q = (url.searchParams.get('q') || '').toLowerCase();
    let result = products.filter(p => (!category || p.category.toLowerCase() === category.toLowerCase()) && (!q || p.name.toLowerCase().includes(q)));
    return json(res, 200, {count:result.length, products:result});
  }

  const productMatch = pathname.match(/^\/api\/products\/(\d+)$/);
  if (productMatch && req.method === 'GET') {
    const product = products.find(p => p.id === Number(productMatch[1]));
    return product ? json(res, 200, product) : json(res, 404, {error:'Product not found'});
  }

  if (pathname === '/api/categories' && req.method === 'GET') {
    return json(res, 200, [...new Set(products.map(p => p.category))]);
  }

  if (pathname === '/api/orders' && req.method === 'POST') {
    try {
      const body = await readBody(req);
      if (!body.customer || !Array.isArray(body.items) || !body.items.length) {
        return json(res, 400, {error:'customer and items are required'});
      }
      const lines = body.items.map(item => {
        const product = products.find(p => p.id === Number(item.productId));
        const quantity = Math.max(1, Number(item.quantity || 1));
        if (!product) throw new Error('Invalid productId: ' + item.productId);
        if (quantity > product.stock) throw new Error('Insufficient stock for product: ' + product.name);
        return {productId:product.id,name:product.name,quantity,unitPrice:product.price,total:Number((product.price*quantity).toFixed(2))};
      });
      const total = Number(lines.reduce((sum,x) => sum+x.total, 0).toFixed(2));
      const id = 'ORD-' + Date.now();
      const order = {id,status:'pending',customer:body.customer,items:lines,total,currency:'USD',createdAt:new Date().toISOString()};
      orders.set(id, order);
      return json(res, 201, order);
    } catch (e) {
      return json(res, 400, {error:e.message});
    }
  }

  const orderMatch = pathname.match(/^\/api\/orders\/([A-Za-z0-9-]+)$/);
  if (orderMatch && req.method === 'GET') {
    const order = orders.get(orderMatch[1]);
    return order ? json(res, 200, order) : json(res, 404, {error:'Order not found'});
  }

  if (pathname.startsWith('/api/')) return json(res, 404, {error:'API endpoint not found'});
  return sendFile(req, res, pathname);
});

server.listen(PORT, '0.0.0.0', () => console.log(`NovaCart + API running on port ${PORT}`));
