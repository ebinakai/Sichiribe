#!/bin/bash

# 環境変数
export LDFLAGS="-L/opt/homebrew/opt/gettext/lib -lintl"
export CPPFLAGS="-I/opt/homebrew/opt/gettext/include"

nuitka \
    --macos-create-app-bundle \
    --macos-app-name=Sichiribe \
    --macos-app-icon=Sichiribe.ico \
    --enable-plugins=pyside6 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model=model \
    --include-data-dir=./gui/images=gui/images \
    --macos-app-protected-resource="NSCameraUsageDescription:Camera access" \
    Sichiribe.py