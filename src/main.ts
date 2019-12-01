import * as path from "path"
import * as url from "url"
import { app, BrowserWindow, screen } from "electron"
const find_process = require("find-process")
const { exec } = require("child_process");
function killPort(port) {
    return new Promise((resolve, reject)=>{

        find_process("port", port).then(result=>{

            if (result.length > 0) {

                let pid = result[0].pid
                let platform = process.platform

                if (platform === "win32") exec(`taskkill /F /PID ${pid}`)
                else if (platform === "darwin") exec(`kill ${pid}`)
                else if (platform === "linux") exec(`killall ${pid}`)
                resolve(`Port ${port} closed`)
            } else {reject(`Port ${port} already closed `)}

        })
    })
}

let mainWindow: BrowserWindow | null;

function createWindow() {

	const { width, height } = screen.getPrimaryDisplay().workAreaSize;
	mainWindow = new BrowserWindow({
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

	mainWindow.loadURL(
		url.format({
			pathname: path.join(__dirname, "../static/index.html"),
			protocol: "file:",
			slashes: true
		})
	);

	// Open the DevTools.
	// mainWindow.openDevTools({ mode: "detach" });

	mainWindow.once("ready-to-show", () => {
		if (mainWindow!=null){mainWindow.show();}
	});

	mainWindow.on("closed", function() {
		killPort(8501).then((result:any)=>console.log(result)).catch((err:any)=>console.log(err))

		mainWindow = null;
	});


	mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {
		event.preventDefault()
		
		Object.assign(options, {
			parent: mainWindow,
			width: width*.75,
			height: 600,
			frame: true,
		})

		let newWindow = event.newGuest = new BrowserWindow(options)
		newWindow.on("closed", ()=>{
			console.log("Window closed")
			killPort(8501).then((result:any)=>console.log(result)).catch((err:any)=>console.log(err))

		})

		// console.log(newWindow)

	  })
}

app.on("ready", createWindow);

app.on("window-all-closed", function() {

	// Except for macOS
	if (process.platform !== "darwin") {
		app.quit();
	}
});

app.on("activate", function() {
	if (mainWindow === null) { createWindow() }
});