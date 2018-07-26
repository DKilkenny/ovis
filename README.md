# OVis: OpenMDAO Visualization
------------------------------

OVis is a desktop application that allows you to visualize the
data you've recorded using [OpenMDAO's](http://openmdao.org) SQLite recorder. To use,
simply open OVis, select your SQLite database file, and use the
N<sup>2</sup> diagram to view model hierarchy and plots
to see iteration history.

### Install

OVis is available for Windows, Mac, and Ubuntu.

1. Go to the OVis's [releases](https://github.com/OpenMDAO/Zune/releases)
and download the correct installer for your operating system from the most
recent release.

    * **Windows**: `OVis.Setup.x.y.z.exe`
    * **Mac**: `OVis-x.y.z.dmg`
    * **Ubuntu**: `OVis-x.y.z-x86_64.AppImage`

2. Once downloaded, double-click to run the installer. Note that,
for Windows, we do not yet sign the installer. As a result,
opening the file will likely result in a "Windows protected your
PC" popup. Click "_More info_" then "_Run anyway_" to proceed with
installation.

3. Follow the installer's instructions. Once complete, you
should be able to run the OVis executable.

## Development

OVis is written in a combination of Node.js, JavaScript,
HTML, and CSS using the Electron framework. Testing uses
Mocha, Chai, and spectron with babel-node
and isparta for code coverage. To begin developing OVis:

1. Install [Node.js and npm](https://nodejs.org/en/download/package-manager/)
2. Run `git clone https://github.com/OpenMDAO/zune.git`
3. Go to the cloned folder with `cd zune`
4. Run `npm install` to install all application dependencies.
    * **Note:** I've noticed there can be problems installing the
    _sqlite3_ library on macOS. If you run into this problem, try
    running the command again with Python 2 active.

If all goes well, you should now be able to start OVis with `npm
start`.

### Architecture

Electron applications run in [two processes](https://electronjs.org/docs/tutorial/application-architecture):
the **main** process and the **renderer** process, with
communication between these being performed
using a built-in IPC module. For OVis, the entirety of the logic for
the main process can be found in _main.js_, which is responsible for
application startup, file selection, and automatic updating. The
renderer process handles plotting, N<sup>2</sup> diagram logic,
layout, and interfacing with the SQLite file.

The renderer process can be
split into the HTML/CSS/JavaScript frontend and a Node.js backend
(formerly the python HTTP server). The backend can be found in the
'src/data_server' folder and implements an explicit three-tier
architecture. The backend's data layer queries the database, the
logic layer transforms the data into a more useful form, and the
presentation layer presents an API for requesting data. The interface between the backend and frontend can be found in
_server.js_.

### Test

As mentioned above, this application uses the _Mocha_ JavaScript test framework with _Chai_ for assertions and _isparta/babel-node_ for code coverage. _Spectron_ is used in end-to-end testing to run the application.

* Run tests with `npm test`
* Run tests and coverage with `npm run test-cov`

Currently, coverage isn't reported for the vanilla JS frontend
tested using the end-to-end Spectron tests. Rather than going
through the effort to get it to report coverage for for those files,
it would probably be best to convert them to Node.js and add unit
tests.

To ensure that new test files are run with the testing command, add them directly or in a sub-directory of the _test_ folder.

### Build, Release, and Updating

OVis takes advantage of the built-in _electron-builder_ and
_electron-updater_ for build and updating, respectively, and GitHub's
_Releases_ for release.

#### Build

Building OVis is as simple as running `npm run build`. This command
builds the installers and associated files for all supported
operating systems and stores them in the _dist_ folder.

* To build for **macOS** only: `npm run build:m`
* To build for **Windows** only: `npm run build:w`
* To build for **Ubuntu** only: `npm run build:l`

#### Release

Releases are handled on the OpenMDAO Zune repository's Releases on
GitHub.

1. Navigate to the Zune repository's [releases](https://github.com/openmdao/zune/releases)
2. Click "_Draft a new release_"
3. Add a tag version and attach the files in the _dist_ directory
that were generated when building
    * Do not attach the _mac_, _win-unpacked_, or _linux-unpacked_
    folders. These are intermediary files that can be discarded
4. Click "_Publish release_" when you're finished

#### Updating

OVis implements automatic updating so that users don't need to 
manually download new versions. Nothing needs to be done
to make this work with each release. A python HTTP server (see
[_github-release-http-server.py_](https://github.com/OpenMDAO/zune/blob/master/github-release-http-server.py)) running on WebFaction
pings GitHub every hour for new releases. If a new version is
available, this server downloads it from GitHub. OVis pings this
python server on startup to determine if a new version is available
and, if there is, downloads the update in the background and installs
it when the application is closed. We use the HTTP server as a
middle-man because Zune is a private repository and cannot be
accessed from OVis without unless it is shipped with a GitHub token
(an obvious security concern).
