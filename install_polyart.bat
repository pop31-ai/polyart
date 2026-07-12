@echo off
:: Установщик PolyArt Viewer
:: Ассоциирует .polyart файлы с просмотрщиком

set VIEWER=%~dp0polyart_viewer.py
set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

echo.
echo  ╔══════════════════════════════════════╗
echo  ║    PolyArt Viewer - Установка        ║
echo  ╚══════════════════════════════════════╝
echo.

:: Проверяем Python
if not exist "%PYTHON%" (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [!] Python не найден. Установите Python 3.10+
        pause
        exit /b 1
    )
    set PYTHON=python
)

echo [1/3] Копирование в Program Files...
if not exist "%PROGRAMFILES%\PolyArt" mkdir "%PROGRAMFILES%\PolyArt"
copy /Y "%VIEWER%" "%PROGRAMFILES%\PolyArt\polyart_viewer.py" >nul
copy /Y "%~dp0polyart_format.py" "%PROGRAMFILES%\PolyArt\polyart_format.py" >nul

echo [2/3] Создание ярлыка...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\shortcut.vbs"
echo Set oLink = oWS.CreateShortcut("%USERPROFILE%\Desktop\PolyArt Viewer.lnk") >> "%temp%\shortcut.vbs"
echo oLink.TargetPath = "%PYTHON%" >> "%temp%\shortcut.vbs"
echo oLink.Arguments = """%PROGRAMFILES%\PolyArt\polyart_viewer.py""" >> "%temp%\shortcut.vbs"
echo oLink.WorkingDirectory = "%PROGRAMFILES%\PolyArt" >> "%temp%\shortcut.vbs"
echo oLink.Description = "PolyArt Polynomial Renderer" >> "%temp%\shortcut.vbs"
echo oLink.IconLocation = "shell32.dll,13" >> "%temp%\shortcut.vbs"
cscript //nologo "%temp%\shortcut.vbs"
del "%temp%\shortcut.vbs"

echo [3/3] Ассоциация файлов...
reg add "HKCR\.polyart" /ve /t REG_SZ /d "PolyArtFile" /f >nul 2>&1
reg add "HKCR\PolyArtFile" /ve /t REG_SZ /d "PolyArt Polynomial Art" /f >nul 2>&1
reg add "HKCR\PolyArtFile\DefaultIcon" /ve /t REG_SZ /d "shell32.dll,13" /f >nul 2>&1
reg add "HKCR\PolyArtFile\shell\open\command" /ve /t REG_SZ /d "\"%PYTHON%\" \"%PROGRAMFILES%\PolyArt\polyart_viewer.py\" \"%%1\"" /f >nul 2>&1

echo.
echo  ✓ Установка завершена!
echo  ✓ Ярлык на рабочем столе: PolyArt Viewer
echo  ✓ Файлы .polyart открываются двойным кликом
echo.
pause
