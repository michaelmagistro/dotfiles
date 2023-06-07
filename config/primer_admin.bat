@echo off

rem Get the path to the user's home directory
set "home=%USERPROFILE%"

rem Copy the files from the config_pointers directory to the home directory
xcopy /I /E "%USERPROFILE%\pro\dotfiles\pointers" "%home%"


@echo off
net session >nul 2>&1
if %errorlevel% == 0 (
    echo Running as administrator

    rem IF you don't have Admin privilege, you can instead use the windows utility "choose a default app for each type of file". Or, win + r and "control /name Microsoft.DefaultPrograms". You should be brought to a page where you can set a default app for each type of file or there should be a link to get there on Win 10.
    rem assoc and ftyle need to be on separate lines (can't be on the same line with &&)
	assoc .txt=txtfile
		ftype txtfile="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .md=mdfile
		ftype mdfile="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .json=jsonfile
		ftype jsonfile="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .ps1=powershellfile
		ftype powershellfile="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .sublime-workspace=sublimeworkspace
		ftype sublimeworkspace="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .sublime-project=sublimeproject
		ftype sublimeproject="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .data=datafile
		ftype datafile="%USERPROFILE%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
	assoc .=sublime
		ftype sublime="C:\path\to\sublime_text.exe" "%1"
	
	rem reset the explorer to see the new file associations take root
	taskkill /f /im explorer.exe
	timeout 3
	start explorer.exe
) else (
    echo Not running as administrator
)


timeout 5