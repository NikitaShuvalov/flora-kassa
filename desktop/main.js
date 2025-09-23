const { app, BrowserWindow } = require('electron');

function createWindow() {
    // Получаем адрес сервиса из аргументов командной строки
    const serviceUrl = process.argv[2] || 'http://127.0.0.1:8000';

    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    win.loadURL(serviceUrl);
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
