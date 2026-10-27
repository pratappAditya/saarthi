; Saarthi Windows Desktop Application Installer Script
; Designed for Inno Setup 6+

#define MyAppName "Saarthi"
#define MyAppVersion "1.0.0-beta.1"
#define MyAppPublisher "Saarthi AI Team"
#define MyAppURL "https://github.com/saarthi-ai/saarthi"
#define MyAppExeName "Saarthi.exe"

[Setup]
AppId={{E7E6C16C-C56B-4725-9921-BF3882EBBDDD}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=Saarthi-v1.0.0-beta.1-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=..\release\windows

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Complete Standalone PyInstaller Bundle (Executables, _internal DLLs, Python runtime, Frontend dist)
Source: "..\dist\Saarthi\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Code]
// Preserve %LOCALAPPDATA%\Saarthi user data directory on uninstall
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // User data in %LOCALAPPDATA%\Saarthi is intentionally PRESERVED across uninstalls.
  end;
end;

