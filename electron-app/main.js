const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');

let fastapiProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Load FastAPI GUI served at localhost
  win.loadURL('http://127.0.0.1:8000/');
}

app.on('ready', () => {
  // Start FastAPI backend via Python
  fastapiProcess = spawn('python', ['run_desktop.py']);

  fastapiProcess.stdout.on('data', (data) => {
    console.log(`FastAPI: ${data}`);
  });

  fastapiProcess.stderr.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
  });

  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
  if (fastapiProcess) {
    fastapiProcess.kill();
  }
});
