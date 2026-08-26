const { app, BrowserWindow, ipcMain } = require('electron');
const axios = require('axios');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: __dirname + '/preload.js',
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadURL('http://127.0.0.1:8000/');
}

// Users
ipcMain.handle('users:getAll', async () => {
  const res = await axios.get('http://127.0.0.1:8000/v1/users');
  return res.data;
});
ipcMain.handle('users:getById', async (event, id) => {
  const res = await axios.get(`http://127.0.0.1:8000/v1/users/${id}`);
  return res.data;
});
ipcMain.handle('users:create', async (event, data) => {
  const res = await axios.post('http://127.0.0.1:8000/v1/users', data);
  return res.data;
});
ipcMain.handle('users:update', async (event, { id, data }) => {
  const res = await axios.put(`http://127.0.0.1:8000/v1/users/${id}`, data);
  return res.data;
});
ipcMain.handle('users:delete', async (event, id) => {
  const res = await axios.delete(`http://127.0.0.1:8000/v1/users/${id}`);
  return res.data;
});

// Items
ipcMain.handle('items:getAll', async () => {
  const res = await axios.get('http://127.0.0.1:8000/v1/items');
  return res.data;
});
// ...similar handlers for items:getById, create, update, delete

// Search
ipcMain.handle('search:query', async (event, q) => {
  const res = await axios.get(`http://127.0.0.1:8000/api/v1/search?q=${encodeURIComponent(q)}`);
  return res.data;
});
ipcMain.handle('search:stats', async () => {
  const res = await axios.get('http://127.0.0.1:8000/api/v1/stats');
  return res.data;
});

// Health
ipcMain.handle('health:liveness', async () => {
  const res = await axios.get('http://127.0.0.1:8000/healthz');
  return res.data;
});
ipcMain.handle('health:readiness', async () => {
  const res = await axios.get('http://127.0.0.1:8000/readyz');
  return res.data;
});

app.on('ready', createWindow);
