#!/bin/bash

# This script downloads the trusted WebUI compiled library by GitHub CI for Linux.

if [[ "$1" == "" ]]; then

    # --- Full -------------------------------------
    # Download WebUI library for all supported OS.
    echo "WebUI Deno Bootstrap"
    echo

    # Creating the temporary cache folder
    mkdir -p "cache" 2>/dev/null

    # Nightly Build
    # LINUX_ARM="https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-arm.zip"
    # LINUX_ARM64="https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-arm64.zip"
    # LINUX_X64="https://github.com/webui-dev/webui/releases/download/nightly/webui-linux-gcc-x64.zip"
    # MACOS_ARM64="https://github.com/webui-dev/webui/releases/download/nightly/webui-macos-clang-arm64.zip"
    # MACOS_X64="https://github.com/webui-dev/webui/releases/download/nightly/webui-macos-clang-x64.zip"
    # WINDOWS_MSVC_X64="https://github.com/webui-dev/webui/releases/download/nightly/webui-windows-msvc-x64.zip"

    # Release
    LINUX_ARM="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-arm.zip"
    LINUX_ARM64="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-arm64.zip"
    LINUX_X64="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-linux-gcc-x64.zip"
    MACOS_ARM64="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-macos-clang-arm64.zip"
    MACOS_X64="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-macos-clang-x64.zip"
    WINDOWS_MSVC_X64="https://github.com/webui-dev/webui/releases/download/2.4.2/webui-windows-msvc-x64.zip"

    # Download and extract archives
    download_and_extract() {
        echo "* Downloading [$1]..."
        wget -q "$1" -O "cache/$2.zip"
        echo "* Extracting [$2.zip]..."
        mkdir -p "cache/$2" 2>/dev/null
        unzip -q "cache/$2.zip" -d "cache"
        if [ -n "$3" ]; then
            echo "* Copying [$3]..."
            mkdir -p "$2" 2>/dev/null
            cp -f "cache/$2/$3" "$2/$3"
        fi
        if [ -n "$4" ]; then
            echo "* Copying [$4]..."
            mkdir -p "$2" 2>/dev/null
            cp -f "cache/$2/$4" "$2/$4"
        fi
    }

    download_and_extract $LINUX_ARM "webui-linux-gcc-arm" "webui-2.so"
    download_and_extract $LINUX_ARM64 "webui-linux-gcc-arm64" "webui-2.so"
    download_and_extract $LINUX_X64 "webui-linux-gcc-x64" "webui-2.so"
    download_and_extract $MACOS_ARM64 "webui-macos-clang-arm64" "webui-2.dylib"
    download_and_extract $MACOS_X64 "webui-macos-clang-x64" "webui-2.dylib"
    download_and_extract $WINDOWS_MSVC_X64 "webui-windows-msvc-x64" "webui-2.dll"

    # Remove cache folder
    echo "* Cleaning..."
    rm -rf "cache"
    exit 0
fi

if [[ "$1" == "minimal" ]]; then

    # --- Minimal ----------------------------------
    # Download WebUI library for only the current OS.

    # Nightly Build
    # BASE_URL="https://github.com/webui-dev/webui/releases/download/nightly/"

    # Release
    BASE_URL="https://github.com/webui-dev/webui/releases/download/2.4.2/"

    # Detect OS (macOS / Linux)
    OS="linux"
    CC="gcc"
    EXT="so"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        CC="clang"
        EXT="dylib"
    fi

    # Check the CPU architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86" ]; then
        # x86 32Bit
        # FILENAME="webui-${OS}-${CC}-x86"
        echo "Error: Linux/macOS x86 32Bit architecture is not supported yet"
        exit 1
    elif [ "$ARCH" = "x86_64" ]; then
        # x86 64Bit
        FILENAME="webui-${OS}-${CC}-x64"
    elif [ "$ARCH" = "arm" ]; then
        # ARM 32Bit
        FILENAME="webui-${OS}-${CC}-arm"
    elif [ "$ARCH" = "aarch64" ]; then
        # ARM 64Bit
        FILENAME="webui-${OS}-${CC}-arm64"
    else
        echo "Error: Unknown architecture '$ARCH'"
        exit 1
    fi

    # Creating the temporary cache folder
    mkdir -p "cache/$FILENAME" 2>/dev/null

    # Download the archive using wget
    wget -q "$BASE_URL$FILENAME.zip" -O "cache/$FILENAME.zip"

    # Extract archive
    unzip -q "cache/$FILENAME.zip" -d "cache"

    # Copy library
    mkdir -p "$FILENAME" 2>/dev/null
    cp -f "cache/$FILENAME/webui-2.${EXT}" "$FILENAME/webui-2.${EXT}"

    # Remove cache folder
    rm -rf "cache"

    exit 0
fi
