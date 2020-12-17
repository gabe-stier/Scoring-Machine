#!/bin/bash
python back_end/__init__.py &
gunicorn -w 4 \
    -b 0.0.0.0:5000 \
    --timeout $TIMEOUT \
    "front_end:app()" 