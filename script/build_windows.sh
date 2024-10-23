#!/bin/bash

python -m nuitka \
    --product-name=Sichiribe \
    --enable-plugins=pyside6 \
    --product-version=1.0.0 \
    --include-module=matplotlib.backends.backend_qt5agg \
    --include-data-dir=./model=model \
    --include-data-dir=./gui/images=gui/images \
    app.py