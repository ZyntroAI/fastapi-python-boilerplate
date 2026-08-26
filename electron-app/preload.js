const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to the renderer
contextBridge.exposeInMainWorld('api', {
  // Call FastAPI backend via IPC
  fetchData: async (endpoint) => {
    return await ipcRenderer.invoke('fetch-data', endpoint);
  },

  // Example: send a message to backend
  sendMessage: (msg) => {
    ipcRenderer.send('log-message', msg);
  }
});
