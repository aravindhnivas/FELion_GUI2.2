'use strict';

function _interopDefault (ex) { return (ex && (typeof ex === 'object') && 'default' in ex) ? ex['default'] : ex; }

var path = require('path');
var path__default = _interopDefault(path);
var url = require('url');
var electron = require('electron');

// const find_process = require("find-process")
// const { exec } = require("child_process");
// function killPort(port:number) {
//     return new Promise((resolve, reject)=>{
//         find_process("port", port).then((result:any)=>{
//             if (result.length > 0) {
//                 let pid = result[0].pid
//                 let platform = process.platform
//                 if (platform === "win32") exec(`taskkill /F /PID ${pid}`)
//                 else if (platform === "darwin") exec(`kill ${pid}`)
//                 else if (platform === "linux") exec(`killall ${pid}`)
// 				resolve(`Port ${port} closed`)
//             } else {reject(`Port ${port} already closed `)}
//         })
//     })
// }
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
        // killPort(8501).then((result:any)=>console.log(result)).catch((err:any)=>console.log(err))
        mainWindow = null;
    });
    mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {
        event.preventDefault();
        Object.assign(options, {
            parent: mainWindow,
            width: width * .75,
            height: 600,
            frame: true,
        });
        let newWindow = event.newGuest = new electron.BrowserWindow(options);
        newWindow.on("closed", () => {
            console.log("Window closed");
            // killPort(8501).then((result:any)=>console.log(result)).catch((err:any)=>console.log(err))
        });
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
//# sourceMappingURL=main.js.map
