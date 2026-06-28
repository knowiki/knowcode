[Setup]
AppName=KnowCode
AppVersion=0.1.10
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

[Code]
const
  EnvironmentKey = 'Environment';

procedure CurUninstallStepChanged(UninstallStep: TUninstallStep);
var
  Path: String;
  AppPath: String;
  Index: Integer;
begin
  if UninstallStep = usPostUninstall then
  begin
    if RegQueryStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path) then
    begin
      AppPath := ExpandConstant('{app}');
      // Remove ';{app}'
      Index := Pos(';' + AppPath, Path);
      if Index > 0 then
      begin
        Delete(Path, Index, Length(';' + AppPath));
        RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path);
      end
      else
      begin
        // Remove '{app};'
        Index := Pos(AppPath + ';', Path);
        if Index > 0 then
        begin
          Delete(Path, Index, Length(AppPath + ';'));
          RegWriteStringValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path', Path);
        end
        else if Path = AppPath then
        begin
          RegDeleteValue(HKEY_CURRENT_USER, EnvironmentKey, 'Path');
        end;
      end;
    end;
  end;
end;
