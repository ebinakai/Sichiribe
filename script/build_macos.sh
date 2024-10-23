#!/bin/bash

set -ex

# アーキテクチャの指定
export LDFLAGS="-L/opt/homebrew/opt/gettext/lib -lintl"
export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"

cp -f app.py Sichiribe.py
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
rm -rf Sichiribe.py Sichiribe.dist
