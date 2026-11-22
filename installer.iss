[Setup]
AppName=ClutterSweep
AppVersion=1.0.0
DefaultDirName={autopf}\ClutterSweep
DefaultGroupName=ClutterSweep
OutputDir=Output
OutputBaseFilename=ClutterSweep-Setup-v1.0.0
SetupIconFile=D:\cleaner\icon.ico
UninstallDisplayIcon={app}\ClutterSweep.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "D:\cleaner\dist\ClutterSweep\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ClutterSweep"; Filename: "{app}\ClutterSweep.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\ClutterSweep"; Filename: "{app}\ClutterSweep.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\ClutterSweep.exe"; Description: "Launch ClutterSweep"; Flags: nowait postinstall skipifsilent