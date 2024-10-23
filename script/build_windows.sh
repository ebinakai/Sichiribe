#!/bin/bash

python -m nuitka \
    --product-name=Sichiribe \
    --windows-icon-from-ico=script/Sichiribe_icon.png \
    --enable-plugins=pyside6 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model/=model \
    --include-data-dir=./gui/images/=gui/images \
    --product-version=1.0.0 \
    app.py