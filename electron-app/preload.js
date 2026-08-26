const { contextBridge, ipcRenderer } = require('electron');

// Expose structured API to the renderer
contextBridge.exposeInMainWorld('api', {
  users: {
    getAll: async () => await ipcRenderer.invoke('users:getAll'),
    getById: async (id) => await ipcRenderer.invoke('users:getById', id),
    create: async (data) => await ipcRenderer.invoke('users:create', data),
    update: async (id, data) => await ipcRenderer.invoke('users:update', { id, data }),
    delete: async (id) => await ipcRenderer.invoke('users:delete', id),
  },
  items: {
    getAll: async () => await ipcRenderer.invoke('items:getAll'),
    getById: async (id) => await ipcRenderer.invoke('items:getById', id),
    create: async (data) => await ipcRenderer.invoke('items:create', data),
    update: async (id, data) => await ipcRenderer.invoke('items:update', { id, data }),
    delete: async (id) => await ipcRenderer.invoke('items:delete', id),
  },
  search: {
    query: async (q) => await ipcRenderer.invoke('search:query', q),
    stats: async () => await ipcRenderer.invoke('search:stats'),
  },
  health: {
    liveness: async () => await ipcRenderer.invoke('health:liveness'),
    readiness: async () => await ipcRenderer.invoke('health:readiness'),
  }
});
