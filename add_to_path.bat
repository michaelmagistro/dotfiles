@echo off

setlocal

set "path_to_add=%USERPROFILE%\prt_spec\VSCodeInsiders\bin;%USERPROFILE%\prt_spec\VSCode\bin"

REM Check if the directories are already in PATH
echo %PATH% | findstr /C:"%path_to_add%" >nul
if %errorlevel% equ 0 (
    echo Directories are already in PATH.
) else (
    REM Add the directories to PATH
    echo Adding directories to PATH.
    setx PATH "%path_to_add%;%PATH%"
    echo PATH updated. Please restart your shell for the changes to take effect.
)

endlocal
