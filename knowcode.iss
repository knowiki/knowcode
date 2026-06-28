[Setup]
AppName=KnowCode
AppVersion=0.1.9
DefaultDirName={localappdata}\KnowCode
DefaultGroupName=KnowCode
UninstallDisplayIcon={app}\know.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=knowcode-windows-installer
DisableProgramGroupPage=yes
DisableDirPage=no
PrivilegesRequired=lowest

[Files]
Source: "dist\know.exe"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "Path"; ValueData: "{olddata};{app}"; Flags: preservestringtype
