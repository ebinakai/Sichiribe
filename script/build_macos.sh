#!/bin/bash

set -ex

# アーキテクチャの指定
ARCH=$(uname -m)

# 環境変数設定
if [ "$ARCH" = "x86_64" ]; then
    export CFLAGS="-arch x86_64"
    export CXXFLAGS="-arch x86_64"
    export LDFLAGS="-arch x86_64 -L/opt/homebrew/opt/gettext/lib -lintl"
    export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"
else
    export LDFLAGS="-L/opt/homebrew/opt/gettext/lib -lintl"
    export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"
fi

echo "Starting build with Nuitka for $ARCH..."

# リネーム（何故か app-name の指定が効かない）
cp -f app.py Sichiribe.py

# ビルド

python -m nuitka \
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
BUILD_STATUS=$? # ビルドの終了ステータスを取得

# 不要なファイルは削除する
rm Sichiribe.py

# ビルドが失敗した場合にエラーメッセージを表示
if [ $BUILD_STATUS -ne 0 ]; then
    echo "ビルドが失敗しました"
fi

# パッケージング
DMG_NAME="Sichiribe.dmg"
if [ "$ARCH" = "x86_64" ]; then
    DMG_NAME="Sichiribe_x86_64.dmg"
fi

# パッケージング
rm -f Sichiribe.dmg
echo "DMG creating..."
create-dmg --window-size 920 660 \
            --background "script/background.png" \
            --icon "Sichiribe.app" 200 240 \
            --app-drop-link 550 240 \
            "$DMG_NAME" \
            Sichiribe.app

echo "DMG created!"

# 不要なファイルを削除
rm -rf Sichiribe.app
rm -rf Sichiribe.dist