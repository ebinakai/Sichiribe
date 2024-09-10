#!/bin/bash

# 環境変数
export LDFLAGS="-L/opt/homebrew/opt/gettext/lib -lintl"
export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"

# ビルド
echo "Starting build with Nuitka..."
nuitka \
    --remove-output \
    --macos-create-app-bundle \
    --macos-app-name=Sichiribe \
    --macos-app-icon=script/Sichiribe_icon.png \
    --enable-plugins=pyside6 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model=model \
    --include-data-dir=./gui/images=gui/images \
    --macos-app-protected-resource="NSCameraUsageDescription:Camera access" \
    Sichiribe.py

# Nuitkaのビルドが成功したかどうかを確認
if [ $? -eq 0 ]; then
    echo "Nuitka build successful."

    # パッケージング
    rm -f Sichiribe.dmg
    echo "DMG creating..."
    create-dmg --window-size 920 660 \
               --background "script/background.png" \
               --icon "Sichiribe.app" 200 240 \
               --app-drop-link 550 240 \
               Sichiribe.dmg \
               Sichiribe.app

    echo "DMG created!"
else
    echo "Nuitka build failed. DMG creation aborted."
fi

# 不要なファイルを削除
rm -rf Sichiribe.app
rm -rf Sichiribe.dist