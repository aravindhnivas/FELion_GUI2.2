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
			nodeIntegration: true
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
