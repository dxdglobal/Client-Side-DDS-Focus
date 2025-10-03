[Setup]
AppName=DDS FocusPro
AppVersion=1.4
DefaultDirName={localappdata}\DDSFocusPro
DefaultGroupName=DDS FocusPro
OutputDir=output
OutputBaseFilename=DDSFocusProSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest 
SetupIconFile=icon.ico 

[Files]
; Main executables (with embedded icons)
Source: "FocusProapp.exe"; DestDir: "{app}"; DestName: "FocusProapp.exe"; Flags: ignoreversion
Source: "connector.exe"; DestDir: "{app}"; DestName: "connector.exe"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Essential Flask application folders (now in same directory)
Source: "static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files (now in same directory)
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion
Source: "themes.json"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Only create essential directories (removed user_cache as per your request)
Name: "{app}\data"
Name: "{app}\logs"
Name: "{app}\output"

[Icons]
Name: "{group}\DDS FocusPro"; Filename: "{app}\FocusProapp.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\DDS FocusPro"; Filename: "{app}\FocusProapp.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
; Optional: Run the application after installation
Filename: "{app}\FocusProapp.exe"; Description: "Launch DDS FocusPro"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up application data on uninstall
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\output"

[Code]
// No additional code needed