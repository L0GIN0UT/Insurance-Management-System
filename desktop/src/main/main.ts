import { app, BrowserWindow, Menu, shell } from 'electron';
import { join } from 'node:path';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

const isDev = !app.isPackaged;

function createWindow(): void {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    },
    icon: join(__dirname, '../public/icon.png'),
    title: 'Insurance Management System',
    show: false, // Don't show until ready-to-show
  });

  // Load the appropriate content based on environment
  const DEV_URL = 'http://localhost:3000';
  const PROD_URL = `file://${join(__dirname, '../renderer/index.html')}`;

  const urlToLoad = isDev ? DEV_URL : PROD_URL;
  console.log('[MAIN] load', urlToLoad);
  
  win.loadURL(urlToLoad).catch((err) => {
    console.error('[MAIN] load failed, fallback → PROD file', err);
    if (isDev) win.loadURL(PROD_URL);
  });

  // Show window when ready to prevent visual flash
  win.once('ready-to-show', () => {
    win.show();
  });

  // Open the DevTools in development
  if (isDev) {
    win.webContents.openDevTools();
  }

  // Безопасный обработчик внешних ссылок
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });
}

const createMenu = (): void => {
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          },
        },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' },
      ],
    },
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(createWindow);

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.setWindowOpenHandler(() => {
    return { action: 'deny' };
  });
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here. 