#!/bin/bash

# 環境変数
export LDFLAGS="-L/opt/homebrew/opt/gettext/lib -lintl"
export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"

nuitka \
    --enable-plugin=pyside6 \
    --macos-create-app-bundle \
    --macos-signed-app-name=tech.ebic.shichribe \
    --macos-app-name=Sichiribe \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model=model \
    --include-data-dir=./gui/images=gui/images \
    --macos-app-icon=Sichiribe.ico \
    --macos-app-protected-resource="NSCameraUsageDescription:Camera access" \
    --output-dir=Sichiribe \
    app.py