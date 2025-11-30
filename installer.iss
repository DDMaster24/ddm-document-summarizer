; Inno Setup Script for Document Summarizer
; This creates a professional Windows installer

#define MyAppName "Document Summarizer"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://yourwebsite.com"
#define MyAppExeName "DocumentSummarizer.exe"

[Setup]
; App information
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=DocumentSummarizerSetup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The main executable
Source: "dist\DocumentSummarizer.exe"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Start Menu icon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon (if user selected it)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Offer to run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Check if the app is already running
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  // Check if app is running
  if CheckForMutexes('DocumentSummarizerMutex') then
  begin
    MsgBox('Document Summarizer is currently running. Please close it before installing.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;
