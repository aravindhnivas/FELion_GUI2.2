'use strict';

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

var path = require('path');
var path__default = _interopDefault(path);
var url = require('url');
var electron = require('electron');

let mainWindow;
function createWindow() {
    const { width, height } = electron.screen.getPrimaryDisplay().workAreaSize;
    mainWindow = new electron.BrowserWindow({
        width: width,
        height: height,
        frame: false,
        titleBarStyle: "hidden",
        backgroundColor: "#1f232b",
        show: false,
        webPreferences: {
            nodeIntegration: true,
            nativeWindowOpen: true,
            webviewTag: true
        }
    });
    mainWindow.loadURL(url.format({
        pathname: path.join(__dirname, "../static/index.html"),
        protocol: "file:",
        slashes: true
    }));
    // Open the DevTools.
    // mainWindow.openDevTools({ mode: "detach" });
    mainWindow.once("ready-to-show", () => {
        if (mainWindow != null) {
            mainWindow.show();
        }
    });
    mainWindow.on("closed", function () {
        mainWindow = null;
    });
    mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {
        if (frameName === 'modal') {
            event.preventDefault();
            Object.assign(options, {
                // modal: true,
                parent: mainWindow,
                width: 1000,
                height: 600,
                frame: true,
                backgroundColor: "#fafafa",
            });
            event.newGuest = new electron.BrowserWindow(options);
        }
    });
}
electron.app.on("ready", createWindow);
electron.app.on("window-all-closed", function () {
    // Except for macOS
    if (process.platform !== "darwin") {
        electron.app.quit();
    }
});
electron.app.on("activate", function () {
    if (mainWindow === null) {
        createWindow();
    }
});
//# sourceMappingURL=main.js.map
