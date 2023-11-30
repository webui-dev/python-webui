@echo off
SETLOCAL

:: This script downloads the trusted WebUI compiled library by GitHub CI for Windows.

IF "%1"=="minimal" (
    goto MINIMAL
)

:: --- Full -------------------------------------
:: Download WebUI library for all supported OS.
echo WebUI Deno Bootstrap
echo.

:: Creating the temporary cache folder
mkdir "cache" 2>nul 1>nul

:: Nightly Build
:: SET "LINUX_ARM=https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-arm.zip"
:: SET "LINUX_ARM64=https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-arm64.zip"
:: SET "LINUX_X64=https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-x64.zip"
:: SET "MACOS_ARM64=https://github.com/webui-dev/webui/releases/download/nightly/webui-macos-clang-arm64.zip"
:: SET "MACOS_X64=https://github.com/webui-dev/webui/releases/download/nightly/webui-macos-clang-x64.zip"
:: SET "WINDOWS_MSVC_X64=https://github.com/webui-dev/webui/releases/download/nightly/webui-windows-msvc-x64.zip"

:: Release
SET "LINUX_ARM=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-arm.zip"
SET "LINUX_ARM64=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-arm64.zip"
SET "LINUX_X64=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-x64.zip"
SET "MACOS_ARM64=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-macos-clang-arm64.zip"
SET "MACOS_X64=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-macos-clang-x64.zip"
SET "WINDOWS_MSVC_X64=https://github.com/webui-dev/webui/releases/download/2.4.2/webui-windows-msvc-x64.zip"

:: Download and extract archives
CALL :DOWNLOAD_AND_EXTRACT %LINUX_ARM% webui-linux-gcc-arm webui-2.so
CALL :DOWNLOAD_AND_EXTRACT %LINUX_ARM64% webui-linux-gcc-arm64 webui-2.so
CALL :DOWNLOAD_AND_EXTRACT %LINUX_X64% webui-linux-gcc-x64 webui-2.so
CALL :DOWNLOAD_AND_EXTRACT %MACOS_ARM64% webui-macos-clang-arm64 webui-2.dylib
CALL :DOWNLOAD_AND_EXTRACT %MACOS_X64% webui-macos-clang-x64 webui-2.dylib
CALL :DOWNLOAD_AND_EXTRACT %WINDOWS_MSVC_X64% webui-windows-msvc-x64 webui-2.dll

:: Remove cache folder
echo * Cleaning...
rmdir /S /Q "cache" 2>nul 1>nul
exit /b

:: Download and Extract Function
:DOWNLOAD_AND_EXTRACT
echo * Downloading [%1]...
SET FULL_URL=%1
SET FILE_NAME=%2
SET LIB_DYN=%3
SET LIB_STATIC=%4
powershell -Command "Invoke-WebRequest '%FULL_URL%' -OutFile 'cache\%FILE_NAME%.zip'"
echo * Extracting [%FILE_NAME%.zip]...
mkdir "cache\%FILE_NAME%" 2>nul 1>nul
tar -xf "cache\%FILE_NAME%.zip" -C "cache"
IF NOT "%LIB_DYN%"=="" (
    :: Copy dynamic library
    echo * Copying [%LIB_DYN%]...
    mkdir "%FILE_NAME%" 2>nul 1>nul
    copy /Y "cache\%FILE_NAME%\%LIB_DYN%" "%FILE_NAME%\%LIB_DYN%" 2>nul 1>nul
)
IF NOT "%LIB_STATIC%"=="" (
    :: Copy dynamic library
    echo * Copying [%LIB_STATIC%]...
    mkdir "%FILE_NAME%" 2>nul 1>nul
    copy /Y "cache\%FILE_NAME%\%LIB_STATIC%" "%FILE_NAME%\%LIB_STATIC%" 2>nul 1>nul
)
GOTO :EOF

:: --- Minimal ----------------------------------
:: Download WebUI library for only the current OS.
:MINIMAL

SET "BASE_URL=https://github.com/webui-dev/webui/releases/download/2.4.2/"

:: Check the CPU architecture
IF "%PROCESSOR_ARCHITECTURE%"=="x86" (
    :: x86 32Bit
    :: SET "FILENAME=webui-windows-msvc-x86"
    ECHO Error: Windows x86 32Bit architecture is not supported yet
    exit /b
) ELSE IF "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    :: x86 64Bit
    SET "FILENAME=webui-windows-msvc-x64"
) ELSE IF "%PROCESSOR_ARCHITECTURE%"=="ARM" (
    :: ARM 32Bit
    :: SET "FILENAME=webui-windows-msvc-arm"
    ECHO Error: Windows ARM architecture is unsupported yet
    exit /b
) ELSE IF "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    :: ARM 64Bit
    :: SET "FILENAME=webui-windows-msvc-arm64"
    ECHO Error: Windows ARM64 architecture is unsupported yet
    exit /b
) ELSE (
    ECHO Error: Unknown architecture '%PROCESSOR_ARCHITECTURE%'
    exit /b
)

:: Creating the temporary cache folder
mkdir "cache" 2>nul 1>nul
mkdir "cache\%FILENAME%" 2>nul 1>nul

:: Download the archive using PowerShell
powershell -Command "Invoke-WebRequest '%BASE_URL%%FILENAME%.zip' -OutFile 'cache\%FILENAME%.zip'"

:: Extract archive (Windows 10 and later)
tar -xf "cache\%FILENAME%.zip" -C "cache"

:: Copy library
mkdir "%FILENAME%" 2>nul 1>nul
copy /Y "cache\%FILENAME%\webui-2.dll" "%FILENAME%\webui-2.dll" 2>nul 1>nul

:: Remove cache folder
rmdir /S /Q "cache" 2>nul 1>nul

ENDLOCAL
