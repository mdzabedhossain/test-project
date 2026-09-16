const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const users = new Map();

app.use(express.static(path.join(__dirname, 'public')));
app.get('/health', (_req, res) => res.json({ status: 'ok', app: 'ZabedChat' }));

io.on('connection', socket => {
  socket.on('join', name => {
    const username = String(name || 'Guest').trim().slice(0, 30) || 'Guest';
    users.set(socket.id, username);
    socket.emit('system', `Welcome to ZabedChat, ${username}!`);
    socket.broadcast.emit('system', `${username} joined the chat`);
    io.emit('users', [...users.values()]);
  });
  socket.on('chat', text => {
    const message = String(text || '').trim().slice(0, 1000);
    if (!message || !users.has(socket.id)) return;
    io.emit('chat', { user: users.get(socket.id), text: message, time: new Date().toISOString() });
  });
  socket.on('disconnect', () => {
    const username = users.get(socket.id);
    if (username) socket.broadcast.emit('system', `${username} left the chat`);
    users.delete(socket.id);
    io.emit('users', [...users.values()]);
  });
});

const port = process.env.PORT || 3000;
server.listen(port, '0.0.0.0', () => console.log(`ZabedChat running on port ${port}`));
