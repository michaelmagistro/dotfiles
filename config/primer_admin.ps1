rem assoc .md=mdfile
rem ftype mdfile="%userprofile%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
rem assoc .txt=txtfile
rem ftype txtfile="%userprofile%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"
rem assoc .json=jsonfile
rem ftype jsonfile="%userprofile%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"

New-Item -Path 'HKCU:\Software\Classes\.md' -Force | Out-Null
New-ItemProperty -Path 'HKCU:\Software\Classes\.md' -Name '(Default)' -Value 'SublimeText' -PropertyType String -Force | Out-Null
New-Item -Path 'HKCU:\Software\Classes\SublimeText' -Force | Out-Null
New-Item -Path 'HKCU:\Software\Classes\SublimeText\shell' -Force | Out-Null
New-Item -Path 'HKCU:\Software\Classes\SublimeText\shell\open' -Force | Out-Null
New-ItemProperty -Path 'HKCU:\Software\Classes\SublimeText\shell\open\command' -Name '(Default)' -Value '"%userprofile%\Dropbox\prt\SublimeText\sublime_text.exe" "%1"' -PropertyType String -Force | Out-Null

New-Item -Path 'HKCU:\Software\Classes\.txt' -Force | Out-Null
New-ItemProperty -Path 'HKCU:\Software\Classes\.txt' -Name '(Default)' -Value 'SublimeText' -PropertyType String -Force | Out-Null
