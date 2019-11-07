import * as path from "path";
import * as url from "url";
import { app, BrowserWindow, screen } from "electron";

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
		mainWindow = null;
	});


	mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {
		if (frameName === 'modal') {
		  event.preventDefault()
		  Object.assign(options, {
			// modal: true,
			parent: mainWindow,
			width: 1000,
			height: 600,
			frame: true,
			backgroundColor: "#fafafa",
		})
		  event.newGuest = new BrowserWindow(options)
		}
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
	if (mainWindow === null) {
		createWindow();
	}
});
