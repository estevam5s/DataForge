; Instalador gráfico do DataForge para Windows — a "caixinha".
;
; Compilado pelo Inno Setup, que vem pré-instalado no runner
; 'windows-latest' do GitHub Actions:
;
;     iscc packaging\windows\dataforge.iss
;
; O que ele instala é o executável único — a pasta que 'gerar_binario.py'
; produz, com o Python dentro. Quem instala por aqui NÃO precisa de
; Python nenhum, que é o ponto de ter um instalador gráfico: a pessoa
; que baixa um .exe não quer aprender o que é pip.

#define Nome "DataForge"
#define Versao "1.0.0"
#define Autor "Estevam Souza"
#define Site "https://dataforge-lang.vercel.app"

[Setup]
AppId={{7F3A9C21-4E8B-4D6A-9B12-DA7AF0RGE001}
AppName={#Nome}
AppVersion={#Versao}
AppPublisher={#Autor}
AppPublisherURL={#Site}
AppSupportURL={#Site}/docs
DefaultDirName={autopf}\{#Nome}
DefaultGroupName={#Nome}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist\pacotes
OutputBaseFilename=DataForge-{#Versao}-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Sem privilégio de administrador: instalar na pasta do usuário é o
; padrão para ferramenta de desenvolvimento, e evita o prompt do UAC.
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\..\editor\vscode\icone.ico
UninstallDisplayIcon={app}\dataforge.exe

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "path"; Description: "Adicionar o DataForge ao PATH (recomendado)"; \
    GroupDescription: "Integração com o sistema:"
Name: "assoc"; Description: "Associar os arquivos .df ao DataForge"; \
    GroupDescription: "Integração com o sistema:"; Flags: unchecked

[Files]
; A pasta inteira do executável — ele procura as bibliotecas ao lado.
Source: "..\..\dist\bin\dataforge\*"; DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#Nome} REPL"; Filename: "{app}\dataforge.exe"; \
    Parameters: "repl"
Name: "{group}\Documentação"; Filename: "{#Site}/docs"
Name: "{group}\Desinstalar {#Nome}"; Filename: "{uninstallexe}"

[Registry]
; O PATH do USUÁRIO, não o do sistema: sem admin, e sem mexer no que
; vale para todo mundo na máquina.
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
    ValueData: "{olddata};{app}"; Tasks: path; \
    Check: NaoEstaNoPath(ExpandConstant('{app}'))

Root: HKCU; Subkey: "Software\Classes\.df"; ValueType: string; \
    ValueName: ""; ValueData: "DataForge.Script"; \
    Flags: uninsdeletevalue; Tasks: assoc
Root: HKCU; Subkey: "Software\Classes\DataForge.Script"; ValueType: string; \
    ValueName: ""; ValueData: "Programa DataForge"; \
    Flags: uninsdeletekey; Tasks: assoc
Root: HKCU; Subkey: "Software\Classes\DataForge.Script\shell\open\command"; \
    ValueType: string; ValueName: ""; \
    ValueData: """{app}\dataforge.exe"" run ""%1"""; Tasks: assoc

[Run]
Filename: "{app}\dataforge.exe"; Parameters: "--version"; \
    Description: "Conferir a instalação"; Flags: postinstall nowait skipifsilent

[Code]
{ Não duplicar a pasta no PATH quando alguém reinstala. Um PATH com a
  mesma entrada quinze vezes é o que acontece quando ninguém confere. }
function NaoEstaNoPath(Pasta: string): Boolean;
var
  Atual: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Atual) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Uppercase(Pasta) + ';', ';' + Uppercase(Atual) + ';') = 0;
end;
