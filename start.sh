#!/bin/bash
engine-front &
engine-back  
# python back_end/__init__.py &
# gunicorn -k eventlet -w 4 -b 0.0.0.0:5000 --timeout 120 "front_end:app()" 