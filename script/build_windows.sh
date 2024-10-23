#!/bin/bash

echo "Yes" | \
python -m nuitka \
    --onefile \
    --standalone \
    --show-progress \
    --product-name=Sichiribe \
    --windows-icon-from-ico=script/Sichiribe_icon.png \
    --enable-plugins=pyside6 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model=model \
    --include-data-dir=./gui/images=gui/images/splash_image.png \
    --product-version=1.0.0 \
    app.py