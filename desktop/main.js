const { app, BrowserWindow } = require("electron");
function createWindow(){const win=new BrowserWindow({width:1440,height:960,webPreferences:{nodeIntegration:false,contextIsolation:true}});win.loadURL(process.env.QC_INTEL_WEB_URL || "http://localhost:5173");}
app.whenReady().then(createWindow);app.on("window-all-closed",()=>{if(process.platform!=="darwin")app.quit();});app.on("activate",()=>{if(BrowserWindow.getAllWindows().length===0)createWindow();});
