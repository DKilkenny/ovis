'use strict'

const electron = require('electron')
const spawn = require('child_process').spawn
const request = require('request')
const querystring = require('querystring')
const logger = require('electron-log');
const fs = require('fs')

// Module to control application life.
const app = electron.app
const Menu = electron.Menu;

// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow

const dialog = require('electron').dialog
const ipcMain = require('electron').ipcMain

const path = require('path')
const url = require('url')

let filename = 'No File Selected'
var py = null;

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({ width: 800, height: 600 })

  // and load the index.html of the app.
  mainWindow.loadURL(url.format({
    pathname: path.join(__dirname, 'need_load.html'),
    protocol: 'file:',
    slashes: true
  }))

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.


// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow()
    mainWindow.maximize();
  }
})

app.on('will-quit', function() {
  py.stdin.pause();
  py.stderr.pause();
  py.stdout.pause();
  py.kill();
})

function findFile() {
  dialog.showOpenDialog((fileNames) => {
    if (fileNames === undefined) {
      logger.info("No file selected");
      return;
    }

    logger.info("Sending 'connect' with: " + fileNames[0])

    request.post('http://127.0.0.1:18403/connect',
      { json: { 'location': fileNames[0] } },
      function (error, response, body) {
        if (error) {
          logger.error("ERROR: " + error.toString())
          return;
        }
        logger.info("Connected to DB");
      });

    filename = fileNames[0]
    mainWindow.webContents.send('connect', fileNames)
    mainWindow.loadURL(url.format({
      pathname: path.join(__dirname, 'index.html'),
      protocol: 'file:',
      slashes: true
    }))
  })
}



// const template = [
//   {
//     label: 'File',
//     submenu: [
//       {
//         role: 'open',
//         label: 'Open',
//         accelerator: 'CmdOrCtrl+o',
//         click() {
//           findFile();
//         }
//       }
//     ]
//   },
//   {
//     label: 'View',
//     submenu: [
//       {
//         accelerator: 'CmdOrCtrl+Shift+i',
//         role: 'toggle dev tools',
//         label: 'Toggle Developer Tools',
//         click() { mainWindow.webContents.openDevTools(); }
//       },
//       {
//         accelerator: 'CmdOrCtrl+r',
//         role: 'refresh',
//         label: 'Refresh Page',
//         click() { mainWindow.webContents.reloadIgnoringCache(); }
//       }
//     ]
//   }
// ]
const template = [
  {
    label: 'Edit',
    submenu: [
      { role: 'undo' },
      { role: 'redo' },
      { type: 'separator' },
      { role: 'cut' },
      { role: 'copy' },
      { role: 'paste' },
      { role: 'pasteandmatchstyle' },
      { role: 'delete' },
      { role: 'selectall' }
    ]
  },
  {
    label: 'View',
    submenu: [
      { role: 'reload' },
      { role: 'forcereload' },
      { role: 'toggledevtools' },
      { type: 'separator' },
      { role: 'resetzoom' },
      { role: 'zoomin' },
      { role: 'zoomout' },
      { type: 'separator' },
      { role: 'togglefullscreen' }
    ]
  },
  {
    role: 'window',
    submenu: [
      { role: 'minimize' },
      { role: 'close' }
    ]
  },
  {
    role: 'help',
    submenu: [
      {
        label: 'Learn More',
        click() { require('electron').shell.openExternal('https://electronjs.org') }
      }
    ]
  }
]

if (process.platform === 'darwin') {
  template.unshift({
    label: app.getName(),
    submenu: [
      // { role: 'about' },
      { type: 'separator' },
      { role: 'services', submenu: [] },
      { type: 'separator' },
      { role: 'hide' },
      { role: 'hideothers' },
      { role: 'unhide' },
      { type: 'separator' },
      { role: 'quit' }
    ]
  })

  // Edit menu
  template[1].submenu.push(
    { type: 'separator' },
    {
      label: 'Speech',
      submenu: [
        { role: 'startspeaking' },
        { role: 'stopspeaking' }
      ]
    }
  )

  // Window menu
  template[3].submenu = [
    { role: 'close' },
    { role: 'minimize' },
    { role: 'zoom' },
    { type: 'separator' },
    { role: 'front' }
  ]
}

ipcMain.on('openFile', (event, arg) => {
  mainWindow.webContents.send('test', ['blah'])
  findFile();
  logger.info('Opening file')
  mainWindow.webContents.send('test')
});

ipcMain.on('getFilename', (event, arg) => {
  let fns = filename.split('\\');
  event.sender.send('filenameReply', fns[fns.length - 1]);
});

function startServer() {
  let resourceLocation = process.resourcesPath;
  py = spawn('python', [resourceLocation + '/main.py'])
  py.stdout.on('data', function (data) {
    logger.info("STDOUT: " + data);
  })
  py.stderr.on('data', function (data) {
    logger.error("ERROR: " + data)
  })
}

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
app.on('ready', createWindow, function() {
})
//Start the server
startServer()