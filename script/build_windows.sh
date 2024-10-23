#!/bin/bash

python -m nuitka \
    --product-name=Sichiribe \
    --windows-icon-from-ico=script/Sichiribe_icon.png \
    --enable-plugins=pyside6 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-files=./model/model_100x100.keras=model/model_100x100.keras \
    --include-data-files=./gui/images/splash_image.png=gui/images/splash_image.png \
    --product-version=1.0.0 \
    --onefile \
    app.py